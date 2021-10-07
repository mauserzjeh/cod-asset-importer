from __future__ import annotations

import io
import struct

from . import (
    log,
    enum
)

class DECODE_FORMAT(metaclass = enum.BaseEnum):
    DXT1 = 0
    DXT3 = 1
    DXT5 = 2

def decode(input: bytes, width: int, height: int, format: int) -> bytearray | bytes:
    if format == DECODE_FORMAT.DXT1:
        return _decodeDXT1(input, width, height)
    elif format == DECODE_FORMAT.DXT3:
        return _decodeDXT3(input, width, height)
    elif format == DECODE_FORMAT.DXT5:
        return _decodeDXT5(input, width, height)
    else:
        log.error_log(f"Unsupported decode format: {format}")
        return input

def _unpack_565(color: int) -> tuple:
    r = (color & 0xF800) >> 8
    g = (color & 0x07E0) >> 3
    b = (color & 0x001F) << 3
    r |= r >> 5
    g |= g >> 6
    b |= b >> 5
    return r, g, b

def _pack_rgba(r: int, g: int, b: int, a: int) -> int:
    return (r << 16) | (g << 8) | b | (a << 24)

def _unpack_rgba(c: int) -> tuple:    
    b = c & 0xFF
    g = (c >> 8) & 0xFF
    r = (c >> 16) & 0xFF
    a = (c >> 24) & 0xFF
    
    return r,g,b,a

def _c2a(c0: int, c1: int) -> int:
    return (2 * c0 + c1) // 3

def _c2b(c0: int, c1: int) -> int:
    return (c0 + c1) // 2

def _c3(c0: int, c1: int) -> int:
    return (c0 + 2 * c1) // 3

def _decodeDXT1(input: bytes, width: int, height: int) -> bytes:
    input = io.BytesIO(input)
    output = bytearray(width * height * 4)
    buffer = bytearray(64)
    
    block_count_x = (width + 3) // 4
    block_count_y = (height + 3) // 4
    length_last = (width + 3) % 4 + 1
    colors = [0,0,0,0]

    for y in range(block_count_y):
        for x in range(block_count_x):
            q0, q1, bitcode = struct.unpack('<HHI', input.read(8))
                      
            r0, g0, b0 = _unpack_565(q0)
            r1, g1, b1 = _unpack_565(q1)
                        
            colors[0] = _pack_rgba(r0, g0, b0, 255)
            colors[1] = _pack_rgba(r1, g1, b1, 255)

            if q0 > q1:
                colors[2] = _pack_rgba(_c2a(r0, r1), _c2a(g0, g1), _c2a(b0, b1), 255)
                colors[3] = _pack_rgba(_c3(r0, r1), _c3(g0, g1), _c3(b0, b1), 255)
            else:
                colors[2] = _pack_rgba(_c2b(r0, r1), _c2b(g0, g1), _c2b(b0, b1), 255)
                colors[3] = _pack_rgba(0,0,0,255)
            
            for i in range(16):
                idx = i * 4
                r,g,b,a = _unpack_rgba(colors[bitcode & 0x03])                
                buffer[idx:idx+4] = struct.pack('4B', r, g, b, a)
                bitcode >>= 2
                        
            length = (4 if x < block_count_x - 1 else length_last) * 4
            i = 0
            j = y * 4            
            while i < 4 and j < height:
                bidx = (i * 4 * 4)
                oidx = (j * width + x * 4) * 4
                
                output[oidx:oidx+length] = buffer[bidx:bidx+length]

                i += 1
                j += 1

    return bytes(output)

def _decodeDXT3(input: bytes, width: int, height: int) -> bytearray:
    pass

def _decodeDXT5(input: bytes, width: int, height: int) -> bytearray:
    pass

            


    