import math
import os
import traceback
import utils

from collections import namedtuple

class XModelPart:
    
    PATH = 'xmodelparts'
    VERSION = 20
    MODEL_TYPES = {
        0: 'rigid',
        1: 'animated',
        2: 'viewmodel',
        3: 'playerbody',
        4: 'viewhands'
    }
    QUATERNION_COMPENSATION = 32768.0
    
    def __init__(self):
        self.name = ''
        self.raw_data = {}
        self.data = {}

    def load(self, asset_path, xmodel_part_name):
        successful_load = self._load_raw_data(asset_path, xmodel_part_name)
        if not successful_load:
            return False

        self._process_raw_data()
        return True


    def _load_raw_data(self, asset_path, xmodel_part_name):
        self.name = xmodel_part_name
        filepath = os.path.join(asset_path, self.PATH, xmodel_part_name)
        try:
            with open(filepath, 'rb') as file:
                header = utils.read_fmt(file, '3H', namedtuple('header', 'version, bone_count, root_bone_count'))
                if header.version != self.VERSION:
                    return False

                self.raw_data['bones'] = []
                for _ in range(header.root_bone_count):
                    self.raw_data['bones'].append({
                        # ----------  x    y    z
                        'position': (0.0, 0.0, 0.0),
                        'rotation': (0.0, 0.0, 0.0),
                        # --------------------------
                        'parent': -1
                    })

                for _ in range(header.bone_count):
                    bone = utils.read_fmt(file, 'B3f3h', namedtuple('bone', 'parent, pos_x, pos_y, pos_z, rot_x, rot_y, rot_z'))

                    self.raw_data['bones'].append({
                        # ----------     x           y           z
                        'position': (bone.pos_x, bone.pos_y, bone.pos_z),
                        'rotation': (bone.rot_x, bone.rot_y, bone.rot_z),
                        # -----------------------------------------------
                        'parent': bone.parent
                    })

                for k in range((header.root_bone_count  + header.bone_count)):
                    bone_name = utils.read_nullstr(file)
                    self.raw_data['bones'][k]['name'] = bone_name 
                
                return True

        except:
            traceback.print_exc()
            return False

    
    def _process_raw_data(self):
        self.data['bones'] = []

        raw_bones = self.raw_data['bones']
        for raw_bone_data in raw_bones:
            
            # position --------------------------
            position = raw_bone_data['position']
            
            px = position[0]
            py = position[1]
            pz = position[2]
            
            bone_position = (px, py, pz)
            # -----------------------------------

            # rotation --------------------------
            rotation = raw_bone_data['rotation']
            
            brx = rotation[0]
            bry = rotation[1]
            brz = rotation[2]

            qx = brx / self.QUATERNION_COMPENSATION
            qy = bry / self.QUATERNION_COMPENSATION
            qz = brz / self.QUATERNION_COMPENSATION
            qw = math.sqrt((1 - math.pow(qx, 2) - math.pow(qy, 2) - math.pow(qz, 2)))

            bone_rotation = (qx, qy, qz, qw)
            # -----------------------------------

            self.data['bones'].append({
                'world_transform': {
                    'position': bone_position,
                    'rotation': bone_rotation
                },
                'local_transform': {
                    'position': bone_position,
                    'rotation': bone_rotation
                },
                'parent': raw_bone_data['parent'],
                'name': raw_bone_data['name']
            })

        for i, bone in enumerate(self.data['bones']):

            parent_index = bone['parent']
            parent_bone = self.data['bones'][parent_index]
            
            if parent_index > -1:
                world_position = tuple(map(lambda i, j: i + j, parent_bone['world_transform']['position'], utils.transform_vector(parent_bone['world_transform']['rotation'], bone['local_transform']['position'])))
                world_rotation = utils.multiply_quaternion(parent_bone['world_transform']['rotation'], bone['local_transform']['rotation'])
            else:
                world_position = bone['local_transform']['position']
                world_rotation = bone['local_transform']['rotation']

            world_transform = {
                'position': world_position,
                'rotation': world_rotation
            }

            self.data['bones'][i]['world_transform'] = world_transform