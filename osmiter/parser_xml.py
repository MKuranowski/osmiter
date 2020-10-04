from datetime import datetime, timezone
from typing import BinaryIO, Iterable, Iterator, Optional
import iso8601
import io

try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree


class OSMError(RuntimeError):
    pass


def _osm_attributes(attributes, filter_attrs):
    result = {}

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


def iter_from_xml_buffer(
        buff: BinaryIO,
        filter_attrs: Optional[Iterable[str]] = None) -> Iterator[dict]:
    """Yields all items inside a given OSM XML buffer.
    `filter_attrs` is explained in osmiter.iter_from_osm documentation.
    """

    buff.seek(0)

    # Set attribute filters
    if filter_attrs is not None:
        node_attrs = {"id", "lat", "lon"}.union(filter_attrs)
        wayrel_attrs = {"id"}.union(filter_attrs)
        member_attrs = {"type", "ref", "role"}.union(filter_attrs)
    else:
        node_attrs = None
        wayrel_attrs = None
        member_attrs = None

    # Iterate over elements in OSM data
    for _, elem in etree.iterparse(buff, events=["end"]):

        # Only interested in fully-populated elements
        if elem.tag not in {"node", "way", "relation"}:
            continue

        item = {}
        item["type"] = elem.tag
        item["tag"] = {i.attrib["k"]: i.attrib["v"] for i in elem.iter("tag")}

        # Update attributes
        if elem.tag == "node":
            item.update(_osm_attributes(elem.attrib, node_attrs))
        else:
            item.update(_osm_attributes(elem.attrib, wayrel_attrs))

        if "id" not in item:
            raise OSMError("osm file contains a feature without id")

        if elem.tag == "node":
            if "lat" not in item or "lon" not in item:
                raise OSMError(f"osm node {item['id']} has no lat/lon")

        elif elem.tag == "way":
            item["nd"] = [int(i.attrib["ref"]) for i in elem.iter("nd")]

        elif elem.tag == "relation":
            item["member"] = [_osm_attributes(i.attrib, member_attrs) for i in elem.iter("member")]

        elem.clear()
        yield item
