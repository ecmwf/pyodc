
# Changelog for pyodc

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


[ODB-530]: https://jira.ecmwf.int/browse/ODB-530
[ODB-525]: https://jira.ecmwf.int/browse/ODB-525
[ODB-524]: https://jira.ecmwf.int/browse/ODB-524
[ODB-523]: https://jira.ecmwf.int/browse/ODB-523
