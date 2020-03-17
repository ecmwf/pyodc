
Installation
============

The package is installed from PyPI with::

    $ pip install pyodc


System dependencies
-------------------

The package contains two different implementations of the same library.

pyodc is a pure-python encoder and decoder for ODB2 data, which encodes data
from, and decodes it into pandas dataframes.

codc is an implementation of the same API as pyodc that depends on the ECMWF
*odc* library. This must be complied and installed on the system and made
available to python (through the CFFI mechanism) as a shared library. This
may involve adding its location to the LD_LIBRARY_PATH variable.

The odc library may be found at https://github.com/ecmwf/odc

Contributing
============

The main repository is hosted on GitHub,
testing, bug reports and contributions are highly welcomed and appreciated:

https://github.com/ecmwf/odyssey

Please see the CONTRIBUTING.rst document for the best way to help.

Lead developer:

- Simon Smart - `ECMWF <https://ecmwf.int>`_

Main contributors:

- Baudouin Raoult - `ECMWF <https://ecmwf.int>`_

See also the list of `contributors <https://github.com/ecmwf/odyssey/contributors>`_ who participated in this project.


License
=======

Copyright 2017-2018 European Centre for Medium-Range Weather Forecasts (ECMWF).

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at: http://www.apache.org/licenses/LICENSE-2.0.
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
