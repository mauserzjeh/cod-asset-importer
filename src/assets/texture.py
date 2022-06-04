import collections
import os
import traceback

from .. utils import (
    decode,
    enum,
    file_io,
    log
)

"""
Texture format constants
"""
class TEXTURE_FORMAT(metaclass = enum.BaseEnum):
    ARGB32 = 0x01
    RGB24 = 0x02
    GA16 = 0x03
    A8 = 0x04
    DXT1 = 0x0B
    DXT3 = 0x0C
    DXT5 = 0x0D

"""
Texture type constants
"""
class TEXTURE_TYPE(metaclass = enum.BaseEnum):
    COLORMAP = 'colorMap'
    DETAILMAP = 'detailMap'
    NORMALMAP = 'normalMap'
    SPECULARMAP = 'specularMap'

"""
IWi class represents an IWi structure 
"""
class IWi:

    class VERSIONS(metaclass = enum.BaseEnum):
        COD2 = 0x05
        COD4 = 0x06 
        COD5 = 0x06 
        CODMW2 = 0x08 
        CODMW3 = 0x08 
        CODBO1 = 0x0D 
        CODBO2 = 0x1B 

    MAGIC = 'IWi'
    PATH = 'images'
    
    __slots__ = ('name', 'format', 'usage', 'width', 'height', 'texture_data')
    
    def __init__(self) -> None:
        self.name = ''
        self.format = None
        self.usage = None
        self.width = 0
        self.height = 0
        self.texture_data = []

    def _highest_mipmap(self, offsets: tuple, first: int, size: int) -> dict:
        mipmaps = []
        for i in range(len(offsets)):
            if i == 0:
                mipmaps.append({
                    'offset': offsets[i],
                    'size': size - offsets[i]
                })
            
            elif i == (len(offsets) - i):
                mipmaps.append({
                    'offset': first,
                    'size': offsets[i] - first,
                })
            
            else:
                mipmaps.append({
                    'offset': offsets[i],
                    'size': offsets[i-1] - offsets[i]
                })
        
        max_idx = 0
        for i in range(len(mipmaps)):
            if mipmaps[i]['size'] > mipmaps[max_idx]['size']:
                max_idx = i

        return mipmaps[max_idx]

    def load(self, texture: str) -> bool:
        self.name = os.path.splitext(os.path.basename(texture))[0]
        try:
            with open(texture, 'rb') as file:
                header = file_io.read_fmt(file, '3sB', collections.namedtuple('header', 'magic, version'))
                header_magic = header.magic.decode('utf-8')
                if header_magic != self.MAGIC or header.version not in self.VERSIONS:
                    log.info_log(f"{header_magic}{header.version} is not supported")
                    return False

                if header.version == self.VERSIONS.CODMW2 or header.version == self.VERSIONS.CODMW3:
                    file.seek(0x8, os.SEEK_SET)

                info = file_io.read_fmt(file, 'BB3H', collections.namedtuple('info', 'format, usage, width, height, depth'))
                self.format = info.format
                self.usage = info.usage
                self.width = info.width
                self.height = info.height

                offset_count = 4
                if header.version == self.VERSIONS.CODBO1 or header.version == self.VERSIONS.CODBO2:
                    offset_count = 8
                    file.seek(0x20, os.SEEK_SET) if header.version == self.VERSIONS.CODBO2 else file.seek(0x10, os.SEEK_SET)
                
                offsets = file_io.read_fmt(file, f"{offset_count}I")
                curr_offset = file.tell()
                file_size = file.seek(0, os.SEEK_END)
                mipmap = self._highest_mipmap(offsets, curr_offset, file_size)

                file.seek(mipmap['offset'], os.SEEK_SET)
                raw_texture_data = file.read(mipmap['size'])
                if len(raw_texture_data) == 0:
                    raise ValueError("data length is 0")
                
                self.texture_data = decode.decode(raw_texture_data, self.width, self.height, self.format)
                return True
        
        except:
            log.error_log(traceback.print_exc())
            return False