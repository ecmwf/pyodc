# This tests a specific case of optimisation from the old encoder, WriteBufferingIterator.
#
# This pre-initialised the rows buffer with missing values. As such, for the first row of
# data, if these contained missing values, it did not differ from the previous row.
#
# If the first values in the row to be encoded (i.e. the slowest varying column) contained
# a missing value, then according to this metric, it did not need to be encoded, and the
# starting row marker would be non-zero.
#
# We need to ensure that these get correctly decoded!

# See ODB-533

import os

import numpy
import pandas
import pytest
from conftest import odc_modules


@pytest.mark.parametrize("odyssey", odc_modules)
def test_initial_missing1(odyssey):
    check_data = {
        "stringval": ["", "testing"],
        "intval": [None, 12345678],
        "realval": [None, 1234.56],
        "doubleval": [None, 9876.54],
    }

    check_df = pandas.DataFrame(check_data)

    data_file = os.path.join(os.path.dirname(__file__), "data/odb_533_1.odb")
    df = odyssey.read_odb(data_file, single=True)

    print(check_df)
    print(df)

    assert set(check_df.columns) == set(df.columns)
    for col in df.columns:
        numpy.testing.assert_array_equal(df[col], check_df[col])


@pytest.mark.parametrize("odyssey", odc_modules)
def test_initial_missing2(odyssey):
    check_data = {
        "stringval": ["", "testing"],
        "intval": [None, 12345678],
        "realval": [None, 1234.56],
        "doubleval": [None, 9876.54],
        "changing": [1234, 5678],
    }

    check_df = pandas.DataFrame(check_data)

    data_file = os.path.join(os.path.dirname(__file__), "data/odb_533_2.odb")
    df = odyssey.read_odb(data_file, single=True)

    print(check_df)
    print(df)

    assert set(check_df.columns) == set(df.columns)
    for col in df.columns:
        numpy.testing.assert_array_equal(df[col], check_df[col])
