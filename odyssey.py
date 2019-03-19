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

import cffi
import ctypes.util
import collections
import pandas
import numpy
import io
import os
import inspect

__version__ = "0.19.0.dev0"

print(ctypes.util.find_library("odccore"))

# Locate the C API
# TODO: Fallback to the python api

ffi = cffi.FFI()


class ODCException(RuntimeError):
    pass

class ODCAPIException(ODCException):
    pass


class PatchedLib:
    """
    Patch a CFFI library with error handling

    Finds the header file associated with the ODC C API and parses it, loads the shared library,
    and patches the accessors with automatic python-C error handling.
    """
    def __init__(self):

        ffi.cdef(self.__read_header())
        self.__lib = ffi.dlopen('libodccore.so')

        # Todo: Version check against __version__

        for f in dir(self.__lib):
            try:
                attr = getattr(self.__lib, f)
                setattr(self, f, self.__check_error(attr, f) if hasattr(attr, '__call__') else attr)
            except Exception as e:
                print(e)
                print("Error retrieving attribute", f, "from library")

    def __read_header(self):
        # TODO: Find this API file properly
        for p in ('/home/ma/mass/git/odb/odc/odc/src/odc/api/odc_c.h',
                  '/home/simon/git/odb/odc/odc/src/odc/api/odc_c.h'):
            if os.path.exists(p):
                with open(p, 'r') as f:
                    return f.read()
        raise RuntimeError("ODC header not found")

    def __check_error(self, fn, name):

        def wrapped_fn(*args, **kwargs):
            retval = fn(*args, **kwargs)

            if self.__lib.odc_errno != 0:
                helpstring = "Failed to execute {}: {}".format(name, ffi.string(self.__lib.odc_error_string()).decode())
                self.__lib.odc_reset_error()
                raise ODCAPIException(helpstring)
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


# And bootstrap the library

lib = PatchedLib()
lib.odc_initialise_api()
lib.odc_error_handling(lib.ODC_ERRORS_CHECKED)
lib.odc_integer_behaviour(lib.ODC_INTEGERS_AS_LONGS)

# Construct lookups/constants as is useful

TYPE_NAMES = [ffi.string(lib.odc_type_name(i)).decode() for i in range(lib.ODC_NUM_TYPES)]
TYPE_IDS = {name: i for i, name in enumerate(TYPE_NAMES)}

IGNORE = TYPE_IDS["ignore"]
INTEGER = TYPE_IDS["integer"]
DOUBLE = TYPE_IDS["double"]
REAL = TYPE_IDS["real"]
STRING = TYPE_IDS["string"]
BITFIELD = TYPE_IDS["bitfield"]


class Odb:
    """This is the main container class for reading ODBs"""

    __odb = None
    __tables = None

    def __init__(self, source):
        if isinstance(source, io.IOBase):
            self.__odb = lib.odc_open_from_fd(source.fileno())
        else:
            assert isinstance(source, str)
            self.__odb = lib.odc_open_for_read(source.encode())

        # Set free function
        self.__odb = ffi.gc(self.__odb, lib.odc_close)

    @property
    def tables(self):
        if self.__tables is None:
            self.__tables = []
            while True:
                t = lib.odc_next_table(self.__odb, True)
                if not t:
                    break
                self.__tables.append(Table(ffi.gc(t, lib.odc_free_table)))

        return self.__tables


class ColumnInfo:
    def __init__(self, name, idx, type, datasize, bitfields):
        self.name = name
        self.type = type
        self.index = idx
        self.datasize = datasize
        self.bitfields = bitfields
        assert (type == BITFIELD) != (bitfields is None)

    def __str__(self):
        if self.bitfields is not None:
            bitfield_str = "(" + ",".join("{}:{}".format(b[0], b[1]) for b in self.bitfields) + ")"
        else:
            bitfield_str = ""
        return "{}:{}{}".format(self.name, TYPE_NAMES[self.type], bitfield_str)

    def __repr__(self):
        return str(self)


class Table:

    def __init__(self, table):
        self.__table = table
        self.__columns = None

    @property
    @memoize_constant
    def columns(self):
        columns = []
        for col in range(self.ncolumns):

            name = ffi.string(lib.odc_table_column_name(self.__table, col)).decode()
            type = lib.odc_table_column_type(self.__table, col)
            datasize = lib.odc_table_column_data_size(self.__table, col)
            bitfields = None

            if type == STRING:
                assert datasize % 8 == 0
            else:
                assert datasize == 8

            if type == BITFIELD:
                num_fields = lib.odc_table_column_bitfield_count(self.__table, col)
                bitfields = []
                for n in range(num_fields):
                    bitfields.append((
                        ffi.string(lib.odc_table_column_bitfield_field_name(self.__table, col, n)).decode(),
                        lib.odc_table_column_bitfield_field_size(self.__table, col, n),
                        lib.odc_table_column_bitfield_field_offset(self.__table, col, n)))

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
        return lib.odc_table_num_rows(self.__table)

    @property
    @memoize_constant
    def ncolumns(self):
        return lib.odc_table_num_columns(self.__table)

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

        columns_data = ffi.new('struct odb_strided_column_t[]', len(columns))

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
                    columns_data[pos].data = ffi.cast("char *", pointer + (i * strides[1]))
                    columns_data[pos].nelem = self.nrows
                    columns_data[pos].elemSize = dsize
                    columns_data[pos].stride = strides[0]
                    columns_data[pos].name = col.name.encode('utf-8')
                    pos += 1

                dataframes.append(pandas.DataFrame(array, columns=[c.name for c in cols], copy=False))

        rows_decoded = lib.odc_table_decode(self.__table, len(columns), self.nrows, columns_data, 4)
        assert rows_decoded == self.nrows

        # And construct the DataFrame from the decoded data

        if len(dataframes) == 1:
            return dataframes[1]
        else:
            return pandas.concat(dataframes, copy=False, axis=1)


def encode_dataframe(df: pandas.DataFrame, f: io.IOBase, types: dict=None, **kwargs):

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

    ncols = df.shape[1]
    nrows = df.shape[0]
    if types is None:
        types = {}

    column_data = ffi.new('struct odb_strided_column_t[]', ncols)

    # We store all of the numpy arrays here. Mostly this is just another reference to an
    # existing array, but some of the types require us to create a new (casted) copy, so
    # we need to put it somewhere to ensure it stays alive appropriately long.
    data_cache = []

    for i, (name, data) in enumerate(df.items()):
        data, typ = infer_column_type(data, types.get(name, None))
        data_cache.append(data)
        column_data[i].type = typ
        column_data[i].data = ffi.cast("char *", data.values.ctypes.data)
        column_data[i].nelem = nrows
        column_data[i].elemSize = data.dtype.itemsize
        column_data[i].stride = data.strides[0]
        column_data[i].name = name.encode("utf-8")

    lib.odc_table_encode_to_file(f.fileno(), ncols, nrows, column_data, 10000)


def decode_dataframe(source, columns=None):

    o = Odb(source)

    assert len(o.tables) == 1
    return o.tables[0].dataframe(columns=columns)
