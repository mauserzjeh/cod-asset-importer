from __future__ import annotations

import collections
import copy
import os
import traceback

from utils import file_io
from utils import log
from utils import quaternion
from utils import vector

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
    ROTATION_DIVISOR = 32768.0

    # --------------------------------------------------------------------------------------------
    class _bone_transform:
        
        def __init__(self, rotation: quaternion.Quaternion, position: vector.Vector3) -> None:
            self.rotation = rotation
            self.position = position

    class _bone:
        
        def __init__(self, local_transform: XModelPart._bone_transform, parent: int = -1, name: str = '') -> None:
            self.name = name
            self.parent = parent
            self.local_transform = local_transform
            self.world_transform = copy.copy(local_transform)

        def generate_world_transform_by_parent(self, parent: XModelPart._bone, debug = False) -> None:
            self.world_transform.position = parent.world_transform.position + self.local_transform.position.rotate_by_quaternion(parent.world_transform.rotation)
            self.world_transform.rotation = parent.world_transform.rotation * self.local_transform.rotation

    # --------------------------------------------------------------------------------------------
    
    def __init__(self) -> None:
        self.name = ''
        self.bones = []
    
    def load(self, asset_path, xmodel_part_name) -> bool:
        self.name = xmodel_part_name
        filepath = os.path.join(asset_path, self.PATH, xmodel_part_name)
        try:
            with open(filepath, 'rb') as file:
                header = file_io.read_fmt(file, '3H', collections.namedtuple('header', 'version, bone_count, root_bone_count'))
                if header.version != self.VERSION:
                    log.info_log(f'Xmodel version {header.version} is not supported!')
                    return False

                for _ in range(header.root_bone_count):
                    rotation = quaternion.Quaternion()
                    position = vector.Vector3()
                    bone_transform = self._bone_transform(rotation, position)
                    bone = self._bone(bone_transform)
                    self.bones.append(bone)

                for _ in range(header.bone_count):
                    raw_bone_data = file_io.read_fmt(file, 'B3f3h', collections.namedtuple('raw_bone_data', 'parent, pos_x, pos_y, pos_z, rot_x, rot_y, rot_z'))
                    
                    rotation = quaternion.Quaternion(
                        raw_bone_data.rot_x / self.ROTATION_DIVISOR,
                        raw_bone_data.rot_y / self.ROTATION_DIVISOR,
                        raw_bone_data.rot_z / self.ROTATION_DIVISOR
                    )
                    position = vector.Vector3(
                        raw_bone_data.pos_x,
                        raw_bone_data.pos_y,
                        raw_bone_data.pos_z
                    )

                    bone_transform = self._bone_transform(rotation, position)
                    bone = self._bone(bone_transform, raw_bone_data.parent)
                    self.bones.append(bone)

                for bone_index in range((header.root_bone_count + header.bone_count)):
                    bone_name = file_io.read_nullstr(file)

                    current_bone = self.bones[bone_index]
                    current_bone.name = bone_name

                    if current_bone.parent > -1:
                        parent_bone = self.bones[current_bone.parent]
                        current_bone.generate_world_transform_by_parent(parent_bone)

                return True
        except:
            traceback.print_exc()
            return False