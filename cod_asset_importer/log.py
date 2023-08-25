import inspect
import os

from . import enum

"""
Logging label constants
"""
class LOG_CONSTANTS(metaclass = enum.BaseEnum):
    ERROR = '[ERROR]'
    DEBUG = '[DEBUG]'
    INFO = '[INFO]'

"""
Write a log message as a certain type
"""
def _log(message: str, log_type: str = LOG_CONSTANTS.INFO) -> None:
    caller = inspect.getframeinfo(inspect.stack()[2][0])
    file_base_name = os.path.basename(caller.filename)
    msg = f' {file_base_name}:{caller.lineno} ' + message.removesuffix('\n') 
    if log_type == LOG_CONSTANTS.ERROR:
        msg = LOG_CONSTANTS.ERROR + msg

    elif log_type == LOG_CONSTANTS.DEBUG:
        msg = LOG_CONSTANTS.DEBUG + msg
        
    elif log_type == LOG_CONSTANTS.INFO:
        msg = LOG_CONSTANTS.INFO + msg

    print(msg)

"""
Write an error log message
"""
def error_log(message) -> None:
    _log(str(message), LOG_CONSTANTS.ERROR)

"""
Write a debug log message
"""
def debug_log(message) -> None:
    _log(str(message), LOG_CONSTANTS.DEBUG)


"""
Write an info log message
"""
def info_log(message) -> None:
    _log(str(message), LOG_CONSTANTS.INFO)