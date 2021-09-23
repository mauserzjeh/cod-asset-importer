import os
import traceback

from .. utils import (
    file_io,
    log
)

class XModel:

    PATH = 'xmodel'
    VERSION = 20

    # --------------------------------------------------------------------------------------------
    class _lod:
        __slots__ = ('name', 'distance', 'materials')
    
        def __init__(self, name: str = "", distance: float = 0.0, materials: list[str] = []) -> None:
            self.name = name
            self.distance = distance
            self.materials = materials
        
    # --------------------------------------------------------------------------------------------

    __slots__ = ('name', 'lods')

    def __init__(self) -> None:
        self.name = ''
        self.lods = []

    def load(self, xmodel: str) -> bool:
        self.name = os.path.basename(xmodel)
        try:
            with open(xmodel, 'rb') as file:
                version = file_io.read_ushort(file)
                if version != self.VERSION:
                    log.info_log(f'Xmodel version {version} is not supported!')
                    return False

                file.read(25) # padding
                
                for _ in range(4):
                    lod_distance = file_io.read_float(file)
                    lod_name = file_io.read_nullstr(file)

                    if len(lod_name):
                        self.lods.append(self._lod(lod_name, lod_distance))

                # padding
                file.read(4) 
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
        except:
            traceback.print_exc()
            return False

