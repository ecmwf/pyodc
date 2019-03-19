import pandas

import pytest
import odyssey


def test_count():

    print("We are here")
    print(odyssey.__version__)

    o = odyssey.Odb("/home/simon/testcases/odb/BTEM.2.odb")
    # o = odyssey.Odb("/home/ma/mass/testcases/odb_play/BTEM.2.odb")

    tables = o.tables

    assert len(tables) == 221
    assert all (t.ncolumns == 113 for t in tables)
    assert sum (t.nrows for t in tables) == 1382274


def test_count_file():
    """Check that we can open a file like object"""
    with open('/home/simon/testcases/odb/BTEM.2.odb', 'rb') as f:
        o = odyssey.Odb(f)

    tables = o.tables
    assert len(tables) == 221
    assert all (t.ncolumns == 113 for t in tables)
    assert sum (t.nrows for t in tables) == 1382274


def test_column_metadata():

    o = odyssey.Odb("/home/simon/testcases/odb/BTEM.2.odb")
    # o = odyssey.Odb("/home/simon/git/odb/python-simpleodb/testout.odb")

    t = o.tables[0]

    # df = o.tables[1].dataframe(columns=('seqno', 'obsvalue', 'statid', 'groupid', 'reportype', 'lat'))

    with pandas.option_context('display.max_rows', None, 'display.max_columns', None):
        t = o.tables[0]
        df = t.dataframe(columns=('seqno', 'obsvalue', 'statid', 'groupid', 'reportype', 'lat'))
        # df = t.dataframe()
        print(df.shape)
        # print(o.tables[0].dataframe())
        # print(o.tables[1].dataframe())

        # print(df[df.keys()[0]   ])
        # print(df['seqno@hdr'])


def test_encode():
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
        'col21': [None] * 7
    }

    df = pandas.DataFrame(data)

    types = {
        'col8': odyssey.REAL,
        'col10': odyssey.REAL,
    }

    with open('abcdef.odb', 'wb') as f:
        odyssey.encode_dataframe(df, f, types=types, rows_per_table=4)

    df2 = odyssey.decode_dataframe('abcdef.odb')
    print(df2)

    with open('abcdef.odb', 'rb') as f:
        df3 = odyssey.decode_dataframe(f, columns=('col6', 'col7'))
        print(df3)

