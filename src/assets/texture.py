import collections
import os
import traceback

from .. utils import (
    decode,
    enum,
    file_io,
    log
)

""""
Texture usage constants
"""
class TEXTURE_USAGE(metaclass = enum.BaseEnum):
    COLOR = 0x00
    DEFAULT = 0x01
    SKYBOX = 0x05

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
Texture class represents a texture structure 
"""
class Texture:

    MAGIC = 'IWi'
    VERSION = 5
    PATH = 'images'
    
    __slots__ = ('name', 'format', 'usage', 'width', 'height', 'texture_data')
    
    def __init__(self) -> None:
        self.name = ''
        self.format = None
        self.usage = None
        self.width = 0
        self.height = 0
        self.texture_data = []

    def load(self, texture: str) -> bool:
        self.name = os.path.splitext(os.path.basename(texture))[0]
        try:
            with open(texture, 'rb') as file:
                header = file_io.read_fmt(file, '3sBBBHH2xIIII', collections.namedtuple('header', 'magic, version, format, usage, width, height, filesize, texture_offset, mipmap1_offset, mipmap2_offset'))
                header_magic = header.magic.decode('utf-8')
                if header_magic != self.MAGIC and header.version != self.VERSION:
                    log.info_log(f"{header_magic}{header.version} is not supported")
                    return False

                self.format = header.format
                self.usage = header.usage
                self.width = header.width
                self.height = header.height

                file.seek(header.texture_offset, os.SEEK_SET)
                raw_texture_data = file.read(header.filesize - header.texture_offset)
                if len(raw_texture_data) == 0:
                    raise ValueError("Data length is 0")
                
                self.texture_data = decode.decode(raw_texture_data, self.width, self.height, self.format)
                return True
        
        except:
            log.error_log(traceback.print_exc())
            return False