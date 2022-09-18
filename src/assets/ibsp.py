from __future__ import annotations

import collections
import json
import traceback
import mathutils
import os
import re
import struct

from .. utils import (
    enum,
    file_io,
    log,
)

"""
Lump constants
"""
class LUMPS(metaclass = enum.BaseEnum):
    # CoD1 & CoD:UO
    v59_MATERIALS = 0
    v59_TRIANGLESOUPS = 6
    v59_VERTICES = 7
    v59_TRIANGLES = 8
    v59_ENTITIES  = 29

    # CoD2
    v4_MATERIALS = 0
    v4_TRIANGLESOUPS = 7
    v4_VERTICES = 8
    v4_TRIANGLES = 9
    v4_ENTITIES = 37

"""
Lump size fmt strings
"""
class LUMPSIZES(metaclass = enum.BaseEnum):
    # CoD1 & CoD:UO
    v59_MATERIALS = '64sQ'
    v59_TRIANGLESOUPS = '2HI2HI'
    v59_VERTICES = '3f2f8x3f4B'
    v59_TRIANGLES = '3H'

    # CoD2
    v4_MATERIALS = '64sQ'
    v4_TRIANGLESOUPS = '2HI2HI'
    v4_VERTICES = '3f3f4B2f32x'
    v4_TRIANGLES = '3H'

"""
Entity key constants
"""
class ENTITY_KEYS(metaclass = enum.BaseEnum):
    MODEL = 'model'
    ANGLES = 'angles'
    ORIGIN = 'origin'
    MODELSCALE = 'modelscale'

"""
IBSP version constants
"""
class VERSIONS(metaclass = enum.BaseEnum):
    COD1 = 0x3B # 59
    COD2 = 0x04 # 4

"""
IBSP class represents an IBSP structure
"""
class IBSP:

    MAGIC = 'IBSP'

    # --------------------------------------------------------------------------------------------
    class _uv:
        __slots__ = ('u', 'v')

        def __init__(self, u: float = 0.0, v: float = 0.0) -> None:
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
    
    class _lump:
        __slots__ = ('length', 'offset')

        def __init__(self, length: int = 0, offset: int = 0) -> None:
            self.length = length
            self.offset = offset

    class _material:
        __slots__ = ('name', 'flag')

        def __init__(self, name: str = '', flag: int = 0) -> None:
            self.name = name
            self.flag = flag

        def read(self, file: bytes, version: int) -> None:
            if version == VERSIONS.COD1:
                material = file_io.read_fmt(file, LUMPSIZES.v59_MATERIALS, collections.namedtuple('material', 'name, flag'))
            else:
                material = file_io.read_fmt(file, LUMPSIZES.v4_MATERIALS, collections.namedtuple('material', 'name, flag'))

            self.name = material.name.rstrip(b'\x00').decode('utf-8')
            self.flag = material.flag

    class _trianglesoup:
        __slots__ = ('material_idx', 'draw_order', 'vertices_offset', 'vertices_length', 'triangles_offset', 'triangles_length')

        def __init__(self, material_idx: int = 0, draw_order: int = 0, vertices_offset: int = 0, vertices_length: int = 0, triangles_offset: int = 0, triangles_length: int = 0) -> None:
            self.material_idx = material_idx
            self.draw_order = draw_order
            self.vertices_offset = vertices_offset
            self.vertices_length = vertices_length
            self.triangles_offset = triangles_offset
            self.triangles_length = triangles_length

        def read(self, file: bytes, version: int) -> None:
            if version == VERSIONS.COD1:
                trianglesoup = file_io.read_fmt(file, LUMPSIZES.v59_TRIANGLESOUPS, collections.namedtuple('trianglesoup', 'material_idx, draw_order, vertices_offset, vertices_length, triangles_length, triangles_offset'))
            else:
                trianglesoup = file_io.read_fmt(file, LUMPSIZES.v4_TRIANGLESOUPS, collections.namedtuple('trianglesoup', 'material_idx, draw_order, vertices_offset, vertices_length, triangles_length, triangles_offset'))


            self.material_idx = trianglesoup.material_idx
            self.draw_order = trianglesoup.draw_order
            self.vertices_offset = trianglesoup.vertices_offset
            self.vertices_length = trianglesoup.vertices_length
            self.triangles_offset = trianglesoup.triangles_offset
            self.triangles_length = trianglesoup.triangles_length


    class _vertex:
        __slots__ = ('position', 'normal', 'color', 'uv')

        def __init__(self) -> None:
            self.position = mathutils.Vector()
            self.normal = mathutils.Vector()
            self.color = IBSP._color()
            self.uv = IBSP._uv()

        def read(self, file: bytes, version: int) -> None:
            if version == VERSIONS.COD1:
                vertex = file_io.read_fmt(file, LUMPSIZES.v59_VERTICES, collections.namedtuple('vertex', 'px, py, pz, u, v, nx, ny, nz, red, green, blue, alpha'))
            else:
                vertex = file_io.read_fmt(file, LUMPSIZES.v4_VERTICES, collections.namedtuple('vertex', 'px, py, pz, nx, ny, nz, red, green, blue, alpha, u, v'))


            self.position = mathutils.Vector((
                vertex.px,
                vertex.py,
                vertex.pz
            ))
            self.normal = mathutils.Vector((
                vertex.nx,
                vertex.ny,
                vertex.nz
            ))
            self.color = IBSP._color(
                vertex.red / 255,
                vertex.green / 255,
                vertex.blue / 255,
                vertex.alpha / 255
            )

            # flip UV
            self.uv = IBSP._uv(
                vertex.u,
                1-vertex.v
            )

    class _entity:
        __slots__ = ('name', 'angles', 'origin', 'scale')

        def __init__(self, name: str = '', angles: mathutils.Vector = None, origin: mathutils.Vector = None, scale: mathutils.Vector = None) -> None:
            self.name = name
            self.angles = angles
            self.origin = origin
            self.scale = scale

    class _surface:
        __slots__ = ('material', 'vertices', 'triangles')

        def __init__(self, material: str, triangles: list[tuple], vertices: dict[int, IBSP._vertex]) -> None:
            self.material = material
            self.vertices = vertices
            self.triangles = triangles

    # --------------------------------------------------------------------------------------------

    __slots__ = ('name', 'version', 'surfaces', 'entities', 'materials')

    def __init__(self) -> None:
        self.name = ''
        self.version = 0
        self.surfaces = []
        self.entities = []
        self.materials = []

    def _read_lumps(self, file: bytes) -> list[_lump]:
        lumps = []
        for _ in range(39):
            lump = file_io.read_fmt(file, '2I', collections.namedtuple('lump', 'length, offset'))
            lumps.append(self._lump(lump.length, lump.offset))

        return lumps

    def _read_materials(self, file: bytes, version: int, lumps: list[_lump]) -> list[_material]:
        if version == VERSIONS.COD1:
            materials_lump = lumps[LUMPS.v59_MATERIALS]
            materials_size = LUMPSIZES.v59_MATERIALS
        else:
            materials_lump = lumps[LUMPS.v4_MATERIALS]
            materials_size = LUMPSIZES.v4_MATERIALS

        materials = []
        file.seek(materials_lump.offset, os.SEEK_SET)
        for _ in range(0, materials_lump.length, struct.calcsize(materials_size)):
            material = self._material()
            material.read(file, version)
            materials.append(material)
        
        return materials

    def _read_trianglesoups(self, file: bytes, version: int, lumps: list[_lump]) -> list[_trianglesoup]:
        if version == VERSIONS.COD1:
            trianglesoups_lump = lumps[LUMPS.v59_TRIANGLESOUPS]
            trianglesoups_size = LUMPSIZES.v59_TRIANGLESOUPS
        else:
            trianglesoups_lump = lumps[LUMPS.v4_TRIANGLESOUPS]
            trianglesoups_size = LUMPSIZES.v4_TRIANGLESOUPS

        trianglesoups = []
        file.seek(trianglesoups_lump.offset, os.SEEK_SET)
        for _ in range(0, trianglesoups_lump.length, struct.calcsize(trianglesoups_size)):
            trianglesoup = self._trianglesoup()
            trianglesoup.read(file, version)
            trianglesoups.append(trianglesoup)

        return trianglesoups

    def _read_vertices(self, file: bytes, version: int, lumps: list[_lump]) -> list[_vertex]:
        if version == VERSIONS.COD1:
            vertices_lump = lumps[LUMPS.v59_VERTICES]
            vertices_size = LUMPSIZES.v59_VERTICES
        else:
            vertices_lump = lumps[LUMPS.v4_VERTICES]
            vertices_size = LUMPSIZES.v4_VERTICES

        vertices = []
        file.seek(vertices_lump.offset, os.SEEK_SET)    
        for _ in range(0, vertices_lump.length, struct.calcsize(vertices_size)):
            vertex = self._vertex()
            vertex.read(file, version)
            vertices.append(vertex)

        return vertices

    def _read_triangles(self, file: bytes, version: int, lumps: list[_lump]) -> list[tuple]:
        if version == VERSIONS.COD1:
            triangles_lump = lumps[LUMPS.v59_TRIANGLES]
            triangles_size = LUMPSIZES.v59_TRIANGLES
        else:
            triangles_lump = lumps[LUMPS.v4_TRIANGLES]
            triangles_size = LUMPSIZES.v4_TRIANGLES

        triangles = []
        file.seek(triangles_lump.offset, os.SEEK_SET)
        for _ in range(0, triangles_lump.length, struct.calcsize(triangles_size)):
            triangle = file_io.read_fmt(file, triangles_size)
            triangles.append(triangle)

        return triangles

    def _parse_transform(self, transform: str, default_value: float) -> tuple:
        t = transform.split(' ')
        if len(t) == 3:
            return [float(t[0]), float(t[1]), float(t[2])]
        elif len(t) == 1:
            if t[0] == '':
                return [default_value, default_value, default_value]
            else:
                return [float(t[0]), float(t[0]), float(t[0])]

        return [default_value, default_value, default_value]

    def _read_entities(self, file: bytes, version: int, lumps: list[_lump]) -> list[_entity]:
        if version == VERSIONS.COD1:
            entities_lump = lumps[LUMPS.v59_ENTITIES]
        else:
            entities_lump = lumps[LUMPS.v4_ENTITIES]

        entities = []
        file.seek(entities_lump.offset, os.SEEK_SET)
        entity_data = file.read(entities_lump.length)
        
        # create a valid json string and parse it
        entity_string = entity_data.rstrip(b'\x00').decode('utf-8')
        entity_string = f'[\n{entity_string}]'
        entity_string = re.sub(r'\}\n\{\n', '},\n{\n', entity_string)
        entity_string = re.sub(r'\"\n\"', '",\n"', entity_string)
        entity_string = re.sub(r'\"[^\n]\"', '":"', entity_string)
        entity_string = entity_string.replace('\\', '/')
        entity_json = json.loads(entity_string)

        for entity in entity_json:
            if ENTITY_KEYS.MODEL not in entity:
                continue
            
            # skip everything that is not a valid xmodel 
            name = entity[ENTITY_KEYS.MODEL]
            valid = re.match(r'^xmodel\/(.*)', name)
            if not valid:
                continue

            name = valid.group(1)

            angles = mathutils.Vector()
            if ENTITY_KEYS.ANGLES in entity:
                a = self._parse_transform(entity[ENTITY_KEYS.ANGLES], 0)
                angles.x = a[0]
                angles.y = a[1]
                angles.z = a[2]

            origin = mathutils.Vector()
            if ENTITY_KEYS.ORIGIN in entity:
                o = self._parse_transform(entity[ENTITY_KEYS.ORIGIN], 0)
                origin.x = o[0]
                origin.y = o[1]
                origin.z = o[2]

            scale = mathutils.Vector((1.0, 1.0, 1.0))
            if ENTITY_KEYS.MODELSCALE in entity:
                s = self._parse_transform(entity[ENTITY_KEYS.MODELSCALE], 1)
                scale.x = s[0]
                scale.y = s[1]
                scale.z = s[2]

            e = self._entity(name, angles, origin, scale)
            entities.append(e)

        return entities

    def load(self, map: str) -> bool:
        self.name = os.path.splitext(os.path.basename(map))[0]
        try:
            with open(map, 'rb') as file:
                header = file_io.read_fmt(file, '4si', collections.namedtuple('header', 'magic, version'))
                header_magic = header.magic.decode('utf-8')
                if header_magic != self.MAGIC or header.version not in VERSIONS:
                    log.info_log(f"{header_magic}{header.version} is not supported")
                    return False

                self.version = header.version

                lumps = self._read_lumps(file) # lumps
                self.materials = self._read_materials(file, self.version, lumps) # materials
                trianglesoups = self._read_trianglesoups(file, self.version, lumps) # trianglesoups
                vertices = self._read_vertices(file, self.version, lumps) # vertices
                triangles = self._read_triangles(file, self.version, lumps) # triangles
                self.entities = self._read_entities(file, self.version, lumps) # entities

                # create surfaces from triangles and vertices
                for trianglesoup in trianglesoups:
                    surface_material = self.materials[trianglesoup.material_idx].name
                    surface_triangles = []
                    surface_vertices = {}
                    
                    triangle_count = int(trianglesoup.triangles_length / 3)
                    for i in range(triangle_count):
                        triangle_id = int(trianglesoup.triangles_offset / 3 + i)
                        triangle = triangles[triangle_id]

                        vertex1_id = int(trianglesoup.vertices_offset + triangle[0])
                        vertex2_id = int(trianglesoup.vertices_offset + triangle[1])
                        vertex3_id = int(trianglesoup.vertices_offset + triangle[2])

                        surface_triangles.append((vertex1_id, vertex2_id, vertex3_id))

                        for j in (vertex1_id, vertex2_id, vertex3_id):
                            surface_vertices[j] = vertices[j]

                    self.surfaces.append(self._surface(surface_material, surface_triangles, surface_vertices))

                return True

        except:
            log.error_log(traceback.print_exc())
            return False