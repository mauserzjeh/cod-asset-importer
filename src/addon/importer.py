from __future__ import annotations

import os
import bpy
import bmesh
import mathutils
import math
import numpy
import time
import subprocess

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
    start_time_d3dbsp = time.monotonic()

    D3DBSP = d3dbsp_asset.D3DBSP()
    if not D3DBSP.load(filepath):
        log.error_log(f"Error loading d3dbsp: {os.path.basename(filepath)}")
        return False
    
    log.info_log(f"Loaded d3dbsp: {D3DBSP.name}")

    map_null = bpy.data.objects.new(D3DBSP.name, None)
    bpy.context.scene.collection.objects.link(map_null)

    map_geometry_null = bpy.data.objects.new(f"{D3DBSP.name}_geometry", None)
    bpy.context.scene.collection.objects.link(map_geometry_null)
    map_geometry_null.parent = map_null

    map_entities_null = bpy.data.objects.new(f"{D3DBSP.name}_entities", None)
    bpy.context.scene.collection.objects.link(map_entities_null)
    map_entities_null.parent = map_null

    # import materials
    start_time_materials = time.monotonic()
    log.info_log(f"Importing materials for {D3DBSP.name}...")
    failed_materials = []
    failed_textures = []
    for material in D3DBSP.materials:
        if not bpy.data.materials.get(material.name) and material.name not in failed_materials:
            if not _import_material(assetpath, material.name, failed_textures):
                failed_materials.append(material.name)
    done_time_materials = time.monotonic()
    log.info_log(f"Imported materials for {D3DBSP.name} in {round(done_time_materials - start_time_materials, 2)} seconds.")

    # import surfaces
    start_time_surfaces = time.monotonic()
    log.info_log(f"Creating surfaces for {D3DBSP.name}...")
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

        # set normals        
        mesh.create_normals_split()
        mesh.validate(clean_customdata=False)
        mesh.normals_split_custom_set(vertex_normal_buffer)

        polygon_count = len(mesh.polygons)
        mesh.polygons.foreach_set('use_smooth', [True] * polygon_count)
        mesh.use_auto_smooth = True

    done_time_surfaces = time.monotonic()
    log.info_log(f"Created surfaces for {D3DBSP.name} in {round(done_time_surfaces - start_time_surfaces, 2)} seconds.")

    # entities
    start_time_entities = time.monotonic()
    log.info_log(f"Importing entities for {D3DBSP.name}...")
    unique_entities = {}
    for entity in D3DBSP.entities:
        if entity.name in unique_entities:
            entity_null = blenderutils.copy_object_hierarchy(unique_entities[entity.name])[0]
            bpy.ops.object.select_all(action='DESELECT')
        else:
            entity_path = os.path.join(assetpath, xmodel_asset.XModel.PATH, entity.name)
            entity_null = import_xmodel(assetpath, entity_path, True, failed_materials, failed_textures)
            
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

    done_time_entities = time.monotonic()
    log.info_log(f"Imported entities for {D3DBSP.name} in {round(done_time_entities - start_time_entities,2)} seconds.")

    done_time_d3dbsp = time.monotonic()
    log.info_log(f"Imported d3dbsp: {D3DBSP.name} in {round(done_time_d3dbsp - start_time_d3dbsp, 2)} seconds.")

    return True

    
def import_xmodel(assetpath: str, filepath: str, import_skeleton: bool, failed_materials: list = None, failed_textures: list = None) -> bpy.types.Object | bool:
    start_time_xmodel = time.monotonic()
    
    XMODEL = xmodel_asset.XModel()
    if not XMODEL.load(filepath):
        log.error_log(f"Error loading xmodel: {os.path.basename(filepath)}")
        return False

    lod0 = XMODEL.lods[0]

    log.info_log(f"Loaded xmodel: {lod0.name}")

    XMODELPART = xmodelpart_asset.XModelPart()
    xmodel_part = os.path.join(assetpath, xmodelpart_asset.XModelPart.PATH, lod0.name)
    if not XMODELPART.load(xmodel_part):
        log.error_log(f"Error loading xmodelpart: {lod0.name}")
        XMODELPART = None

    XMODELSURF = xmodelsurf_asset.XModelSurf()
    xmodel_surf = os.path.join(assetpath, xmodelsurf_asset.XModelSurf.PATH, lod0.name)
    if not XMODELSURF.load(xmodel_surf, XMODELPART):
        log.error_log(f"Error loading xmodelsurf: {lod0.name}")
        return False

    xmodel_null = bpy.data.objects.new(XMODEL.name, None)
    bpy.context.scene.collection.objects.link(xmodel_null)

    mesh_objects = []

    # import materials
    start_time_materials = time.monotonic()
    log.info_log(f"Importing materials for {lod0.name}...")
    failed_materials = [] if failed_materials == None else failed_materials
    failed_textures = [] if failed_textures == None else failed_textures
    for material in lod0.materials:
        if not bpy.data.materials.get(material) and material not in failed_materials:
            if not _import_material(assetpath, material, failed_textures):
                failed_materials.append(material)

    done_time_materials = time.monotonic()
    log.info_log(f"Imported materials for {lod0.name} in {round(done_time_materials - start_time_materials, 2)} seconds.")

    # create mesh
    start_time_surfaces = time.monotonic()
    log.info_log(f"Creating surfaces for {lod0.name}...")
    for i, surface in enumerate(XMODELSURF.surfaces):
        mesh = bpy.data.meshes.new(XMODELSURF.name)
        obj = bpy.data.objects.new(XMODELSURF.name, mesh)
        obj.active_material = bpy.data.materials.get(lod0.materials[i])

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
        mesh.validate(clean_customdata=False)
        mesh.normals_split_custom_set(vertex_normal_buffer)

        polygon_count = len(mesh.polygons)
        mesh.polygons.foreach_set('use_smooth', [True] * polygon_count)
        mesh.use_auto_smooth = True

        mesh_objects.append(obj)

    done_time_surfaces = time.monotonic()
    log.info_log(f"Created surfaces for {lod0.name} in {round(done_time_surfaces - start_time_surfaces, 2)} seconds.")

    # create skeleton
    skeleton = None
    if import_skeleton and XMODELPART != None and len(XMODELPART.bones) > 1:
        start_time_skeleton = time.monotonic()
        log.info_log(f"Creating skeleton for {lod0.name}...")

        armature = bpy.data.armatures.new(f"{lod0.name}_armature")
        armature.display_type = 'STICK'

        skeleton = bpy.data.objects.new(f"{lod0.name}_skeleton", armature)
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

        done_time_skeleton = time.monotonic()
        log.info_log(f"Created skeleton for {lod0.name} in {round(done_time_skeleton - start_time_skeleton, 2)} seconds.")

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

    done_time_xmodel = time.monotonic()
    log.info_log(f"Imported xmodel: {lod0.name} in {round(done_time_xmodel - start_time_xmodel, 2)} seconds.")

    return xmodel_null

def _import_material(assetpath: str, material_name: str, failed_textures: list = None) -> bpy.types.Material | bool:
    start_time_material = time.monotonic()

    MATERIAL = material_asset.Material()
    material_file = os.path.join(assetpath, material_asset.Material.PATH, material_name)
    if not MATERIAL.load(material_file):
        log.error_log(f"Error loading material: {material_name}")
        return False

    log.info_log(f"Loaded material: {MATERIAL.name}")
    
    material = bpy.data.materials.new(MATERIAL.name)
    material.use_nodes = True
    material.blend_method = 'HASHED'
    material.shadow_method = 'HASHED'

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
        output_node = nodes.new(blenderutils.BLENDER_SHADERNODES.SHADERNODE_OUTPUTMATERIAL)

    output_node.location = (300, 0)

    mix_shader_node = nodes.new(blenderutils.BLENDER_SHADERNODES.SHADERNODE_MIXSHADER)
    mix_shader_node.location = (100, 0)
    links.new(mix_shader_node.outputs[blenderutils.BLENDER_SHADERNODES.OUTPUT_MIXSHADER_SHADER], output_node.inputs[blenderutils.BLENDER_SHADERNODES.INPUT_OUTPUTMATERIAL_SURFACE])

    transparent_bsdf_node = nodes.new(blenderutils.BLENDER_SHADERNODES.SHADERNODE_BSDFTRANSPARENT)
    transparent_bsdf_node.location = (-200, 100)
    links.new(transparent_bsdf_node.outputs[blenderutils.BLENDER_SHADERNODES.OUTPUT_BSDFTRANSPARENT_BSDF], mix_shader_node.inputs[blenderutils.BLENDER_SHADERNODES.INPUT_MIXSHADER_SHADER1])

    principled_bsdf_node = nodes.new(blenderutils.BLENDER_SHADERNODES.SHADERNODE_BSDFPRINCIPLED)
    principled_bsdf_node.location = (-200, 0)
    principled_bsdf_node.width = 200
    links.new(principled_bsdf_node.outputs[blenderutils.BLENDER_SHADERNODES.OUTPUT_BSDFTRANSPARENT_BSDF], mix_shader_node.inputs[blenderutils.BLENDER_SHADERNODES.INPUT_MIXSHADER_SHADER2])

    log.info_log(f"Importing textures and creating material for {MATERIAL.name}...")

    failed_textures = [] if failed_textures == None else failed_textures
    for i, t in enumerate(MATERIAL.textures):
        if t.name in failed_textures:
            continue

        texture_image = bpy.data.images.get(t.name)
        if texture_image == None:
            texture_image = import_texture(assetpath, t.name, t.type == texture_asset.TEXTURE_TYPE.NORMALMAP)
            if texture_image == False:
                failed_textures.append(t.name)
                continue

        texture_node = nodes.new(blenderutils.BLENDER_SHADERNODES.SHADERNODE_TEXIMAGE)
        texture_node.label = t.type
        texture_node.location = (-700, -255 * i)
        texture_node.image = texture_image

        if t.type == texture_asset.TEXTURE_TYPE.COLORMAP:
            links.new(texture_node.outputs[blenderutils.BLENDER_SHADERNODES.OUTPUT_TEXIMAGE_COLOR], principled_bsdf_node.inputs[blenderutils.BLENDER_SHADERNODES.INPUT_BSDFPRINCIPLED_BASECOLOR])
            links.new(texture_node.outputs[blenderutils.BLENDER_SHADERNODES.OUTPUT_TEXIMAGE_ALPHA], mix_shader_node.inputs[blenderutils.BLENDER_SHADERNODES.INPUT_MIXSHADER_FAC])
        elif t.type == texture_asset.TEXTURE_TYPE.SPECULARMAP:
            links.new(texture_node.outputs[blenderutils.BLENDER_SHADERNODES.OUTPUT_TEXIMAGE_COLOR], principled_bsdf_node.inputs[blenderutils.BLENDER_SHADERNODES.INPUT_BSDFPRINCIPLED_SPECULAR])
            texture_node.image.colorspace_settings.name = blenderutils.BLENDER_SHADERNODES.TEXIMAGE_COLORSPACE_LINEAR
            texture_node.location = (-700, -255)
        elif t.type == texture_asset.TEXTURE_TYPE.NORMALMAP:
            texture_node.image.colorspace_settings.name = blenderutils.BLENDER_SHADERNODES.TEXIMAGE_COLORSPACE_LINEAR
            texture_node.location = (-1900, -655)
            
            normal_map_node = nodes.new(blenderutils.BLENDER_SHADERNODES.SHADERNODE_NORMALMAP)
            normal_map_node.location = (-450, -650)
            normal_map_node.space = blenderutils.BLENDER_SHADERNODES.NORMALMAP_SPACE_TANGENT
            normal_map_node.inputs[blenderutils.BLENDER_SHADERNODES.INPUT_NORMALMAP_STRENGTH].default_value = 0.3
            links.new(normal_map_node.outputs[blenderutils.BLENDER_SHADERNODES.OUTPUT_NORMALMAP_NORMAL], principled_bsdf_node.inputs[blenderutils.BLENDER_SHADERNODES.INPUT_BSDFPRINCIPLED_NORMAL])

            combine_rgb_node = nodes.new(blenderutils.BLENDER_SHADERNODES.SHADERNODE_COMBINERGB)
            combine_rgb_node.location = (-650, -750)
            links.new(combine_rgb_node.outputs[blenderutils.BLENDER_SHADERNODES.OUTPUT_COMBINERGB_IMAGE], normal_map_node.inputs[blenderutils.BLENDER_SHADERNODES.INPUT_NORMALMAP_COLOR])

            math_sqrt_node = nodes.new(blenderutils.BLENDER_SHADERNODES.SHADERNODE_MATH)
            math_sqrt_node.location = (-850, -850)
            math_sqrt_node.operation = blenderutils.BLENDER_SHADERNODES.OPERATION_MATH_SQRT
            links.new(math_sqrt_node.outputs[blenderutils.BLENDER_SHADERNODES.OUTPUT_MATH_VALUE], combine_rgb_node.inputs[blenderutils.BLENDER_SHADERNODES.INPUT_COMBINERGB_B])

            math_subtract_node = nodes.new(blenderutils.BLENDER_SHADERNODES.SHADERNODE_MATH)
            math_subtract_node.location = (-1050, -850)
            math_subtract_node.operation = blenderutils.BLENDER_SHADERNODES.OPERATION_MATH_SUBTRACT
            links.new(math_subtract_node.outputs[blenderutils.BLENDER_SHADERNODES.OUTPUT_MATH_VALUE], math_sqrt_node.inputs[blenderutils.BLENDER_SHADERNODES.INPUT_MATH_SQRT_VALUE])

            math_subtract_node2 = nodes.new(blenderutils.BLENDER_SHADERNODES.SHADERNODE_MATH)
            math_subtract_node2.location = (-1250, -950)
            math_subtract_node2.operation = blenderutils.BLENDER_SHADERNODES.OPERATION_MATH_SUBTRACT
            math_subtract_node2.inputs[blenderutils.BLENDER_SHADERNODES.INPUT_MATH_SUBTRACT_VALUE1].default_value = 1.0
            links.new(math_subtract_node2.outputs[blenderutils.BLENDER_SHADERNODES.OUTPUT_MATH_VALUE], math_subtract_node.inputs[blenderutils.BLENDER_SHADERNODES.INPUT_MATH_SUBTRACT_VALUE1])

            math_power_node = nodes.new(blenderutils.BLENDER_SHADERNODES.SHADERNODE_MATH)
            math_power_node.location = (-1250, -750)
            math_power_node.operation = blenderutils.BLENDER_SHADERNODES.OPERATION_MATH_POWER
            math_power_node.inputs[blenderutils.BLENDER_SHADERNODES.INPUT_MATH_POWER_EXPONENT].default_value = 2.0
            links.new(math_power_node.outputs[blenderutils.BLENDER_SHADERNODES.OUTPUT_MATH_VALUE], math_subtract_node.inputs[blenderutils.BLENDER_SHADERNODES.INPUT_MATH_SUBTRACT_VALUE2])

            math_power_node2 = nodes.new(blenderutils.BLENDER_SHADERNODES.SHADERNODE_MATH)
            math_power_node2.location = (-1500, -950)
            math_power_node2.operation = blenderutils.BLENDER_SHADERNODES.OPERATION_MATH_POWER
            math_power_node2.inputs[blenderutils.BLENDER_SHADERNODES.INPUT_MATH_POWER_EXPONENT].default_value = 2.0
            links.new(math_power_node2.outputs[blenderutils.BLENDER_SHADERNODES.OUTPUT_MATH_VALUE], math_subtract_node2.inputs[blenderutils.BLENDER_SHADERNODES.INPUT_MATH_SUBTRACT_VALUE2])
            links.new(texture_node.outputs[blenderutils.BLENDER_SHADERNODES.OUTPUT_TEXIMAGE_ALPHA], math_power_node2.inputs[blenderutils.BLENDER_SHADERNODES.INPUT_MATH_POWER_BASE])

            separate_rgb_node = nodes.new(blenderutils.BLENDER_SHADERNODES.SHADERNODE_SEPARATERGB)
            separate_rgb_node.location = (-1500, -450)
            links.new(separate_rgb_node.outputs[blenderutils.BLENDER_SHADERNODES.OUTPUT_SEPARATERGB_G], combine_rgb_node.inputs[blenderutils.BLENDER_SHADERNODES.INPUT_COMBINERGB_G])
            links.new(separate_rgb_node.outputs[blenderutils.BLENDER_SHADERNODES.OUTPUT_SEPARATERGB_G], math_power_node.inputs[blenderutils.BLENDER_SHADERNODES.INPUT_MATH_POWER_BASE])
            links.new(texture_node.outputs[blenderutils.BLENDER_SHADERNODES.OUTPUT_TEXIMAGE_COLOR], separate_rgb_node.inputs[blenderutils.BLENDER_SHADERNODES.INPUT_SEPARATERGB_IMAGE])
            links.new(texture_node.outputs[blenderutils.BLENDER_SHADERNODES.OUTPUT_TEXIMAGE_ALPHA], math_power_node2.inputs[blenderutils.BLENDER_SHADERNODES.INPUT_MATH_POWER_BASE])
            links.new(texture_node.outputs[blenderutils.BLENDER_SHADERNODES.OUTPUT_TEXIMAGE_ALPHA], combine_rgb_node.inputs[blenderutils.BLENDER_SHADERNODES.INPUT_COMBINERGB_R])




    done_time_material = time.monotonic()
    log.info_log(f"Imported material {MATERIAL.name} in {round(done_time_material - start_time_material, 2)} seconds.")

    return material

def import_texture(assetpath: str, texture_name: str, normal_map: bool) -> bpy.types.Texture | bool:
    start_time_texture = time.monotonic()

    TEXTURE = texture_asset.Texture()

    texture_file = os.path.join(assetpath, texture_asset.Texture.PATH, texture_name)

    # if no .dds exists then try to convert it on the fly via iwi2dds 
    if not os.path.isfile(texture_file + '.dds'):
        iwi2dds = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'bin', 'iwi2dds.exe'))
        if os.path.isfile(iwi2dds):
            result = subprocess.run((iwi2dds, '-i', texture_file + '.iwi'))
            if result.returncode != 0:
                log.error_log(result.stderr)

    try:
        # try to load .dds 
        texture_image = bpy.data.images.load(texture_file + '.dds', check_existing=True)
        log.info_log(f"Loaded texture: {texture_name}")
        pixels = texture_image.pixels

    except:

        # if error happens when loading the dds just fall back to .iwi parsing 
        if not TEXTURE.load(texture_file + '.iwi'):
            log.error_log(f"Error loading texture: {texture_name}")
            return False

        log.info_log(f"Loaded texture: {texture_name}")

        texture_image = bpy.data.images.new(texture_name, TEXTURE.width, TEXTURE.height, alpha=True)
        pixels = TEXTURE.texture_data
    

    # flip the image
    p = numpy.asarray(pixels)
    p.shape = (TEXTURE.height, TEXTURE.width, 4)
    p = numpy.flipud(p)

    texture_image.pixels = p.flatten().tolist()
    texture_image.file_format = 'TARGA'
    texture_image.pack()

    done_time_texture = time.monotonic()
    log.info_log(f"Imported texture: {texture_name} in {round(done_time_texture - start_time_texture, 2)} seconds.")

    return texture_image