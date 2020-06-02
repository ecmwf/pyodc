
from .constants import *
from .lib import ffi, lib, memoize_constant

from collections import Iterable
import numpy
import pandas
import os


class ColumnInfo:

    class Bitfield:
        def __init__(self, name, size, offset):
            self.name = name
            self.size = size
            self.offset = offset

    def __init__(self, name, idx, dtype, datasize, bitfields):
        self.name = name
        self.dtype = dtype
        self.index = idx
        self.datasize = datasize
        self.bitfields = bitfields
        assert (dtype == BITFIELD) != (bitfields is None)
        if self.bitfields:
            assert isinstance(self.bitfields, Iterable)
            assert all(isinstance(b, ColumnInfo.Bitfield) for b in self.bitfields)

    def __str__(self):
        if self.bitfields is not None:
            bitfield_str = "(" + ",".join("{}:{}".format(b[0], b[1]) for b in self.bitfields) + ")"
        else:
            bitfield_str = ""
        return "{}:{}{}".format(self.name, self.dtype, bitfield_str)

    def __repr__(self):
        return str(self)


class Frame:

    def __init__(self, table):
        self.__frame = table
        self.__columns = None

    @property
    @memoize_constant
    def columns(self):
        columns = []
        for col in range(self.ncolumns):

            pname = ffi.new('const char**')
            ptype = ffi.new('int*')
            pdatasize = ffi.new('int*')
            pbitfield_count = ffi.new('int*')
            lib.odc_frame_column_attributes(self.__frame, col, pname, ptype, pdatasize, pbitfield_count)
            name = ffi.string(pname[0]).decode('utf-8')
            dtype = DataType(int(ptype[0]))
            datasize = int(pdatasize[0])
            bitfield_count = int(pbitfield_count[0])
            bitfields = None

            if dtype == STRING:
                assert datasize % 8 == 0
            else:
                assert datasize == 8

            if dtype == BITFIELD:
                bitfields = []
                for n in range(bitfield_count):

                    pbitfield_name = ffi.new('const char**')
                    poffset = ffi.new('int*')
                    psize = ffi.new('int*')
                    lib.odc_frame_bitfield_attributes(self.__frame, col, n, pbitfield_name, poffset, psize)

                    bitfields.append(ColumnInfo.Bitfield(
                        name=ffi.string(pbitfield_name[0]).decode('utf-8'),
                        size=int(psize[0]),
                        offset=int(poffset[0])))

            columns.append(ColumnInfo(name, col, dtype, datasize, bitfields))

        return columns

    @property
    @memoize_constant
    def column_dict(self):
        return {c.name: c for c in self.columns}

    @property
    @memoize_constant
    def simple_column_dict(self):
        return {c.name.split('@')[0]: c for c in self.columns}

    @property
    @memoize_constant
    def nrows(self):
        count = ffi.new('long*')
        lib.odc_frame_row_count(self.__frame, count)
        return int(count[0])

    @property
    @memoize_constant
    def ncolumns(self):
        count = ffi.new('int*')
        lib.odc_frame_column_count(self.__frame, count)
        return int(count[0])

    def dataframe(self, columns=None):

        # Some constants that are useful

        pmissing_integer = ffi.new('long*')
        pmissing_double = ffi.new('double*')
        lib.odc_missing_integer(pmissing_integer)
        lib.odc_missing_double(pmissing_double)
        missing_integer = pmissing_integer[0]
        missing_double = pmissing_double[0]

        if columns is None:
            columns = [c.name for c in self.columns]

        assert columns is not None

        cd = self.column_dict
        scd = self.simple_column_dict

        integer_cols = []
        double_cols = []
        string_cols = {}
        for name in columns:
            try:
                col = cd[name]
            except KeyError:
                col = scd[name]
            if col.dtype == INTEGER or col.dtype == BITFIELD:
                integer_cols.append(col)
            elif col.dtype == REAL or col.dtype == DOUBLE:
                double_cols.append(col)
            elif col.dtype == STRING:
                string_cols.setdefault(col.datasize, []).append(col)

        decoder = ffi.new('odc_decoder_t**')
        lib.odc_new_decoder(decoder)
        decoder = ffi.gc(decoder[0], lib.odc_free_decoder)

        lib.odc_decoder_set_row_count(decoder, self.nrows)

        dataframes = []
        pos = 0
        string_seq = tuple((cols, "|S{}".format(dataSize), dataSize) for dataSize, cols in string_cols.items())
        for cols, dtype, dsize in ((integer_cols, numpy.int64, 8),
                                   (double_cols, numpy.double, 8)) + string_seq:

            if len(cols) > 0:

                array = numpy.empty((self.nrows, len(cols)), dtype=dtype, order='C')

                pointer = array.ctypes.data
                strides = array.ctypes.strides

                for i, col in enumerate(cols):

                    lib.odc_decoder_add_column(decoder, col.name.encode('utf-8'))
                    lib.odc_decoder_column_set_data_array(decoder, pos, dsize, strides[0],
                                                          ffi.cast('void*', pointer + (i * strides[1])))
                    pos += 1

                dataframes.append(pandas.DataFrame(array, columns=[c.name for c in cols], copy=False))

        try:
            threads = len(os.shed_getaffinity(0))
        except AttributeError:
            threads = os.cpu_count()

        prows_decoded = ffi.new('long*')
        lib.odc_decode_threaded(decoder, self.__frame, prows_decoded, threads)
        assert prows_decoded[0] == self.nrows

        # Update the missing values (n.b., still sorted by type), and decode strings

        for i in range(len(dataframes)):
            df = dataframes[i]
            if df.dtypes[0] == numpy.int64:
                df.mask(df == missing_integer, inplace=True)
            elif df.dtypes[0] == numpy.double:
                df.mask(df == missing_double, inplace=True)
            else:
                # This is a bit yucky, but I haven't found any other way to decode from b'' strings to real ones
                # Also note, result_type added to work around bug in pandas
                # https://github.com/pandas-dev/pandas/issues/34529
                dataframes[i] = df.apply(lambda x: x.astype('object').str.decode('utf-8'), result_type='expand')

        # And construct the DataFrame from the decoded data

        if len(dataframes) == 1:
            return dataframes[0]
        else:
            return pandas.concat(dataframes, copy=False, axis=1)

