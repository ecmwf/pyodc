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

__version__ = "0.19.0.dev0"

# Locate the C API
# TODO: Fallback to the python apy

print("CTYPES PATH: ", ctypes.util.find_library("libodbcore.so"))

# TODO: Find this API file properly
with open('/home/ma/mass/git/odb/odc/odc/src/odc/api/odc_c.h', 'r') as f:
    hdr = f.read()

ffi = cffi.FFI()
ffi.cdef(hdr)

lib = ffi.dlopen('libodccore.so')

print(lib)
