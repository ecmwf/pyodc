#
# Copyright 2017-2018 European Centre for Medium-Range Weather Forecasts (ECMWF).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from collections import Iterable

import cffi
import pandas
import numpy
import io
import os
from functools import reduce
from pkg_resources import parse_version
from enum import IntEnum, unique

__version__ = '1.0.1'

__odc_version__ = "1.0.2"

ffi = cffi.FFI()


class ODCException(RuntimeError):
    pass


class CFFIModuleLoadFailed(ODCException):
    pass


class PatchedLib:
    """
    Patch a CFFI library with error handling

    Finds the header file associated with the ODC C API and parses it, loads the shared library,
    and patches the accessors with automatic python-C error handling.
    """
    __type_names = {}

    def __init__(self):

        ffi.cdef(self.__read_header())
        try:
            self.__lib = ffi.dlopen('libodccore.so')
        except Exception as e:
            raise CFFIModuleLoadFailed() from e

        # Todo: Version check against __version__

        # All of the executable members of the CFFI-loaded library are functions in the ODC
        # C API. These should be wrapped with the correct error handling. Otherwise forward
        # these on directly.

        for f in dir(self.__lib):
            try:
                attr = getattr(self.__lib, f)
                setattr(self, f, self.__check_error(attr, f) if callable(attr) else attr)
            except Exception as e:
                print(e)
                print("Error retrieving attribute", f, "from library")

        # Initialise the library, and sett it up for python-appropriate behaviour

        self.odc_initialise_api()
        self.odc_integer_behaviour(self.ODC_INTEGERS_AS_LONGS)

        # Check the library version

        tmp_str = ffi.new('char**')
        self.odc_version(tmp_str)
        versionstr = ffi.string(tmp_str[0]).decode('utf-8')

        if parse_version(versionstr) < parse_version(__odc_version__):
            raise RuntimeError("Version of libodc found is too old. {} < {}".format(versionstr, __odc_version__))

    def type_name(self, typ: 'DataType'):
        name = self.__type_names.get(typ, None)
        if name is not None:
            return name

        name_tmp = ffi.new('char**')
        self.odc_column_type_name(typ, name_tmp)
        name = ffi.string(name_tmp[0]).decode('utf-8')
        self.__type_names[typ] = name
        return name

    def __read_header(self):
        with open(os.path.join(os.path.dirname(__file__), 'processed_odc.h'), 'r') as f:
            return f.read()

    def __check_error(self, fn, name):
        """
        If calls into the ODC library return errors, ensure that they get detected and reported
        by throwing an appropriate python exception.
        """
        def wrapped_fn(*args, **kwargs):
            retval = fn(*args, **kwargs)
            if retval not in (self.__lib.ODC_SUCCESS, self.__lib.ODC_ITERATION_COMPLETE):
                error_str = "Error in function {}: {}".format(name, self.__lib.odc_error_string(retval))
                raise ODCException(error_str)
            return retval

        return wrapped_fn


def memoize_constant(fn):
    """Memoize constant values to avoid repeatedly crossing the API layer unecessarily"""
    attr_name = "__memoized_{}".format(fn.__name__)

    def wrapped_fn(self):
        value = getattr(self, attr_name, None)
        if value is None:
            value = fn(self)
            setattr(self, attr_name, value)
        return value

    return wrapped_fn


# Bootstrap the library

try:
    lib = PatchedLib()
except CFFIModuleLoadFailed as e:
    raise ImportError() from e

# Construct lookups/constants as is useful

@unique
class DataType(IntEnum):
    IGNORE = lib.ODC_IGNORE
    INTEGER = lib.ODC_INTEGER
    DOUBLE = lib.ODC_DOUBLE
    REAL = lib.ODC_REAL
    STRING = lib.ODC_STRING
    BITFIELD = lib.ODC_BITFIELD

IGNORE = DataType.IGNORE
INTEGER = DataType.INTEGER
REAL = DataType.REAL
STRING = DataType.STRING
BITFIELD = DataType.BITFIELD
DOUBLE = DataType.DOUBLE


class Reader:
    """This is the main container class for reading ODBs"""

    __reader = None
    __frames = None

    def __init__(self, source, aggregated=True, max_aggregated=-1):

        self.__aggregated = aggregated
        self.__max_aggregated = max_aggregated

        reader = ffi.new('odc_reader_t**')
        if isinstance(source, io.IOBase):
            lib.odc_open_file_descriptor(reader, source.fileno())
        else:
            assert isinstance(source, str)
            lib.odc_open_path(reader, source.encode())

        # Set free function
        self.__reader = ffi.gc(reader[0], lib.odc_close)

    @property
    def frames(self):
        if self.__frames is None:
            self.__frames = []

            frame = ffi.new('odc_frame_t**')
            lib.odc_new_frame(frame, self.__reader)
            frame = ffi.gc(frame[0], lib.odc_free_frame)
            while (lib.odc_next_frame_aggregated(frame, self.__max_aggregated) if self.__aggregated else lib.odc_next_frame(frame)) != lib.ODC_ITERATION_COMPLETE:

                copy_frame = ffi.new('odc_frame_t**')
                lib.odc_copy_frame(frame, copy_frame)
                self.__frames.append(Frame(ffi.gc(copy_frame[0], lib.odc_free_frame)))

        return self.__frames


class ColumnInfo:

    class Bitfield:
        def __init__(self, name, size, offset):
            self.name = name
            self.size = size
            self.offset = offset

    def __init__(self, name, idx, typ, datasize, bitfields):
        self.name = name
        self.typ = typ
        self.index = idx
        self.datasize = datasize
        self.bitfields = bitfields
        assert (typ == BITFIELD) != (bitfields is None)
        if self.bitfields:
            assert isinstance(self.bitfields, Iterable)
            assert all(isinstance(b, ColumnInfo.Bitfield) for b in self.bitfields)

    def __str__(self):
        if self.bitfields is not None:
            bitfield_str = "(" + ",".join("{}:{}".format(b[0], b[1]) for b in self.bitfields) + ")"
        else:
            bitfield_str = ""
        return "{}:{}{}".format(self.name, self.typ, bitfield_str)

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
            typ = DataType(int(ptype[0]))
            datasize = int(pdatasize[0])
            bitfield_count = int(pbitfield_count[0])
            bitfields = None

            if typ == STRING:
                assert datasize % 8 == 0
            else:
                assert datasize == 8

            if typ == BITFIELD:
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

            columns.append(ColumnInfo(name, col, typ, datasize, bitfields))

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
            print("Using default columns (all)")

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
            if col.typ == INTEGER or col.typ == BITFIELD:
                integer_cols.append(col)
            elif col.typ == REAL or col.typ == DOUBLE:
                double_cols.append(col)
            elif col.typ == STRING:
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
                dataframes[i] = df.apply(lambda x: x.astype('object').str.decode('utf-8'))

        # And construct the DataFrame from the decoded data

        if len(dataframes) == 1:
            return dataframes[1]
        else:
            return pandas.concat(dataframes, copy=False, axis=1)


def encode_odb(df: pandas.DataFrame, f, types: dict=None, rows_per_frame=10000, properties=None, **kwargs):
    """
    Encode a pandas dataframe into ODB2 format

    :param df: The dataframe to encode
    :param f: The file-like object into which to encode the ODB2 data
    :param types: An optional (sparse) dictionary. Each key-value pair maps the name of a column to
                  encode to an ODB2 data type to use to encode it.
    :param rows_per_frame: The maximum number of rows to encode per frame. If this number is exceeded,
                           a sequence of frames will be encoded
    :param kwargs: Accept extra arguments that may be used by the python pyodc encoder.
    :return:
    """
    if isinstance(f, str):
        with open(f, 'wb') as freal:
            return encode_odb(df, freal, types=types, rows_per_frame=rows_per_frame, **kwargs)

    # Some constants that are useful

    pmissing_integer = ffi.new('long*')
    pmissing_double = ffi.new('double*')
    lib.odc_missing_integer(pmissing_integer)
    lib.odc_missing_double(pmissing_double)
    missing_integer = pmissing_integer[0]
    missing_double = pmissing_double[0]

    def infer_column_type(arr, override_type):
        """
        Given a column of data, infer the encoding type.
        :param arr: The column of data to encode
        :param override_type:
        :return: (return_arr, typ)
            - return_arr is the column of data to encode. This may be of a different internal type/contents
              to that supplied to the function, but it will normally not be.
            - The ODB2 type to encode with.
        """
        return_arr = arr
        typ = override_type

        if typ is None:
            if arr.dtype in ('uint64', 'int64'):
                typ = INTEGER
            elif arr.dtype == 'float64':
                if not data.isnull().all() and all(pandas.isnull(v) or float(v).is_integer() for v in arr):
                    typ = INTEGER
                    return_arr = arr.fillna(value=missing_integer).astype('int64')
                else:
                    typ = DOUBLE
                    return_arr = arr.fillna(value=missing_double)
            elif arr.dtype == 'object':
                if not arr.isnull().all() and all(s is None or isinstance(s, str) for s in arr):
                    typ = STRING
                elif arr.isnull().all():
                    typ = INTEGER

        if arr.dtype == 'object':
            # Map strings into an array that can be read in C
            if typ == STRING:
                return_arr = return_arr.astype("|S{}".format(max(8, 8 * (1 + ((max(len(s) for s in arr)- 1) // 8)))))
            elif typ == INTEGER:
                return_arr = return_arr.fillna(value=missing_integer).astype("int64")

        if typ is None:
            raise ValueError("Unsupported value type: {}".format(arr.dtype))

        return return_arr, typ

    nrows = df.shape[0]
    if types is None:
        types = {}

    encoder = ffi.new('odc_encoder_t**')
    lib.odc_new_encoder(encoder)
    encoder = ffi.gc(encoder[0], lib.odc_free_encoder)

    for k, v in (properties or {}).items():
        lib.odc_encoder_add_property(encoder, k.encode('utf-8'), v.encode('utf-8'))

    lib.odc_encoder_set_row_count(encoder, nrows)
    lib.odc_encoder_set_rows_per_frame(encoder, rows_per_frame)

    # We store all of the numpy arrays here. Mostly this is just another reference to an
    # existing array, but some of the types require us to create a new (casted) copy, so
    # we need to put it somewhere to ensure it stays alive appropriately long.
    data_cache = []

    for i, (name, data) in enumerate(df.items()):
        data, typ = infer_column_type(data, types.get(name, None))
        data_cache.append(data)

        lib.odc_encoder_add_column(encoder, name.encode('utf-8'), typ)
        lib.odc_encoder_column_set_data_array(encoder, i, data.dtype.itemsize, data.strides[0],
                                              ffi.cast('void*', data.values.ctypes.data))

    lib.odc_encode_to_file_descriptor(encoder, f.fileno(), ffi.NULL)


def _read_odb_generator(source, columns=None, aggregated=True, max_aggregated=-1):
    r = Reader(source, aggregated=aggregated, max_aggregated=max_aggregated)
    for f in r.frames:
        yield f.dataframe()


def _read_odb_oneshot(source, columns=None):
    return reduce(lambda df1, df2: df1.append(df2, sort=False), read_odb(source, columns))

def read_odb(source, columns=None, aggregated=True, single=False, max_aggregated=-1):
    if single:
        assert aggregated
        return _read_odb_oneshot(source, columns)
    else:
        return _read_odb_generator(source, columns, aggregated, max_aggregated)

