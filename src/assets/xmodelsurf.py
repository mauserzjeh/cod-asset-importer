from __future__ import annotations

import collections
import mathutils
import os
import traceback

from . import ( 
    xmodel,
    xmodelpart
)
from .. utils import (
    file_io,
    log,
)

"""
XModelSurf class represents an xmodelsurf structure
"""
class XModelSurf:
    
    PATH = 'xmodelsurfs'
    RIGGED = 65535

    # --------------------------------------------------------------------------------------------
    class _weight:
        __slots__ = ('bone', 'influence')

        def __init__(self, bone: int, influence: float) -> None:
            self.bone = bone
            self.influence = influence
    
    class _uv:
        __slots__ = ('u', 'v')

        def __init__(self, u: float, v: float) -> None:
            self.u = u
            self.v = v

        def to_tuple(self) -> tuple:
            return (self.u, self.v)
    
    class _color:
        __slots__ = ('red', 'green', 'blue', 'alpha')

        def __init__(self, red: float = 0.0, green: float = 0.0, blue: float = 0.0, alpha: float = 0.0) -> None:
            self.red = red
            self.green = green
            self.blue = blue
            self.alpha = alpha
        
        def to_tuple(self) -> tuple:
            return (self.red, self.green, self.blue, self.alpha)
    
    class _vertex:
        __slots__ = ('normal', 'color', 'uv', 'bone', 'position', 'weights')

        def __init__(self, normal: mathutils.Vector , color: XModelSurf._color, uv: XModelSurf._uv, bone: int, position: mathutils.Vector, weights: list[XModelSurf._weight]) -> None:
            self.normal = normal
            self.color = color
            self.uv = uv
            self.bone = bone
            self.position = position
            self.weights = weights
    
    class _surface:
        __slots__ = ('vertices', 'triangles')

        def __init__(self, vertices: list[XModelSurf._vertex], triangles: list[tuple]) -> None:
            self.vertices = vertices
            self.triangles = triangles

    # --------------------------------------------------------------------------------------------

    __slots__ = ('name', 'version', 'surfaces')

    def __init__(self) -> None:
        self.name = ''
        self.version = 0
        self.surfaces = []

    def _load_v14(self, file: bytes, xmodel_part: xmodelpart.XModelPart = None) -> bool:
        surface_count = file_io.read_ushort(file)
        for _ in range(surface_count):
            surface_header = file_io.read_fmt(file, 'x2H2xH', collections.namedtuple('surface_header', 'vertex_count, triangle_count, default_bone'))

            default_bone = 0
            if surface_header.default_bone == self.RIGGED:
                file.read(4)
            else:
                default_bone = surface_header.default_bone
            
            triangles = []
            while(True):
                idx_count = file_io.read_uchar(file)

                idx1 = file_io.read_ushort(file)
                idx2 = file_io.read_ushort(file)
                idx3 = file_io.read_ushort(file)

                if idx1 != idx2 and idx1 != idx3 and idx2 != idx3:
                    triangles.append([idx1, idx2, idx3])
                
                v = 0
                i = 3
                while i < idx_count:
                    idx4 = idx3
                    idx5 = file_io.read_ushort(file)

                    if idx4 != idx2 and idx4 != idx5 and idx2 != idx5:
                        triangles.append([idx4, idx2, idx5])

                    v = i + 1
                    if v >= idx_count:
                        break

                    idx2 = idx5
                    idx3 = file_io.read_ushort(file)

                    if idx4 != idx2 and idx4 != idx3 and idx2 != idx3:
                        triangles.append([idx4, idx2, idx3])

                    i = v + 1

                if len(triangles) >= surface_header.triangle_count:
                    break
            
            bone_weight_counts = [0] * surface_header.vertex_count
            vertices = []
            for i in range(surface_header.vertex_count):

                vn = file_io.read_fmt(file, '3f')
                vertex_normal = mathutils.Vector((vn[0], vn[1], vn[2]))

                uv = file_io.read_fmt(file, '2f')
                vertex_uv = self._uv(uv[0], 1 - uv[1]) # flip UV

                weight_count = 0
                vertex_bone = default_bone

                if surface_header.default_bone == self.RIGGED:
                    weight_count = file_io.read_ushort(file)
                    vertex_bone = file_io.read_ushort(file)

                vp = file_io.read_fmt(file, '3f')
                vertex_position = mathutils.Vector((vp[0], vp[1], vp[2]))

                if weight_count != 0:
                    file.read(4) # padding

                bone_weight_counts[i] = weight_count

                # if the xmodel is a skeletal mesh then transform vertices
                # by their bones so they wont be distorted
                if xmodel_part != None:
                    xmodel_part_bone = xmodel_part.bones[vertex_bone]

                    vertex_position.rotate(xmodel_part_bone.world_transform.rotation)
                    vertex_position += xmodel_part_bone.world_transform.position

                    vertex_normal.rotate(xmodel_part_bone.world_transform.rotation)

                vertices.append(self._vertex(
                    normal=vertex_normal,
                    color=self._color(1.0, 1.0, 1.0, 1.0),
                    uv=vertex_uv,
                    bone=vertex_bone,
                    position=vertex_position,
                    weights=[self._weight(vertex_bone, 1.0)]
                ))

            for i in range(surface_header.vertex_count):
                for _ in range(0, bone_weight_counts[i]):
                    weight_bone = file_io.read_ushort(file)
                    
                    file.read(12) # padding

                    weight_influence = file_io.read_float(file)
                    weight_influence = float(weight_influence / self.RIGGED)

                    vertices[i].weights[0].influence -= weight_influence
                    vertices[i].weights.append(self._weight(weight_bone, weight_influence))

            self.surfaces.append(self._surface(vertices, triangles))

        return True

    def _load_v20(self, file: bytes, xmodel_part: xmodelpart.XModelPart = None) -> bool:
        surface_count = file_io.read_ushort(file)
        for _ in range(surface_count):
            surface_header = file_io.read_fmt(file, 'x3H', collections.namedtuple('surface_header', 'vertex_count, triangle_count, default_bone'))

            default_bone = 0
            if surface_header.default_bone == self.RIGGED:
                file.read(2) #padding
            else:
                default_bone = surface_header.default_bone

            vertices = []
            for _ in range(surface_header.vertex_count):

                vn = file_io.read_fmt(file, '3f')
                vertex_normal = mathutils.Vector((vn[0], vn[1], vn[2]))

                clr = file_io.read_fmt(file, '4B')
                vertex_color = self._color(
                    clr[0] / 255,
                    clr[1] / 255,
                    clr[2] / 255,
                    clr[3] / 255
                )

                uv = file_io.read_fmt(file, '2f')
                vertex_uv = self._uv(uv[0], 1 - uv[1]) # flip UV

                file.read(24) # padding

                weight_count = 0
                vertex_bone = default_bone

                if surface_header.default_bone == self.RIGGED:
                    weight_count = file_io.read_uchar(file)
                    vertex_bone = file_io.read_ushort(file)

                vp = file_io.read_fmt(file, '3f')
                vertex_position = mathutils.Vector((vp[0], vp[1], vp[2]))

                vertex_weights = []
                vertex_weights.append(self._weight(vertex_bone, 1.0))

                if weight_count > 0:
                    file.read(1) # padding

                    for _ in range(weight_count):
                        weight_bone = file_io.read_ushort(file)
                        file.read(12) # padding
                        weight_influence = file_io.read_ushort(file)
                        weight_influence = float(weight_influence / self.RIGGED)

                        vertex_weights[0].influence -= weight_influence
                        vertex_weights.append(self._weight(weight_bone, weight_influence))

                # if the xmodel is a skeletal mesh then transform vertices
                # by their bones so they wont be distorted
                if xmodel_part != None:
                    xmodel_part_bone = xmodel_part.bones[vertex_bone]
                    
                    vertex_position.rotate(xmodel_part_bone.world_transform.rotation)
                    vertex_position += xmodel_part_bone.world_transform.position

                    vertex_normal.rotate(xmodel_part_bone.world_transform.rotation)

                vertices.append(self._vertex(
                    normal=vertex_normal,
                    color=vertex_color,
                    uv=vertex_uv,
                    bone=vertex_bone,
                    position=vertex_position,
                    weights=vertex_weights
                ))

            triangles = []
            for _ in range(surface_header.triangle_count):
                triangle = file_io.read_fmt(file, '3H')
                triangles.append(triangle)

            self.surfaces.append(self._surface(vertices, triangles))

        return True

    def _load_v25(self, file: bytes) -> bool:
        surface_count = file_io.read_ushort(file)
        for _ in range(surface_count):
            surface_header = file_io.read_fmt(file, '3x3H', collections.namedtuple('surface_header', 'vertex_count, triangle_count, vertex_count2'))
            if surface_header.vertex_count != surface_header.vertex_count2:
                while True:
                    p = file_io.read_ushort(file)
                    if p == 0:
                        break
                
                file.read(2) # padding
            else:
                file.read(4) # padding
            
            vertices = []
            for _ in range(surface_header.vertex_count):

                vn = file_io.read_fmt(file, '3f')
                vertex_normal = mathutils.Vector((vn[0], vn[1], vn[2]))

                clr = file_io.read_fmt(file, '4B')
                vertex_color = self._color(
                    clr[0] / 255,
                    clr[1] / 255,
                    clr[2] / 255,
                    clr[3] / 255
                )

                uv = file_io.read_fmt(file, '2f')
                vertex_uv = self._uv(uv[0], 1 - uv[1]) # flip UV

                file.read(24) # padding

                weight_count = 0
                vertex_bone = 0
                if surface_header.vertex_count != surface_header.vertex_count2:
                    weight_count = file_io.read_uchar(file)
                    vertex_bone = file_io.read_ushort(file)

                vp = file_io.read_fmt(file, '3f')
                vertex_position = mathutils.Vector((vp[0], vp[1], vp[2]))

                vertex_weights = []
                vertex_weights.append(self._weight(vertex_bone, 1.0))

                if weight_count > 0:
                    for _ in range(weight_count):
                        weight_bone = file_io.read_ushort(file)
                        weight_influence = file_io.read_ushort(file)
                        weight_influence = float(weight_influence / self.RIGGED)
                        vertex_weights[0].influence -= weight_influence
                        vertex_weights.append(self._weight(weight_bone, weight_influence))
                
                vertices.append(self._vertex(
                    normal=vertex_normal,
                    color=vertex_color,
                    uv=vertex_uv,
                    bone=vertex_bone,
                    position=vertex_position,
                    weights=vertex_weights
                ))

            triangles = []
            for _ in range(surface_header.triangle_count):
                triangle = file_io.read_fmt(file, '3H')
                triangles.append(triangle)

            self.surfaces.append(self._surface(vertices, triangles))

        return True

    def load(self, xmodel_surf: str, xmodel_part: xmodelpart.XModelPart = None) -> bool:
        self.name = os.path.basename(xmodel_surf)
        try:
            with open(xmodel_surf, 'rb') as file:
                version = file_io.read_ushort(file)
                if version not in xmodel.VERSIONS:
                    log.info_log(f'xmodelsurf version {version} is not supported')
                    return False

                self.version = version
                
                if self.version == xmodel.VERSIONS.COD1:
                    return self._load_v14(file, xmodel_part)

                elif self.version == xmodel.VERSIONS.COD2:
                    return self._load_v20(file, xmodel_part)

                elif self.version == xmodel.VERSIONS.COD4:
                    return self._load_v25(file)

                return False # not gonna reach this part, just in case...
        except:
            log.error_log(traceback.print_exc())
            return False