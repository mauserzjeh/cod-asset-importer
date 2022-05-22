import os
import traceback

from .. utils import ( 
    file_io,
    log
)

"""
Material class represents a material structure
"""
class Material:

    PATH = 'materials'
    
     # --------------------------------------------------------------------------------------------
    class _texture:
        __slots__ = ('type', 'flags', 'name')

        def __init__(self, type: str, flags: int, name: str) -> None:
            self.type = type
            self.flags = flags
            self.name = name
    
     # --------------------------------------------------------------------------------------------

    __slots__ = ('name', 'techset', 'textures')

    def __init__(self) -> None:
        self.name = ''
        self.techset = ''
        self.textures = []

    def load(self, material: str) -> bool:
        self.name = os.path.basename(material)
        try:
            with open(material, 'rb') as file:
                name_offset = file_io.read_uint(file)

                current_offset = file.tell()
                file.seek(name_offset, os.SEEK_SET)
                self.name = file_io.read_nullstr(file)
                file.seek(current_offset, os.SEEK_SET)

                file.read(48) # padding

                texture_count = file_io.read_ushort(file)

                file.read(2) # padding

                techset_offset = file_io.read_uint(file)
                textures_offset = file_io.read_uint(file)

                file.seek(techset_offset, os.SEEK_SET)
                self.techset = file_io.read_nullstr(file)

                file.seek(textures_offset, os.SEEK_SET)
                for _ in range (texture_count):
                    texture_type_offset = file_io.read_uint(file)
                    texture_flags = file_io.read_uint(file)
                    texture_name_offset = file_io.read_uint(file)
                    current_offset = file.tell()

                    file.seek(texture_type_offset, os.SEEK_SET)
                    texture_type = file_io.read_nullstr(file)

                    file.seek(texture_name_offset, os.SEEK_SET)
                    texture_name = file_io.read_nullstr(file)

                    self.textures.append(self._texture(texture_type, texture_flags, texture_name))
                    file.seek(current_offset, os.SEEK_SET)

                return True

        except Exception as e:
            log.error_log(e)
            return False