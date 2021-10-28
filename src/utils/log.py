import inspect
import os

from . import enum

class LOG_CONSTANTS(metaclass = enum.BaseEnum):
    ERROR = '[ERROR]'
    DEBUG = '[DEBUG]'
    INFO = '[INFO]'

def _log(message: str, log_type: str = LOG_CONSTANTS.INFO) -> None:
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

def error_log(message) -> None:
    _log(str(message), LOG_CONSTANTS.ERROR)

def debug_log(message) -> None:
    _log(str(message), LOG_CONSTANTS.DEBUG)

def info_log(message) -> None:
    _log(str(message), LOG_CONSTANTS.INFO)