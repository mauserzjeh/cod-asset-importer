from __future__ import annotations

import collections
import os
import traceback

from . import xmodelpart
from .. utils import (
    file_io,
    log,
    vector
)


class XModelSurf:

    PATH = 'xmodelsurfs'
    VERSION = 20
    RIGGED = 65535
    
    # --------------------------------------------------------------------------------------------
    class _weight:
        def __init__(self, bone: int, weight: int) -> None:
            self.bone = bone
            self.weight = weight
    
    class _uv:
        def __init__(self, u: float, v: float) -> None:
            self.u = u
            self.v = v

        def to_tuple(self) -> tuple:
            return (self.u, self.v)
    
    class _color:
        def __init__(self, red: int, green: int, blue: int, alpha: int) -> None:
            self.red = red
            self.green = green
            self.blue = blue
            self.alpha = alpha
        
        def to_tuple(self) -> tuple:
            return (self.red, self.green, self.blue, self.alpha)
    
    class _vertex:
        def __init__(self, normal: vector.Vector3 , color: XModelSurf._color, uv: XModelSurf._uv, binormal: vector.Vector3, tangent: vector.Vector3, bone: int, position: vector.Vector3, weights: list[XModelSurf._weight]) -> None:
            self.normal = normal
            self.color = color
            self.uv = uv
            self.binormal = binormal
            self.tangent = tangent
            self.bone = bone
            self.position = position
            self.weights = weights
    
    class _surface:
        def __init__(self, vertices: list[XModelSurf._vertex], triangles: list[tuple]) -> None:
            self.vertices = vertices
            self.triangles = triangles

    # --------------------------------------------------------------------------------------------
    
    def __init__(self) -> None:
        self.name = ''
        self.surfaces = []

    def load(self, asset_path: str, xmodel_surf_name: str, xmodel_part: xmodelpart.XModelPart = None) -> bool:
        self.name = xmodel_surf_name
        filepath = os.path.join(asset_path, self.PATH, xmodel_surf_name)
        try:
            with open(filepath, 'rb') as file:
                header = file_io.read_fmt(file, '2H', collections.namedtuple('header', 'version, surface_count'))
                if header.version != self.VERSION:
                    log.info_log(f'Xmodel version {header.version} is not supported!')
                    return False

                for j in range(header.surface_count):
                    surface_header = file_io.read_fmt(file, 'x3H', collections.namedtuple('surface_header', 'vertex_count, triangle_count, rigged'))

                    rigged = False
                    if surface_header.rigged == self.RIGGED:
                        rigged = True

                    if rigged:
                        file.read(2) #padding

                    vertices = []
                    for i in range(surface_header.vertex_count):

                        vn = file_io.read_fmt(file, '3f')
                        vertex_normal = vector.Vector3(vn[0], vn[1], vn[2])

                        clr = file_io.read_fmt(file, '4B')
                        vertex_color = self._color(
                            clr[0] / 255,
                            clr[1] / 255,
                            clr[2] / 255,
                            clr[3] / 255
                        )

                        uv = file_io.read_fmt(file, '2f')
                        vertex_uv = self._uv(uv[0], uv[1])

                        bn = file_io.read_fmt(file, '3f')
                        vertex_binormal = vector.Vector3(bn[0], bn[1], bn[2])

                        tn = file_io.read_fmt(file, '3f')
                        vertex_tangent = vector.Vector3(tn[0], tn[1], tn[2])

                        weight_count = 0
                        vertex_bone = 0
                        if rigged:
                            weight_count = file_io.read_uchar(file)
                            vertex_bone = file_io.read_ushort(file)

                        vp = file_io.read_fmt(file, '3f')
                        vertex_position = vector.Vector3(vp[0], vp[1], vp[2])

                        vertex_weights = []
                        if weight_count > 0:
                            file.read(1) # padding

                            for _ in range(weight_count):
                                weight_bone = file_io.read_ushort(file)
                                file.read(12) # padding
                                weight_weight = file_io.read_ushort(file)

                                vertex_weights.append(self._weight(weight_bone, weight_weight))

                        if xmodel_part != None:
                            xmodel_part_bone = xmodel_part.bones[vertex_bone]
                            
                            vertex_position = vertex_position.rotate_by_quaternion(xmodel_part_bone.world_transform.rotation)
                            vertex_position += xmodel_part_bone.world_transform.position

                            vertex_normal = vertex_normal.rotate_by_quaternion(xmodel_part_bone.world_transform.rotation)
                            vertex_tangent = vertex_tangent.rotate_by_quaternion(xmodel_part_bone.world_transform.rotation)

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
            traceback.print_exc()
            return False