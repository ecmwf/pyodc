
import pytest
import odyssey


def test_count():

    print("We are here")
    print(odyssey.__version__)

    o = odyssey.Odb("/home/ma/mass/testcases/odb_play/BTEM.2.odb")

    tables = o.tables

    print("Num tables: ", len(tables))

    for t in tables:
        print(t.ncolumns, t.nrows)

    tables[1].decode_all()

    assert False
