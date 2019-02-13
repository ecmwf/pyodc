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
import io
import os

__version__ = "0.19.0.dev0"

# Locate the C API
# TODO: Fallback to the python apy

# TODO: Find this API file properly
with open('/home/ma/mass/git/odb/odc/odc/src/odc/api/odc_c.h', 'r') as f:
    hdr = f.read()

# print("hdr", hdr)

ffi = cffi.FFI()
ffi.cdef(hdr)

print("ffi", ffi)

lib = ffi.dlopen('libodccore.so')
print("lib", lib)
lib.odc_error_handling(lib.ODC_ERRORS_CHECKED)


# Set up error handling

class ODCException(RuntimeError):
    pass


def __check_errors(helpstring=None):

    if lib.odc_errno != 0:
        if helpstring is None:
            helpstring = "make API call"

        helpstring = "Failed to {}: {}".format(helpstring, ffi.string(lib.odc_error_string()))
        lib.odc_reset_error()

        raise ODCException(helpstring)


# Initialise the API, and we are away


lib.odc_initialise_api()


class Odb:

    __odb = None
    __tables = None

    def __init__(self, source):
        if isinstance(source, io.IOBase):
            self.__odb = lib.odc_
        else:
            assert isinstance(source, str)
            self.__odb = lib.odc_open_for_read(source.encode())

        # Set free function
        self.__odb = ffi.gc(self.__odb, lib.odc_close)

    @property
    def tables(self):
        if self.__tables is None:
            ntables = lib.odc_num_tables(self.__odb)
            self.__tables = [
                Table(ffi.gc(
                    lib.odc_get_table(self.__odb, n),
                    lib.odc_free_table
                ))
                for n in range(ntables)
            ]

        return self.__tables


class Table:

    def __init__(self, table):
        self.__table = table

    @property
    def nrows(self):
        return lib.odc_table_num_rows(self.__table)

    @property
    def ncolumns(self):
        return lib.odc_table_num_columns(self.__table)

    def decode(self):
        decoded = lib.odc_table_decode_all(self.__table)
        return None




