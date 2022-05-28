from __future__ import annotations
import traceback

from . import (
    file_io,
    log
)

"""
Read the version of an xmodel file and return it
"""
def PeekXmodelVersion(file: bytes) -> int:
    try:
        with open(file, 'rb') as f:
            version = file_io.read_ushort(f)
            return version
    except:
        log.error_log(traceback.print_exc())
        return -1

"""
Read the version of a map file and return
"""
def PeekMapVersion(file: bytes) -> int:
    try:
        with open(file, 'rb') as f:
            version = file_io.read_fmt(f, '4xi')
            return version
    except:
        log.error_log(traceback.print_exc())
        return -1

