import os
import traceback

from utils import file_io
from utils import log

class XModel:

    PATH = 'xmodel'
    VERSION = 20

    # --------------------------------------------------------------------------------------------
    class _lod:
    
        def __init__(self, name: str = "", distance: float = 0.0, materials: list[str] = []) -> None:
            self.name = name
            self.distance = distance
            self.materials = materials
        
    # --------------------------------------------------------------------------------------------

    def __init__(self) -> None:
        self.name = ''
        self.lods = []

    def load(self, asset_path: str, xmodel_name: str) -> bool:
        self.name = xmodel_name
        filepath = os.path.join(asset_path, self.PATH, xmodel_name)
        try:
            with open(filepath, 'rb') as file:
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

