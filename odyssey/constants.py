from enum import IntEnum, unique
import struct

# Current version information

FORMAT_VERSION_NUMBER_MAJOR = 0
FORMAT_VERSION_NUMBER_MINOR = 5

# Default missing values

MISSING_INTEGER = 2147483647
MISSING_REAL = -2147483647
MISSING_STRING = struct.unpack('<d', b'\x00\x00\x00\x00\x00\x00\x00\x00')[0]

INTERNAL_REAL_MISSING = (
    struct.unpack("<f", b"\x00\x00\x80\x00")[0],
    struct.unpack("<f", b"\xff\xff\x7f\x7f")[0]
)

# Constants for header encoding

NEW_HEADER = 65535
MAGIC = b"ODA"
ENDIAN_MARKER = 1

# Types

@unique
class DataType(IntEnum):

    IGNORE = 0
    INTEGER = 1
    REAL = 2
    STRING = 3
    BITFIELD = 4
    DOUBLE = 5

IGNORE = DataType.IGNORE
INTEGER = DataType.INTEGER
REAL = DataType.REAL
STRING = DataType.STRING
BITFIELD = DataType.BITFIELD
DOUBLE = DataType.DOUBLE

TYPE_NAMES = {
    IGNORE: 'ignore',
    INTEGER: 'integer',
    REAL: 'real',
    STRING: 'string',
    BITFIELD: 'bitfield',
    DOUBLE: 'double'
}
