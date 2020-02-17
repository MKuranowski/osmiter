from typing import Union, BinaryIO, Iterator, Optional
import gzip
import bz2
import os

from .parser_pbf import iter_from_pbf_buffer
from .parser_xml import iter_from_xml_buffer

__title__ = "osmiter"
__description__ = "Library for reading OSM XML/GZ/BZ2/PBF files"
__url__ = "https://github.com/MKuranowski/osmiter"
__author__ = "Mikołaj Kuranowski"
__copyright__ = "Copyright 2020 Mikolaj Kuranowski"
__license__ = "MIT"
__version__ = "1.0.4"
__email__ = "mkuranowski@gmail.com"

def iter_from_osm(
        source: Union[str, bytes, int, BinaryIO],
        file_format: Optional[str] = None) -> Iterator[dict]:
    """Yields all items from provided source file.

    If source is a str/bytes (path) the format will be guess based on file extension.
    Otherwise, if source is an int (file descriptior) or a file-like object,
    the `format` argument must be provided, if the file format is different then OSM XML.

    File-like sources have to be opened in binary mode.

    Format has to be one of "xml", "gz", "bz2", "pbf".
    """

    # Convert byte paths to str
    if type(source) is bytes:
        source = os.fsdecode(source)

    # detect file format
    if type(source) is str and file_format is None:
        if source.endswith((".osm", ".xml")):
            file_format = "xml"

        elif source.endswith((".osm.gz", ".xml.gz")):
            file_format = "gz"

        elif source.endswith((".osm.bz2", ".xml.bz2")):
            file_format = "bz2"

        elif source.endswith((".osm.pbf", ".osm.pb")):
            file_format = "pbf"

        else:
            raise ValueError(f"unable to guess OSM file format for file name: {source!r}")

    # check if valid file format is provided
    if file_format not in {"xml", "gz", "bz2", "pbf"}:
        raise ValueError(f"invalid file format {file_format!r}")

    file_like = hasattr(source, "read")

    # simple xml
    if file_format == "xml":

        if file_like:
            yield from iter_from_xml_buffer(source)

        else:
            with open(source, mode="rb") as f:
                yield from iter_from_xml_buffer(f)

    # gzip compression
    elif file_format == "gz":

        with gzip.open(source, mode="rb") as decompressed_buff:
            yield from iter_from_xml_buffer(decompressed_buff)

    # bz2 compression
    elif file_format == "bz2":

        with bz2.open(source, mode="rb") as decompressed_buff:
            yield from iter_from_xml_buffer(decompressed_buff)

    # pbf format
    elif file_format == "pbf":

        if file_like:
            yield from iter_from_pbf_buffer(source)

        else:
            with open(source, mode="rb") as f:
                yield from iter_from_pbf_buffer(f)
