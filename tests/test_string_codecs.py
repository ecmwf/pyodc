import pytest

from pyodc.constants import DataType
from pyodc.stream import LittleEndianStream
from pyodc import codec
import struct
import os

from conftest import odc_modules


def _check_decode(cdc, encoded, check):

    st = LittleEndianStream(encoded)
    v = cdc.decode(st)
    assert v == check


def test_null_terminated_constant_string():
    """
    This tests the (somewhat dubious) 'missing' values in some (older) data
    encoded from ODB-1 using the migrator. This data uses the integer missing value,
    casted to a double, that happens to start with \x00 --> "NULL STRING"

    We need to support decoding this data...
    """
    constant_value = struct.unpack("<d", b"\x00\x00\xc0\xff\xff\xff\xdfA")[0]
    cdc = codec.ConstantString("column", constant_value, constant_value, DataType.STRING, has_missing=False)
    encoded = b""

    _check_decode(cdc, encoded, "")


def test_stripped_constant_string():
    constant_value = struct.unpack("<d", b"hello\x00\x00\x00")[0]
    cdc = codec.ConstantString("column", constant_value, constant_value, DataType.STRING, has_missing=False)
    encoded = b""

    _check_decode(cdc, encoded, "hello")


def test_normal_constant_string():
    constant_value = struct.unpack("<d", b"helloAAA")[0]
    cdc = codec.ConstantString("column", constant_value, constant_value, DataType.STRING, has_missing=False)
    encoded = b""

    _check_decode(cdc, encoded, "helloAAA")


@pytest.mark.parametrize("odyssey", odc_modules)
def test_decode_odb1_missing_strings(odyssey):
    """
    Tests that we can decode missing (NULL) strings from data encoded
    from ODB-1 using the migrator. This data uses the integer missing value,
    casted to a double, that happens to start with \x00.

    The test sample contains valid data pre-encoded (which cannot be encoded
    through the python API, as we (correctly) encode the missing value as a
    null string).
    """
    with open(os.path.join(os.path.dirname(__file__), "data/odb1_missing_string.odb"), "rb") as f:
        df = odyssey.read_odb(f, single=True)

    assert df.shape == (4, 1)
    series = df["col1"]
    assert series.dtype == "object"

    for v in series:
        assert isinstance(v, str)
        assert v == ""
