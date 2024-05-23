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

    # Constant columns of strings of more than 8 bytes currently get promoted to 
    #  codec.Int8String but working on a version of ConstantString that supports longer strings.
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
    # [np.float32([999.99, 888.88, 777.77, 666.66, 555.55, 444.44, 333.33]), codec.ShortReal2],
    # [np.float32([INTERNAL_REAL_MISSING[1], 888.88, 777.77, 666.66, 555.55, 444.44, 333.33]), codec.ShortReal],
    
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