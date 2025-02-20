
# Changelog for pyodc

## 1.6.0

* `pip install pyodc` will now install the C++ backend so `codc` will work immediately.
    * The C++ backed is now installable with pip from `odclib`.
    * Added `findlibs` and `odclib` as dependencies.
    * To force the use of a different `odc` shared library, set the environment variable `ODC_DIR` to the directory containing the shared library. See the [findlibs] documentation for more information.


## 1.5.0

* Add a new LongConstantString codec which permits encoding constant columns where the constant is a string > 8 characters in length.
    * This saves 1 byte per row compared the previous way these columns were encoded.
    * A C++ implementation has been added to ODC at the same time, version 1.6.0
    * Bumped required ODC version to 1.6.0 for feature parity.
    * Decoding data using this codec will work straight away.
    * Encoding data with the new codec is disabled by default and can be enabled with the environment variable "ODC_ENABLE_WRITING_LONG_STRING_CODEC=1".
    * At some point in a future release, encoding will be enabled by default.

* Accept various new datatypes and tighten datatype selection logic (fixes [ODB-559]):
    * Unsigned Integers: uint8 - uint32 (note uint64 is not supported).
    * Signed Integers: int8 - int64.
    * Float32 in addition to float64.
    * Fixed the selection logic for ShortReal2 and ShortReal codecs so the smallest positive normal float32 number `struct.unpack("<f", b"\x00\x00\x80\x00")[0]` can now be used in data.

* Converted to a pyproject.toml based package.

* Fix various warnings:
    * Pandas Deprecation warning about `df.dtypes[0]` needing to become `df.dtypes.iloc[0]`.
    * Pandas Deprecation warning about converting implicitly converting dataframe column dtype.
    * Pandas Future Warning about concatenation with empty or all-NA dataframes.
    * "pkg_resources is deprecated as an API."

## 1.4.1

* Use findlibs instead of custom finder for odc
* Support constant bitfields
* Correct encoding with constant strings > 8 characters in length
* Support pandas native string type
* Fix access to exploded bitfield columns

## 1.1.3

* Improved github/ci integration

## 1.1.2

* Fixed [#6]: pip install breaks codc

## 1.1.1

* Fixed [ODB-534]: PyPI package is missing CHANGELOG

## 1.1.0

* Fixed [ODB-533]: Decode data starting with missing values correctly
* Fixed [ODB-530]: Bitfield column inspection returns incomplete data in pure-Python implementation
* Bumped up required `odc` version number to 1.4.0
* Added missing frame properties accessor to `codc` interface
* Fixed [ODB-525]: Setting odc prefix variable (`odc_DIR`) does not work as expected on macOS
* Fixed [ODB-524]: Keys and values in decoded frame properties are switched on older Python version
* Added test flag to skip `codc` tests on demand (`PYODC_SKIP_CODC`)
* Fixed [ODB-523]: Additional properties parameter is omitted in encode_odb() when string is passed as file
* Fixed package setup metadata
* Added documentation

## 1.0.4

* Correct support for constant codecs
* Decoding by column short name

## 1.0.3

* Specify `odc` library location with `odc/ODC_DIR`
* Correct `setup.py` dependencies to include pandas
* Support missing ConstantString values encoded from ODB1 using the `odb_migrator`

## 1.0.2

* String missing values should be `None` not `NaN`
* Refactor oneshot behaviour (`read_odb_oneshot` --> `read_odb(..., single=True)`)
* Raise correct error on `odc` not found
* Split `codb.py` into a full `codc` module
* Fix miscellaneous bugs

## 1.0.1

* Fixed automatic selection of integral codecs

## 1.0.0

* Initial version


[findlibs]: https://github.com/ecmwf/findlibs/
[#6]: https://github.com/ecmwf/pyodc/issues/6
[ODB-559]: https://jira.ecmwf.int/browse/ODB-559
[ODB-534]: https://jira.ecmwf.int/browse/ODB-534
[ODB-533]: https://jira.ecmwf.int/browse/ODB-533
[ODB-530]: https://jira.ecmwf.int/browse/ODB-530
[ODB-525]: https://jira.ecmwf.int/browse/ODB-525
[ODB-524]: https://jira.ecmwf.int/browse/ODB-524
[ODB-523]: https://jira.ecmwf.int/browse/ODB-523
