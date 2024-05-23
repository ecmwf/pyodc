from tempfile import NamedTemporaryFile

import pandas as pd
import pytest
from conftest import odc_modules

# Quick sanity check from Tom Hodson, that things don't randomly fall apart. Doesn't check correctness of the data.


def _helper(encoder, decoder, original_columns, requested_columns):
    with NamedTemporaryFile() as file:
        df = pd.DataFrame(
            {
                c: [
                    c,
                ]
                for c in original_columns
            }
        )
        encoder.encode_odb(df, file.name)
        df2 = decoder.read_odb(file.name, single=True, columns=requested_columns)
        assert set(df2.columns) == set(requested_columns)
        selected_columns_full_names = df2.iloc[0].values
        return df, df2, selected_columns_full_names


@pytest.mark.parametrize("encoder", odc_modules)
@pytest.mark.parametrize("decoder", odc_modules)
def test_basic(encoder, decoder):
    "Check the most basic column selection works"
    _helper(encoder, decoder, original_columns=["foo@bar"], requested_columns=["foo@bar"])


@pytest.mark.parametrize("encoder", odc_modules)
@pytest.mark.parametrize("decoder", odc_modules)
def test_shortform(encoder, decoder):
    "Check that you can retrieve a column by short name"
    df, df2, full_names = _helper(encoder, decoder, original_columns=["foo@bar", "bar@des"], requested_columns=["foo"])
    assert "foo@bar" in full_names


@pytest.mark.parametrize("encoder", odc_modules)
@pytest.mark.parametrize("decoder", odc_modules)
def test_ambiguous_short_name(encoder, decoder):
    "Check that we get an error if you request foo when both foo@bar and foo@baz are present as columns"
    with pytest.raises(KeyError):
        _helper(encoder, decoder, original_columns=["foo@bar", "foo@desc"], requested_columns=["foo"])


@pytest.mark.parametrize("encoder", odc_modules)
@pytest.mark.parametrize("decoder", odc_modules)
def test_unambiguous_short_name(encoder, decoder):
    "Check that we DON'T get an error if you request foo when both foo and foo@baz are present as columns"
    df, df2, full_names = _helper(encoder, decoder, original_columns=["foo", "foo@desc"], requested_columns=["foo"])
    assert "foo" in df2
    assert "foo" in full_names


@pytest.mark.parametrize("encoder", odc_modules)
@pytest.mark.parametrize("decoder", odc_modules)
def test_literal_dot_in_name(encoder, decoder):
    "Check you can use request a column with a literal dot in it"
    df, df2, full_names = _helper(encoder, decoder, original_columns=["foo.bar@bar"], requested_columns=["foo.bar@bar"])
    assert "foo.bar@bar" in df2


@pytest.mark.parametrize("encoder", odc_modules)
@pytest.mark.parametrize("decoder", odc_modules)
def test_literal_dot_in_shortname(encoder, decoder):
    "Check you can use a shortname with a literal dot in it"
    df, df2, full_names = _helper(encoder, decoder, original_columns=["foo.bar@bar"], requested_columns=["foo.bar"])
    assert "foo.bar" in df2
    assert "foo.bar@bar" in full_names


@pytest.mark.parametrize("encoder", odc_modules)
@pytest.mark.parametrize("decoder", odc_modules)
def test_precedence(encoder, decoder):
    df, df2, full_names = _helper(
        encoder, decoder, original_columns=["foo.bitfield@bar", "foo@bar"], requested_columns=["foo.bitfield@bar"]
    )
    assert "foo.bitfield@bar" in df2
    assert "foo.bitfield@bar" in full_names
