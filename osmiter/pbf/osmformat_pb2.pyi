# Warning! These stubs are not complete, and only
# contain methods and attributes used by osmiter.

from typing import List
from typing_extensions import Literal

class _AbstractMessage:
    def ParseFromString(self, seralized: bytes) -> None: ...
    def HasField(self, field_name: str) -> bool: ...

class HeaderBBox(_AbstractMessage):
    left: int
    right: int
    top: int
    bottom: int

class HeaderBlock(_AbstractMessage):
    bbox: HeaderBBox
    required_features: List[str]
    optional_features: List[str]
    writingprogram: str
    source: str

class Info(_AbstractMessage):
    version: int
    timestamp: int
    changeset: int
    uid: int
    user_sid: int
    visible: bool

class DenseInfo(_AbstractMessage):
    version: List[int]
    timestamp: List[int]  # delta coded
    changeset: List[int]  # delta coded
    uid: List[int]        # delta coded
    user_sid: List[int]   # delta coded
    visible: List[bool]


class Node(_AbstractMessage):
    id: int
    keys: List[int]
    vals: List[int]
    info: Info
    lat: int
    lon: int

class DenseNodes(_AbstractMessage):
    id: List[int]  # delta coded
    denseinfo: DenseInfo
    lat: List[int]  # delta coded
    lon: List[int]  # delta coded
    keys_vals: List[int]

class Way(_AbstractMessage):
    id: int
    keys: List[int]
    vals: List[int]
    info: Info
    refs: List[int]  # delta coded

class Relation(_AbstractMessage):
    id: int
    keys: List[int]
    vals: List[int]
    info: Info

    roles_sid: List[int]
    memids: List[int]  # delta coded
    types: List[Literal[0, 1, 2]]

class ChangeSet(_AbstractMessage):
    id: int

class PrimitiveGroup(_AbstractMessage):
    nodes: List[Node]
    dense: DenseNodes
    ways: List[Way]
    relations: List[Relation]
    changesets: List[ChangeSet]

class StringTable(_AbstractMessage):
    s: List[bytes]

class PrimitiveBlock(_AbstractMessage):
    def ParseFromString(self, seralized: bytes) -> None: ...
    def HasField(self, field_name: str) -> bool: ...

    stringtable: StringTable
    primitivegroup: List[PrimitiveGroup]
    granulity: int
    lat_offset: int
    lon_offset: int
    date_granulity: int
