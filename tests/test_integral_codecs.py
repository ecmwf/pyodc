import io

import pandas as pd
import pytest

from pyodc import codec
from pyodc.codec import select_codec
from pyodc.stream import LittleEndianStream


def _check_encode(codec, series, encode_compare):
    f = io.BytesIO()
    st = LittleEndianStream(f)

    for v in series:
        codec.encode(st, v)

    f.seek(0)
    assert f.read() == encode_compare


def test_int8_range_encoding():
    # Also test with negative numbers!

    for offset in (0, -100):
        s = pd.Series((1 + offset, 2**8 + offset))
        c = select_codec("column", s, None)

        assert type(c) == codec.Int8
        assert c.min == 1 + offset

    _check_encode(c, s, b"\x00\xff")


def test_int16_range_encoding_minimal():
    """
    A span of integers that _just_ requires int16
    """

    # Also test with negative numbers!

    for offset in (0, -10000):
        s = pd.Series((1 + offset, 2**8 + offset + 1))
        c = select_codec("column", s, None)

        assert type(c) == codec.Int16
        assert c.min == 1 + offset

        _check_encode(c, s, b"\x00\x00\x00\x01")


def test_int16_range_encoding_maximal():
    # Also test with negative numbers!

    for offset in (0, -10000):
        s = pd.Series((1 + offset, 2**8 + offset, 2**16 + offset))
        c = select_codec("column", s, None)

        assert type(c) == codec.Int16
        assert c.min == 1 + offset

        _check_encode(c, s, b"\x00\x00\xff\x00\xff\xff")


def test_int32_range_encoding():
    """
    n.b. the Int32 codec is a bit crappy. It does _not_ include an offset value
    --> It only encodes the legit values of a SIGNED 32bit integer
    --> 64bit integers are todo (but break some fortran compatibility, as not all
        64bit integers can be represented as doubles).
    --> Can include missing values
    """
    s = pd.Series((-(2**31), None, 2**31 - 2))
    c = select_codec("column", s, None)

    assert isinstance(c, codec.Int32)
    assert c.min == -(2**31)

    _check_encode(c, s, b"\x00\x00\x00\x80\xff\xff\xff\x7f\xfe\xff\xff\x7f")


def test_wider_range_unsupported():
    s = pd.Series((-(2**31), 2**31 - 1))
    with pytest.raises(NotImplementedError):
        select_codec("column", s, None)


def test_int8_missing_range_encoding():
    # Also test with negative numbers!

    for offset in (0, -100):
        s = pd.Series((1 + offset, None, 2**8 + offset - 1))
        c = select_codec("column", s, None)

        assert type(c) == codec.Int8Missing
        assert c.min == 1 + offset

    _check_encode(c, s, b"\x00\xff\xfe")


def test_int16_missing_range_encoding_minimal():
    # Also test with negative numbers!

    for offset in (0, -100):
        s = pd.Series((1 + offset, None, 2**8 + offset))
        c = select_codec("column", s, None)

        assert type(c) == codec.Int16Missing
        assert c.min == 1 + offset

    _check_encode(c, s, b"\x00\x00\xff\xff\xff\x00")


def test_int16_missing_range_encoding_maximal():
    # Also test with negative numbers!

    for offset in (0, -100):
        s = pd.Series((1 + offset, None, 2**16 + offset - 1))
        c = select_codec("column", s, None)

        assert type(c) == codec.Int16Missing
        assert c.min == 1 + offset

    _check_encode(c, s, b"\x00\x00\xff\xff\xfe\xff")
