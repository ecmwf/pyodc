pyodc
=====

The package contains two different implementations of the same library:

* `pyodc` is a pure-python encoder and decoder for ODB2 data, which encodes data from, and decodes it into pandas data frames
* `codc` is an implementation of the same API as `pyodc` that depends on the ECMWF odc library


Requirements
------------

* Python 2/2.7/3/3.5/3.6/3.7
* [odc](https://github.com/ecmwf/odc) _(optional)_
  This must be compiled and installed on the system and made available to Python (through the CFFI mechanism) as a shared library for `codc` to work. This may involve adding its location to the `LD_LIBRARY_PATH` variable.


Installation
------------

```sh
pip install --user pyodc
```

Check if the module was installed correctly:

```sh
python
>>> import pyodc
>>> quit()
```


<!--
Usage
-----
-->


Development
-----------

Install from the code repository:

```sh
git clone git@github.com:ecmwf/pyodc.git
cd pyodc
pip install --user .
```

Install the `pytest` module first on order to run the unit tests:

```sh
pip install --user pytest
python -m pytest
```


License
-------

It is distributed under the Apache license 2.0 - see the accompanying [LICENSE](./LICENSE) file for more details.
