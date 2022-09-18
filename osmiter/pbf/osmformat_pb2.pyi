from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ChangeSet(_message.Message):
    __slots__ = ["id"]
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class DenseInfo(_message.Message):
    __slots__ = ["changeset", "timestamp", "uid", "user_sid", "version", "visible"]
    CHANGESET_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    UID_FIELD_NUMBER: _ClassVar[int]
    USER_SID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    VISIBLE_FIELD_NUMBER: _ClassVar[int]
    changeset: _containers.RepeatedScalarFieldContainer[int]
    timestamp: _containers.RepeatedScalarFieldContainer[int]
    uid: _containers.RepeatedScalarFieldContainer[int]
    user_sid: _containers.RepeatedScalarFieldContainer[int]
    version: _containers.RepeatedScalarFieldContainer[int]
    visible: _containers.RepeatedScalarFieldContainer[bool]
    def __init__(self, version: _Optional[_Iterable[int]] = ..., timestamp: _Optional[_Iterable[int]] = ..., changeset: _Optional[_Iterable[int]] = ..., uid: _Optional[_Iterable[int]] = ..., user_sid: _Optional[_Iterable[int]] = ..., visible: _Optional[_Iterable[bool]] = ...) -> None: ...

class DenseNodes(_message.Message):
    __slots__ = ["denseinfo", "id", "keys_vals", "lat", "lon"]
    DENSEINFO_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    KEYS_VALS_FIELD_NUMBER: _ClassVar[int]
    LAT_FIELD_NUMBER: _ClassVar[int]
    LON_FIELD_NUMBER: _ClassVar[int]
    denseinfo: DenseInfo
    id: _containers.RepeatedScalarFieldContainer[int]
    keys_vals: _containers.RepeatedScalarFieldContainer[int]
    lat: _containers.RepeatedScalarFieldContainer[int]
    lon: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, id: _Optional[_Iterable[int]] = ..., denseinfo: _Optional[_Union[DenseInfo, _Mapping]] = ..., lat: _Optional[_Iterable[int]] = ..., lon: _Optional[_Iterable[int]] = ..., keys_vals: _Optional[_Iterable[int]] = ...) -> None: ...

class HeaderBBox(_message.Message):
    __slots__ = ["bottom", "left", "right", "top"]
    BOTTOM_FIELD_NUMBER: _ClassVar[int]
    LEFT_FIELD_NUMBER: _ClassVar[int]
    RIGHT_FIELD_NUMBER: _ClassVar[int]
    TOP_FIELD_NUMBER: _ClassVar[int]
    bottom: int
    left: int
    right: int
    top: int
    def __init__(self, left: _Optional[int] = ..., right: _Optional[int] = ..., top: _Optional[int] = ..., bottom: _Optional[int] = ...) -> None: ...

class HeaderBlock(_message.Message):
    __slots__ = ["bbox", "optional_features", "osmosis_replication_base_url", "osmosis_replication_sequence_number", "osmosis_replication_timestamp", "required_features", "source", "writingprogram"]
    BBOX_FIELD_NUMBER: _ClassVar[int]
    OPTIONAL_FEATURES_FIELD_NUMBER: _ClassVar[int]
    OSMOSIS_REPLICATION_BASE_URL_FIELD_NUMBER: _ClassVar[int]
    OSMOSIS_REPLICATION_SEQUENCE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    OSMOSIS_REPLICATION_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_FEATURES_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    WRITINGPROGRAM_FIELD_NUMBER: _ClassVar[int]
    bbox: HeaderBBox
    optional_features: _containers.RepeatedScalarFieldContainer[str]
    osmosis_replication_base_url: str
    osmosis_replication_sequence_number: int
    osmosis_replication_timestamp: int
    required_features: _containers.RepeatedScalarFieldContainer[str]
    source: str
    writingprogram: str
    def __init__(self, bbox: _Optional[_Union[HeaderBBox, _Mapping]] = ..., required_features: _Optional[_Iterable[str]] = ..., optional_features: _Optional[_Iterable[str]] = ..., writingprogram: _Optional[str] = ..., source: _Optional[str] = ..., osmosis_replication_timestamp: _Optional[int] = ..., osmosis_replication_sequence_number: _Optional[int] = ..., osmosis_replication_base_url: _Optional[str] = ...) -> None: ...

class Info(_message.Message):
    __slots__ = ["changeset", "timestamp", "uid", "user_sid", "version", "visible"]
    CHANGESET_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    UID_FIELD_NUMBER: _ClassVar[int]
    USER_SID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    VISIBLE_FIELD_NUMBER: _ClassVar[int]
    changeset: int
    timestamp: int
    uid: int
    user_sid: int
    version: int
    visible: bool
    def __init__(self, version: _Optional[int] = ..., timestamp: _Optional[int] = ..., changeset: _Optional[int] = ..., uid: _Optional[int] = ..., user_sid: _Optional[int] = ..., visible: bool = ...) -> None: ...

class Node(_message.Message):
    __slots__ = ["id", "info", "keys", "lat", "lon", "vals"]
    ID_FIELD_NUMBER: _ClassVar[int]
    INFO_FIELD_NUMBER: _ClassVar[int]
    KEYS_FIELD_NUMBER: _ClassVar[int]
    LAT_FIELD_NUMBER: _ClassVar[int]
    LON_FIELD_NUMBER: _ClassVar[int]
    VALS_FIELD_NUMBER: _ClassVar[int]
    id: int
    info: Info
    keys: _containers.RepeatedScalarFieldContainer[int]
    lat: int
    lon: int
    vals: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, id: _Optional[int] = ..., keys: _Optional[_Iterable[int]] = ..., vals: _Optional[_Iterable[int]] = ..., info: _Optional[_Union[Info, _Mapping]] = ..., lat: _Optional[int] = ..., lon: _Optional[int] = ...) -> None: ...

class PrimitiveBlock(_message.Message):
    __slots__ = ["date_granularity", "granularity", "lat_offset", "lon_offset", "primitivegroup", "stringtable"]
    DATE_GRANULARITY_FIELD_NUMBER: _ClassVar[int]
    GRANULARITY_FIELD_NUMBER: _ClassVar[int]
    LAT_OFFSET_FIELD_NUMBER: _ClassVar[int]
    LON_OFFSET_FIELD_NUMBER: _ClassVar[int]
    PRIMITIVEGROUP_FIELD_NUMBER: _ClassVar[int]
    STRINGTABLE_FIELD_NUMBER: _ClassVar[int]
    date_granularity: int
    granularity: int
    lat_offset: int
    lon_offset: int
    primitivegroup: _containers.RepeatedCompositeFieldContainer[PrimitiveGroup]
    stringtable: StringTable
    def __init__(self, stringtable: _Optional[_Union[StringTable, _Mapping]] = ..., primitivegroup: _Optional[_Iterable[_Union[PrimitiveGroup, _Mapping]]] = ..., granularity: _Optional[int] = ..., lat_offset: _Optional[int] = ..., lon_offset: _Optional[int] = ..., date_granularity: _Optional[int] = ...) -> None: ...

class PrimitiveGroup(_message.Message):
    __slots__ = ["changesets", "dense", "nodes", "relations", "ways"]
    CHANGESETS_FIELD_NUMBER: _ClassVar[int]
    DENSE_FIELD_NUMBER: _ClassVar[int]
    NODES_FIELD_NUMBER: _ClassVar[int]
    RELATIONS_FIELD_NUMBER: _ClassVar[int]
    WAYS_FIELD_NUMBER: _ClassVar[int]
    changesets: _containers.RepeatedCompositeFieldContainer[ChangeSet]
    dense: DenseNodes
    nodes: _containers.RepeatedCompositeFieldContainer[Node]
    relations: _containers.RepeatedCompositeFieldContainer[Relation]
    ways: _containers.RepeatedCompositeFieldContainer[Way]
    def __init__(self, nodes: _Optional[_Iterable[_Union[Node, _Mapping]]] = ..., dense: _Optional[_Union[DenseNodes, _Mapping]] = ..., ways: _Optional[_Iterable[_Union[Way, _Mapping]]] = ..., relations: _Optional[_Iterable[_Union[Relation, _Mapping]]] = ..., changesets: _Optional[_Iterable[_Union[ChangeSet, _Mapping]]] = ...) -> None: ...

class Relation(_message.Message):
    __slots__ = ["id", "info", "keys", "memids", "roles_sid", "types", "vals"]
    class MemberType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    ID_FIELD_NUMBER: _ClassVar[int]
    INFO_FIELD_NUMBER: _ClassVar[int]
    KEYS_FIELD_NUMBER: _ClassVar[int]
    MEMIDS_FIELD_NUMBER: _ClassVar[int]
    NODE: Relation.MemberType
    RELATION: Relation.MemberType
    ROLES_SID_FIELD_NUMBER: _ClassVar[int]
    TYPES_FIELD_NUMBER: _ClassVar[int]
    VALS_FIELD_NUMBER: _ClassVar[int]
    WAY: Relation.MemberType
    id: int
    info: Info
    keys: _containers.RepeatedScalarFieldContainer[int]
    memids: _containers.RepeatedScalarFieldContainer[int]
    roles_sid: _containers.RepeatedScalarFieldContainer[int]
    types: _containers.RepeatedScalarFieldContainer[Relation.MemberType]
    vals: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, id: _Optional[int] = ..., keys: _Optional[_Iterable[int]] = ..., vals: _Optional[_Iterable[int]] = ..., info: _Optional[_Union[Info, _Mapping]] = ..., roles_sid: _Optional[_Iterable[int]] = ..., memids: _Optional[_Iterable[int]] = ..., types: _Optional[_Iterable[_Union[Relation.MemberType, str]]] = ...) -> None: ...

class StringTable(_message.Message):
    __slots__ = ["s"]
    S_FIELD_NUMBER: _ClassVar[int]
    s: _containers.RepeatedScalarFieldContainer[bytes]
    def __init__(self, s: _Optional[_Iterable[bytes]] = ...) -> None: ...

class Way(_message.Message):
    __slots__ = ["id", "info", "keys", "lat", "lon", "refs", "vals"]
    ID_FIELD_NUMBER: _ClassVar[int]
    INFO_FIELD_NUMBER: _ClassVar[int]
    KEYS_FIELD_NUMBER: _ClassVar[int]
    LAT_FIELD_NUMBER: _ClassVar[int]
    LON_FIELD_NUMBER: _ClassVar[int]
    REFS_FIELD_NUMBER: _ClassVar[int]
    VALS_FIELD_NUMBER: _ClassVar[int]
    id: int
    info: Info
    keys: _containers.RepeatedScalarFieldContainer[int]
    lat: _containers.RepeatedScalarFieldContainer[int]
    lon: _containers.RepeatedScalarFieldContainer[int]
    refs: _containers.RepeatedScalarFieldContainer[int]
    vals: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, id: _Optional[int] = ..., keys: _Optional[_Iterable[int]] = ..., vals: _Optional[_Iterable[int]] = ..., info: _Optional[_Union[Info, _Mapping]] = ..., refs: _Optional[_Iterable[int]] = ..., lat: _Optional[_Iterable[int]] = ..., lon: _Optional[_Iterable[int]] = ...) -> None: ...
