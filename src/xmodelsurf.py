import os
import traceback
import utils

from collections import namedtuple

class XModelSurf:

    PATH = 'xmodelsurfs'
    VERSION = 20
    PHYSIQUED = 65535
    
    def __init__(self):
        self.name = ''
        self.surfaces = []

    def load(self, asset_path, xmodel_surf_name):
        self.name = xmodel_surf_name
        filepath = os.path.join(asset_path, self.PATH, xmodel_surf_name)
        try:
            with open(filepath, 'rb') as file:
                header = utils.read_fmt(file, '2H', namedtuple('header', 'version, surfaces_count'))
                if header.version != self.VERSION:
                    return False

                for _ in range(header.surfaces_count):
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
                    for _ in range(surface_header.vertex_count):
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
                            for _ in range(weight_count):
                                file.read(16) # padding
                            if weight_count:
                                file.read(1) # padding
                        
                        surface['vertices'].append(vertex)

                    # read triangles
                    for _ in range(surface_header.triangle_count):
                        triangle = utils.read_fmt(file, '3H')
                        surface['triangles'].append(triangle)

                    # add surface
                    self.surfaces.append(surface)

                return True
        except:
            traceback.print_exc()
            return False