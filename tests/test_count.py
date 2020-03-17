from tempfile import NamedTemporaryFile

import pyodc
import codc
odc_modules = [pyodc, codc]

import pandas
import pytest
import os


data_file1 = os.path.join(os.path.dirname(__file__), 'data/data1.odb')


@pytest.mark.parametrize("odyssey", odc_modules)
def test_count(odyssey):

    print("We are here")
    print(odyssey.__version__)

    r = odyssey.Reader(data_file1, aggregated=False)

    frames = r.frames

    assert len(frames) == 11
    assert all (t.ncolumns == 55 for t in frames)
    assert sum (t.nrows for t in frames) == 13


@pytest.mark.parametrize("odyssey", odc_modules)
def test_count_file(odyssey):
    """Check that we can open a file like object"""
    with open(data_file1, 'rb') as f:
        r = odyssey.Reader(f, aggregated=False)

    frames = r.frames
    assert len(frames) == 11
    assert all (t.ncolumns == 55 for t in frames)
    assert sum (t.nrows for t in frames) == 13


@pytest.mark.parametrize("odyssey", odc_modules)
def test_count_aggregated_file(odyssey):
    """Check that we can open a file like object"""
    with open(data_file1, 'rb') as f:
        r = odyssey.Reader(f, aggregated=True)

    frames = r.frames
    assert len(frames) == 1
    assert all (t.ncolumns == 55 for t in frames)
    assert sum (t.nrows for t in frames) == 13


@pytest.mark.parametrize("odyssey", odc_modules)
def test_encode(odyssey):
    data = {
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

    df = pandas.DataFrame(data)

    types = {
        'col8': odyssey.REAL,
        'col10': odyssey.REAL,
        # 'col21': odyssey.REAL
    }

    properties = {
        'property1': 'this is a string ....',
        'property2': '.......and another .......',
    }

    with NamedTemporaryFile() as fencode:
        odyssey.encode_odb(df, fencode, types=types, rows_per_frame=4, properties=properties)
        fencode.flush()

        df2 = odyssey.read_odb(fencode.name)
        print(df2)

        with open(fencode.name, 'rb') as fread:
            df3 = odyssey.read_odb(fread, columns=('col6', 'col7'))
            print(df3)


if __name__ == "__main__":
    pytest.main()
