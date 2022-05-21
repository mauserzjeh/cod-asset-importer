from __future__ import annotations

import collections
import struct
import traceback

from . import (
    enum,
    log,
)

"""
Format character constants for file IO
"""
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
    LONG_LONG =             'q' # long long
    UNSIGNED_LONG_LONG =    'Q' # unsigned long long
    FLOAT =                 'f' # float
    DOUBLE =                'd' # double

"""
Read bytes as a specific format described by fmt_str. Optionally return the result as a namedtuple
"""
def read_fmt(file: bytes, fmt_str: str, namedtuple: collections.namedtuple = None, fmt_byte_order: str = '<') -> tuple | collections.namedtuple | int | float:
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

"""
Read a character
"""
def read_char(file: bytes) -> int:
    return read_fmt(file, FMT_CHARACTER_CONSTANTS.CHAR)

"""
Read a signed character
"""
def read_schar(file: bytes) -> int:
    return read_fmt(file, FMT_CHARACTER_CONSTANTS.SIGNED_CHAR)

"""
Read an unsigned character
"""
def read_uchar(file: bytes) -> int:
    return read_fmt(file, FMT_CHARACTER_CONSTANTS.UNSIGNED_CHAR)

"""
Read a short
"""
def read_short(file: bytes) -> int:
    return read_fmt(file, FMT_CHARACTER_CONSTANTS.SHORT)

"""
Read an unsigned short
"""
def read_ushort(file: bytes) -> int:
    return read_fmt(file, FMT_CHARACTER_CONSTANTS.UNSIGNED_SHORT)

"""
Read an integer 
"""
def read_int(file: bytes) -> int:
    return read_fmt(file, FMT_CHARACTER_CONSTANTS.INTEGER)

"""
Read an unsigned integer 
"""
def read_uint(file: bytes) -> int:
    return read_fmt(file, FMT_CHARACTER_CONSTANTS.UNSIGNED_INTEGER)

"""
Read a long
"""
def read_long(file: bytes) -> int:
    return read_fmt(file, FMT_CHARACTER_CONSTANTS.LONG)

"""
Read an unsigned long 
"""
def read_ulong(file: bytes) -> int:
    return read_fmt(file, FMT_CHARACTER_CONSTANTS.UNSIGNED_LONG)

"""
Read a long long 
"""
def read_longlong(file: bytes) -> int:
    return read_fmt(file, FMT_CHARACTER_CONSTANTS.LONG_LONG)

"""
Read an unsigned long long
"""
def read_ulonglong(file: bytes) -> int:
    return read_fmt(file, FMT_CHARACTER_CONSTANTS.UNSIGNED_LONG_LONG)

"""
Read a float 
"""
def read_float(file: bytes) -> float:
    return read_fmt(file, FMT_CHARACTER_CONSTANTS.FLOAT)

"""
Read a double 
"""
def read_double(file: bytes) -> float:
    return read_fmt(file, FMT_CHARACTER_CONSTANTS.DOUBLE)

"""
Read a null terminated string 
"""
def read_nullstr(file: bytes) -> str:
    string = b''
    character = None
    while(character != b'\x00'):
        character = file.read(1)
        string += character
    return string.rstrip(b'\x00').decode('utf-8')