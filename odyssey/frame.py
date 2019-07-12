#
# (C) Copyright 2014 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#

from __future__ import absolute_import

from .stream import BigEndianStream, LittleEndianStream
from .constants import TYPE_NAMES, BITFIELD, MAGIC, ENDIAN_MARKER, FORMAT_VERSION_NUMBER_MAJOR, FORMAT_VERSION_NUMBER_MINOR, NEW_HEADER
from .codec import read_codec

from collections import Iterable
from itertools import accumulate, chain
import pandas as pd


class MismatchedFramesError(ValueError):
    pass


class ColumnInfo:
    """
    Represent the type of a column
    """

    class Bitfield:
        def __init__(self, name, size, offset):
            self.name = name
            self.size = size
            self.offset = offset

        def __eq__(self, other):
            return (self.name == other.name and
                    self.size == other.size and
                    self.offset == other.offset)

    def __init__(self, name, idx, typ, datasize, bitfields):
        self.name = name
        self.typ = typ
        self.index = idx
        self.datasize = datasize
        self.bitfields = bitfields
        assert (typ == BITFIELD) != (len(bitfields) == 0)
        if self.bitfields:
            assert isinstance(self.bitfields, Iterable)
            assert all(isinstance(b, ColumnInfo.Bitfield) for b in self.bitfields)

    def __str__(self):
        if self.typ == BITFIELD:
            bitfield_str = "(" + ",".join("{}:{}".format(b.name, b.size) for b in self.bitfields) + ")"
        else:
            bitfield_str = ""
        return "{}:{}{}".format(self.name, TYPE_NAMES.get(self.typ, '<unknown>'), bitfield_str)

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return (self.name == other.name and
                self.typ == other.typ and
                self.index == other.index and    # This may be overzealous?
                self.datasize == other.datasize and
                self.bitfields == other.bitfields)



class Frame:

    def __init__(self, f):

        # Read marker and magic

        m = f.read(2)
        if len(m) == 0:
            raise EOFError()
        assert int.from_bytes(m, byteorder='big', signed=False) == NEW_HEADER

        assert f.read(3) == MAGIC

        # Get byte ordering

        endian_marker = f.read(4)
        if int.from_bytes(endian_marker, byteorder='little') == ENDIAN_MARKER:
            stream = LittleEndianStream(f)
        else:
            stream = BigEndianStream(f)

        # TODO: Some inequalities here, rather than plain statement
        assert stream.readInt32() == FORMAT_VERSION_NUMBER_MAJOR
        assert stream.readInt32() == FORMAT_VERSION_NUMBER_MINOR

        md5 = stream.readString()

        headerLength = stream.readInt32()
        self._dataStartPosition = stream.position() + headerLength

        # 0 means we don't know offset of next header.

        self._dataSize = stream.readInt64()
        self._dataEndPosition = self._dataStartPosition + self._dataSize

        # prevFrameOffset
        assert stream.readInt64() == 0

        self._numberOfRows = stream.readInt64()

        self.flags = [stream.readReal64() for _ in range(stream.readInt32())]
        self.properties = {stream.readString(): stream.readString() for _ in range(stream.readInt32())}

        self._numberOfColumns = stream.readInt32()
        self._columnPosition = stream.position()

        self.__columnCodecs = None
        self._columns = None

        self._stream = stream

        # Support frame aggregation
        self._trailingAggregatedFrames = []

    def seekToEnd(self):
        self._stream.seek(self._dataEndPosition)

    @property
    def _column_codecs(self):
        """
        Internal method to get the codecs for the given column.
        These are read/constructed lazily from the file handle so that we can do scans through the file rapdily.

        :return: A list of coders
        """
        if self.__columnCodecs is None:
            self._stream.seek(self._columnPosition)
            self.__columnCodecs = [read_codec(self._stream) for _ in range(self._numberOfColumns)]
            assert self._stream.position() == self._dataStartPosition
        return self.__columnCodecs

    @property
    def columns(self):
        return [
            ColumnInfo(codec.column_name, idx, codec.type, codec.data_size,
                       [ColumnInfo.Bitfield(name=nm, size=sz, offset=off)
                        for nm, sz, off in zip(codec.bitfield_names,
                                               codec.bitfield_sizes,
                                               accumulate(chain([0]), codec.bitfield_sizes))])
            for idx, codec in enumerate(self._column_codecs)
        ]

    @property
    def column_dict(self):
        return {c.name: c for c in self.columns}

    @property
    def simple_column_dict(self):
        return {c.name.split('@')[0]: c for c in self.columns}

    @property
    def nrows(self):
        return self._numberOfRows + sum(f.nrows for f in self._trailingAggregatedFrames)

    @property
    def ncolumns(self):
        if self.__columnCodecs is not None:
            assert self._numberOfColumns == len(self.__columnCodecs)
        return self._numberOfColumns

    def dataframe(self, columns=None):
        """
        Actually decode the data!
        """
        columns = self._column_codecs

        self._stream.seek(self._dataStartPosition)

        output_cols = [[] for _ in range(self._numberOfColumns)]
        output = {c.column_name: data for c, data in zip(columns, output_cols)}
        lastDecoded = [0] * self._numberOfColumns

        lastStartCol = 0
        for row in range(self._numberOfRows):

            startCol = self._stream.readMarker()

            # Fill in missing data in columns
            if lastStartCol > startCol:
                for col in range(startCol, lastStartCol):
                    last = output_cols[col][-1]
                    output_cols[col].extend(last for _ in range(row - lastDecoded[col] - 1))

            lastStartCol = startCol

            for col in range(startCol, self._numberOfColumns):
                output_cols[col].append(columns[col].decode(self._stream))
                lastDecoded[col] = row

        for col in range(lastStartCol):
            last = output_cols[col][-1]
            output_cols[col].extend(last for _ in range(self._numberOfRows - lastDecoded[col] - 1))

        df = pd.DataFrame(output)

        if len(self._trailingAggregatedFrames) > 0:
            return pd.concat([df] + [f.dataframe() for f in self._trailingAggregatedFrames], copy=False, axis=0)
        else:
            return df

    def _append(self, frame: 'Frame'):
        if self.column_dict != frame.column_dict:
            raise MismatchedFramesError
        self._trailingAggregatedFrames.append(frame)

