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

test_column_metadata()

