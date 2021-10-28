from __future__ import annotations

import collections
import mathutils
import os
import traceback

from . import xmodelpart
from .. utils import (
    file_io,
    log,
)


class XModelSurf:

    PATH = 'xmodelsurfs'
    VERSION = 20
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

        def __init__(self, red: int, green: int, blue: int, alpha: int) -> None:
            self.red = red
            self.green = green
            self.blue = blue
            self.alpha = alpha
        
        def to_tuple(self) -> tuple:
            return (self.red, self.green, self.blue, self.alpha)
    
    class _vertex:
        __slots__ = ('normal', 'color', 'uv', 'binormal', 'tangent', 'bone', 'position', 'weights')

        def __init__(self, normal: mathutils.Vector , color: XModelSurf._color, uv: XModelSurf._uv, binormal: mathutils.Vector, tangent: mathutils.Vector, bone: int, position: mathutils.Vector, weights: list[XModelSurf._weight]) -> None:
            self.normal = normal
            self.color = color
            self.uv = uv
            self.binormal = binormal
            self.tangent = tangent
            self.bone = bone
            self.position = position
            self.weights = weights
    
    class _surface:
        __slots__ = ('vertices', 'triangles')

        def __init__(self, vertices: list[XModelSurf._vertex], triangles: list[tuple]) -> None:
            self.vertices = vertices
            self.triangles = triangles

    # --------------------------------------------------------------------------------------------
    
    __slots__ = ('name', 'surfaces')

    def __init__(self) -> None:
        self.name = ''
        self.surfaces = []

    def load(self, xmodel_surf: str, xmodel_part: xmodelpart.XModelPart = None) -> bool:
        self.name = os.path.basename(xmodel_surf)
        try:
            with open(xmodel_surf, 'rb') as file:
                header = file_io.read_fmt(file, '2H', collections.namedtuple('header', 'version, surface_count'))
                if header.version != self.VERSION:
                    log.info_log(f'Xmodel version {header.version} is not supported!')
                    return False

                for _ in range(header.surface_count):
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
                        vertex_uv = self._uv(uv[0], 1 - uv[1])

                        bn = file_io.read_fmt(file, '3f')
                        vertex_binormal = mathutils.Vector((bn[0], bn[1], bn[2]))

                        tn = file_io.read_fmt(file, '3f')
                        vertex_tangent = mathutils.Vector((tn[0], tn[1], tn[2]))

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

                        if xmodel_part != None:
                            xmodel_part_bone = xmodel_part.bones[vertex_bone]
                            
                            vertex_position.rotate(xmodel_part_bone.world_transform.rotation)
                            vertex_position += xmodel_part_bone.world_transform.position

                            vertex_normal.rotate(xmodel_part_bone.world_transform.rotation)
                            vertex_tangent.rotate(xmodel_part_bone.world_transform.rotation)

                        vertices.append(self._vertex(
                            vertex_normal,
                            vertex_color,
                            vertex_uv,
                            vertex_binormal,
                            vertex_tangent,
                            vertex_bone,
                            vertex_position,
                            vertex_weights
                        ))

                    triangles = []
                    for _ in range(surface_header.triangle_count):
                        triangle = file_io.read_fmt(file, '3H')
                        triangles.append(triangle)


                    self.surfaces.append(self._surface(vertices,triangles))

                return True

        except:
            log.error_log(traceback.format_exc())
            return False