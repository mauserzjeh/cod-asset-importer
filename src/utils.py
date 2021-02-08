import struct

from collections import namedtuple

class BaseEnum(type):
    def __iter__(self):
        _attr_values = []
        _vars = vars(self)
        for _name, _value in _vars.items():
            if not callable(getattr(self, _name)) and not _name.startswith('__') and not _name.endswith('__'):
                _attr_values.append(_value)
        return iter(_attr_values)
            

class FMT_CHARS(metaclass = BaseEnum):
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
    return read_fmt(file, FMT_CHARS.CHAR)

def read_schar(file):
    return read_fmt(file, FMT_CHARS.SIGNED_CHAR)

def read_uchar(file):
    return read_fmt(file, FMT_CHARS.UNSIGNED_CHAR)

def read_short(file):
    return read_fmt(file, FMT_CHARS.SHORT)

def read_ushort(file):
    return read_fmt(file, FMT_CHARS.UNSIGNED_SHORT)

def read_int(file):
    return read_fmt(file, FMT_CHARS.INTEGER)

def read_uint(file):
    return read_fmt(file, FMT_CHARS.UNSIGNED_INTEGER)

def read_long(file):
    return read_fmt(file, FMT_CHARS.LONG)

def read_ulong(file):
    return read_fmt(file, FMT_CHARS.UNSIGNED_LONG)

def read_longlong(file):
    return read_fmt(file, FMT_CHARS.LONG_LONG)

def read_ulonglong(file):
    return read_fmt(file, FMT_CHARS.UNSIGNED_LONG_LONG)

def read_float(file):
    return read_fmt(file, FMT_CHARS.FLOAT)

def read_double(file):
    return read_fmt(file, FMT_CHARS.DOUBLE)

def read_nullstr(file):
    string = b''
    character = None
    while(character != b'\x00'):
        character = file.read(1)
        string += character
    return string.rstrip(b'\x00').decode('ascii')