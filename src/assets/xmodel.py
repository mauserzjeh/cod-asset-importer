from __future__ import annotations

import os
import traceback

from .. utils import (
    enum,
    file_io,
    log
)

"""
xmodel type constants
"""
class TYPES(metaclass = enum.BaseEnum):
    RIGID = '0'
    ANIMATED = '1'
    VIEWMODEL = '2'
    PLAYERBODY = '3'
    VIEWHANDS = '4'

"""
xmodel version constants
"""
class VERSIONS(metaclass = enum.BaseEnum):
    COD1 = 0x0E # 14
    COD2 = 0x14 # 20
    COD4 = 0x19 # 25

"""
XModel class represents an xmodel structure
"""
class XModel:



    PATH = 'xmodel'

     # --------------------------------------------------------------------------------------------
    class _lod:
        __slots__ = ('name', 'distance', 'materials')
    
        def __init__(self, name: str = "", distance: float = 0.0, materials: list[str] = None) -> None:
            self.name = name
            self.distance = distance
            self.materials = [] if materials == None else materials
        
    # --------------------------------------------------------------------------------------------

    __slots__ = ('name', 'version', 'lods')

    def __init__(self) -> None:
        self.name = ''
        self.version = 0
        self.lods = []

    def _load_v14(self, file: bytes) -> bool:
        file.read(24) # padding

        for _ in range(3):
            lod_distance = file_io.read_float(file)
            lod_name = file_io.read_nullstr(file)

            if len(lod_name):
                self.lods.append(self._lod(lod_name, lod_distance))

        file.read(4) # padding

        padding_count = file_io.read_uint(file)
        for _ in range(padding_count):
            sub_padding_count = file_io.read_uint(file)
            file.read(((sub_padding_count*48)+36))

        for k in range(len(self.lods)):
            material_count = file_io.read_ushort(file)
            for _ in range(material_count):
                texture = file_io.read_nullstr(file)
                self.lods[k].materials.append(texture)

        return True
    
    def _load_v20(self, file: bytes) -> bool:
        file.read(25) # padding
                
        for _ in range(4):
            lod_distance = file_io.read_float(file)
            lod_name = file_io.read_nullstr(file)

            if len(lod_name):
                self.lods.append(self._lod(lod_name, lod_distance))

        file.read(4) # padding

        padding_count = file_io.read_uint(file)
        for _ in range(padding_count):
            sub_padding_count = file_io.read_uint(file)
            file.read(((sub_padding_count*48)+36))

        for k in range(len(self.lods)):
            material_count = file_io.read_ushort(file)
            for _ in range(material_count):
                material = file_io.read_nullstr(file)
                self.lods[k].materials.append(material)

        return True

    def _load_v25(self, file: bytes) -> bool:
        file.read(26) # padding
                
        for _ in range(4):
            lod_distance = file_io.read_float(file)
            lod_name = file_io.read_nullstr(file)

            if len(lod_name):
                self.lods.append(self._lod(lod_name, lod_distance))
        
        file.read(4) # padding

        padding_count = file_io.read_uint(file)
        for _ in range(padding_count):
            sub_padding_count = file_io.read_uint(file)
            file.read(((sub_padding_count*48)+36))

        for k in range(len(self.lods)):
            material_count = file_io.read_ushort(file)
            for _ in range(material_count):
                material = file_io.read_nullstr(file)
                self.lods[k].materials.append(material)

        return True

    def load(self, xmodel: str) -> bool:
        self.name = os.path.basename(xmodel)
        try:
            with open(xmodel, 'rb') as file:
                version = file_io.read_ushort(file)
                if version not in VERSIONS:
                    log.info_log(f'xmodel version {version} is not supported')
                    return False
                
                self.version = version

                if self.version == VERSIONS.COD1:
                    return self._load_v14(file)

                elif self.version == VERSIONS.COD2:
                    return self._load_v20(file)

                elif self.version == VERSIONS.COD4:
                    return self._load_v25(file)

                return False # not gonna reach this part, just in case...
        except:
            log.error_log(traceback.print_exc())
            return False

    
    