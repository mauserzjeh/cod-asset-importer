import collections
import struct

from . import (
    log,
    enum,
)

class FMT_CHARACTER_CONSTANTS(metaclass = enum.BaseEnum):
    CHAR =                  'c' # char
    SIGNED_CHAR =           'b' # signed char
    UNSIGNED_CHAR =         'B' # unsigned char
    SHORT =                 'h' # short
    UNSIGNED_SHORT =        'H' # unsigned short
    INTEGER =               'i' # int
    UNSIGNED_INTEGER =      'I' # unsigned int
    LONG =                  'l' # long
    UNSIGNED_LONG =         'L' # unsigned long
    LONG_LONG =             'q' # unsigned long
    UNSIGNED_LONG_LONG =    'Q' # unsigned long long
    FLOAT =                 'f' # float
    DOUBLE =                'd' # double

def read_fmt(file, fmt_str: str, namedtuple: collections.namedtuple = False, fmt_byte_order: str = '<'):
    fmt = fmt_byte_order + fmt_str
    size = struct.calcsize(fmt)
    data_raw = file.read(size)
    data_unpacked = struct.unpack(fmt, data_raw)

    if namedtuple:
        try:
            return namedtuple._make(data_unpacked)
        except Exception as e:
            log.error_log(e)

    if fmt_str in FMT_CHARACTER_CONSTANTS:
        return data_unpacked[0]

    return data_unpacked


def read_char(file):
    return read_fmt(file, FMT_CHARACTER_CONSTANTS.CHAR)

def read_schar(file):
    return read_fmt(file, FMT_CHARACTER_CONSTANTS.SIGNED_CHAR)

def read_uchar(file):
    return read_fmt(file, FMT_CHARACTER_CONSTANTS.UNSIGNED_CHAR)

def read_short(file):
    return read_fmt(file, FMT_CHARACTER_CONSTANTS.SHORT)

def read_ushort(file):
    return read_fmt(file, FMT_CHARACTER_CONSTANTS.UNSIGNED_SHORT)

def read_int(file):
    return read_fmt(file, FMT_CHARACTER_CONSTANTS.INTEGER)

def read_uint(file):
    return read_fmt(file, FMT_CHARACTER_CONSTANTS.UNSIGNED_INTEGER)

def read_long(file):
    return read_fmt(file, FMT_CHARACTER_CONSTANTS.LONG)

def read_ulong(file):
    return read_fmt(file, FMT_CHARACTER_CONSTANTS.UNSIGNED_LONG)

def read_longlong(file):
    return read_fmt(file, FMT_CHARACTER_CONSTANTS.LONG_LONG)

def read_ulonglong(file):
    return read_fmt(file, FMT_CHARACTER_CONSTANTS.UNSIGNED_LONG_LONG)

def read_float(file):
    return read_fmt(file, FMT_CHARACTER_CONSTANTS.FLOAT)

def read_double(file):
    return read_fmt(file, FMT_CHARACTER_CONSTANTS.DOUBLE)

def read_nullstr(file) -> str:
    string = b''
    character = None
    while(character != b'\x00'):
        character = file.read(1)
        string += character
    return string.rstrip(b'\x00').decode('ascii')