
from tempfile import NamedTemporaryFile
import pandas
import pytest
import numpy.testing

from conftest import odc_modules


SAMPLE_DATA = {
    'col1': [1, 2, 3, 4, 5, 6, 7],
    'col2': [0, 0, 0, 0, 0, 0, 0],
    'col3': [73] * 7,
    'col4': [1.432] * 7,
    'col5': [-17, -7, -7, None, 1, 4, 4],
    'col6': ['aoeu', 'aoeu', 'aaaaaaaooooooo', 'None', 'boo', 'squiggle', 'a'],
    'col7': ['abcd'] * 7,
    'col8': [2.345] * 7,
    'col9': [999.99, 888.88, 777.77, 666.66, 555.55, 444.44, 333.33],
    'col10': [999.99, 888.88, 777.77, 666.66, 555.55, 444.44, 333.33],
    'col11': [1, None, 3, 4, 5, None, 7],
    'col12': [-512, None, 3, 7623, -22000, None, 7],
    'col13': [-1234567, 8765432, None, 22, 22222222, -81222323, None],
    # 'col21': [None] * 7
}


def encode_sample(odyssey, f):

    df = pandas.DataFrame(SAMPLE_DATA)

    types = {
        'col8': odyssey.REAL,
        'col10': odyssey.REAL,
        # 'col21': odyssey.REAL
    }

    properties = {
        'property1': 'this is a string ....',
        'property2': '.......and another .......',
    }

    odyssey.encode_odb(df, f, types=types, rows_per_frame=4, properties=properties)
    f.flush()
    return df


@pytest.mark.parametrize("odyssey", odc_modules)
def test_encode_decode_filename(odyssey):

    with NamedTemporaryFile() as fencode:
        df = encode_sample(odyssey, fencode)

        df2 = odyssey.read_odb(fencode.name, single=True)
        assert isinstance(df2, pandas.DataFrame)

        for col in df.keys():
            s1 = df[col]
            s2 = df2[col]
            if col in ('col8', 'col10'):
                numpy.testing.assert_array_almost_equal(s1, s2, decimal=2)
            else:
                numpy.testing.assert_array_equal(s1, s2)


@pytest.mark.parametrize("odyssey", odc_modules)
def test_encode_decode_file_object(odyssey):

    with NamedTemporaryFile() as fencode:
        df = encode_sample(odyssey, fencode)

        with open(fencode.name, 'rb') as fread:
            df2 = odyssey.read_odb(fread, single=True)
            assert isinstance(df2, pandas.DataFrame)

        for col in df.keys():
            s1 = df[col]
            s2 = df2[col]
            if col in ('col8', 'col10'):
                numpy.testing.assert_array_almost_equal(s1, s2, decimal=2)
            else:
                numpy.testing.assert_array_equal(s1, s2)


@pytest.mark.parametrize("odyssey", odc_modules)
def test_encode_decode_simple_columns(odyssey):

    with NamedTemporaryFile() as fencode:
        df = encode_sample(odyssey, fencode)

        cols = ('col6', 'col7')
        df2 = odyssey.read_odb(fencode.name, columns=cols, single=True)
        assert isinstance(df2, pandas.DataFrame)
        assert df2.shape[1] == len(cols)

        for col in cols:
            numpy.testing.assert_array_equal(df[col], df2[col])


@pytest.mark.parametrize("odyssey", odc_modules)
def test_aggregate_non_matching(odyssey):
    """
    Where we aggregate tables with non-matching columns, ensure that the infilled
    missing values are type appropriate
    """
    sample1 = {
        'col1': [111, 222, 333]
    }

    sample2 = {
        'col2': ['aaa', 'bbb', 'ccc']
    }

    with NamedTemporaryFile() as fencode:

        odyssey.encode_odb(pandas.DataFrame(sample1), fencode)
        odyssey.encode_odb(pandas.DataFrame(sample2), fencode)
        fencode.flush()

        df = odyssey.read_odb(fencode.name, single=True)
        assert isinstance(df, pandas.DataFrame)

        assert df['col1'].dtype == 'float64'
        assert df['col2'].dtype == 'object'
        assert df['col2'][0] is None
        numpy.testing.assert_array_equal(df['col1'], [111., 222., 333., numpy.nan, numpy.nan, numpy.nan])
        numpy.testing.assert_array_equal(df['col2'], [None, None, None, 'aaa', 'bbb', 'ccc'])


@pytest.mark.parametrize("odyssey", odc_modules)
def test_unqualified_names(odyssey):
    """
    Check that we can extract columns by unqualified name, and by fully qualified name
    (that is, where the name contains an '@', we can extract by short name
    """
    sample = {
        'col1@tbl1': [11, 12, 13, 14, 15, 16],
        'col2@tbl1': [21, 22, 23, 24, 25, 26],
        'col1@tbl2': [31, 32, 33, 34, 35, 36],
        'col3@tbl2': [41, 42, 43, 44, 45, 46],
        'col4': [51, 52, 53, 54, 55, 56],
    }

    input_df = pandas.DataFrame(sample)

    with NamedTemporaryFile() as fencode:
        odyssey.encode_odb(input_df, fencode)
        fencode.flush()

        # Check fully-qualified naming

        cols = ['col1@tbl1', 'col3@tbl2', 'col4']
        df = odyssey.read_odb(fencode.name, single=True, columns=cols)
        expected_df = input_df[cols]
        assert expected_df.equals(df)

        # Check quick-access naming

        cols = ['col2', 'col3', 'col4']
        df = odyssey.read_odb(fencode.name, single=True, columns=cols)
        assert len(df.keys()) == 3
        assert set(df.keys()) == set(cols)
        expected_df = pandas.DataFrame({
            'col2': sample['col2@tbl1'],
            'col3': sample['col3@tbl2'],
            'col4': sample['col4']
        })
        assert expected_df.equals(df)

        # What happens if we try and access an ambiguous columns?

        with pytest.raises(KeyError):
            odyssey.read_odb(fencode.name, single=True, columns=['col1'])
