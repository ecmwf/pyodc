
Changelog for pyodc
=====================

1.0.4
--------------------

- Correct support for constant codecs
- Decoding by column short name

1.0.3
--------------------

- Specify odc library location with odc/ODC_DIR
- Correct setup.py dependencies to include pandas
- Support missing ConstantString values encoded from ODB1 using the odb_migrator

1.0.2
--------------------

- String missing values should be None not NaN
- Refactor oneshot behaviour (read_odb_oneshot --> read_odb(..., single=True)
- Raise correct error on odc not found
- Split codb.py into a full codc module
- Fix miscellaneous bugs

1.0.1
--------------------

- Fixed automatic selection of integral codecs

1.0.0
--------------------

- Initial version
