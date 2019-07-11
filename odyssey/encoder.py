from .constants import (NEW_HEADER, MAGIC, FORMAT_VERSION_NUMBER_MAJOR, FORMAT_VERSION_NUMBER_MINOR,
                        ENDIAN_MARKER)
from .codec import select_codec
from .stream import LittleEndianStream, BigEndianStream

import hashlib
import pandas as pd
import numpy as np
import io


def encode_dataframe(dataframe: pd.DataFrame, f: io.IOBase, rows_per_table=10000, types=None, bigendian: bool=False):
    """
    :param dataframe: A pandas dataframe to encode
    :param f: A file-like object to write the encoded data to
    :param columns: A dict of (optional) column-name : constant DataType pairs, or None
    :param bigendian: Encode in big- endian byte order if True
    """
    column_order = None

    # Split the dataframe into chunks of appropriate size
    for i, sub_df in dataframe.groupby(np.arange(len(dataframe)) // rows_per_table):
        column_order = encode_single_dataframe(sub_df, f,
                                               types=types,
                                               column_order=column_order,
                                               bigendian=bigendian)


def encode_single_dataframe(dataframe: pd.DataFrame, f, types: dict=None, column_order: list=None, bigendian: bool=False):
    """
    :param dataframe: A pandas dataframe to encode
    :param f: A file-like object to write the encoded data to
    :param columns: A dict of (optional) column-name : constant DataType pairs, or None
    :param column_order: A list of column names specifying the encode order. If None, optimise according
                         to the rate of value changes in the columns
    :param bigendian: Encode in big- endian byte order if True
    :return: The column order used for encoding as a list of column names
    """

    stream_class = BigEndianStream if bigendian else LittleEndianStream

    codecs = [select_codec(name, data, (types or {}).get(name, None)) for name, data in dataframe.iteritems()]

    # If a column order has been specified, sort the codecs according to it. otherwise sort
    # the codecs for the most efficient use of the given data

    if column_order:
        assert len(column_order) == len(set(column_order))
        assert set(column_order) == set(c.column_name for c in codecs)
        codecs = {c.column_name: c for c in codecs}
        codecs = [codecs[column_name] for column_name in column_order]
    else:
        codecs.sort(key=lambda c: c.numChanges)
        column_order = [c.column_name for c in codecs]
        assert len(column_order) == len(set(column_order))

    data = _encodeData(dataframe, codecs, stream_class)
    headerPart2 = _encodeHeaderPart2(dataframe, codecs, stream_class, len(data))
    headerPart1 = _encodeHeaderPart1(headerPart2, stream_class)

    f.write(headerPart1)
    f.write(headerPart2)
    f.write(data)

    return column_order


def _encodeData(dataframe, codecs, stream_class):
    """
    Encode the data into a memory buffer
    """
    dataIO = io.BytesIO()
    stream = stream_class(dataIO)

    # Encode the column in the order supplied in the indexes list, rather than that
    # inherent in the dataframe.

    column_indexes = {column_name: i for i, column_name in enumerate(dataframe.columns)}
    column_indexes = [column_indexes[codec.column_name] for codec in codecs]

    # Iterate over rows

    last_row = None
    codec_indexes = list(zip(codecs, column_indexes))

    for row in dataframe.itertuples(index=False):

        for i, (codec, index) in enumerate(codec_indexes):
            if last_row is None or (row[index] != last_row[index] and not (pd.isnull(row[index]) and pd.isnull(last_row[index]))):
                break

        stream.encodeMarker(i)

        for codec, index in codec_indexes[i:]:
            codec.encode(stream, row[index])

        last_row = row

    return dataIO.getbuffer()


def _encodeHeaderPart2(dataframe, codecs, stream_class, data_len):
    """
    Encode the second part of the header - whose size and md5 is required to encode
    the first part of the header.
    """
    headerIO = io.BytesIO()
    stream = stream_class(headerIO)

    # Data Size (nextFrameOffset)
    stream.encodeInt64(data_len)

    # prevFrameOffset = 0
    stream.encodeInt64(0)

    # Number of rows
    stream.encodeInt64(dataframe.shape[0])

    # Flags... --> Currently no flags, no properties (remember to update Header Length)
    stream.encodeInt32(0)
    stream.encodeInt32(0)

    # Number of columns
    stream.encodeInt32(dataframe.shape[1])

    # Encode the codec information
    for codec in codecs:
        codec.encode_header(stream)

    return headerIO.getbuffer()


def _encodeHeaderPart1(headerPart2, stream_class):
    """
    Encode the first part of the header. This _could_ be done directly
    on the file-like object, although that would incurr many more filesystem
    operations.
    """
    headerIO = io.BytesIO()
    stream = stream_class(headerIO)

    stream.encodeMarker(NEW_HEADER)
    stream.write(MAGIC)

    stream.encodeInt32(ENDIAN_MARKER)

    stream.encodeInt32(FORMAT_VERSION_NUMBER_MAJOR)
    stream.encodeInt32(FORMAT_VERSION_NUMBER_MINOR)

    # MD5
    m = hashlib.md5()
    m.update(headerPart2)
    md = m.hexdigest()
    stream.encodeString(md)

    # Header Length
    stream.encodeInt32(len(headerPart2))

    return headerIO.getbuffer()



