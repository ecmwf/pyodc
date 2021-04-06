pyodc
=====

A python API for handling ODB2 data.

The package contains two different implementations of the same library:

* `pyodc` is a pure-python encoder and decoder for ODB2 data, which encodes data from, and decodes it into pandas data frames
* `codc` is an implementation of the same API as `pyodc` that depends on the ECMWF **odc** library, and comes with _much_ better performance


Requirements
------------

* Python 2/2.7/3/3.5/3.6/3.7
* [odc](https://github.com/ecmwf/odc) _(optional)_

In order for `codc` to work, **odc** library must be compiled and installed on the system and made available to Python (through the CFFI mechanism) as a shared library.


Installation
------------

```sh
pip install --user pyodc
```

Check if the module was installed correctly:

```sh
python
>>> import pyodc
>>> import codc # optional
>>> quit()
```


Usage
-----

An introductory [Jupyter Notebook](https://jupyter.org/) with helpful usage examples is provided in the root of this repository:

```sh
git clone git@github.com:ecmwf/pyodc.git
cd pyodc
jupyter notebook Introduction.ipynb
```


Development
-----------

Install from the code repository:

```sh
git clone git@github.com:ecmwf/pyodc.git
cd pyodc
pip install --user .
```

To run the unit tests, make sure that the `pytest` module is installed first:

```sh
pip install --user pytest
python -m pytest
```


License
-------

It is distributed under the Apache license 2.0 - see the accompanying [LICENSE](./LICENSE) file for more details.
