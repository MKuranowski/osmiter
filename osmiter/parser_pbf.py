from datetime import datetime, timezone
from typing import BinaryIO, Iterator
import struct
import lzma
import zlib

from .pbf.fileformat_pb2 import Blob, BlobHeader
from .pbf.osmformat_pb2 import HeaderBlock, PrimitiveBlock

# pylint: disable=E1101
# pylint doesn't understand the reflecion done by protobuff implementation


def _dummy_iterator(thing=None):
    while True:
        yield thing


def _get_field(message, attr, default=None):
    if message.HasField(attr):
        return getattr(message, attr)

    else:
        return default


class PBFError(RuntimeError):
    pass


class ParserPbf:

    def __init__(self, buffer):
        self.buffer = buffer
        self.clear_pblock_values()

    def parse(self):
        blob_header = self._read_blob_header("OSMHeader")
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
            self.string_table = pblock.stringtable

            self.granulity = _get_field(pblock, "granularity", 100)
            self.offset_lat = _get_field(pblock, "lat_offset", 0)
            self.offset_lon = _get_field(pblock, "lon_offset", 0)
            self.tstamp_granulity = _get_field(pblock, "date_granularity", 1000)

            # Parse data from all nested PrimitiveGroups
            yield from self._parse_pgroups(pblock.primitivegroup)

    @staticmethod
    def check_required_features(required_features):
        for feature in required_features:
            if feature not in {"OsmSchema-V0.6", "DenseNodes"}:
                raise PBFError(f"HeaderBlock requests feature {feature}, which is not implemented")

    def clear_pblock_values(self):
        self.granulity = None
        self.offset_lat = None
        self.offset_lon = None
        self.string_table = None
        self.tstamp_granulity = None

    def _read_blob(self, blob_len: int):
        """Return the decompressed blob, given its length.
        """

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

    def _read_blob_header(self, verify_header_type: str):
        """Parse and return the BlobHeader, while verifying that its type is what is expected.
        """
        header_len_raw = self.buffer.read(4)

        if len(header_len_raw) == 0:
            return None

        elif len(header_len_raw) != 4:
            raise PBFError("invalid BlobHeader length prefix")

        header_len = struct.unpack("!L", header_len_raw)[0]

        blob_header = BlobHeader()
        blob_header.ParseFromString(self.buffer.read(header_len))

        if blob_header.type != verify_header_type:
            raise PBFError(
                f"expected a BlobHeader of type {verify_header_type}, "
                f"but got {blob_header.type}"
            )

        return blob_header

    def _read_info(self, info_item):
        """Parse Info message and return all set metadata
        """
        info_dict = {
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
            info_dict["user"] = self.string_table.s[info_item.user_sid].decode("utf8")

        # uid
        if info_item.HasField("visible"):
            info_dict["visible"] = info_item.visible

        return info_dict

    def _read_denseinfo(self, dinfo_item):
        """Parse all parallel arrays of a DenseInfo object
        """
        get_iterator = lambda attr_name, fallback: \
            getattr(dinfo_item, attr_name) if len(getattr(dinfo_item, attr_name)) > 0 \
            else _dummy_iterator(fallback)

        # Iterators for all metadata
        versions = get_iterator("version", -1)
        tstamps = get_iterator("timestamp", None)
        changesets = get_iterator("changeset", None)
        uids = get_iterator("uid", None)
        user_sids = get_iterator("user_sid", None)
        visibles = get_iterator("visible", None)

        # Delta Coded Values
        tstamp = 0
        changeset = 0
        uid = 0
        user_sid = 0

        for version, dtstamp, dchangeset, duid, duser_sid, visible in \
                zip(versions, tstamps, changesets, uids, user_sids, visibles):

            info_dict = {}

            # Normal values, always defined
            info_dict["version"] = version

            # Delta Coded values, sometimes None
            if duid is not None:
                uid += duid
                info_dict["uid"] = uid

            if duser_sid is not None:
                user_sid += duser_sid
                info_dict["user"] = self.string_table.s[user_sid].decode("utf8")

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

    def _get_tags(self, keys, values):
        """Parse parallel arrays of keys and values and return a dict with object's tags
        """
        tags = {}

        if len(keys) > 0 and len(values) > 0:

            for key, value in zip(keys, values):
                tags[self.string_table.s[key].decode("utf8")] = \
                    self.string_table.s[value].decode("utf8")

        return tags

    def _get_dense_tags(self, keys_vals):
        """Decode the key_vals array of a DenseNodes message.
        """
        # WHO THOUGHT THIS IS A GREAT IDEA??????
        tag_index = 0
        max_item = len(keys_vals)

        while tag_index < max_item:
            tags = {}

            while keys_vals[tag_index] != 0:
                k = keys_vals[tag_index]
                v = keys_vals[tag_index + 1]
                tag_index += 2

                tags[self.string_table.s[k].decode("utf8")] = \
                    self.string_table.s[v].decode("utf8")

            yield tags
            tag_index += 1

    def _parse_pgroups(self, all_groups):
        """Yields all OSM features (nodes, ways, relations) from current PrimitiveBlock
        """
        for group in all_groups:

            if len(group.nodes) > 0:
                yield from self._parse_nodes(group.nodes)

            elif group.HasField("dense"):
                yield from self._parse_dense(group.dense)

            elif len(group.ways) > 0:
                yield from self._parse_ways(group.ways)

            elif len(group.relations) > 0:
                yield from self._parse_rels(group.relations)

    def _parse_nodes(self, all_nodes):
        """Parse all Node messages and yield all found nodes.
        """
        for node in all_nodes:
            item = {"type": "node"}

            item["id"] = node.id
            item["tag"] = self._get_tags(node.keys, node.vals)

            if node.HasField("info"):
                item.update(self._read_info(node.info))

            item["lat"] = (node.lat * self.granulity + self.offset_lat) / 10**9
            item["lon"] = (node.lon * self.granulity + self.offset_lon) / 10**9

            yield item

    def _parse_dense(self, all_dense):
        """Return all nodes encoded inside a given DenseNodes element
        """
        # start for delta_coding lats and lons
        node_lat, node_lon = 0, 0

        # node ids, default to -1
        if len(all_dense.id) < 1:
            node_id = -1
            id_generator = _dummy_iterator(0)

        else:
            node_id = 0
            id_generator = all_dense.id

        # lats & lons
        if len(all_dense.lat) < 1:
            raise PBFError("Encountered a DenseNodes message with no latitudes!")

        if len(all_dense.lon) < 1:
            raise PBFError("Encountered a DenseNodes message with no longitudes!")

        # Dense Info
        if all_dense.HasField("denseinfo"):
            dense_info = self._read_denseinfo(all_dense.denseinfo)

        else:
            dense_info = _dummy_iterator(dict())

        # Tags
        if len(all_dense.keys_vals) > 0:
            tags = self._get_dense_tags(all_dense.keys_vals)

        else:
            tags = _dummy_iterator(dict())

        # Wrapping-up the generator
        item_generator = zip(
            id_generator, all_dense.lat, all_dense.lon,
            dense_info, tags
        )

        for delta_id, delta_lat, delta_lon, info, tags in item_generator:
            node_id += delta_id
            node_lat += delta_lat
            node_lon += delta_lon

            item = {"type": "node"}

            item["id"] = node_id
            item["tag"] = tags
            item.update(info)

            item["lat"] = (node_lat * self.granulity + self.offset_lat) / 10**9
            item["lon"] = (node_lon * self.granulity + self.offset_lon) / 10**9

            yield item

    def _parse_ways(self, all_ways):
        """Parse all Way messages and yield all found ways.
        """
        for way in all_ways:
            item = {"type": "way"}

            item["id"] = way.id
            item["tag"] = self._get_tags(way.keys, way.vals)

            if way.HasField("info"):
                item.update(self._read_info(way.info))

            item["nd"] = []

            current_node = 0
            for delta in way.refs:
                current_node += delta
                item["nd"].append(current_node)

            yield item

    def _parse_rels(self, all_rels):
        """Parse all Relation messages and yield all found relations.
        """
        for rel in all_rels:
            item = {"type": "relation"}

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

                role_name = self.string_table.s[role_sid].decode("utf8")

                item["member"].append({
                    "ref": member_id,
                    "type": member_type,
                    "role": role_name,
                })

            yield item


def iter_from_pbf_buffer(buff: BinaryIO) -> Iterator[dict]:
    """Yields all items inside a given OSM PBF buffer.
    """

    buff.seek(0)
    parser = ParserPbf(buff)
    yield from parser.parse()
