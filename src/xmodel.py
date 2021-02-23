import struct
import traceback

from collections import namedtuple

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
        filepath = asset_path + self.PATH + '\\' + xmodel_name
        try:
            with open(filepath, 'rb') as file:
                self.name = xmodel_name
                
                file.seek(0)
                
                version = utils.read_ushort(file)
                if version != self.VERSION:
                    return False

                file.read(25) # padding
                for i in range(4):
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
                for j in range(padding_count):
                    sub_padding_count = utils.read_uint(file)
                    file.read(((sub_padding_count*48)+36))

                for k in range(len(self.lods)):
                    material_count = utils.read_ushort(file)
                    lodmaterials = []
                    for l in range(material_count):
                        lodmaterial = utils.read_nullstr(file)
                        lodmaterials.append(lodmaterial)

                    self.lods[k]['materials'] = lodmaterials

                return True
        except:
            traceback.print_exc()
            return False


class XModelSurf:

    PATH = 'xmodelsurf'
    VERSION = 20
    PHYSIQUED = 65535
    
    def __init__(self):
        self.name = ''
        self.surfaces = []

    def load(self, asset_path, xmodel_surf_name):
        filepath = asset_path + self.PATH + '\\' + xmodel_surf_name
        try:
            with open(filepath, 'rb') as file:
                header = utils.read_fmt(file, '2H', namedtuple('header', 'version, surfaces_count'))
                if header.version != self.VERSION:
                    return False

                for i in range(header.surfaces_count):
                    surface_header = utils.read_fmt(file, 'x3H', namedtuple('surface_header', 'vertex_count, triangle_count, physiqued'))
                    
                    is_physiqued = False
                    if surface_header.physiqued == self.PHYSIQUED:
                        is_physiqued = True

                    if is_physiqued:
                        file.read(2) # padding

                    surface = {
                        'vertices' : [],
                        'triangles' : []
                    }

                    # read vertices
                    for j in range(surface_header.vertex_count):
                        vertex = {
                            'normal' : utils.read_fmt(file, '3f'),
                            'color' : utils.read_fmt(file, '4B'),
                            'uv' : utils.read_fmt(file, '2f')
                        }
                        file.read(24) # padding

                        if is_physiqued:
                            weight_count = utils.read_uchar(file)
                            file.read(2) # padding

                        vertex['position'] = utils.read_fmt(file, '3f')
                        
                        if is_physiqued:
                            for k in range(weight_count):
                                file.read(16) # padding
                            if weight_count:
                                file.read(1) # padding
                        
                        surface['vertices'].append(vertex)

                    # read triangles
                    for l in range(surface_header.triangle_count):
                        triangle = utils.read_fmt(file, '3H')
                        surface['triangles'].append(triangle)

                    # add surface
                    self.surfaces.append(surface)

                return True
        except:
            traceback.print_exc()
            return False

class XModelPart:
    
    PATH = 'xmodelpart'
    VERSION = 20
    
    def __init__(self):
        pass

    def load(self, asset_path, xmodel_part_name):
        pass
