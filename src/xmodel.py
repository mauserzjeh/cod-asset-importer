import os
import traceback
import utils


class XModel:

    PATH = 'xmodel'
    VERSION = 20

    ENTITY_KEY_MODEL = 'model'
    ENTITY_KEY_ANGLES = 'angles'
    ENTITY_KEY_ORIGIN = 'origin'
    ENTITY_KEY_MODELSCALE = 'modelscale'

    def __init__(self):
        self.name = ''
        self.lods = []

    def load(self, asset_path, xmodel_name):
        self.name = xmodel_name
        filepath = os.path.join(asset_path, self.PATH, xmodel_name)
        try:
            with open(filepath, 'rb') as file:
                version = utils.read_ushort(file)
                if version != self.VERSION:
                    return False

                file.read(25) # padding
                for _ in range(4):
                    lod = {
                        'distance' : utils.read_float(file),
                        'name' : utils.read_nullstr(file)
                    }

                    # only add valid lods
                    if len(lod['name']):
                        self.lods.append(lod)

                file.read(4) # padding

                # padding
                padding_count = utils.read_uint(file)
                for _ in range(padding_count):
                    sub_padding_count = utils.read_uint(file)
                    file.read(((sub_padding_count*48)+36))

                for k in range(len(self.lods)):
                    material_count = utils.read_ushort(file)
                    lodmaterials = []
                    for _ in range(material_count):
                        lodmaterial = utils.read_nullstr(file)
                        lodmaterials.append(lodmaterial)

                    self.lods[k]['materials'] = lodmaterials

                return True
        except:
            traceback.print_exc()
            return False

