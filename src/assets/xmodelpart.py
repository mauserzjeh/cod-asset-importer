from __future__ import annotations

import collections
import copy
import math
import mathutils
import os
import traceback

from .. utils import (
    enum,
    file_io,
    log
)

"""
XModel type constants
"""
class XModelType(metaclass = enum.BaseEnum):
    RIGID = '0'
    ANIMATED = '1'
    VIEWMODEL = '2'
    PLAYERBODY = '3'
    VIEWHANDS = '4'

"""
XModelPartV20 represents xmodelpart structure for CoD2
"""
class XModelPartV20:
    
    PATH = 'xmodelparts'
    VERSION = 20
    ROTATION_DIVISOR = 32768.0
    VIEWHANDS_BONE_POSITIONS = {
        "tag_view":         mathutils.Vector((  0.0,             0.0,             0.0       )),
        "tag_torso":        mathutils.Vector(( -11.76486,        0.0,            -3.497466  )),
        "j_shoulder_le":    mathutils.Vector((  2.859542,        20.16072,       -4.597286  )),
        "j_elbow_le":       mathutils.Vector((  30.7185,        -8E-06,           3E-06     )),
        "j_wrist_le":       mathutils.Vector((  29.3906,         1.9E-05,        -3E-06     )),
        "j_thumb_le_0":     mathutils.Vector((  2.786345,        2.245192,        0.85161   )),
        "j_thumb_le_1":     mathutils.Vector((  4.806596,       -1E-06,           3E-06     )),
        "j_thumb_le_2":     mathutils.Vector((  2.433519,       -2E-06,           1E-06     )),
        "j_thumb_le_3":     mathutils.Vector((  3.0,            -1E-06,          -1E-06     )),
        "j_flesh_le":       mathutils.Vector((  4.822557,        1.176307,       -0.110341  )),
        "j_index_le_0":     mathutils.Vector((  10.53435,        2.786251,       -3E-06     )),
        "j_index_le_1":     mathutils.Vector((  4.563,          -3E-06,           1E-06     )),
        "j_index_le_2":     mathutils.Vector((  2.870304,        3E-06,          -2E-06     )),
        "j_index_le_3":     mathutils.Vector((  2.999999,        4E-06,           1E-06     )),
        "j_mid_le_0":       mathutils.Vector((  10.71768,        0.362385,       -0.38647   )),
        "j_mid_le_1":       mathutils.Vector((  4.842623,       -1E-06,          -1E-06     )),
        "j_mid_le_2":       mathutils.Vector((  2.957112,       -1E-06,          -1E-06     )),
        "j_mid_le_3":       mathutils.Vector((  3.000005,        4E-06,           0.0       )),
        "j_ring_le_0":      mathutils.Vector((  9.843364,       -1.747671,       -0.401116  )),
        "j_ring_le_1":      mathutils.Vector((  4.842618,        4E-06,          -3E-06     )),
        "j_ring_le_2":      mathutils.Vector((  2.755294,       -2E-06,           5E-06     )),
        "j_ring_le_3":      mathutils.Vector((  2.999998,       -2E-06,          -4E-06     )),
        "j_pinky_le_0":     mathutils.Vector((  8.613766,       -3.707476,        0.16818   )),
        "j_pinky_le_1":     mathutils.Vector((  3.942609,        1E-06,           1E-06     )),
        "j_pinky_le_2":     mathutils.Vector((  1.794117,        3E-06,          -3E-06     )),
        "j_pinky_le_3":     mathutils.Vector((  2.83939,        -1E-06,           4E-06     )),
        "j_wristtwist_le":  mathutils.Vector((  21.60379,        1.2E-05,        -3E-06     )),
        "j_shoulder_ri":    mathutils.Vector((  2.859542,       -20.16072,       -4.597286  )),
        "j_elbow_ri":       mathutils.Vector(( -30.71852,        4E-06,          -2.4E-05   )),
        "j_wrist_ri":       mathutils.Vector(( -29.39067,        4.4E-05,         2.2E-05   )),
        "j_thumb_ri_0":     mathutils.Vector(( -2.786155,       -2.245166,       -0.851634  )),
        "j_thumb_ri_1":     mathutils.Vector(( -4.806832,       -6.6E-05,         0.000141  )),
        "j_thumb_ri_2":     mathutils.Vector(( -2.433458,       -3.8E-05,        -5.3E-05   )),
        "j_thumb_ri_3":     mathutils.Vector(( -3.000123,        0.00016,         2.5E-05   )),
        "j_flesh_ri":       mathutils.Vector(( -4.822577,       -1.176315,        0.110318  )),
        "j_index_ri_0":     mathutils.Vector(( -10.53432,       -2.786281,       -7E-06     )),
        "j_index_ri_1":     mathutils.Vector(( -4.562927,       -5.8E-05,         5.4E-05   )),
        "j_index_ri_2":     mathutils.Vector(( -2.870313,       -6.5E-05,         0.0001    )),
        "j_index_ri_3":     mathutils.Vector(( -2.999938,        0.000165,       -6.5E-05   )),
        "j_mid_ri_0":       mathutils.Vector(( -10.71752,       -0.362501,        0.386463  )),
        "j_mid_ri_1":       mathutils.Vector(( -4.842728,        0.000151,        2.8E-05   )),
        "j_mid_ri_2":       mathutils.Vector(( -2.957152,       -8.7E-05,        -2.2E-05   )),
        "j_mid_ri_3":       mathutils.Vector(( -3.00006,        -6.8E-05,        -1.9E-05   )),
        "j_ring_ri_0":      mathutils.Vector(( -9.843175,        1.747613,        0.401109  )),
        "j_ring_ri_1":      mathutils.Vector(( -4.842774,        0.000176,       -6.3E-05   )),
        "j_ring_ri_2":      mathutils.Vector(( -2.755269,       -1.1E-05,         0.000149  )),
        "j_ring_ri_3":      mathutils.Vector(( -3.000048,       -4.1E-05,        -4.9E-05   )),
        "j_pinky_ri_0":     mathutils.Vector(( -8.613756,        3.707438,       -0.168202  )),
        "j_pinky_ri_1":     mathutils.Vector(( -3.942537,       -0.000117,       -6.5E-05   )),
        "j_pinky_ri_2":     mathutils.Vector(( -1.794038,        0.000134,        0.000215  )),
        "j_pinky_ri_3":     mathutils.Vector(( -2.839375,        5.6E-05,        -0.000115  )),
        "j_wristtwist_ri":  mathutils.Vector(( -21.60388,        9.7E-05,         8E-06     )),
        "tag_weapon":       mathutils.Vector((  38.5059,         0.0,            -17.15191  )),
        "tag_cambone":      mathutils.Vector((  0.0,             0.0,             0.0       )),
        "tag_camera":       mathutils.Vector((  0.0,             0.0,             0.0       )),
    }

    # --------------------------------------------------------------------------------------------
    class _bone_transform:
        __slots__ = ('rotation', 'position')
        
        def __init__(self, rotation: mathutils.Quaternion, position: mathutils.Vector) -> None:
            self.rotation = rotation
            self.position = position

    class _bone:
        __slots__ = ('name', 'parent', 'local_transform', 'world_transform')

        def __init__(self, local_transform: XModelPartV20._bone_transform, parent: int = -1, name: str = '') -> None:
            self.name = name
            self.parent = parent
            self.local_transform = local_transform
            self.world_transform = copy.deepcopy(local_transform)

        def generate_world_transform_by_parent(self, parent: XModelPartV20._bone) -> None:
            self.world_transform.position = parent.world_transform.position + (parent.world_transform.rotation @ self.local_transform.position)        
            self.world_transform.rotation = parent.world_transform.rotation @ self.local_transform.rotation

    # --------------------------------------------------------------------------------------------
    
    __slots__ = ('name', 'model_type', 'bones')

    def __init__(self) -> None:
        self.name = ''
        self.model_type = 0
        self.bones = []
    
    def load(self, xmodel_part: str) -> bool:
        self.name = os.path.basename(xmodel_part)
        self.model_type = self.name[-1]
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

                    # read raw bone data
                    raw_bone_data = file_io.read_fmt(file, 'B3f3h', collections.namedtuple('raw_bone_data', 'parent, px, py, pz, rx, ry, rz'))
                    
                    qx = raw_bone_data.rx / self.ROTATION_DIVISOR
                    qy = raw_bone_data.ry / self.ROTATION_DIVISOR
                    qz = raw_bone_data.rz / self.ROTATION_DIVISOR
                    qw = math.sqrt((1 - (qx ** 2) - (qy ** 2) - (qz ** 2)))

                    # generate rotation
                    rotation = mathutils.Quaternion((qw, qx, qy, qz))

                    # generate positioon
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

                    # set viewmodel positions
                    if self.model_type == XModelType.VIEWHANDS and  bone_name in self.VIEWHANDS_BONE_POSITIONS:
                        local_viewmodel_position = self.VIEWHANDS_BONE_POSITIONS[bone_name]
                        world_viewmodel_position = copy.deepcopy(local_viewmodel_position)
                        current_bone.local_transform.position = local_viewmodel_position / 2.54
                        current_bone.world_transform.position = world_viewmodel_position / 2.54

                    # transform bones by their parents to the correct place
                    if current_bone.parent > -1:
                        parent_bone = self.bones[current_bone.parent]
                        current_bone.generate_world_transform_by_parent(parent_bone)

                return True

        except:
            log.error_log(traceback.print_exc())
            return False

"""
XModelPartV14 represents xmodelpart structure for CoD1
"""
class XModelPartV14:

    PATH = 'xmodelparts'
    VERSION = 14
    ROTATION_DIVISOR = 32768.0
    VIEWHANDS_BONE_POSITIONS = {
        "tag_view":             mathutils.Vector((  0.0, 0.0, 0.0  )),
        "tag_torso":            mathutils.Vector((  0.0, 0.0, 0.0  )),
        "tag_weapon":           mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 l upperarm":     mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 l forearm":      mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 l hand":         mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 l finger0":      mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 l finger01":     mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 l finger02":     mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 l finger0nub":   mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 l finger1":      mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 l finger11":     mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 l finger12":     mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 l finger1nub":   mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 l finger2":      mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 l finger21":     mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 l finger22":     mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 l finger2nub":   mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 l finger3":      mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 l finger31":     mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 l finger32":     mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 l finger3nub":   mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 l finger4":      mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 l finger41":     mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 l finger42":     mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 l finger4nub":   mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 r upperarm":     mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 r forearm":      mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 r hand":         mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 r finger0":      mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 r finger01":     mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 r finger02":     mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 r finger0nub":   mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 r finger1":      mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 r finger11":     mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 r finger12":     mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 r finger1nub":   mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 r finger2":      mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 r finger21":     mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 r finger22":     mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 r finger2nub":   mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 r finger3":      mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 r finger31":     mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 r finger32":     mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 r finger3nub":   mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 r finger4":      mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 r finger41":     mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 r finger42":     mathutils.Vector((  0.0, 0.0, 0.0  )),
        "bip01 r finger4nub":   mathutils.Vector((  0.0, 0.0, 0.0  )),
        "l hand webbing":       mathutils.Vector((  0.0, 0.0, 0.0  )),
        "r hand webbing":       mathutils.Vector((  0.0, 0.0, 0.0  )),
        "r cuff":               mathutils.Vector((  0.0, 0.0, 0.0  )),
        "r cuff01":             mathutils.Vector((  0.0, 0.0, 0.0  )),
        "r wrist":              mathutils.Vector((  0.0, 0.0, 0.0  )),
        "r wrist01":            mathutils.Vector((  0.0, 0.0, 0.0  )),
    }

    # --------------------------------------------------------------------------------------------
    class _bone_transform:
        __slots__ = ('rotation', 'position')
        
        def __init__(self, rotation: mathutils.Quaternion, position: mathutils.Vector) -> None:
            self.rotation = rotation
            self.position = position

    class _bone:
        __slots__ = ('name', 'parent', 'local_transform', 'world_transform')

        def __init__(self, local_transform: XModelPartV14._bone_transform, parent: int = -1, name: str = '') -> None:
            self.name = name
            self.parent = parent
            self.local_transform = local_transform
            self.world_transform = copy.deepcopy(local_transform)

        def generate_world_transform_by_parent(self, parent: XModelPartV14._bone) -> None:
            self.world_transform.position = parent.world_transform.position + (parent.world_transform.rotation @ self.local_transform.position)        
            self.world_transform.rotation = parent.world_transform.rotation @ self.local_transform.rotation

    # --------------------------------------------------------------------------------------------

    __slots__ = ('name', 'model_type', 'bones')

    def __init__(self) -> None:
        self.name = ''
        self.model_type = 0
        self.bones = []
    
    def load(self, xmodel_part: str) -> bool:
        self.name = os.path.basename(xmodel_part)
        self.model_type = self.name[-1]
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

                    # read raw bone data
                    raw_bone_data = file_io.read_fmt(file, 'B3f3h', collections.namedtuple('raw_bone_data', 'parent, px, py, pz, rx, ry, rz'))
                    
                    qx = raw_bone_data.rx / self.ROTATION_DIVISOR
                    qy = raw_bone_data.ry / self.ROTATION_DIVISOR
                    qz = raw_bone_data.rz / self.ROTATION_DIVISOR
                    qw = math.sqrt((1 - (qx ** 2) - (qy ** 2) - (qz ** 2)))

                    # generate rotation
                    rotation = mathutils.Quaternion((qw, qx, qy, qz))

                    # generate positioon
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

                    file.read(24) # padding

                    current_bone = self.bones[bone_index]
                    current_bone.name = bone_name

                    # set viewmodel positions
                    if self.model_type == XModelType.VIEWHANDS and  bone_name in self.VIEWHANDS_BONE_POSITIONS:
                        local_viewmodel_position = self.VIEWHANDS_BONE_POSITIONS[bone_name]
                        world_viewmodel_position = copy.deepcopy(local_viewmodel_position)
                        current_bone.local_transform.position = local_viewmodel_position / 2.54
                        current_bone.world_transform.position = world_viewmodel_position / 2.54

                    # transform bones by their parents to the correct place
                    if current_bone.parent > -1:
                        parent_bone = self.bones[current_bone.parent]
                        current_bone.generate_world_transform_by_parent(parent_bone)

                return True

        except:
            log.error_log(traceback.print_exc())
            return False

"""
XModelPartV25 represents xmodelpart structure for CoD4
"""
class XModelPartV25:
    
    PATH = 'xmodelparts'
    VERSION = 25
    ROTATION_DIVISOR = 32768.0

    # --------------------------------------------------------------------------------------------
    class _bone_transform:
        __slots__ = ('rotation', 'position')
        
        def __init__(self, rotation: mathutils.Quaternion, position: mathutils.Vector) -> None:
            self.rotation = rotation
            self.position = position

    class _bone:
        __slots__ = ('name', 'parent', 'local_transform', 'world_transform')

        def __init__(self, local_transform: XModelPartV25._bone_transform, parent: int = -1, name: str = '') -> None:
            self.name = name
            self.parent = parent
            self.local_transform = local_transform
            self.world_transform = copy.deepcopy(local_transform)

        def generate_world_transform_by_parent(self, parent: XModelPartV25._bone) -> None:
            self.world_transform.position = parent.world_transform.position + (parent.world_transform.rotation @ self.local_transform.position)        
            self.world_transform.rotation = parent.world_transform.rotation @ self.local_transform.rotation

    # --------------------------------------------------------------------------------------------

    __slots__ = ('name', 'model_type', 'bones')

    def __init__(self) -> None:
        self.name = ''
        self.model_type = 0
        self.bones = []
    
    def load(self, xmodel_part: str) -> bool:
        self.name = os.path.basename(xmodel_part)
        self.model_type = self.name[-1]
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

                    # read raw bone data
                    raw_bone_data = file_io.read_fmt(file, 'B3f3h', collections.namedtuple('raw_bone_data', 'parent, px, py, pz, rx, ry, rz'))
                    
                    qx = raw_bone_data.rx / self.ROTATION_DIVISOR
                    qy = raw_bone_data.ry / self.ROTATION_DIVISOR
                    qz = raw_bone_data.rz / self.ROTATION_DIVISOR
                    qw = math.sqrt((1 - (qx ** 2) - (qy ** 2) - (qz ** 2)))

                    # generate rotation
                    rotation = mathutils.Quaternion((qw, qx, qy, qz))

                    # generate positioon
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

                    # transform bones by their parents to the correct place
                    if current_bone.parent > -1:
                        parent_bone = self.bones[current_bone.parent]
                        current_bone.generate_world_transform_by_parent(parent_bone)

                return True

        except:
            log.error_log(traceback.print_exc())
            return False