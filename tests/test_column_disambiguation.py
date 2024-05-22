import pandas as pd
from conftest import odc_modules
import pytest
from tempfile import NamedTemporaryFile

# Quick sanity check from Tom Hodson, that things don't randomly fall apart. Doesn't check correctness of the data.

def _helper(encoder, decoder, original_columns, requested_columns):
    with NamedTemporaryFile() as file:
        df = pd.DataFrame({c : [1,2,3] for c in original_columns})
        encoder.encode_odb(df, file.name)
        df2 = decoder.read_odb(file.name, single = True, columns = requested_columns)
        return df, df2


@pytest.mark.parametrize("encoder", odc_modules)
@pytest.mark.parametrize("decoder", odc_modules)
def test_basic(encoder, decoder):
    "Check the most basic column selection works"
    _helper(encoder, decoder,
                original_columns = ["foo@bar"],
                requested_columns = ["foo@bar"])


@pytest.mark.parametrize("encoder", odc_modules)
@pytest.mark.parametrize("decoder", odc_modules)
def test_shortform(encoder, decoder):
    "Check that you can retrieve a column by short name"
    _helper(encoder, decoder,
                original_columns = ["foo@bar", "bar@des"],
                requested_columns = ["foo"])

@pytest.mark.parametrize("encoder", odc_modules)
@pytest.mark.parametrize("decoder", odc_modules)
def test_ambiguous_short_name(encoder, decoder):
    "Check that we get an error if you request foo when both foo@bar and foo@baz are present as columns"
    with pytest.raises(KeyError):
        _helper(encoder, decoder,
            original_columns = ["foo@bar", "foo@desc"],
            requested_columns = ["foo"])

@pytest.mark.parametrize("encoder", odc_modules)
@pytest.mark.parametrize("decoder", odc_modules)
def test_ambiguous_short_name(encoder, decoder):
    "Check that we DON'T get an error if you request foo when both foo and foo@baz are present as columns"
    _helper(encoder, decoder,
        original_columns = ["foo", "foo@desc"],
        requested_columns = ["foo"])

@pytest.mark.parametrize("encoder", odc_modules)
@pytest.mark.parametrize("decoder", odc_modules)
def test_literal_dot_in_name(encoder, decoder):
    _helper(encoder, decoder,
        original_columns = ["foo.bar@bar"],
        requested_columns = ["foo.bar@bar"])

@pytest.mark.parametrize("encoder", odc_modules)
@pytest.mark.parametrize("decoder", odc_modules)
def test_precedence(encoder, decoder):
    _helper(encoder, decoder,
        original_columns = ["foo.bitfield@bar", "foo@bar"],
        requested_columns = ["foo.bitfield@bar"])