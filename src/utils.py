import struct
from collections import namedtuple

FMT_CHARS = [
    'c', # char
    'b', # signed char
    'B', # unsigned char
    'h', # short
    'H', # unsigned short
    'i', # int
    'I', # unsigned int
    'l', # long
    'L', # unsigned long
    'q', # long long
    'Q', # unsigned long long
    'f', # float
    'd'  # double
]

def read_fmt(file, fmt_str: str, namedtuple = False, fmt_byte_order: str = '<'):
    fmt = fmt_byte_order + fmt_str
    size = struct.calcsize(fmt)
    data_raw = file.read(size)
    data_unpacked = struct.unpack(fmt, data_raw)

    if namedtuple:
        try:
            return namedtuple._make(data_unpacked)
        except Exception as e:
            print(type(e).__name__ + ' - unpacked data will not be returned as namedtuple')

    if fmt_str in FMT_CHARS:
        return data_unpacked[0]

    return data_unpacked


def read_char(file):
    return read_fmt(file, 'c')

def read_schar(file):
    return read_fmt(file, 'b')

def read_uchar(file):
    return read_fmt(file, 'B')

def read_short(file):
    return read_fmt(file, 'h')

def read_ushort(file):
    return read_fmt(file, 'H')

def read_int(file):
    return read_fmt(file, 'i')

def read_uint(file):
    return read_fmt(file, 'I')

def read_long(file):
    return read_fmt(file, 'l')

def read_ulong(file):
    return read_fmt(file, 'L')

def read_longlong(file):
    return read_fmt(file, 'q')

def read_ulonglong(file):
    return read_fmt(file, 'Q')

def read_float(file):
    return read_fmt(file, 'f')

def read_double(file):
    return read_fmt(file, 'd')

def read_nullstr(file):
    string = b''
    character = None
    while(character != b'\x00'):
        character = file.read(1)
        string += character
    return string.rstrip(b'\x00').decode('ascii')