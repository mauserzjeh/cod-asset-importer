from __future__ import annotations

import os
import bpy
import bmesh
import mathutils
import math

from .. assets import (
    d3dbsp as d3dbsp_asset,
    material as material_asset,
    texture as texture_asset,
    xmodel as xmodel_asset,
    xmodelpart as xmodelpart_asset,
    xmodelsurf as xmodelsurf_asset
)

from .. utils import (
    blender as blenderutils,
    data as datautils,
    log
)


def import_d3dbsp(assetpath: str, filepath: str) -> bool:
    D3DBSP = d3dbsp_asset.D3DBSP()
    if not D3DBSP.load(filepath):
        log.error_log(f"Error loading d3dbsp: {os.path.basename(filepath)}")
        return False

    map_null = bpy.data.objects.new(D3DBSP.name, None)
    bpy.context.scene.collection.objects.link(map_null)

    map_geometry_null = bpy.data.objects.new(f"{D3DBSP.name}_geometry", None)
    bpy.context.scene.collection.objects.link(map_geometry_null)
    map_geometry_null.parent = map_null

    map_entities_null = bpy.data.objects.new(f"{D3DBSP.name}_entities", None)
    bpy.context.scene.collection.objects.link(map_entities_null)
    map_entities_null.parent = map_null

    # import materials
    for material in D3DBSP.materials:
        if not bpy.data.materials.get(material.name):
            _import_material(assetpath, material.name)

    # import surfaces
    for surface in D3DBSP.surfaces:
        name = f"{D3DBSP.name}_geometry"

        mesh = bpy.data.meshes.new(name)
        obj = bpy.data.objects.new(name, mesh)
        obj.parent = map_geometry_null
        obj.active_material = bpy.data.materials.get(surface.material)

        bpy.context.scene.collection.objects.link(obj)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        mesh_data = bpy.context.object.data
        bm = bmesh.new()

        surface_uvs = []
        surface_vertex_colors = []
        surface_normals = []

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

            triangle_normals = []
            triangle_normals.append(vertex1.normal.to_tuple())
            triangle_normals.append(vertex2.normal.to_tuple())
            triangle_normals.append(vertex3.normal.to_tuple())
            surface_normals.append(triangle_normals)

            bm.verts.ensure_lookup_table()
            bm.verts.index_update()

            bm.faces.new((v1, v2, v3))
            bm.faces.ensure_lookup_table()
            bm.faces.index_update()

        uv_layer = bm.loops.layers.uv.new()
        vertex_color_layer = bm.loops.layers.color.new()
        vertex_normal_buffer = []

        for face, uv, color, normal in zip(bm.faces, surface_uvs, surface_vertex_colors, surface_normals):
            for loop, uv_data, color_data, normal_data in zip(face.loops, uv, color, normal):
                loop[uv_layer].uv = uv_data
                loop[vertex_color_layer] = color_data
                vertex_normal_buffer.append(normal_data)

        bm.to_mesh(mesh_data)
        bm.free()

        mesh.create_normals_split()

        for loop_idx, loop in enumerate(mesh.loops):
            mesh.loops[loop_idx].normal = vertex_normal_buffer[loop_idx]

        mesh.validate(clean_customdata=False)

        custom_normals = [0.0] * len(mesh.loops) * 3
        mesh.loops.foreach_get('normal', custom_normals)

        polygon_count = len(mesh.polygons)
        mesh.polygons.foreach_set('use_smooth', [True] * polygon_count)

        custom_normals = tuple(zip(*(iter(custom_normals),) * 3))
        mesh.normals_split_custom_set(custom_normals)
        mesh.use_auto_smooth = True

    # entities
    unique_entities = {}
    for entity in D3DBSP.entities:
        if entity.name in unique_entities:
            entity_null = blenderutils.copy_object_hierarchy(unique_entities[entity.name])[0]
            bpy.ops.object.select_all(action='DESELECT')
        else:
            entity_path = os.path.join(assetpath, xmodel_asset.XModel.PATH, entity.name)
            entity_null = import_xmodel(assetpath, entity_path, True)
            
        if entity_null:
            entity_null.parent = map_entities_null
            entity_null.location = entity.origin.to_tuple()

            rot_x, rot_y, rot_z = datautils.fix_rotation(entity.angles.x, entity.angles.y, entity.angles.z)

            entity_null.rotation_euler = (
                math.radians(rot_x), 
                math.radians(rot_y), 
                math.radians(rot_z)
            )
            entity_null.scale = (entity.scale, entity.scale, entity.scale)

            if entity.name not in unique_entities:
                unique_entities[entity.name] = entity_null

    return True

    
def import_xmodel(assetpath: str, filepath: str, import_skeleton: bool) -> bpy.types.Object | bool:
    XMODEL = xmodel_asset.XModel()
    if not XMODEL.load(filepath):
        log.error_log(f"Error loading xmodel: {os.path.basename(filepath)}")
        return False

    xmodel = XMODEL.lods[0]

    XMODELPART = xmodelpart_asset.XModelPart()
    xmodel_part = os.path.join(assetpath, xmodelpart_asset.XModelPart.PATH, xmodel.name)
    if not XMODELPART.load(xmodel_part):
        log.error_log(f"Error loading xmodelpart: {xmodel.name}")
        XMODELPART = None

    XMODELSURF = xmodelsurf_asset.XModelSurf()
    xmodel_surf = os.path.join(assetpath, xmodelsurf_asset.XModelSurf.PATH, xmodel.name)
    if not XMODELSURF.load(xmodel_surf, XMODELPART):
        log.error_log(f"Error loading xmodelsurf: {xmodel.name}")
        return False

    xmodel_null = bpy.data.objects.new(XMODEL.name, None)
    bpy.context.scene.collection.objects.link(xmodel_null)

    mesh_objects = []

    # import materials
    for material in xmodel.materials:
        if not bpy.data.materials.get(material):
            _import_material(assetpath, material)

    # create mesh
    for i, surface in enumerate(XMODELSURF.surfaces):
        mesh = bpy.data.meshes.new(XMODELSURF.name)
        obj = bpy.data.objects.new(XMODELSURF.name, mesh)
        obj.active_material = bpy.data.materials.get(xmodel.materials[i])

        bpy.context.scene.collection.objects.link(obj)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)


        mesh_data = bpy.context.object.data
        bm = bmesh.new()
        vertex_weight_layer = bm.verts.layers.deform.new()

        surface_uvs = []
        surface_vertex_colors = []
        surface_normals = []

        for triangle in surface.triangles:
            
            vertex1 = surface.vertices[triangle[0]]
            vertex2 = surface.vertices[triangle[2]]
            vertex3 = surface.vertices[triangle[1]]

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

            triangle_normals = []
            triangle_normals.append(vertex1.normal.to_tuple())
            triangle_normals.append(vertex2.normal.to_tuple())
            triangle_normals.append(vertex3.normal.to_tuple())
            surface_normals.append(triangle_normals)

            v1 = bm.verts.new(vertex1.position.to_tuple())
            v2 = bm.verts.new(vertex2.position.to_tuple())
            v3 = bm.verts.new(vertex3.position.to_tuple())

            bm.verts.ensure_lookup_table()
            bm.verts.index_update()

            verts_assoc = {
                v1: vertex1,
                v2: vertex2,
                v3: vertex3
            }

            for bvert, svert in verts_assoc.items():
                for weight in svert.weights:
                    bm.verts[bvert.index][vertex_weight_layer][weight.bone] = weight.influence

            bm.faces.new((v1, v2, v3))
            bm.faces.ensure_lookup_table()
            bm.faces.index_update()

        uv_layer = bm.loops.layers.uv.new()
        vertex_color_layer = bm.loops.layers.color.new()
        vertex_normal_buffer = []

        for face, uv, color, normal in zip(bm.faces, surface_uvs, surface_vertex_colors, surface_normals):
            for loop, uv_data, color_data, normal_data in zip(face.loops, uv, color, normal):
                loop[uv_layer].uv = uv_data
                loop[vertex_color_layer] = color_data
                vertex_normal_buffer.append(normal_data)

        bm.to_mesh(mesh_data)
        bm.free()

        # set normals        
        mesh.create_normals_split()

        for loop_idx, loop in enumerate(mesh.loops):
            mesh.loops[loop_idx].normal = vertex_normal_buffer[loop_idx]

        mesh.validate(clean_customdata=False)

        # fill default normals
        custom_normals = [0.0] * len(mesh.loops) * 3
        mesh.loops.foreach_get('normal', custom_normals)

        polygon_count = len(mesh.polygons)
        mesh.polygons.foreach_set('use_smooth', [True] * polygon_count)

        custom_normals = tuple(zip(*(iter(custom_normals),) * 3))
        mesh.normals_split_custom_set(custom_normals)
        mesh.use_auto_smooth = True

        mesh_objects.append(obj)

    # create skeleton
    skeleton = None
    if import_skeleton and XMODELPART != None and len(XMODELPART.bones) > 1:
        armature = bpy.data.armatures.new(f"{xmodel.name}_armature")
        armature.display_type = 'STICK'

        skeleton = bpy.data.objects.new(f"{xmodel.name}_skeleton", armature)
        skeleton.parent = xmodel_null
        skeleton.show_in_front = True
        bpy.context.scene.collection.objects.link(skeleton)
        bpy.context.view_layer.objects.active = skeleton
        bpy.ops.object.mode_set(mode='EDIT')

        bone_matrices = {}

        for bone in XMODELPART.bones:

            new_bone = armature.edit_bones.new(bone.name)
            new_bone.tail = (0, 0.05, 0)

            matrix_rotation = bone.local_transform.rotation.to_matrix().to_4x4()
            matrix_transform = mathutils.Matrix.Translation(bone.local_transform.position)

            matrix = matrix_transform @ matrix_rotation
            bone_matrices[bone.name] = matrix

            if bone.parent > -1:
                new_bone.parent = armature.edit_bones[bone.parent]

        bpy.context.view_layer.objects.active = skeleton
        bpy.ops.object.mode_set(mode='POSE')

        for bone in skeleton.pose.bones:
            bone.matrix_basis.identity()
            bone.matrix = bone_matrices[bone.name]
        
        bpy.ops.pose.armature_apply()

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=2)
        bone_visualizer = bpy.context.active_object
        bone_visualizer.data.name = bone_visualizer.name = 'bone_visualizer'
        bone_visualizer.use_fake_user = True

        bpy.context.view_layer.active_layer_collection.collection.objects.unlink(bone_visualizer)
        bpy.context.view_layer.objects.active = skeleton

        maxs = [0,0,0]
        mins = [0,0,0]

        for bone in armature.bones:
            for i in range(3):
                maxs[i] = max(maxs[i], bone.head_local[i])
                mins[i] = min(mins[i], bone.head_local[i])

        dimensions = []
        for i in range(3):
            dimensions.append(maxs[i] - mins[i])

        length = max(0.001, (dimensions[0] + dimensions[1] + dimensions[2]) / 600)
        bpy.ops.object.mode_set(mode='EDIT')
        for bone in [armature.edit_bones[b.name] for b in XMODELPART.bones]:
            bone.tail = bone.head + (bone.tail - bone.head).normalized() * length
            skeleton.pose.bones[bone.name].custom_shape = bone_visualizer

        bpy.ops.object.mode_set(mode='OBJECT')

    for mesh_object in mesh_objects:
        if skeleton == None:
            mesh_object.parent = xmodel_null
            continue

        for bone in XMODELPART.bones:
            mesh_object.vertex_groups.new(name=bone.name)

        mesh_object.parent = skeleton
        modifier = mesh_object.modifiers.new('armature_rig', 'ARMATURE')
        modifier.object = skeleton
        modifier.use_bone_envelopes = False
        modifier.use_vertex_groups = True


    
    bpy.context.view_layer.update()
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    return xmodel_null

def _import_material(assetpath: str, material_name: str) -> bpy.types.Material | bool:
    MATERIAL = material_asset.Material()
    material_file = os.path.join(assetpath, material_asset.Material.PATH, material_name)
    if not MATERIAL.load(material_file):
        log.error_log(f"Error loading material: {material_name}")
        return False
    
    material = bpy.data.materials.new(MATERIAL.name)
    material.use_nodes = True

    nodes = material.node_tree.nodes
    links = material.node_tree.links

    output_node = None
    for node in nodes:
        if node.type != 'OUTPUT_MATERIAL':
            nodes.remove(node)
            continue

        if node.type == 'OUTPUT_MATERIAL' and output_node == None:
            output_node = node

    if output_node == None:
        output_node = nodes.new('ShaderNodeOutputMaterial')

    output_node.location = (300, 0)

    mix_shader_node = nodes.new('ShaderNodeMixShader')
    mix_shader_node.location = (100, 0)
    links.new(mix_shader_node.outputs['Shader'], output_node.inputs['Surface'])

    transparent_bsdf_node = nodes.new('ShaderNodeBsdfTransparent')
    transparent_bsdf_node.location = (-200, 100)
    links.new(transparent_bsdf_node.outputs['BSDF'], mix_shader_node.inputs[1])

    principled_bsdf_node = nodes.new('ShaderNodeBsdfPrincipled')
    principled_bsdf_node.location = (-200, 0)
    principled_bsdf_node.width = 200
    links.new(principled_bsdf_node.outputs['BSDF'], mix_shader_node.inputs[2])

    for i, t in enumerate(MATERIAL.textures):
        texture = bpy.data.textures.get(t.name)
        if texture == None:
            texture = _import_texture(assetpath, t.name)
            if texture == False:
                continue

        texture_node = nodes.new('ShaderNodeTexImage')
        texture_node.label = t.type
        texture_node.location = (-700, -250 * i)
        texture_node.image = texture.image

        if t.type == texture_asset.TEXTURE_TYPE.COLORMAP:
            links.new(texture_node.outputs['Color'], principled_bsdf_node.inputs['Base Color'])
            links.new(texture_node.outputs['Alpha'], mix_shader_node.inputs['Fac'])
        elif t.type == texture_asset.TEXTURE_TYPE.SPECULARMAP:
            links.new(texture_node.outputs['Color'], principled_bsdf_node.inputs['Specular'])
        elif t.type == texture_asset.TEXTURE_TYPE.NORMALMAP:
            bump_node = nodes.new('ShaderNodeBump')
            bump_node.location = (-450, -500)
            links.new(texture_node.outputs['Color'], bump_node.inputs['Height'])
            links.new(bump_node.outputs['Normal'], principled_bsdf_node.inputs['Normal'])

    textcoord_node = nodes.new('ShaderNodeTexCoord')
    textcoord_node.location = (-1000, -150)
    for node in nodes:
        if node.type == 'TEX_IMAGE':
            links.new(textcoord_node.outputs['UV'], node.inputs['Vector'])

    return material

def _import_texture(assetpath: str, texture_name: str) -> bpy.types.Texture | bool:
    TEXTURE = texture_asset.Texture()
    texture_file = os.path.join(assetpath, texture_asset.Texture.PATH, texture_name + '.iwi')
    if not TEXTURE.load(texture_file):
        log.error_log(f"Error loading texture: {texture_name}")
        return False
    
    image = bpy.data.images.new(texture_name, TEXTURE.width, TEXTURE.height, alpha=True)
    image.pixels = TEXTURE.texture_data

    texture = bpy.data.textures.new(texture_name, type='IMAGE')
    texture.image = image

    return texture