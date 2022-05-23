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
    MATERIALS = 0
    TRIANGLESOUPS = 6
    VERTICES = 7
    TRIANGLES = 8
    ENTITIES  = 29

"""
Lump size fmt strings
"""
class LUMPSIZES(metaclass = enum.BaseEnum):
    MATERIALS = '64sQ'
    TRIANGLESOUPS = '2HI2HI'
    VERTICES = '3f3f4B2f8x'
    TRIANGLES = '3H'

"""
Entity key constants
"""
class ENTITY_KEYS(metaclass = enum.BaseEnum):
    MODEL = 'model'
    ANGLES = 'angles'
    ORIGIN = 'origin'
    MODELSCALE = 'modelscale'

"""
BSP class representing a BSP structure
"""
class BSP:

    MAGIC = 'IBSP'
    VERSION = 59

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

        def __init__(self, red: int = 0, green: int = 0, blue: int = 0, alpha: int = 0) -> None:
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

        def read(self, file) -> None:
            material = file_io.read_fmt(file, LUMPSIZES.MATERIALS, collections.namedtuple('material', 'name, flag'))
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

        def read(self, file) -> None:
            trianglesoup = file_io.read_fmt(file, LUMPSIZES.TRIANGLESOUPS, collections.namedtuple('trianglesoup', 'material_idx, draw_order, vertices_offset, vertices_length, triangles_length, triangles_offset'))
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
            self.color = BSP._color()
            self.uv = BSP._uv()

        def read(self, file) -> None:
            vertex = file_io.read_fmt(file, LUMPSIZES.VERTICES, collections.namedtuple('vertex', 'px, py, pz, nx, ny, nz, red, green, blue, alpha, u, v'))
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
            self.color = BSP._color(
                vertex.red / 255,
                vertex.green / 255,
                vertex.blue / 255,
                vertex.alpha / 255
            )

            # flip UV
            self.uv = BSP._uv(
                vertex.u,
                1-vertex.v
            )

    class _entity:
        __slots__ = ('name', 'angles', 'origin', 'scale')

        def __init__(self, name: str = '', angles: mathutils.Vector = None, origin: mathutils.Vector = None, scale: float = 1.0) -> None:
            self.name = name
            self.angles = angles
            self.origin = origin
            self.scale = scale

    class _surface:
        __slots__ = ('material', 'vertices', 'triangles')

        def __init__(self, material: str, triangles: list[tuple], vertices: dict[int, BSP._vertex]) -> None:
            self.material = material
            self.vertices = vertices
            self.triangles = triangles

    # --------------------------------------------------------------------------------------------

    __slots__ = ('name', 'surfaces', 'entities', 'materials')

    def __init__(self) -> None:
        self.name = ''
        self.surfaces = []
        self.entities = []
        self.materials = []

    def _read_lumps(self, file) -> list[_lump]:
        lumps = []
        for _ in range(32):
            lump = file_io.read_fmt(file, '2I', collections.namedtuple('lump', 'length, offset'))
            lumps.append(self._lump(lump.length, lump.offset))

        return lumps

    def _read_materials(self, file, materials_lump: _lump) -> list[_material]:
        materials = []
        file.seek(materials_lump.offset, os.SEEK_SET)
        for _ in range(0, materials_lump.length, struct.calcsize(LUMPSIZES.MATERIALS)):
            material = self._material()
            material.read(file)
            materials.append(material)
        
        return materials

    def _read_trianglesoups(self, file, trianglesoups_lump: _lump) -> list[_trianglesoup]:
        trianglesoups = []
        file.seek(trianglesoups_lump.offset, os.SEEK_SET)
        for _ in range(0, trianglesoups_lump.length, struct.calcsize(LUMPSIZES.TRIANGLESOUPS)):
            trianglesoup = self._trianglesoup()
            trianglesoup.read(file)
            trianglesoups.append(trianglesoup)

        return trianglesoups

    def _read_vertices(self, file, vertices_lump: _lump) -> list[_vertex]:
        vertices = []
        file.seek(vertices_lump.offset, os.SEEK_SET)    
        for _ in range(0, vertices_lump.length, struct.calcsize(LUMPSIZES.VERTICES)):
            vertex = self._vertex()
            vertex.read(file)
            vertices.append(vertex)

        return vertices

    def _read_triangles(self, file, triangles_lump: _lump) -> list[tuple]:
        triangles = []
        file.seek(triangles_lump.offset, os.SEEK_SET)
        for _ in range(0, triangles_lump.length, struct.calcsize(LUMPSIZES.TRIANGLES)):
            triangle = file_io.read_fmt(file, LUMPSIZES.TRIANGLES)
            triangles.append(triangle)

        return triangles

    def _read_entities(self, file, entities_lump: _lump) -> list[_entity]:
        entities = []
        file.seek(entities_lump.offset, os.SEEK_SET)
        entity_data = file.read(entities_lump.length)
        
        # create a valid json string and parse it
        entity_string = entity_data.rstrip(b'\x00').decode('utf-8')
        entity_string = f'[\n{entity_string}]'
        entity_string = re.sub(r'\}\n\{\n', '},\n{\n', entity_string)
        entity_string = re.sub(r'\"\n\"', '",\n"', entity_string)
        entity_string = re.sub(r'\"[^\n]\"', '":"', entity_string)
        entity_json = json.loads(entity_string)

        for entity in entity_json:
            if ENTITY_KEYS.MODEL not in entity:
                continue
            
            # skip everything that is not a valid xmodel 
            name = entity[ENTITY_KEYS.MODEL]
            valid = re.match('^xmodel\/(.*)', name)
            if not valid:
                continue

            name = valid.group(1)

            angles = mathutils.Vector()
            if ENTITY_KEYS.ANGLES in entity:
                a = entity[ENTITY_KEYS.ANGLES].split(' ')
                angles.x = float(a[0])
                angles.y = float(a[1])
                angles.z = float(a[2])

            origin = mathutils.Vector()
            if ENTITY_KEYS.ORIGIN in entity:
                o = entity[ENTITY_KEYS.ORIGIN].split(' ')
                origin.x = float(o[0])
                origin.y = float(o[1])
                origin.z = float(o[2])

            scale = 1.0
            if ENTITY_KEYS.MODELSCALE in entity:
                scale = float(entity[ENTITY_KEYS.MODELSCALE])

            e = self._entity(name, angles, origin, scale)
            entities.append(e)

        return entities

    def load(self, map: str) -> bool:
        self.name = os.path.splitext(os.path.basename(map))[0]
        try:
            with open(map, 'rb') as file:
                header = file_io.read_fmt(file, '4si', collections.namedtuple('header', 'magic, version'))
                header_magic = header.magic.decode('utf-8')
                if header_magic != self.MAGIC and header.version != self.VERSION:
                    log.info_log(f"{header_magic}{header.version} is not supported")
                    return False

                # lumps
                lumps = self._read_lumps(file)

                # materials
                materials_lump = lumps[LUMPS.MATERIALS]
                self.materials = self._read_materials(file, materials_lump)
                
                # trianglesoups
                trianglesoups_lump = lumps[LUMPS.TRIANGLESOUPS]
                trianglesoups = self._read_trianglesoups(file, trianglesoups_lump)
                
                # vertices
                vertices_lump = lumps[LUMPS.VERTICES]
                vertices = self._read_vertices(file, vertices_lump)
                
                # triangles
                triangles_lump = lumps[LUMPS.TRIANGLES]
                triangles = self._read_triangles(file, triangles_lump)
               
                # entities
                entities_lump = lumps[LUMPS.ENTITIES]
                self.entities = self._read_entities(file, entities_lump)

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