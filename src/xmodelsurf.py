import copy
import os
import traceback
import utils
import xmodelpart

from collections import namedtuple

class XModelSurf:

    PATH = 'xmodelsurfs'
    VERSION = 20
    PHYSIQUED = 65535
    
    def __init__(self):
        self.name = ''
        self.raw_data = {}
        self.data = {}
    
    def load(self, asset_path, xmodel_surf_name, xmodel_part: xmodelpart.XModelPart = None):
        successful_load = self._load_raw_data(asset_path, xmodel_surf_name)
        if not successful_load:
            return False

        if xmodel_part != None:
            self._process_raw_data(xmodel_part)

        return True

    def _load_raw_data(self, asset_path, xmodel_surf_name):
        self.name = xmodel_surf_name
        filepath = os.path.join(asset_path, self.PATH, xmodel_surf_name)
        try:
            with open(filepath, 'rb') as file:
                header = utils.read_fmt(file, '2H', namedtuple('header', 'version, surfaces_count'))
                if header.version != self.VERSION:
                    return False

                self.raw_data['surfaces'] = []
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
                            'uv' : utils.read_fmt(file, '2f'),
                            'binormal': utils.read_fmt(file, '3f'),
                            'tangent': utils.read_fmt(file, '3f'),
                        }

                        weight_count = 0
                        vertex['bone'] = 0
                        if is_physiqued:
                            weight_count = utils.read_uchar(file)
                            vertex['bone'] = utils.read_ushort(file)

                        vertex['position'] = utils.read_fmt(file, '3f')
                        

                        if weight_count:
                            file.read(1) # padding

                            vertex['weights'] = []
                            for _ in range(weight_count):
                                blend_bone = utils.read_ushort(file)
                                file.read(12) # padding
                                blend_weight = utils.read_ushort(file)

                                vertex['weights'].append({
                                    'blend_bone': blend_bone,
                                    'blend_weight': blend_weight
                                })
                        
                        surface['vertices'].append(vertex)

                    # read triangles
                    for _ in range(surface_header.triangle_count):
                        triangle = utils.read_fmt(file, '3H')
                        surface['triangles'].append(triangle)

                    # add surface
                    self.raw_data['surfaces'].append(surface)

                return True
        except:
            traceback.print_exc()
            return False

    def _process_raw_data(self, xmodel_part: xmodelpart.XModelPart):
        self.data['surfaces'] = []
        for j, raw_surface_data in enumerate(self.raw_data['surfaces']):
            vertices = []
            raw_vertices = raw_surface_data['vertices']
            for i, raw_vertex in enumerate(raw_vertices):
                
                vertex = copy.deepcopy(raw_vertex)

                vertex_bone = xmodel_part.data['bones'][vertex['bone']]
                bone_rotation = vertex_bone['world_transform']['rotation']

                tposition = utils.transform_vector(bone_rotation, vertex['position'])
                if j == 0 and i < 20:
                    utils.debug_log(f"i: {i} vpos: {vertex['position']} tpos: {tposition}\n bone_idx: {vertex['bone']}\n bone_name: {vertex_bone['name']}\n bone_rotation: {bone_rotation}\n bone_position: {vertex_bone['world_transform']['position']}" )
                if tposition != None:
                    
                    bone_position = vertex_bone['world_transform']['position']

                    tpx = tposition[0] + bone_position[0]
                    tpy = tposition[1] + bone_position[1]
                    tpz = tposition[2] + bone_position[2]

                    vertex['position'] = (tpx, tpy, tpz)
                if j == 0 and i < 20:
                    utils.debug_log(f"i: {i} final_pos: {vertex['position']}")
                tnormal = utils.transform_vector(bone_rotation, vertex['normal'])
                if tnormal != None:
                    vertex['normal'] = tnormal

                vertices.append(vertex)

            surface = {
                'vertices': vertices,
                'triangles': raw_surface_data['triangles']
            }

            self.data['surfaces'].append(surface)
            

