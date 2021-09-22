import os
import bpy
import bmesh

from .. assets import (
    d3dbsp,
    material,
    xmodel,
    xmodelpart,
    xmodelsurf
)
from .. utils import log

def import_d3dbsp(assetpath: str, filepath: str) -> bool:
    D3DBSP = d3dbsp.D3DBSP()
    if(not D3DBSP.load(filepath)):
        log.error_log(f"Error loading d3dbsp: {os.path.basename(filepath)}")
        return False

    map_null = bpy.data.objects.new(D3DBSP.name, None)
    bpy.context.scene.collection.objects.link(map_null)

    map_geometry_null = bpy.data.objects.new(f"{D3DBSP.name}_geometry", None)
    bpy.context.scene.collection.objects.link(map_geometry_null)
    map_geometry_null.parent = map_null

    #TODO import materials

    # import surfaces
    for surface in D3DBSP.surfaces:
        name = f"{D3DBSP.name}_geometry"

        mesh = bpy.data.meshes.new(name)
        obj = bpy.data.objects.new(name, mesh)
        obj.parent = map_geometry_null

        bpy.context.scene.collection.objects.link(obj)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        mesh_data = bpy.context.object.data
        bm = bmesh.new()

        surface_uvs = []
        surface_vertex_colors = []

        for triangle in surface.triangles:
            
            vertex1 = surface.vertices[triangle[0]]
            vertex2 = surface.vertices[triangle[2]]
            vertex3 = surface.vertices[triangle[1]]

            v1 = bm.verts.new(vertex1.position.to_tuple())
            v2 = bm.verts.new(vertex2.position.to_tuple())
            v3 = bm.verts.new(vertex3.position.to_tuple())

            triangle_uvs = []
            triangle_uvs.append(vertex1.uv.to_tuple())
            triangle_uvs.append(vertex2.uv.to_tuple())
            triangle_uvs.append(vertex3.uv.to_tuple())
            surface_uvs.append(triangle_uvs)

            triangle_vertex_colors = []
            triangle_vertex_colors.append(vertex1.color.to_tuple())
            triangle_vertex_colors.append(vertex2.color.to_tuple())
            triangle_vertex_colors.append(vertex3.color.to_tuple())
            surface_vertex_colors.append(triangle_vertex_colors)

            bm.verts.ensure_lookup_table()
            bm.verts.index_update()

            bm.faces.new((v1, v2, v3))
            bm.faces.ensure_lookup_table()
            bm.faces.index_update()

        uv_layer = bm.loops.layers.uv.new()
        vertex_color_layer = bm.loops.layers.color.new()

        for face, uv, vertex_color in zip(bm.faces, surface_uvs, surface_vertex_colors):
            for loop, uv_data, vertex_color_data in zip(face.loops, uv, vertex_color):
                loop[uv_layer].uv = uv_data
                loop[vertex_color_layer] = vertex_color_data

        bm.to_mesh(mesh_data)
        bm.free()


    return True

    
def import_xmodel(assetpath: str, filepath: str) -> bool:
    XMODEL = xmodel.XModel()
    if(not XMODEL.load(filepath)):
        log.error_log(f"Error loading xmodel: {os.path.basename(filepath)}")
        return False

    #TODO
    return True

def _import_material(assetpath: str, material_name: str) -> bool:
    MATERIAL = material.Material()
    material_file = os.path.join(assetpath, MATERIAL.PATH, material_name)
    if(not MATERIAL.load(material_file)):
        log.error_log(f"Error loading material: {material_name}")
        return False
    
    #TODO
    return True