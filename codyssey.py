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
import ctypes.util
import pandas
import numpy
import io
import os
from pkg_resources import parse_version

__version__ = "0.99.0"

print(ctypes.util.find_library("odccore"))

# TODO: Fallback to the python api

ffi = cffi.FFI()


class ODCException(RuntimeError):
    pass

class ODCException(ODCException):
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
        self.__lib = ffi.dlopen('libodccore.so')

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
        versionstr = ffi.string(tmp_str[0]) .decode('utf-8')

        v1 = parse_version(versionstr)
        v2 = parse_version(__version__)

        if parse_version(versionstr) < parse_version(__version__):
            raise RuntimeError("Version of libodc found is too old. {} < {}".format(versionstr, __version__))

    def type_name(self, type):
        name = self.__type_names.get(type, None)
        if name is not None:
            return name

        name_tmp = ffi.new('char**')
        self.odc_type_name(type, name_tmp)
        name = ffi.string(name_tmp[0]).decode('utf-8')
        self.__type_names[type] = name
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
                error_str = self.__lib.odc_error_string(retval)
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

lib = PatchedLib()

# Construct lookups/constants as is useful

IGNORE = lib.ODC_IGNORE
INTEGER = lib.ODC_IGNORE
DOUBLE = lib.ODC_IGNORE
REAL = lib.ODC_IGNORE
STRING = lib.ODC_IGNORE
BITFIELD = lib.ODC_IGNORE


class Reader:
    """This is the main container class for reading ODBs"""

    __reader = None
    __frames = None

    def __init__(self, source, aggregated=True):

        self.__aggregated = aggregated

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
            while (lib.odc_next_frame_aggregated(frame, -1) if self.__aggregated else lib.odc_next_frame(frame)) != lib.ODC_ITERATION_COMPLETE:

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

    def __init__(self, name, idx, type, datasize, bitfields):
        self.name = name
        self.type = type
        self.index = idx
        self.datasize = datasize
        self.bitfields = bitfields
        assert (type == BITFIELD) != (bitfields is None)
        if self.bitfields:
            assert isinstance(self.bitfields, Iterable)
            assert all(isinstance(b, ColumnInfo.Bitfield) for b in self.bitfields)

    def __str__(self):
        if self.bitfields is not None:
            bitfield_str = "(" + ",".join("{}:{}".format(b[0], b[1]) for b in self.bitfields) + ")"
        else:
            bitfield_str = ""
        return "{}:{}{}".format(self.name, lib.type_name(self.type), bitfield_str)

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

            name = ffi.string(lib.odc_frame_column_name(self.__frame, col)).decode()
            type = lib.odc_frame_column_type(self.__frame, col)
            datasize = lib.odc_frame_column_data_size(self.__frame, col)
            bitfields = None

            if type == STRING:
                assert datasize % 8 == 0
            else:
                assert datasize == 8

            if type == BITFIELD:
                num_fields = lib.odc_frame_column_bitfield_count(self.__frame, col)
                bitfields = []
                for n in range(num_fields):
                    bitfields.append(ColumnInfo.Bitfield(
                        name=ffi.string(lib.odc_frame_column_bitfield_field_name(self.__frame, col, n)).decode(),
                        size=lib.odc_frame_column_bitfield_field_size(self.__frame, col, n),
                        offset=lib.odc_frame_column_bitfield_field_offset(self.__frame, col, n)))

            columns.append(ColumnInfo(name, col, type, datasize, bitfields))

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
            if col.type == INTEGER or col.type == BITFIELD:
                integer_cols.append(col)
            elif col.type == REAL or col.type == DOUBLE:
                double_cols.append(col)
            elif col.type == STRING:
                string_cols.setdefault(col.datasize, []).append(col)

        decode_target = ffi.gc(lib.odc_alloc_decode_target(), lib.odc_free_decode_target)
        lib.odc_decode_target_set_row_count(decode_target, self.nrows)

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

                    assert pos == lib.odc_decode_target_add_column(decode_target, col.name.encode('utf-8'))
                    lib.odc_decode_target_column_set_size(decode_target, pos, dsize)
                    lib.odc_decode_target_column_set_stride(decode_target, pos, strides[0])
                    lib.odc_decode_target_column_set_data(decode_target, pos, ffi.cast("void*", pointer + (i * strides[1])))
                    pos += 1

                dataframes.append(pandas.DataFrame(array, columns=[c.name for c in cols], copy=False))

        rows_decoded = lib.odc_frame_decode(self.__frame, decode_target, len(os.sched_getaffinity(0)))
        assert rows_decoded == self.nrows

        # And construct the DataFrame from the decoded data

        if len(dataframes) == 1:
            return dataframes[1]
        else:
            return pandas.concat(dataframes, copy=False, axis=1)


def encode_dataframe(df: pandas.DataFrame, f: io.IOBase, types: dict=None, rows_per_frame=10000, **kwargs):

    def infer_column_type(arr, override_type):

        return_arr = arr
        typ = override_type

        if typ is None:
            if arr.dtype in ('uint64', 'int64'):
                typ = INTEGER
            elif arr.dtype == 'float64':
                if not data.isnull().all() and all(pandas.isnull(v) or float(v).is_integer() for v in arr):
                    typ = INTEGER
                    return_arr = arr.fillna(value=lib.odc_missing_integer()).astype('int64')
                else:
                    typ = DOUBLE
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
                return_arr = return_arr.fillna(value=lib.odc_missing_integer()).astype("int64")

        if typ is None:
            raise ValueError("Unsupported value type: {}".format(arr.dtype))

        return return_arr, typ

    nrows = df.shape[0]
    if types is None:
        types = {}

    encoder = ffi.gc(lib.odc_alloc_encoder(), lib.odc_free_encoder)
    lib.odc_encoder_set_row_count(encoder, nrows)
    lib.odc_encoder_set_rows_per_frame(encoder, rows_per_frame)

    # We store all of the numpy arrays here. Mostly this is just another reference to an
    # existing array, but some of the types require us to create a new (casted) copy, so
    # we need to put it somewhere to ensure it stays alive appropriately long.
    data_cache = []

    for i, (name, data) in enumerate(df.items()):
        data, typ = infer_column_type(data, types.get(name, None))
        data_cache.append(data)
        assert i == lib.odc_encoder_add_column(encoder, name.encode('utf-8'), typ)
        lib.odc_encoder_column_set_size(encoder, i, data.dtype.itemsize)
        lib.odc_encoder_column_set_stride(encoder, i, data.strides[0])
        lib.odc_encoder_column_set_data(encoder, i, ffi.cast("void*", data.values.ctypes.data))

    lib.odc_encode_to_file_descriptor(encoder, f.fileno())


def decode_dataframe(source, columns=None):

    o = Odb(source)

    assert len(o.frames) == 1
    return o.frames[0].dataframe(columns=columns)
