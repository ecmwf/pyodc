from tempfile import NamedTemporaryFile

import numpy.testing
import pandas
import pytest
from conftest import ODC_VERSION, codc, odc_modules

SAMPLE_DATA = {
    "col1": [1, 2, 3, 4, 5, 6, 7],
    "col2": [0, 0, 0, 0, 0, 0, 0],
    "col3": [73] * 7,
    "col4": [1.432] * 7,
    "col5": [-17, -7, -7, None, 1, 4, 4],
    "col6": ["aoeu", "aoeu", "aaaaaaaooooooo", "None", "boo", "squiggle", "a"],
    "col7": ["abcd"] * 7,
    "col8": [2.345] * 7,
    "col9": [999.99, 888.88, 777.77, 666.66, 555.55, 444.44, 333.33],
    "col10": [999.99, 888.88, 777.77, 666.66, 555.55, 444.44, 333.33],
    "col11": [1, None, 3, 4, 5, None, 7],
    "col12": [-512, None, 3, 7623, -22000, None, 7],
    "col13": [-1234567, 8765432, None, 22, 22222222, -81222323, None],
    "col14": [0b0000, 0b1001, 0b0110, 0b0101, 0b1010, 0b1111, 0b0000],
    "col15": [0b0000, 0b1001, None, 0b0101, 0b1010, 0b1111, 0b0000],
    "constant_bitfield": [0b1100] * 7,
}

SAMPLE_PROPERTIES = {
    "property1": "this is a string ....",
    "property2": ".......and another .......",
}

SAMPLE_BITFIELDS = {
    "col14": ["bf1", ("bfextended", 2), ("bf3", 1)],
    "col15": ["bf1", ("bfextended", 2), ("bf3", 1)],
    "constant_bitfield": ["bf1", ("bfextended", 2), ("bf3", 1)],
}


def assert_dataframe_equal(df1, df2):
    """
    Assert that two dataframes are equal, but ignoring column order
    """
    pandas.testing.assert_frame_equal(
        df1.sort_index(axis=1),
        df2.sort_index(axis=1),
    )


def encode_sample(odyssey, f):
    df = pandas.DataFrame(SAMPLE_DATA)

    types = {
        "col8": odyssey.REAL,
        "col10": odyssey.REAL,
        "col14": odyssey.BITFIELD,
        "col15": odyssey.BITFIELD,
        "constant_bitfield": odyssey.BITFIELD,
        # 'col21': odyssey.REAL
    }

    properties = SAMPLE_PROPERTIES

    bitfields = SAMPLE_BITFIELDS

    odyssey.encode_odb(df, f, types=types, rows_per_frame=4, properties=properties, bitfields=bitfields)

    if not isinstance(f, str):
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
            if col in ("col8", "col10"):
                numpy.testing.assert_array_almost_equal(s1, s2, decimal=2)
            else:
                numpy.testing.assert_array_equal(s1, s2)


@pytest.mark.parametrize("odyssey", odc_modules)
def test_encode_decode_file_object(odyssey):
    with NamedTemporaryFile() as fencode:
        df = encode_sample(odyssey, fencode)

        with open(fencode.name, "rb") as fread:
            df2 = odyssey.read_odb(fread, single=True)
            assert isinstance(df2, pandas.DataFrame)

        for col in df.keys():
            s1 = df[col]
            s2 = df2[col]
            if col in ("col8", "col10"):
                numpy.testing.assert_array_almost_equal(s1, s2, decimal=2)
            else:
                numpy.testing.assert_array_equal(s1, s2)


@pytest.mark.parametrize("odyssey", odc_modules)
def test_encode_decode_simple_columns(odyssey):
    with NamedTemporaryFile() as fencode:
        df = encode_sample(odyssey, fencode)

        cols = ("col6", "col7")
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
    sample1 = {"col1": [111, 222, 333]}

    sample2 = {"col2": ["aaa", "bbb", "ccc"]}

    with NamedTemporaryFile() as fencode:
        odyssey.encode_odb(pandas.DataFrame(sample1), fencode)
        odyssey.encode_odb(pandas.DataFrame(sample2), fencode)
        fencode.flush()

        df = odyssey.read_odb(fencode.name, single=True)
        assert isinstance(df, pandas.DataFrame)

        assert df["col1"].dtype == "float64"
        assert df["col2"].dtype == "object"
        assert df["col2"][0] is None
        numpy.testing.assert_array_equal(df["col1"], [111.0, 222.0, 333.0, numpy.nan, numpy.nan, numpy.nan])
        numpy.testing.assert_array_equal(df["col2"], [None, None, None, "aaa", "bbb", "ccc"])


@pytest.mark.parametrize("odyssey", odc_modules)
def test_unqualified_names(odyssey):
    """
    Check that we can extract columns by unqualified name, and by fully qualified name
    (that is, where the name contains an '@', we can extract by short name
    """
    sample = {
        "col1@tbl1": [11, 12, 13, 14, 15, 16],
        "col2@tbl1": [21, 22, 23, 24, 25, 26],
        "col1@tbl2": [31, 32, 33, 34, 35, 36],
        "col3@tbl2": [41, 42, 43, 44, 45, 46],
        "col4": [51, 52, 53, 54, 55, 56],
    }

    input_df = pandas.DataFrame(sample)

    with NamedTemporaryFile() as fencode:
        odyssey.encode_odb(input_df, fencode)
        fencode.flush()

        # Check fully-qualified naming

        cols = ["col1@tbl1", "col3@tbl2", "col4"]
        df = odyssey.read_odb(fencode.name, single=True, columns=cols)
        expected_df = input_df[cols]
        assert_dataframe_equal(df, expected_df)

        # Check quick-access naming

        cols = ["col2", "col3", "col4"]
        df = odyssey.read_odb(fencode.name, single=True, columns=cols)
        assert len(df.keys()) == 3
        assert set(df.keys()) == set(cols)
        expected_df = pandas.DataFrame(
            {
                "col2": sample["col2@tbl1"],
                "col3": sample["col3@tbl2"],
                "col4": sample["col4"],
            }
        )
        assert_dataframe_equal(df, expected_df)

        # What happens if we try and access an ambiguous columns?

        with pytest.raises(KeyError):
            odyssey.read_odb(fencode.name, single=True, columns=["col1"])


@pytest.mark.parametrize("odyssey", odc_modules)
def test_encode_decode_properties(odyssey):
    """Check that additional properties are encoded and decoded properly."""

    with NamedTemporaryFile() as fencode:
        # Test both by passing file handle and name to the encoding function.
        #   Please see ODB-523 for more information.
        for f in [fencode, fencode.name]:
            encode_sample(odyssey, f)

            reader = odyssey.Reader(fencode.name)

            for frame in reader.frames:
                expected_properties = SAMPLE_PROPERTIES

                # C library adds an implicit `encoder` property to each frame
                if odyssey == codc:
                    expected_properties["encoder"] = "odc version " + ODC_VERSION

                assert frame.properties == expected_properties


@pytest.mark.parametrize("odyssey", odc_modules)
def test_encode_decode_bitfields(odyssey):
    """
    Check that bitfields are appropriately encoded with all the details
    """
    EXPECTED_ALL = [0b0000, 0b1001, 0b0110, 0b0101, 0b1010, 0b1111, 0b0000]
    EXPECTED1 = [False, True, False, True, False, True, False]
    EXPECTED2 = [0, 0, 3, 2, 1, 3, 0]
    EXPECTED3 = [False, True, False, False, True, True, False]

    EXPECTED_ALLb = [0b0000, 0b1001, None, 0b0101, 0b1010, 0b1111, 0b0000]
    EXPECTED1b = [False, True, None, True, False, True, False]
    EXPECTED2b = [0, 0, None, 2, 1, 3, 0]
    EXPECTED3b = [False, True, None, False, True, True, False]

    with NamedTemporaryFile() as fencode:
        encode_sample(odyssey, fencode)

        reader = odyssey.Reader(fencode.name)

        # Check that the frame contains the correct bitfield info

        for frame in reader.frames:
            for colname in ("col14", "col15"):
                col = frame.column_dict[colname]
                assert col.dtype == odyssey.BITFIELD
                assert len(col.bitfields) == 3
                assert col.bitfields[0].name == "bf1"
                assert col.bitfields[0].size == 1
                assert col.bitfields[0].offset == 0
                assert col.bitfields[1].name == "bfextended"
                assert col.bitfields[1].size == 2
                assert col.bitfields[1].offset == 1
                assert col.bitfields[2].name == "bf3"
                assert col.bitfields[2].size == 1
                assert col.bitfields[2].offset == 3

        # Check that the decoded columns look right

        df = odyssey.read_odb(fencode.name, single=True)

        data = df["col14"]
        expected = pandas.Series(EXPECTED_ALL, name="col14")
        pandas.testing.assert_series_equal(data, expected)

        data = df["col15"]
        expected = pandas.Series(EXPECTED_ALLb, name="col15")
        pandas.testing.assert_series_equal(data, expected)

        # Check that we can decode specific bitfield colmuns

        df = odyssey.read_odb(fencode.name, columns=["col14.bf3", "col14.bfextended", "col14.bf1"], single=True)
        expected_df = pandas.DataFrame({"col14.bf1": EXPECTED1, "col14.bfextended": EXPECTED2, "col14.bf3": EXPECTED3})
        assert_dataframe_equal(df, expected_df)

        df = odyssey.read_odb(fencode.name, columns=["col15.bf3", "col15.bfextended", "col15.bf1"], single=True)
        expected_df = pandas.DataFrame(
            {"col15.bf1": EXPECTED1b, "col15.bfextended": EXPECTED2b, "col15.bf3": EXPECTED3b}
        )
        assert_dataframe_equal(df, expected_df)

        # Check that we can decode all the things at the same time...

        df = odyssey.read_odb(fencode.name, columns=["col14.bf3", "col14", "col14.bf1"], single=True)
        expected_df = pandas.DataFrame({"col14.bf1": EXPECTED1, "col14": EXPECTED_ALL, "col14.bf3": EXPECTED3})
        assert_dataframe_equal(df, expected_df)

        df = odyssey.read_odb(fencode.name, columns=["col15.bf3", "col15", "col15.bf1"], single=True)
        expected_df = pandas.DataFrame({"col15.bf1": EXPECTED1b, "col15": EXPECTED_ALLb, "col15.bf3": EXPECTED3b})
        assert_dataframe_equal(df, expected_df)

        # Check that we get a sensible error if we request a bitfield that doesn't exist

        with pytest.raises(KeyError):
            odyssey.read_odb(fencode.name, columns=["col14.badbf"], single=True)


@pytest.mark.parametrize("odyssey", odc_modules)
def test_encode_decode_bitfield_like(odyssey):
    sample = {
        "col1.bf1": [1, 0, 1, 0, 1, 0, 1],
        "col1.bf2": [1, 3, 2, 1, 3, 1, 2],
        "col1.bf3": [0, 1, 0, 1, 0, 1, 0],
    }

    input_df = pandas.DataFrame(sample)

    with NamedTemporaryFile() as fencode:
        odyssey.encode_odb(input_df, fencode)
        fencode.flush()

        # We can extract columns with more complex names

        df = odyssey.read_odb(fencode.name, single=True)
        assert isinstance(df, pandas.DataFrame)
        assert_dataframe_equal(df, input_df)

        assert "col1.bf1" in df
        assert "col1.bf2" in df
        assert "col1.bf3" in df

        # We can extract a subset of these columns

        df = odyssey.read_odb(fencode.name, single=True, columns=("col1.bf2",))

        assert "col1.bf1" not in df
        assert "col1.bf2" in df
        assert "col1.bf3" not in df

        numpy.testing.assert_array_equal(df["col1.bf2"], input_df["col1.bf2"])


@pytest.mark.parametrize("odyssey", odc_modules)
def test_encode_decode_bitfield_like_fully_qualified(odyssey):
    sample = {
        "col1.bf1@tbl": [1, 0, 1, 0, 1, 0, 1],
        "col1.bf2@tbl": [1, 3, 2, 1, 3, 1, 2],
        "col1.bf3@tbl": [0, 1, 0, 1, 0, 1, 0],
        "col1@tbl": [0, 0, 0, 0, 0, 0, 0],
    }

    input_df = pandas.DataFrame(sample)

    with NamedTemporaryFile() as fencode:
        odyssey.encode_odb(input_df, fencode)
        fencode.flush()

        # We can extract columns with more complex names

        df = odyssey.read_odb(fencode.name, single=True)
        assert isinstance(df, pandas.DataFrame)
        assert_dataframe_equal(df, input_df)

        assert "col1.bf1@tbl" in df
        assert "col1.bf2@tbl" in df
        assert "col1.bf3@tbl" in df

        # We can extract a subset of these columns

        df = odyssey.read_odb(fencode.name, single=True, columns=("col1.bf2", "col1"))

        assert "col1" in df
        assert "col1.bf1" not in df
        assert "col1.bf2" in df
        assert "col1.bf3" not in df
        assert "col1@tbl" not in df
        assert "col1.bf1@tbl" not in df
        assert "col1.bf2@tbl" not in df
        assert "col1.bf3@tbl" not in df

        numpy.testing.assert_array_equal(df["col1.bf2"], input_df["col1.bf2@tbl"])
        numpy.testing.assert_array_equal(df["col1"], input_df["col1@tbl"])

        # And by fully qualified name

        df = odyssey.read_odb(fencode.name, single=True, columns=("col1.bf2@tbl", "col1@tbl"))

        assert "col1" not in df
        assert "col1.bf1" not in df
        assert "col1.bf2" not in df
        assert "col1.bf3" not in df
        assert "col1@tbl" in df
        assert "col1.bf1@tbl" not in df
        assert "col1.bf2@tbl" in df
        assert "col1.bf3@tbl" not in df

        numpy.testing.assert_array_equal(df["col1.bf2@tbl"], input_df["col1.bf2@tbl"])
        numpy.testing.assert_array_equal(df["col1@tbl"], input_df["col1@tbl"])


@pytest.mark.parametrize("encode_odc, decode_odc", [(e, d) for e in odc_modules for d in odc_modules])
def test_cross_library_encode_decode(encode_odc, decode_odc):
    "Check that all the four (encoder, decoder) pairs work across pyodc and codc, (if codc is present)."
    SAMPLE_TYPES = {
        "col14": encode_odc.BITFIELD,
        "col15": encode_odc.BITFIELD,
        "constant_bitfield": encode_odc.BITFIELD,
    }

    with NamedTemporaryFile() as f:
        df1 = pandas.DataFrame(SAMPLE_DATA)
        encode_odc.encode_odb(df1, f, types=SAMPLE_TYPES, bitfields=SAMPLE_BITFIELDS)
        f.flush()
        df2 = decode_odc.read_odb(f.name, single=True)
        assert_dataframe_equal(df1, df2)
