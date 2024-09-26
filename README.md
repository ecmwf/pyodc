# pyodc

[![PyPI](https://img.shields.io/pypi/v/pyodc)](https://pypi.org/project/pyodc/)
[![Build Status](https://img.shields.io/github/workflow/status/ecmwf/pyodc/Continuous%20Integration/develop)](https://github.com/ecmwf/pyodc/actions/workflows/ci.yml)
[![Documentation Status](https://readthedocs.org/projects/pyodc/badge/?version=latest)](https://pyodc.readthedocs.io/en/latest/?badge=latest)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Licence](https://img.shields.io/github/license/ecmwf/pyodc)](https://github.com/ecmwf/pyodc/blob/develop/LICENSE)

A Python interface to `odc` for encoding/decoding ODB\-2 files.

The package contains two different implementations of the same library:

* `pyodc` is a pure-python encoder and decoder for ODB\-2 data, which encodes data from, and decodes it into pandas data frames
* `codc` is an implementation of the same API as `pyodc` that depends on the ECMWF `odc` library, and comes with _much_ better performance

[Documentation] [Changelog]

## Dependencies

### Required

* Python 3.x

### Optional

* [odc]
* [pytest]
* [pandoc]
* [Jupyter Notebook]

For `codc` to work, `odc` library must be compiled and installed on the system and made available to Python (through the CFFI mechanism) as a shared library. There are multiple ways to make the library visible to CFFI: it can be installed as a system library, the installation prefix can be passed in the `odc_DIR` or `ODC_DIR` environment variables, or the library directory can be included in `LD_LIBRARY_PATH`.

## Installation

```sh
pip install --user pyodc
```

Check if the module was installed correctly:

```sh
python
>>> import pyodc
>>> import codc # optional
```

## Usage

An introductory Jupyter Notebook with helpful usage examples is provided in the root of this repository:

```sh
git clone git@github.com:ecmwf/pyodc.git
cd pyodc
jupyter notebook Introduction.ipynb
```

## Development

### Run Unit Tests

To run the unit tests, make sure that the `pytest` module is installed first:

```sh
python -m pytest
```

### Run Unit Tests across multiple python versions with Tox

Tox is a useful tool to quickly run pytest across multiple python versions by managing a set of python environments for you. A tox.ini file is provided that targets python3.8 - 3.12. Note that this will also install older versions of libraries like numpy which helps to catch incompatibilities with older versions of those libraries too.

To run tox, [install it](https://tox.wiki/), modify the `ODC_HOME = ../build` line in tox.ini to point to a build of odc, this will be reused for all the tests. Then run
```sh
tox
```
The first run will take a while for it to install all the environments but after that it's very fast.

### Build Documentation

To build the documentation locally, please install the Python dependencies first:

```sh
cd docs
pip install -r requirements.txt
make html
```

The built HTML documentation will be available under the `docs/_build/html/index.html` path.

## License

This software is licensed under the terms of the Apache Licence Version 2.0 which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

In applying this licence, ECMWF does not waive the privileges and immunities granted to it by virtue of its status as an intergovernmental organisation nor does it submit to any jurisdiction.

[Documentation]: https://pyodc.readthedocs.io/en/latest/
[Changelog]: ./CHANGELOG.md
[odc]: https://github.com/ecmwf/odc
[pytest]: https://pytest.org
[pandoc]: https://pandoc.org/
[Jupyter Notebook]: https://jupyter.org
