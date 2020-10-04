# osmiter

A simple library for parsing OSM data.
Supports simple OSM XML files as well as OSM GZ, OSM BZ2 and OSM PBF.

Please be aware that osmiter uses Google's [protobuf](https://pypi.org/project/protobuf/) library,
written in pure Python, which isn't particularly fast.


## Example Usage

```python
import osmiter

shop_count = 0

for feature in osmiter.iter_from_osm("some_osm_file.osm"):
    if feature["type"] == "node" and "shop" in feature["tag"]:
        shop_count += 1

print(f"this osm file containes {shop_count} shop nodes")
```

## What is osmiter generating?

For each feature (node/way/relation) it yields a dict containing element attributes
(like `id`, `lat` or `timestamp`) and 2 additional items: key `"type"` holding `"node"/"way"/"relation"`
and key `"tag"` holding a dict with feature tags (this dict may be empty).

Additionally nodes will contain keys `"lat"` and `"lon"` with node coordinates,
ways will contain key `"nd"` with a list of all node_ids references by this way,
and relations contain a key `"member"` with a list of dicts of each member's attributes.

Almost all attributes are returned as strings with the exception for:
- `id`, `ref`, `version`, `changeset`, `uid` and `changeset_count` → int
- `lat`, `lon` → float
- `open` and `visible` → bool
- `timestamp` → [aware](https://docs.python.org/3/library/datetime.html#aware-and-naive-objects) [datetime.datetime](https://docs.python.org/3/library/datetime.html#datetime-objects) item.


#### Data validation
osmiter preforms almost no data validation, so it is possible to recieve ways with no nodes,
relations with no members, empty tag values, invalid coordinates, references to non-existing items,
or duplicate ids※.

However, several data assumptions are made:
1. Each feature has an `id` attribute.  
   (※) For OSM PBF files, if an object is missing an id `-1` will be assigned, per the osmformat.proto definition.
   This can result in multiple objects with an id equal to `-1`.
2. Each node has to have both `lat` and `lon` defined.
3. Every attribute defined in the table on attribute type conversion has to be convertible to its type.  
   So, `id == 0x1453`, `changeset_count == AAAAAA`, `ref == 12.433` or `lat == 1.23E+10` will cause an exception;  
   `timestamp` value has to be either ISO8601-compliant or epoch time represented by an integer.
4. Boolean atributes are only considered truthy if they're set to `true` (case-insensitive).
   Values `1`, `on`, `yes`, `ＴＲＵＥ` will all evaluate to False.

#### Minimum requirements for each element

Bare-minimum node:
```
{
    "id": int,
    "type": "node",
    "lat": float,
    "lon": float,
    "tag": Dict[str, str], # May be empty
}
```

Bare-minimum way:
```
{
    "id": int,
    "type": "way",
    "tag": Dict[str, str], # May be empty
    "nd": List[int],
}
```

Bare-minimum relation:
```
{
    "id": int,
    "type": "relation",
    "tag": Dict[str, str], # May be empty
    "member": List[ dict ]
}
```


#### Example elements

See the corresponding [OSM XML examples](https://wiki.openstreetmap.org/wiki/OSM_XML).

```
{
    "type": "node",
    "tag": {}
    "id": 298887269,
    "lat": 54.0901746,
    "lon": 12.2482632,
    "user": "SvenHRO",
    "uid": 46882,
    "visible": True,
    "version": 1,
    "changeset": 676636,
    "timestamp": datetime.datetime(2008, 9, 21, 21, 37, 45, tzinfo=datetime.timezone.utc)
}
```

```
{
    "type": "node",
    "tag": {"name": "Neu Broderstorf", "traffic_sign": "city_limit"},
    "id": 1831881213,
    "version": 1,
    "changeset": 12370172,
    "lat": 54.0900666,
    "lon": 12.2539381,
    "user": "lafkor",
    "uid": 75625,
    "visible": True,
    "timestamp": datetime.datetime(2012, 7, 20, 9, 43, 19, tzinfo=datetime.timezone.utc),
}
```

```
{
    "type": "way",
    "tag": {"highway": "unclassified", "name": "Pastower Straße"},
    "id": 26659127,
    "user": "Masch",
    "uid": 55988,
    "visible": True,
    "version": 5,
    "changeset": 4142606,
    "timestamp": datetime.datetime(2010, 3, 16, 11, 47, 8, tzinfo=datetime.timezone.utc),
    "nd": [292403538, 298884289, 261728686]
}
```

```
{
    "type": "relation",
    "tag": {
        "name": "Küstenbus Linie 123",
        "network": "VVW",
        "operator": "Regionalverkehr Küste",
        "ref": "123",
        "route": "bus",
        "type": "route"
    },
    "id": 56688,
    "user": "kmvar",
    "uid": 56190,
    "visible": True,
    "version": 28,
    "changeset": 6947637,
    "timestamp": datetime.datetime(2011, 1, 12, 14, 23, 49, tzinfo=datetime.timezone.utc),
    "member": [
        {"type": "node", "ref": 294942404, "role": ""},
        {"type": "node", "ref": 364933006, "role": ""},
        {"type": "way", "ref": 4579143, "role": ""},
        {"type": "node", "ref": 249673494, "role": ""},
    ]
}
```

## Reference

---

### osmiter.iter_from_osm
```
iter_from_osm(  
    source: Union[str, bytes, int, BinaryIO],  
    file_format: Union[str, NoneType] = None,  
    filter_attrs: Union[Iterable[str], NoneType] = None) -> Iterator[dict]
```

Yields all items from provided source file.

If source is a str/bytes (path) the format will be guess based on file extension.
Otherwise, if source is an int (file descriptior) or a file-like object,
the `format` argument must be provided, if the file format is different then OSM XML.

File-like sources have to be opened in binary mode.
Format has to be one of "xml", "gz", "bz2", "pbf".

osmiter spends most of its time parsing element attributes.
If only specific attributes are going to be used, pass an Iterable (most likely a set)
with wanted attributes to `filter_attrs`.

No matter what attributes you define in `filter_attrs`, some attributes are always parsed:
- "id", "lat" and "lon": for nodes
- "id": for ways and relations
- "type", "ref" and "role": for members

`filter_attrs` ignored for pbf files.

---

### osmiter.iter_from_xml_buffer
```
iter_from_xml_buffer(
    buff: BinaryIO,
    filter_attrs: Union[Iterable[str], NoneType] = None) -> Iterator[dict]
```

Yields all items inside a given OSM XML buffer.
`filter_attrs` is explained in osmiter.iter_from_osm documentation.

---

### osmiter.parser_xml.iter_from_xml_buffer
Same as `osmiter.iter_from_xml_buffer`.

---
### osmiter.parser_xml.OSMError
An exception (inheriting from `RuntimeException`) used to represent issues with XML data.

---

### osmiter.iter_from_pbf_buffer
```
iter_from_pbf_buffer(buff: BinaryIO) -> Iterator[dict]
```

Yields all items inside a given OSM PBF file.

---

### osmiter.parser_pbf.iter_from_pbf_buffer
Same as `osmiter.iter_from_pbf_buffer`.

---

### osmiter.parser_pbf.ParserPbf
Internal object used to parse PBF files. Don't use.

---

### osmiter.parser_pbf.PBFError
An Exception (inheriting from `RuntimeException`) used to represent issues with OSM PBF files.

---

## License

**osmiter** is provided under the MIT license, included in the `license.md` file.
