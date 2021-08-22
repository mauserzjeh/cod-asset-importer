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
        self.bones = []

    def load(self, asset_path, xmodel_part_name):
        self.name = xmodel_part_name
        filepath = os.path.join(asset_path, self.PATH, xmodel_part_name)
        try:
            with open(filepath, 'rb') as file:
                header = utils.read_fmt(file, '3H', namedtuple('header', 'version, bone_count, root_bone_count'))
                if header.version != self.VERSION:
                    return False

                for _ in range(header.root_bone_count):
                    self.bones.append({
                        'quaternion': (0.0, 0.0, 0.0, 1.0), # x, y, z, w
                        'transform': (0.0, 0.0, 0.0), # x, y, z
                        'parent': -1
                    })

                for _ in range(header.bone_count):
                    bone = utils.read_fmt(file, 'B3f3h', namedtuple('bone', 'parent, pos_x, pos_y, pos_z, rot_x, rot_y, rot_z'))

                    brx = bone.rot_x
                    bry = bone.rot_y
                    brz = bone.rot_z
                    
                    qx = brx / self.QUATERNION_COMPENSATION
                    qy = bry / self.QUATERNION_COMPENSATION
                    qz = brz / self.QUATERNION_COMPENSATION
                    qw = math.sqrt((1 - math.pow(qx, 2) - math.pow(qy, 2) - math.pow(qz, 2)))

                    tx = bone.pos_x
                    ty = bone.pos_y
                    tz = bone.pos_z
                    
                    self.bones.append({
                        'quaternion': (qx, qy, qz, qw),
                        'transform': (tx, ty, tz),
                        'parent': bone.parent,
                    })

                for k in range((header.root_bone_count  + header.bone_count)):
                    bone_name = utils.read_nullstr(file)
                    self.bones[k]['name'] = bone_name
                

                return True
        except:
            traceback.print_exc()
            return False