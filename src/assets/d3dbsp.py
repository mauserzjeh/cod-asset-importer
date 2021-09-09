from __future__ import annotations

import collections
import json
import os
import re
import struct
import traceback

from utils import enum
from utils import file_io
from utils import log
from utils import vector

class LUMPS(metaclass = enum.BaseEnum):
    MATERIALS = 0
    LIGHTMAPS = 1
    LIGHT_GRID_HASH = 2
    LIGHT_GRID_VALUES = 3
    PLANES = 4
    BRUSHSIDES = 5
    BRUSHES = 6
    TRIANGLESOUPS = 7
    VERTICES = 8
    TRIANGLES = 9
    CULL_GROUPS = 10
    CULL_GROUP_INDEXES = 11
    PORTAL_VERTS = 17
    OCCLUDER = 18
    OCCLUDER_PLANES = 19
    OCCLUDER_EDGES = 20
    OCCLUDER_INDEXES = 21
    AABB_TREES = 22
    CELLS = 23
    PORTALS = 24
    NODES = 25
    LEAFS = 26
    LEAF_BRUSHES = 27
    COLLISION_VERTS = 29
    COLLISION_EDGES = 30
    COLLISION_TRIS = 31
    COLLISION_BORDERS = 32
    COLLISION_PARTS = 33
    COLLISION_AABBS = 34
    MODELS = 35
    VISIBILITY = 36
    ENTITIES = 37
    PATHS = 38

class LUMPSIZES(metaclass = enum.BaseEnum):
    MATERIALS = '64sQ'
    TRIANGLESOUPS = '2HI2HI'
    VERTICES = '3f3f4B2f32x'
    TRIANGLES = '3H'

class ENTITY_KEYS(metaclass = enum.BaseEnum):
    MODEL = 'model'
    ANGLES = 'angles'
    ORIGIN = 'origin'
    MODELSCALE = 'modelscale'

class D3DBSP:

    PATH = 'maps'
    MAGIC = 'IBSP'
    VERSION = 4

    # --------------------------------------------------------------------------------------------
    class _uv:
        def __init__(self, u: float = 0.0, v: float = 0.0) -> None:
            self.u = u
            self.v = v

        def to_tuple(self) -> tuple:
            return (self.u, self.v)
    
    class _color:
        def __init__(self, red: int = 0, green: int = 0, blue: int = 0, alpha: int = 0) -> None:
            self.red = red
            self.green = green
            self.blue = blue
            self.alpha = alpha
        
        def to_tuple(self) -> tuple:
            return (self.red, self.green, self.blue, self.alpha)
    
    class _lump:
        def __init__(self, length: int = 0, offset: int = 0) -> None:
            self.length = length
            self.offset = offset

    class _material:
        def __init__(self, name: str = '', flag: int = 0) -> None:
            self.name = name
            self.flag = flag

        def read(self, file) -> None:
            material = file_io.read_fmt(file, LUMPSIZES.MATERIALS, collections.namedtuple('material', 'name, flag'))
            self.name = material.name.decode('ascii')
            self.flag = material.flag

    class _trianglesoup:
        def __init__(self, material_id: int = 0, draw_order: int = 0, vertices_offset: int = 0, vertices_length: int = 0, triangles_offset: int = 0, triangles_length: int = 0) -> None:
            self.material_id = material_id
            self.draw_order = draw_order
            self.vertices_offset = vertices_offset
            self.vertices_length = vertices_length
            self.triangles_offset = triangles_offset
            self.triangles_length = triangles_length

        def read(self, file) -> None:
            trianglesoup = file_io.read_fmt(file, LUMPSIZES.TRIANGLESOUPS, collections.namedtuple('trianglesoup', 'material_id, draw_order, vertices_offset, vertices_length, triangles_length, triangles_offset'))
            self.material_id = trianglesoup.material_id
            self.draw_order = trianglesoup.draw_order
            self.vertices_offset = trianglesoup.vertices_offset
            self.vertices_length = trianglesoup.vertices_length
            self.triangles_offset = trianglesoup.triangles_offset
            self.triangles_length = trianglesoup.triangles_length


    class _vertex:
        def __init__(self) -> None:
            self.position = vector.Vector3()
            self.normal = vector.Vector3
            self.color = D3DBSP._color()
            self.uv = D3DBSP._uv()

        def read(self, file) -> None:
            vertex = file_io.read_fmt(file, LUMPSIZES.VERTICES, collections.namedtuple('vertex', 'px, py, pz, nx, ny, nz, red, green, blue, alpha, u, v'))
            self.position = vector.Vector3(
                vertex.px,
                vertex.py,
                vertex.pz
            )
            self.normal = vector.Vector3(
                vertex.nx,
                vertex.ny,
                vertex.nz
            )
            self.color = D3DBSP._color(
                vertex.red / 255,
                vertex.green / 255,
                vertex.blue / 255,
                vertex.alpha / 255
            )
            self.uv = D3DBSP._uv(
                vertex.u,
                vertex.v
            )

    class _entity:
        def __init__(self, name: str = '', angles: vector.Vector3 = vector.Vector3, origin: vector.Vector3 = vector.Vector3, scale: float = 1.0) -> None:
            self.name = name
            self.angles = angles
            self.origin = origin
            self.scale = scale

    class _surface:
        def __init__(self, material: str, triangles: list[tuple], vertices: dict[int, D3DBSP._vertex]) -> None:
            self.material = material
            self.vertices = vertices
            self.triangles = triangles

    # --------------------------------------------------------------------------------------------

    def __init__(self) -> None:
        self.name = ''
        self.surfaces = []
        self.entities = []
        self.materials = []

    def _read_lumps(self, file) -> list[_lump]:
        lumps = []
        for _ in range(39):
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
        entity_string = entity_data.rstrip(b'\x00').decode('ascii')
        entity_string = f'[\n{entity_string}]'
        entity_string = re.sub(r'\}\n\{\n', '},\n{\n', entity_string)
        entity_string = re.sub(r'\"\n\"', '",\n"', entity_string)
        entity_string = re.sub(r'\"[^\n]\"', '":"', entity_string)
        entity_json = json.loads(entity_string)

        for entity in entity_json:
            if ENTITY_KEYS.MODEL not in entity:
                continue
            
            name = entity[ENTITY_KEYS.MODEL]
            model = re.match('^xmodel\/(.*)', name)
            if model:
                name = model.group(1)

            angles = vector.Vector3()
            if ENTITY_KEYS.ANGLES in entity:
                a = entity[ENTITY_KEYS.ANGLES].split(' ')
                angles.x = float(a[0])
                angles.y = float(a[1])
                angles.z = float(a[2])

            origin = vector.Vector3()
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


    def load(self, asset_path: str, map_name: str) -> bool:
        self.name = map_name
        filepath = os.path.join(asset_path, self.PATH, map_name)
        try:
            with open(filepath, 'rb') as file:
                header = file_io.read_fmt(file, '4si', collections.namedtuple('header', 'magic, version'))
                header_magic = header.magic.decode('ascii')
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

                for trianglesoup in trianglesoups:
                    surface_material = self.materials[trianglesoup.material_id].name
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
            traceback.print_exc()
            return False
