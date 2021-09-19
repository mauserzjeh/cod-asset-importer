import collections
import os
import traceback

from .. utils import (
    enum,
    file_io,
    log
)

class TEXTURE_USAGE(metaclass = enum.BaseEnum):
    COLOR = 0x00
    DEFAULT = 0x01
    SKYBOX = 0x05

class TEXTURE_FORMAT(metaclass = enum.BaseEnum):
    ARGB32 = 0x01
    RGB24 = 0x02
    GA16 = 0x03
    A8 = 0x04
    DXT1 = 0x0B
    DXT3 = 0x0C
    DXT5 = 0x0D

class Texture:

    MAGIC = 'IWi'
    VERSION = 5
    PATH = 'images'
    
    def __init__(self) -> None:
        self.name = ''
        self.format = None
        self.usage = None
        self.width = 0
        self.height = 0
        self.texture_data = []

    def load(self, asset_path: str, image_name: str) -> bool:
        self.name = image_name
        filepath = os.path.join(asset_path, self.PATH, image_name)
        try:
            with open(filepath, 'rb') as file:
                header = file_io.read_fmt(file, '3sBBBHH2xIIII', collections.namedtuple('header', 'magic, version, format, usage, width, height, filesize, texture_offset, mipmap1_offset, mipmap2_offset'))
                header_magic = header.magic.decode('ascii')
                if header_magic != self.MAGIC and header.version != self.VERSION:
                    log.info_log(f"{header_magic}{header.version} is not supported")
                    return False

                self.format = header.format
                self.usage = header.usage
                self.width = header.width
                self.height = header.height

                file.seek(header.texture_offset, os.SEEK_SET)
                self.texture_data = file.read(header.filesize - header.texture_offset)

                return True
        except:
            traceback.print_exc()
            return False