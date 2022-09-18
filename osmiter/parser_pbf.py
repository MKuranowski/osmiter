import itertools
import lzma
import struct
import zlib
from datetime import datetime, timezone
from typing import (IO, Any, Dict, Iterable, Iterator, Optional, Sequence,
                    TypeVar)

from .pbf.fileformat_pb2 import Blob, BlobHeader
from .pbf.osmformat_pb2 import (DenseNodes, HeaderBlock, Info, Node,
                                PrimitiveBlock, PrimitiveGroup, Relation, Way)

_T = TypeVar("_T")


class PBFError(RuntimeError):
    pass


class ParserPbf:
    buffer: IO[bytes]
    granulity: int
    offset_lat: int
    offset_lon: int
    string_table: Sequence[bytes]
    tstamp_granulity: int

    def __init__(self, buffer: IO[bytes]) -> None:
        self.buffer = buffer
        self.clear_pblock_values()

    def parse(self) -> Iterator[Dict[str, Any]]:
        # Read the header
        blob_header = self._read_blob_header("OSMHeader")
        if blob_header is None:
            raise PBFError("OSMHeader missing (is the file empty?)")
        blob_data = self._read_blob(blob_header.datasize)

        osm_header = HeaderBlock()
        osm_header.ParseFromString(blob_data)

        self.check_required_features(osm_header.required_features)

        # Iterate over all blobs
        while True:
            blob_header = self._read_blob_header("OSMData")

            # End of file
            if blob_header is None:
                break

            blob_data = self._read_blob(blob_header.datasize)

            pblock = PrimitiveBlock()
            pblock.ParseFromString(blob_data)

            # Save pblock attrs
            self.string_table = pblock.stringtable.s

            self.granulity = pblock.granularity
            self.offset_lat = pblock.lat_offset
            self.offset_lon = pblock.lon_offset
            self.tstamp_granulity = pblock.date_granularity

            # Parse data from all nested PrimitiveGroups
            yield from self._parse_pgroups(pblock.primitivegroup)

    @staticmethod
    def check_required_features(required_features: Iterable[str]) -> None:
        for feature in required_features:
            if feature not in {"OsmSchema-V0.6", "DenseNodes"}:
                raise PBFError(f"HeaderBlock requests feature {feature}, which is not implemented")

    def clear_pblock_values(self) -> None:
        self.granulity = 100
        self.offset_lat = 0
        self.offset_lon = 0
        self.string_table = []
        self.tstamp_granulity = 1000

    def _read_blob(self, blob_len: int) -> bytes:
        """Return the decompressed blob, given its length."""
        blob = Blob()
        blob.ParseFromString(self.buffer.read(blob_len))

        if blob.HasField("raw"):
            return blob.raw

        elif blob.HasField("zlib_data"):
            return zlib.decompress(blob.zlib_data)

        elif blob.HasField("lzma_data"):
            return lzma.decompress(blob.lzma_data)

        else:
            raise PBFError("pbf file has an empty blob or is using an unsupported compression")

    def _read_blob_header(self, verify_header_type: str) -> Optional[BlobHeader]:
        """Parse and return the BlobHeader, while verifying that its type is what is expected.
        Returns None if EOF was reached in the PBF file."""
        header_len_raw = self.buffer.read(4)

        if len(header_len_raw) == 0:
            return None

        elif len(header_len_raw) != 4:
            raise PBFError("invalid BlobHeader length prefix")

        header_len: int = struct.unpack("!L", header_len_raw)[0]

        blob_header = BlobHeader()
        blob_header.ParseFromString(self.buffer.read(header_len))

        if blob_header.type != verify_header_type:
            raise PBFError(
                f"expected a BlobHeader of type {verify_header_type}, "
                f"but got {blob_header.type}"
            )

        return blob_header

    def _read_info(self, info_item: Info) -> Dict[str, Any]:
        """Parse Info message and return all set metadata"""
        info_dict: Dict[str, Any] = {
            "version": info_item.version,
        }

        # timestamp
        if info_item.HasField("timestamp"):
            tstamp = (info_item.timestamp * self.tstamp_granulity) / 1000
            info_dict["timestamp"] = datetime.fromtimestamp(tstamp, tz=timezone.utc)

        # changeset
        if info_item.HasField("changeset"):
            info_dict["changeset"] = info_item.changeset

        # uid
        if info_item.HasField("uid"):
            info_dict["uid"] = info_item.uid

        # username
        if info_item.HasField("user_sid"):
            info_dict["user"] = self.string_table[info_item.user_sid].decode("utf8")

        # uid
        if info_item.HasField("visible"):
            info_dict["visible"] = info_item.visible

        return info_dict

    def _read_denseinfo(self, all_dense: DenseNodes) -> Iterator[Dict[str, Any]]:
        """Parse all parallel arrays of a DenseInfo object"""
        if not all_dense.HasField("denseinfo"):
            return itertools.repeat({})

        # Iterators for all metadata
        versions = all_dense.denseinfo.version or itertools.repeat(0)
        tstamps = all_dense.denseinfo.timestamp or itertools.repeat(None)
        changesets = all_dense.denseinfo.changeset or itertools.repeat(None)
        uids = all_dense.denseinfo.uid or itertools.repeat(None)
        user_sids = all_dense.denseinfo.user_sid or itertools.repeat(None)
        visibles = all_dense.denseinfo.visible or itertools.repeat(None)

        # Delta Coded Values
        tstamp: int = 0
        changeset: int = 0
        uid: int = 0
        user_sid: int = 0

        for version, dtstamp, dchangeset, duid, duser_sid, visible in \
                zip(versions, tstamps, changesets, uids, user_sids, visibles):

            info_dict: Dict[str, Any] = {}

            # Normal values, always defined
            info_dict["version"] = version

            # Delta Coded values, sometimes None
            if duid is not None:
                uid += duid
                info_dict["uid"] = uid

            if duser_sid is not None:
                user_sid += duser_sid
                info_dict["user"] = self.string_table[user_sid].decode("utf8")

            if dchangeset is not None:
                changeset += dchangeset
                info_dict["changeset"] = uid

            if dtstamp is not None:
                tstamp += dtstamp
                tstamp_val = (tstamp * self.tstamp_granulity) / 1000
                info_dict["timestamp"] = datetime.fromtimestamp(tstamp_val, tz=timezone.utc)

            if visible is not None:
                info_dict["visible"] = visible

            yield info_dict

    def _get_tags(self, keys: Sequence[int], values: Sequence[int]) -> Dict[str, str]:
        """Parse parallel arrays of keys and values and return a dict with object's tags"""
        tags: Dict[str, str] = {}

        if len(keys) > 0 and len(values) > 0:

            for key, value in zip(keys, values):
                tags[self.string_table[key].decode("utf8")] = \
                    self.string_table[value].decode("utf8")

        return tags

    def _get_dense_tags(self, keys_vals: Sequence[int]) -> Iterator[Dict[str, str]]:
        """Decode the keys_vals array of a DenseNodes message."""
        if not keys_vals:
            while True:
                yield {}

        # WHO THOUGHT THIS IS A GREAT IDEA??????
        tag_index = 0
        max_item = len(keys_vals)

        while tag_index < max_item:
            tags: Dict[str, Any] = {}

            while keys_vals[tag_index] != 0:
                k = keys_vals[tag_index]
                v = keys_vals[tag_index + 1]
                tag_index += 2

                tags[self.string_table[k].decode("utf8")] = \
                    self.string_table[v].decode("utf8")

            yield tags
            tag_index += 1

    def _parse_pgroups(self, all_groups: Iterable[PrimitiveGroup]) -> Iterator[Dict[str, Any]]:
        """Yields all OSM features (nodes, ways, relations) from current PrimitiveBlock"""
        for group in all_groups:

            if len(group.nodes) > 0:
                yield from self._parse_nodes(group.nodes)

            elif group.HasField("dense"):
                yield from self._parse_dense(group.dense)

            elif len(group.ways) > 0:
                yield from self._parse_ways(group.ways)

            elif len(group.relations) > 0:
                yield from self._parse_rels(group.relations)

    def _parse_nodes(self, all_nodes: Iterable[Node]) -> Iterator[Dict[str, Any]]:
        """Parse all Node messages and yield all found nodes."""
        for node in all_nodes:
            item: Dict[str, Any] = {"type": "node"}

            item["id"] = node.id
            item["tag"] = self._get_tags(node.keys, node.vals)

            if node.HasField("info"):
                item.update(self._read_info(node.info))

            item["lat"] = (node.lat * self.granulity + self.offset_lat) / 10**9
            item["lon"] = (node.lon * self.granulity + self.offset_lon) / 10**9

            yield item

    def _parse_dense(self, all_dense: DenseNodes) -> Iterator[Dict[str, Any]]:
        """Return all nodes encoded inside a given DenseNodes element"""
        # start for delta_coding lats and lons
        node_lat, node_lon = 0, 0

        # node ids, default to -1
        if len(all_dense.id) < 1:
            node_id = -1
            id_generator = itertools.repeat(0)

        else:
            node_id = 0
            id_generator = all_dense.id

        # lats & lons
        if len(all_dense.lat) < 1:
            raise PBFError("Encountered a DenseNodes message with no latitudes!")

        if len(all_dense.lon) < 1:
            raise PBFError("Encountered a DenseNodes message with no longitudes!")

        # Dense Info
        dense_info = self._read_denseinfo(all_dense)

        # Tags
        tags = self._get_dense_tags(all_dense.keys_vals)

        # Wrapping-up the generator
        item_generator = zip(
            id_generator,
            all_dense.lat,
            all_dense.lon,
            dense_info,
            tags,
        )

        for delta_id, delta_lat, delta_lon, info, item_tags in item_generator:
            node_id += delta_id
            node_lat += delta_lat
            node_lon += delta_lon

            item: Dict[str, Any] = {"type": "node"}

            item["id"] = node_id
            item["tag"] = item_tags
            item.update(info)

            item["lat"] = (node_lat * self.granulity + self.offset_lat) / 10**9
            item["lon"] = (node_lon * self.granulity + self.offset_lon) / 10**9

            yield item

    def _parse_ways(self, all_ways: Iterable[Way]) -> Iterator[Dict[str, Any]]:
        """Parse all Way messages and yield all found ways."""
        for way in all_ways:
            item: Dict[str, Any] = {"type": "way"}

            item["id"] = way.id
            item["tag"] = self._get_tags(way.keys, way.vals)

            if way.HasField("info"):
                item.update(self._read_info(way.info))

            item["nd"] = []

            current_node = 0
            for delta in way.refs:
                current_node += delta
                item["nd"].append(current_node)  # type: ignore

            yield item

    def _parse_rels(self, all_rels: Iterable[Relation]) -> Iterator[Dict[str, Any]]:
        """Parse all Relation messages and yield all found relations."""
        for rel in all_rels:
            item: Dict[str, Any] = {"type": "relation"}

            item["id"] = rel.id
            item["tag"] = self._get_tags(rel.keys, rel.vals)

            if rel.HasField("info"):
                item.update(self._read_info(rel.info))

            item["member"] = []

            member_id = 0
            for role_sid, member_delta, member_type in \
                    zip(rel.roles_sid, rel.memids, rel.types):

                member_id += member_delta
                member_type = ["node", "way", "relation"][member_type]

                role_name = self.string_table[role_sid].decode("utf8")

                item["member"].append({  # type: ignore
                    "ref": member_id,
                    "type": member_type,
                    "role": role_name,
                })

            yield item


def iter_from_pbf_buffer(buff: IO[bytes]) -> Iterator[Dict[str, Any]]:
    """Yields all items inside a given OSM PBF buffer."""
    parser = ParserPbf(buff)
    yield from parser.parse()
