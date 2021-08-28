import inspect
import math
import os
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
            
# -------------------- File reading utilities --------------------

class FMT_CHARACTER_CONSTANTS(metaclass = BaseEnum):
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

def read_fmt(file, fmt_str: str, namedtuple: namedtuple = False, fmt_byte_order: str = '<'):
    fmt = fmt_byte_order + fmt_str
    size = struct.calcsize(fmt)
    data_raw = file.read(size)
    data_unpacked = struct.unpack(fmt, data_raw)

    if namedtuple:
        try:
            return namedtuple._make(data_unpacked)
        except Exception as e:
            error_log(e)

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

def read_nullstr(file):
    string = b''
    character = None
    while(character != b'\x00'):
        character = file.read(1)
        string += character
    return string.rstrip(b'\x00').decode('ascii')

# -------------------- Logging utilities --------------------

class LOG_CONSTANTS(metaclass = BaseEnum):
    ERROR = '[ERROR]'
    DEBUG = '[DEBUG]'
    INFO = '[INFO]'

def _log(message: str, log_type: str = LOG_CONSTANTS.INFO):
    caller = inspect.getframeinfo(inspect.stack()[2][0])
    file_base_name = os.path.basename(caller.filename)
    msg = f' {file_base_name}:{caller.lineno} ' + message 
    if log_type == LOG_CONSTANTS.ERROR:
        msg = LOG_CONSTANTS.ERROR + msg

    elif log_type == LOG_CONSTANTS.DEBUG:
        msg = LOG_CONSTANTS.DEBUG + msg
        
    elif log_type == LOG_CONSTANTS.INFO:
        msg = LOG_CONSTANTS.INFO + msg

    print(msg)

def error_log(message):
    _log(str(message), LOG_CONSTANTS.ERROR)

def debug_log(message):
    _log(str(message), LOG_CONSTANTS.DEBUG)

def info_log(message):
    _log(str(message), LOG_CONSTANTS.INFO)


# -------------------- Math --------------------
def transform_vector(quaternion: tuple, vector3: tuple):
    if len(quaternion) != 4 or len(vector3) != 3:
        return None

    qx = quaternion[0]
    qy = quaternion[1]
    qz = quaternion[2]
    qw = quaternion[3]

    vx = vector3[0]
    vy = vector3[1]
    vz = vector3[2]

    ax = (qy * vz) - (qz * vy) + (vx * qw)
    ay = (qz * vx) - (qx * vz) + (vy * qw)
    az = (qx * vy) - (qy * vx) + (vz * qw)

    bx = (qy * az) - (qz * ay)
    by = (qz * ax) - (qx * az)
    bz = (qx * ay) - (qy * ax)

    rx = (vx + bx + bx)
    ry = (vy + by + by)
    rz = (vz + bz + bz)

    return (rx, ry, rz)

def multiply_quaternion(a: tuple, b: tuple):
    if len(a) != 4 or len(b) != 4:
        return None

    ax = a[0]
    ay = a[1]
    az = a[2]
    aw = a[3]
    
    bx = b[0]
    by = b[1]
    bz = b[2]
    bw = b[3]

    x = aw * bx + ax * bw + ay * bz - az * by
    y = aw * by - ax * bz + ay * bw + az * bx
    z = aw * bz + ax * by - ay * bx + az * bw 
    w = aw * bw - ax * bx - ay * by - az * bz

    return (x, y, z, w)




