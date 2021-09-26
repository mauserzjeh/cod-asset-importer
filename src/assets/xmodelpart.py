from __future__ import annotations

import collections
import copy
import math
import mathutils
import os
import traceback

from .. utils import (
    file_io,
    log
)

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
        __slots__ = ('rotation', 'position')
        
        def __init__(self, rotation: mathutils.Quaternion, position: mathutils.Vector) -> None:
            self.rotation = rotation
            self.position = position

    class _bone:
        __slots__ = ('name', 'parent', 'local_transform', 'world_transform')

        def __init__(self, local_transform: XModelPart._bone_transform, parent: int = -1, name: str = '') -> None:
            self.name = name
            self.parent = parent
            self.local_transform = local_transform
            self.world_transform = copy.deepcopy(local_transform)

        def generate_world_transform_by_parent(self, parent: XModelPart._bone) -> None:
            self.world_transform.position = parent.world_transform.position + (parent.world_transform.rotation @ self.local_transform.position)        
            self.world_transform.rotation = parent.world_transform.rotation @ self.local_transform.rotation

    # --------------------------------------------------------------------------------------------
    
    __slots__ = ('name', 'bones')

    def __init__(self) -> None:
        self.name = ''
        self.bones = []
    
    def load(self, xmodel_part: str) -> bool:
        self.name = os.path.basename(xmodel_part)
        try:
            with open(xmodel_part, 'rb') as file:
                header = file_io.read_fmt(file, '3H', collections.namedtuple('header', 'version, bone_count, root_bone_count'))
                if header.version != self.VERSION:
                    log.info_log(f'Xmodel version {header.version} is not supported!')
                    return False

                for _ in range(header.root_bone_count):
                    rotation = mathutils.Quaternion()
                    position = mathutils.Vector()
                    bone_transform = self._bone_transform(rotation, position)
                    bone = self._bone(bone_transform)
                    self.bones.append(bone)

                for _ in range(header.bone_count):
                    raw_bone_data = file_io.read_fmt(file, 'B3f3h', collections.namedtuple('raw_bone_data', 'parent, px, py, pz, rx, ry, rz'))
                    
                    qx = raw_bone_data.rx / self.ROTATION_DIVISOR
                    qy = raw_bone_data.ry / self.ROTATION_DIVISOR
                    qz = raw_bone_data.rz / self.ROTATION_DIVISOR
                    qw = math.sqrt((1 - (qx ** 2) - (qy ** 2) - (qz ** 2)))

                    rotation = mathutils.Quaternion((qw, qx, qy, qz))

                    position = mathutils.Vector((
                        raw_bone_data.px,
                        raw_bone_data.py,
                        raw_bone_data.pz
                    ))

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