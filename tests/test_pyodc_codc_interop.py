from tempfile import NamedTemporaryFile

import numpy.testing
import pandas
import pytest
from conftest import ODC_VERSION, codc, odc_modules

import pyodc
from pyodc import codec, Reader
from pyodc.constants import INTERNAL_REAL_MISSING

import pandas as pd
import numpy as np
import os

# Each case is a single column and the expected codec 
testcases = [
    # Anything constant that fits in less than 8 bytes goes into codec.Constant
    [[0, 0, 0, 0, 0, 0, 0], codec.Constant],
    [[73] * 7, codec.Constant],
    [[1.432] * 7, codec.Constant],

    # Like the above but with missing values
    [[1, 1, 1, None, 1, 1, 1], codec.ConstantOrMissing],
    [[.1, .1, .1, None, .1, .1, .1], codec.RealConstantOrMissing],
    
    # Constant columns of strings of less than 8 bytes go into ConstantString
    [["abcd"] * 7, codec.ConstantString],

    # Constant columns of strings of more than 8 bytes must be handled differently
    [["abcdefghi"] * 7, codec.Int8String],

    # Columns of strings with less than 2^n unique values go into Int8String or Int16String
    [["aoeu", "aoeu", "aaaaaaaooooooo", "None", "boo", "squiggle", "a"], codec.Int8String],
    [["longconstant"] + [str(num) for num in range(256)], codec.Int16String],

    # Integers
    [[1, 2, 3, 4, 5, 6, 7], codec.Int8],
    [[1, None, 3, 4, 5, None, 7], codec.Int8Missing],
    [[-512, None, 3, 7623, -22000, None, 7], codec.Int16Missing],

    # Breaking the pattern, codec.Int32 accepts missing values.
    [[-1234567, 8765432, None, 22, 22222222, -81222323, None], codec.Int32],

    # Reals
    [[999.99, 888.88, 777.77, 666.66, 555.55, 444.44, 333.33], codec.LongReal],

    # ShortReal2 is the default codec for float32 which uses INTERNAL_REAL_MISSING[1] to represent missing data
    [np.array([999.99, 888.88, 777.77, 666.66, 555.55, 444.44, 333.33], dtype = np.float32), codec.ShortReal2], 

    # When INTERNAL_REAL_MISSING[1] is present, the codec switches to ShortReal which uses a different value to represent missing data
    [np.array([INTERNAL_REAL_MISSING[1], 888.88, 777.77, 666.66, 555.55, 444.44, 333.33], dtype = np.float32), codec.ShortReal],
    
]

def first_codec(file):
    return Reader(file).frames[0]._column_codecs[0]


@pytest.mark.parametrize("encoder", odc_modules)
@pytest.mark.parametrize("decoder", odc_modules)
@pytest.mark.parametrize("testcase", testcases)
def test_codec_choice(testcase, encoder, decoder):
    "Check that codc and pyodc choose the same codec for all the test data"
    testdata, expected_codec = testcase
    df = pd.DataFrame(dict(column = testdata))

    with NamedTemporaryFile() as fencode:
        encoder.encode_odb(df, fencode.name)
        round_tripped_data = decoder.read_odb(fencode.name, single = True)
        codec = first_codec(fencode.name)

    assert type(codec) == expected_codec

    # Check the data round tripped
    numpy.testing.assert_array_equal(df.column.values, round_tripped_data.column.values)

@pytest.mark.parametrize("encoder", odc_modules)
@pytest.mark.parametrize("decoder", odc_modules)
def test_codec_choice_long_string(encoder, decoder):
    "Check that codc and pyodc choose the same codec for long constant strings in the presence of ODC_ENABLE_WRITING_LONG_STRING_CODEC"
    testdata, expected_codec = [["abcdefghi"] * 7, codec.LongConstantString]
    df = pd.DataFrame(dict(column = testdata))

    os.environ["ODC_ENABLE_WRITING_LONG_STRING_CODEC"] = "true"

    with NamedTemporaryFile() as fencode:
        encoder.encode_odb(df, fencode.name)
        round_tripped_data = decoder.read_odb(fencode.name, single = True)
        chosen_codec = first_codec(fencode.name)

    del os.environ["ODC_ENABLE_WRITING_LONG_STRING_CODEC"]

    assert type(chosen_codec) == expected_codec

    # Check the data round tripped
    numpy.testing.assert_array_equal(df.column.values, round_tripped_data.column.values)