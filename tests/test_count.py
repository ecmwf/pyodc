from tempfile import NamedTemporaryFile

import odyssey as odyssey_python
import codyssey
odyssey_modules = [odyssey_python, codyssey]

import pandas
import pytest
import os


data_file1 = os.path.join(os.path.dirname(__file__), 'data/data1.odb')


@pytest.mark.parametrize("odyssey", odyssey_modules)
def test_count(odyssey):

    print("We are here")
    print(odyssey.__version__)

    r = odyssey.Reader(data_file1, aggregated=False)

    frames = r.frames

    assert len(frames) == 11
    assert all (t.ncolumns == 55 for t in frames)
    assert sum (t.nrows for t in frames) == 13


@pytest.mark.parametrize("odyssey", odyssey_modules)
def test_count_file(odyssey):
    """Check that we can open a file like object"""
    with open(data_file1, 'rb') as f:
        r = odyssey.Reader(f, aggregated=False)

    frames = r.frames
    assert len(frames) == 11
    assert all (t.ncolumns == 55 for t in frames)
    assert sum (t.nrows for t in frames) == 13


@pytest.mark.parametrize("odyssey", odyssey_modules)
def test_count_aggregated_file(odyssey):
    """Check that we can open a file like object"""
    with open(data_file1, 'rb') as f:
        r = odyssey.Reader(f, aggregated=True)

    frames = r.frames
    assert len(frames) == 1
    assert all (t.ncolumns == 55 for t in frames)
    assert sum (t.nrows for t in frames) == 13

#
#def test_column_metadata():
#
#    o = odyssey.Odb("/home/simon/testcases/odb/BTEM.2.odb")
#    # o = odyssey.Odb("/home/simon/git/odb/python-simpleodb/testout.odb")
#
#    t = o.frames[0]
#
#    # df = o.tables[1].dataframe(columns=('seqno', 'obsvalue', 'statid', 'groupid', 'reportype', 'lat'))
#
#    with pandas.option_context('display.max_rows', None, 'display.max_columns', None):
#        t = o.frames[0]
#        df = t.dataframe(columns=('seqno', 'obsvalue', 'statid', 'groupid', 'reportype', 'lat'))
#        # df = t.dataframe()
#        print(df.shape)
#        # print(o.tables[0].dataframe())
#        # print(o.tables[1].dataframe())
#
#        # print(df[df.keys()[0]   ])
#        # print(df['seqno@hdr'])


@pytest.mark.parametrize("odyssey", odyssey_modules)
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

    with NamedTemporaryFile() as fencode:
        odyssey.encode_odb(df, fencode, types=types, rows_per_table=4)
        fencode.flush()

        df2 = odyssey.read_odb(fencode.name)
        print(df2)

        with open(fencode.name, 'rb') as fread:
            df3 = odyssey.read_odb(fread, columns=('col6', 'col7'))
            print(df3)


if __name__ == "__main__":
    pytest.main()