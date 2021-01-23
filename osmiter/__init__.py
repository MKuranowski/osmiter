import bz2
import gzip
import os
from typing import IO, Iterable, Iterator, Optional, Union

from typing_extensions import Literal

from .parser_pbf import iter_from_pbf_buffer
from .parser_xml import iter_from_xml_buffer

__title__ = "osmiter"
__description__ = "Library for reading OSM XML/GZ/BZ2/PBF files"
__url__ = "https://github.com/MKuranowski/osmiter"
__author__ = "Mikołaj Kuranowski"
__copyright__ = "Copyright 2020 Mikolaj Kuranowski"
__license__ = "MIT"
__version__ = "1.1.1"
__email__ = "".join(chr(i) for i in [109, 107, 117, 114, 97, 110, 111, 119, 115, 107, 105, 32, 91,
                                     1072, 116, 93, 32, 103, 109, 97, 105, 108, 46, 99, 111, 109])


def iter_from_osm(
        source: Union[str, bytes, os.PathLike, int, IO[bytes]],
        file_format: Optional[Literal["xml", "gz", "bz2", "pbf"]] = None,
        filter_attrs: Optional[Iterable[str]] = None) -> Iterator[dict]:
    """Yields all items from provided source file.

    If source is a str/bytes/os.PathLike (path) the format will be guess based on file extension.
    Otherwise, if source is an int (file descriptior) or a file-like object,
    the `file_format` argument must be provided.

    File-like sources have to be opened in binary mode.
    Format has to be one of "xml", "gz", "bz2", "pbf".

    osmiter spends most of its time parsing element attributes.
    If only specific attributes are going to be used, pass an Iterable (most prefereably a set)
    with wanted attributes to filter_attrs.

    No matter what attributes you define in filter_attrs, some attributes are always parsed:
    - "id", "lat" and "lon": for nodes
    - "id": for ways and relations
    - "type", "ref" and "role": for members

    `filter_attrs` is ignored for pbf files.
    """

    # Try to guess the extension
    if file_format is None:
        if hasattr(source, "read") or isinstance(source, int):
            raise ValueError("file_format is required for file-like or file-descriptor sources")

        fname = os.fsdecode(source)  # type: ignore
        if fname.endswith((".osm", ".xml")):
            file_format = "xml"

        elif fname.endswith((".osm.gz", ".xml.gz")):
            file_format = "gz"

        elif fname.endswith((".osm.bz2", ".xml.bz2")):
            file_format = "bz2"

        elif fname.endswith((".osm.pbf", ".osm.pb")):
            file_format = "pbf"

        else:
            raise ValueError(f"unable to guess OSM file format for file name: {source!r}")

    # Check if valid file format is provided
    if file_format not in {"xml", "gz", "bz2", "pbf"}:
        raise ValueError(f"invalid file format {file_format!r}")

    # Try to open the file
    buffer_provided: bool = hasattr(source, "read")
    buffer: IO[bytes] = source if buffer_provided else open(source, mode="rb")  # type: ignore

    # Parse file contents
    try:
        # simple xml
        if file_format == "xml":
            yield from iter_from_xml_buffer(buffer)

        # gzip compression
        elif file_format == "gz":

            with gzip.open(buffer, mode="rb") as decompressed_buff:
                yield from iter_from_xml_buffer(decompressed_buff, filter_attrs)  # type: ignore

        # bz2 compression
        elif file_format == "bz2":

            with bz2.open(buffer, mode="rb") as decompressed_buff:
                yield from iter_from_xml_buffer(decompressed_buff, filter_attrs)

        # pbf format
        elif file_format == "pbf":
            yield from iter_from_pbf_buffer(buffer)

    # Ensure buffer closure
    finally:
        if not buffer_provided:
            buffer.close()
