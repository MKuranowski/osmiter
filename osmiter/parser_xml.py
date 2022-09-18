import xml.sax
import xml.sax.xmlreader
from datetime import datetime, timezone
from typing import (IO, Any, Container, Dict, Iterable, Iterator, List,
                    Mapping, Optional)

import iso8601


class OSMError(RuntimeError):
    pass


def _osm_attributes(attributes: Mapping[str, str],
                    filter_attrs: Optional[Container[str]]) -> Dict[str, Any]:
    """Parses and converts OSM attributes"""
    result: Dict[str, Any] = {}

    for k, v in attributes.items():
        # check if attr filter was given and k should be parsed
        if filter_attrs is not None and k not in filter_attrs:
            continue

        # convert some keys to int
        if k in {"id", "ref", "version", "changeset", "uid", "comments_count"}:
            v = int(v)

        # convert those to float
        elif k in {"lat", "lon"}:
            v = float(v)

        # and those to bools
        elif k in {"open", "visible"}:
            v = v.casefold() == "true"

        # and parse timestamps
        elif k in {"timestamp"}:
            if v.isdigit():
                v = datetime.fromtimestamp(int(v), timezone.utc)

            else:
                v = iso8601.parse_date(v)

        # every other key stays as-is.
        result[k] = v

    return result


class OSMContentHandler(xml.sax.ContentHandler):
    """ContentHandler is a SAX Content Handler that collects encountered OSM elements"""
    def __init__(self, filter_attrs: Optional[Iterable[str]]) -> None:
        super().__init__()
        # All fully-processed features
        self.features: List[Dict[str, Any]] = []

        # Feature currently being processed
        self.feature: Dict[str, Any] = {}

        # Attribute filters for speed
        if filter_attrs is not None:
            self.node_attrs = {"id", "lat", "lon"}.union(filter_attrs)
            self.wayrel_attrs = {"id"}.union(filter_attrs)
            self.member_attrs = {"type", "ref", "role"}.union(filter_attrs)
        else:
            self.node_attrs = None
            self.wayrel_attrs = None
            self.member_attrs = None

    def startElement(self, name: str, attrs: Mapping[str, str]) -> None:
        """Handler when an XML element starts"""
        # New feature - reset `self.feature` & set attributes
        if name == "node":
            self.feature = {"type": name, "tag": {}}
            self.feature.update(_osm_attributes(attrs, self.node_attrs))

        elif name == "way":
            self.feature = {"type": name, "tag": {}, "nd": []}
            self.feature.update(_osm_attributes(attrs, self.wayrel_attrs))

        elif name == "relation":
            self.feature = {"type": name, "tag": {}, "member": []}
            self.feature.update(_osm_attributes(attrs, self.wayrel_attrs))

        # Nested xml elements

        elif name == "tag":
            self.feature["tag"][attrs["k"]] = attrs["v"]

        elif name == "nd":
            assert self.feature["type"] == "way"
            self.feature["nd"].append(int(attrs["ref"]))

        elif name == "member":
            assert self.feature["type"] == "relation"
            self.feature["member"].append(_osm_attributes(attrs, self.member_attrs))

    def endElement(self, name: str) -> None:
        """Handler when an XML element ends"""
        # We only care about closing of features
        if name not in {"node", "way", "relation"}:
            return

        # Sanity checks
        if "id" not in self.feature:
            raise OSMError("osm file contains a feature without id")

        if name == "node":
            if "lat" not in self.feature or "lon" not in self.feature:
                raise OSMError(f"osm node {self.feature['id']} has no lat/lon")

        # Move feature to processed features
        self.features.append(self.feature)
        self.feature = {}


def iter_from_xml_buffer(
        buff: IO[bytes],
        filter_attrs: Optional[Iterable[str]] = None,
        read_chunk_size: int = 8192) -> Iterator[Dict[str, Any]]:
    """Yields all items inside a given OSM XML buffer.
    `filter_attrs` is explained in osmiter.iter_from_osm documentation.
    """
    # Create helper objects
    handler = OSMContentHandler(filter_attrs)
    parser = xml.sax.make_parser()
    if not isinstance(parser, xml.sax.xmlreader.IncrementalParser):
        raise RuntimeError("xml.sax.make_parser() returned a non-incremental parser")
    parser.setContentHandler(handler)

    # Read data in chunks
    data = buff.read(read_chunk_size)
    while data:
        # Parse XML
        parser.feed(data)

        # Check if some features are available -
        # if so _move_ them to the user (so that we can discard them).
        if handler.features:
            yield from handler.features
            handler.features = []

        # Read next chunk
        data = buff.read(read_chunk_size)

    # Finalize the parser
    parser.close()

    # Final check if some features are left
    if handler.features:
        yield from handler.features
