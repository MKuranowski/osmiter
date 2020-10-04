from datetime import datetime, timezone
import osmiter
import pytest
import os

# IMPORTANT NOTICE
# IF MAKING CHANGES TO example.osm **ALWAYS** CHECK IF BELOW CHECK VALUES ARE STILL CORRECT

# .OSM.PBF IS CONVERTED IN 3 STEPS:
# 1. osmconvert example.osm --fake-author -o=example.osm.valid;
# 2. Manually revert metadata for features with check_meta=yes
# 3. osmosis --rx example.osm.valid --wb example.osm.pbf
# THIS MEANS THAT PBF VALIDATION MAY FAIL ON VERIFYING METADATA

true_rel_count = 1
true_rel_mragowska = 3, "street", "way"  # no of elements, roles

true_way_warszawska_nd = [
    108213, 108215, 108217, 108219, 108221, 108223,
    108225, 108227, 108229, 108307, 108309, 108311,
]

true_way_bridge = 2
true_way_oneway = 2
true_way_count = 9

true_node_namedhotels = 5
true_node_giveway = 3
true_node_parking = 3
true_node_count = 62

true_meta_timestamp = datetime(2020, 2, 14, 13, 1, 15, tzinfo=timezone.utc)
true_meta_visible = True
true_meta_user = "Natsuyasumi"
true_meta_uid = 1384396


def actually_verify(feature_iterator, is_pbf=False):

    rel_count = 0
    way_count = 0
    node_count = 0

    way_bridge = 0
    way_oneway = 0

    node_namedhotels = 0
    node_giveway = 0
    node_parking = 0

    for feature in feature_iterator:

        # Check Metadata
        if feature["tag"].get("check_meta") == "yes":
            assert feature["timestamp"] == true_meta_timestamp
            assert feature["user"] == true_meta_user
            assert feature["uid"] == true_meta_uid

            if not is_pbf:
                assert feature["visible"] == true_meta_visible

        # Check relations
        if feature["type"] == "relation":
            rel_count += 1

            # Check Mrągowska street relation
            if feature["tag"].get("name") == "Mrągowska":

                assert len(feature["member"]) == true_rel_mragowska[0]

                for member in feature["member"]:
                    assert member["role"] == true_rel_mragowska[1]
                    assert member["type"] == true_rel_mragowska[2]

        elif feature["type"] == "way":
            way_count += 1

            # Check Warszawska street way
            if feature["tag"].get("name") == "Warszawska":
                assert feature["nd"] == true_way_warszawska_nd

            if feature["tag"].get("bridge") == "yes":
                way_bridge += 1

            if feature["tag"].get("oneway") == "yes":
                way_oneway += 1

        elif feature["type"] == "node":
            node_count += 1

            assert type(feature["lat"]) is float
            assert type(feature["lon"]) is float

            if feature["tag"].get("highway") == "give_way":
                node_giveway += 1

            elif feature["tag"].get("amenity") == "parking":
                node_parking += 1

            elif feature["tag"].get("tourism") == "hotel" and feature["tag"].get("name"):
                node_namedhotels += 1

    assert rel_count == true_rel_count
    assert way_count == true_way_count
    assert node_count == true_node_count

    assert way_bridge == true_way_bridge
    assert way_oneway == true_way_oneway

    assert node_namedhotels == true_node_namedhotels
    assert node_giveway == true_node_giveway
    assert node_parking == true_node_parking


def test_xml_str_source():
    source = "tests/example.osm"
    actually_verify(osmiter.iter_from_osm(source))


def test_gzip_bytes_source():
    source = os.fsencode("tests/example.osm.gz")
    actually_verify(osmiter.iter_from_osm(source))


def test_bz2_buffer_source():
    with open("tests/example.osm.bz2", mode="rb") as source:
        actually_verify(osmiter.iter_from_osm(source, file_format="bz2"))


def test_pbf_str_source():
    source = "tests/example.osm.pbf"
    actually_verify(osmiter.iter_from_osm(source), is_pbf=True)
