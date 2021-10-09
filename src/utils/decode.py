from __future__ import annotations

import io
import struct

from . import (
    log,
    enum
)

class DECODE_FORMAT(metaclass = enum.BaseEnum):
    DXT1 = 0x0B
    DXT3 = 0x0C
    DXT5 = 0x0D

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
    colors = [0] * 4

    for y in range(block_count_y):
        for x in range(block_count_x):
            c0, c1, bitcode = struct.unpack('<HHI', input.read(8))
                      
            r0, g0, b0 = _unpack_565(c0)
            r1, g1, b1 = _unpack_565(c1)
                        
            colors[0] = _pack_rgba(r0, g0, b0, 255)
            colors[1] = _pack_rgba(r1, g1, b1, 255)

            if c0 > c1:
                colors[2] = _pack_rgba(_c2a(r0, r1), _c2a(g0, g1), _c2a(b0, b1), 255)
                colors[3] = _pack_rgba(_c3(r0, r1), _c3(g0, g1), _c3(b0, b1), 255)
            else:
                colors[2] = _pack_rgba(_c2b(r0, r1), _c2b(g0, g1), _c2b(b0, b1), 255)
            
            for i in range(16):
                idx = i * 4
                r, g, b, a = _unpack_rgba(colors[bitcode & 0x03])                
                buffer[idx:idx+4] = struct.pack('<4B', r, g, b, a)
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

def _decodeDXT3(input: bytes, width: int, height: int) -> bytes:
    input = io.BytesIO(input)
    output = bytearray(width * height * 4)
    buffer = bytearray(64)

    block_count_x = (width + 3) // 4
    block_count_y = (height + 3) // 4
    length_last = (width + 3) % 4 + 1
    colors = [0] * 4
    alphas = [0] * 16

    for y in range(block_count_y):
        for x in range(block_count_x):
            for i in range(4):
                alpha = struct.unpack('<H', input.read(2))[0]
                alphas[i * 4 + 0] = (((alpha >> 0) & 0x0F) * 0x11) << 24
                alphas[i * 4 + 1] = (((alpha >> 4) & 0x0F) * 0x11) << 24
                alphas[i * 4 + 2] = (((alpha >> 8) & 0x0F) * 0x11) << 24
                alphas[i * 4 + 3] = (((alpha >> 12) & 0x0F) * 0x11) << 24

            c0, c1, bitcode = struct.unpack('<HHI', input.read(8))

            r0, g0, b0 = _unpack_565(c0)
            r1, g1, b1 = _unpack_565(c1)

            colors[0] = _pack_rgba(r0, g0, b0, 0)
            colors[1] = _pack_rgba(r1, g1, b1, 0)

            if c0 > c1:
                colors[2] = _pack_rgba(_c2a(r0, r1), _c2a(g0, g1), _c2a(b0, b1), 0)
                colors[3] = _pack_rgba(_c3(r0, r1), _c3(g0, g1), _c3(b0, b1), 0)
            else:
                colors[2] = _pack_rgba(_c2b(r0, r1), _c2b(g0, g1), _c2b(b0, b1), 0)

            for i in range(16):
                idx = i * 4
                r, g, b, a = _unpack_rgba(colors[bitcode & 0x03] | alphas[i])
                buffer[idx:idx+4] = struct.pack('<4B', r, g, b, a)
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

def _decodeDXT5(input: bytes, width: int, height: int) -> bytes:
    input = io.BytesIO(input)
    output = bytearray(width * height * 4)
    buffer = bytearray(64)

    block_count_x = (width + 3) // 4
    block_count_y = (height + 3) // 4
    length_last = (width + 3) % 4 + 1
    colors = [0] * 4
    alphas = [0] * 8

    for y in range(block_count_y):
        for x in range(block_count_x):
            a0, a1, ac0, ac1, c0, c1, bitcode_c = struct.unpack('<BBHIHHI', input.read(16))
            bitcode_a = struct.unpack('<Q', struct.pack('<BBHI', a0, a1, ac0, ac1))[0] >> 16

            alphas[0] = a0
            alphas[1] = a1

            if alphas[0] > alphas[1]:
                alphas[2] = (alphas[0] * 6 + alphas[1]    ) // 7
                alphas[3] = (alphas[0] * 5 + alphas[1] * 2) // 7
                alphas[4] = (alphas[0] * 4 + alphas[1] * 3) // 7
                alphas[5] = (alphas[0] * 3 + alphas[1] * 4) // 7
                alphas[6] = (alphas[0] * 2 + alphas[1] * 5) // 7
                alphas[7] = (alphas[0]     + alphas[1] * 6) // 7
            else:
                alphas[2] = (alphas[0] * 4 + alphas[1]    ) // 5
                alphas[3] = (alphas[0] * 3 + alphas[1] * 2) // 5
                alphas[4] = (alphas[0] * 2 + alphas[1] * 3) // 5
                alphas[5] = (alphas[0]     + alphas[1] * 4) // 5
                alphas[7] = 255

            for i in range(8):
                alphas[i] <<= 24

            r0, g0, b0 = _unpack_565(c0)
            r1, g1, b1 = _unpack_565(c1)

            colors[0] = _pack_rgba(r0, g0, b0, 0)
            colors[1] = _pack_rgba(r1, g1, b1, 0)

            if c0 > c1:
                colors[2] = _pack_rgba(_c2a(r0, r1), _c2a(g0, g1), _c2a(b0, b1), 0)
                colors[3] = _pack_rgba(_c3(r0, r1), _c3(g0, g1), _c3(b0, b1), 0)
            else:
                colors[2] = _pack_rgba(_c2b(r0, r1), _c2b(g0, g1), _c2b(b0, b1), 0)

            for i in range(16):
                idx = i * 4
                r, g, b, a = _unpack_rgba(alphas[bitcode_a & 0x07] | colors[bitcode_c & 0x03])
                buffer[idx:idx+4] = struct.pack('<4B', r, g, b ,a)
                bitcode_a >>= 3
                bitcode_c >>= 2

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

            


    