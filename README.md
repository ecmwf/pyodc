# pyodc

A Python interface to odc for encoding/decoding ODB\-2 files.

The package contains two different implementations of the same library:

* `pyodc` is a pure-python encoder and decoder for ODB\-2 data, which encodes data from, and decodes it into pandas data frames
* `codc` is an implementation of the same API as `pyodc` that depends on the ECMWF `odc` library, and comes with _much_ better performance

[CHANGELOG]

## Dependencies

### Required

* Python 3/3.5/3.6/3.7

### Optional

* [odc]
* [pytest]
* [Jupyter Notebook]

In order for `codc` to work, the `odc` library must be compiled and installed on the system and made available to Python (through the CFFI mechanism) as a shared library.

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

To run the unit tests, make sure that the `pytest` module is installed first:

```sh
python -m pytest
```

## License

`pyodc` is distributed under the Apache license 2.0 - see the accompanying [LICENSE] file for more details.

[CHANGELOG]: ./CHANGELOG.md
[LICENSE]: ./LICENSE
[odc]: https://github.com/ecmwf/odc
[pytest]: https://pytest.org
[Jupyter Notebook]: https://jupyter.org
