# Warning! These stubs are not complete, and only
# contain methods and attributes used by osmiter.


class Blob:
    def ParseFromString(self, seralized: bytes) -> None: ...
    def HasField(self, field_name: str) -> bool: ...

    raw: bytes
    raw_size: int
    zlib_data: bytes
    lzma_data: bytes

class BlobHeader:
    def ParseFromString(self, seralized: bytes) -> None: ...
    def HasField(self, field_name: str) -> bool: ...

    type: str
    indexdata: bytes
    datasize: int

