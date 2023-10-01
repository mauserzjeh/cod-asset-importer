import bmesh
import bpy
import mathutils
import os
import traceback
from .cod_asset_importer import (
    IBSP_VERSIONS,
    XMODEL_VERSIONS,
    XMODEL_TYPES,
    LoadedModel,
    LoadedIbsp,
    LoadedMaterial,
    Loader,
    debug_log,
    error_log,
)
from .blender_utils import (
    BLENDER_SHADERNODES,
)
from . import (
    base_enum,
)


class Importer:
    def xmodel(self, loaded_model: LoadedModel) -> None:
        model_name = loaded_model.name()

        xmodel_null = bpy.data.objects.new(model_name, None)
        bpy.context.scene.collection.objects.link(xmodel_null)

        mesh_objects = []

        materials = loaded_model.materials()
        for material in materials:
            self.material(material)

        for i, surface in enumerate(loaded_model.surfaces()):
            mesh = bpy.data.meshes.new(model_name)
            obj = bpy.data.objects.new(model_name, mesh)

            # TODO
            # active_material = materials[i]
            # if loaded_model.version() == XMODEL_VERSIONS.V14:
            #     active_material = os.path.splitext(materials[i])[0]

            # obj.active_material = active_material

            bpy.context.scene.collection.objects.link(obj)
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)

            mesh_data = bpy.context.object.data
            bm = bmesh.new()
            vertex_weight_layer = bm.verts.layers.deform.new()

            surface_uvs = []
            surface_vertex_colors = []
            surface_normals = []

            vertices = surface.vertices()
            for triangle in surface.triangles():
                
                vertex1 = vertices[triangle[0]]
                vertex2 = vertices[triangle[2]]
                vertex3 = vertices[triangle[1]]

                triangle_uvs = []
                triangle_uvs.append(vertex1.uv())
                triangle_uvs.append(vertex2.uv())
                triangle_uvs.append(vertex3.uv())
                surface_uvs.append(triangle_uvs)

                triangle_vertex_colors = []
                triangle_vertex_colors.append(vertex1.color())
                triangle_vertex_colors.append(vertex2.color())
                triangle_vertex_colors.append(vertex3.color())
                surface_vertex_colors.append(triangle_vertex_colors)

                triangle_normals = []
                triangle_normals.append(vertex1.normal())
                triangle_normals.append(vertex2.normal())
                triangle_normals.append(vertex3.normal())
                surface_normals.append(triangle_normals)

                v1 = bm.verts.new(vertex1.position())
                v2 = bm.verts.new(vertex2.position())
                v3 = bm.verts.new(vertex3.position())

                bm.verts.ensure_lookup_table()
                bm.verts.index_update()

                verts_assoc = {
                    v1: vertex1,
                    v2: vertex2,
                    v3: vertex3
                }

                for bvert, svert in verts_assoc.items():
                    for weight in svert.weights():
                        bm.verts[bvert.index][vertex_weight_layer][weight.bone()] = weight.influence()

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

        loaded_bones = loaded_model.bones()
        skeleton = None
        # TODO 
        # if len(loaded_bones) > 0:

        #     armature = bpy.data.armatures.new(f"{model_name}_armature")
        #     armature.display_type = 'STICK'

        #     skeleton = bpy.data.objects.new(f"{model_name}_skeleton", armature)
        #     skeleton.parent = xmodel_null
        #     skeleton.show_in_front = True
        #     bpy.context.scene.collection.objects.link(skeleton)
        #     bpy.context.view_layer.objects.active = skeleton
        #     bpy.ops.object.mode_set(mode='EDIT')

        #     bone_matrices = {}

        #     for loaded_bone in loaded_bones:
        #         bone_name = loaded_bone.name()

        #         new_bone = armature.edit_bones.new(bone_name)
        #         new_bone.tail = (0, 0.05, 0)

        #         matrix_rotation = mathutils.Quaternion(loaded_bone.rotation()).to_matrix().to_4x4()
        #         matrix_transform = mathutils.Matrix.Translation(loaded_bone.position())

        #         matrix = matrix_transform @ matrix_rotation
        #         bone_matrices[bone_name] = matrix

        #         bone_parent = loaded_bone.parent()
        #         if bone_parent > -1:
        #             new_bone.parent = armature.edit_bones[bone_parent]

        #     bpy.context.view_layer.objects.active = skeleton
        #     bpy.ops.object.mode_set(mode='POSE')

        #     for bone in skeleton.pose.bones:
        #         bone.matrix_basis.identity()
        #         bone.matrix = bone_matrices[bone.name]

        #     bpy.ops.pose.armature_apply()
        #     bpy.context.view_layer.objects.active = skeleton

        #     maxs = [0,0,0]
        #     mins = [0,0,0]

        #     for bone in armature.bones:
        #         for i in range(3):
        #             maxs[i] = max(maxs[i], bone.head_local[i])
        #             mins[i] = min(mins[i], bone.head_local[i])

        #     dimensions = []
        #     for i in range(3):
        #         dimensions.append(maxs[i] - mins[i])

        #     length = max(0.001, (dimensions[0] + dimensions[1] + dimensions[2]) / 600)
        #     bpy.ops.object.mode_set(mode='EDIT')
        #     for bone in [armature.edit_bones[lb.name()] for lb in loaded_bones]:
        #         bone.tail = bone.head + (bone.tail - bone.head).normalized() * length

        #     bpy.ops.object.mode_set(mode='OBJECT')

        for mesh_object in mesh_objects:
            if skeleton == None:
                mesh_object.parent = xmodel_null
                continue

            for loaded_bone in loaded_bones:
                mesh_object.vertex_groups.new(name=loaded_bone.name())

            mesh_object.parent = skeleton
            modifier = mesh_object.modifiers.new('armature_rig', 'ARMATURE')
            modifier.object = skeleton
            modifier.use_bone_envelopes = False
            modifier.use_vertex_groups = True

        bpy.context.view_layer.update()
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')

                

    def ibsp(self, loaded_ibsp: LoadedIbsp) -> None:
        debug_log(loaded_ibsp.name())

    def material(self, loaded_material: LoadedMaterial) -> None:
        pass # TODO
        # if loaded_material.version() == XMODEL_VERSIONS.V14:
        #     self._import_material_v14(loaded_material)
        # else:
        #     self._import_material_v20_v25(loaded_material)

    def _import_material_v14(self, loaded_material: LoadedMaterial) -> None:
        pass

    def _import_material_v20_v25(self, loaded_material: LoadedMaterial) -> None:
        material_name = loaded_material.name()

        if bpy.data.materials.get(material_name):
            return

        material = bpy.data.materials.new(material_name)
        material.use_nodes = True
        material.blend_method = "HASHED"
        material.shadow_method = "HASHED"

        nodes = material.node_tree.nodes
        links = material.node_tree.links

        output_node = None

        for node in nodes:
            if node.type != "OUTPUT_MATERIAL":
                nodes.remove(node)
                continue

            if node.type == "OUTPUT_MATERIAL" and output_node == None:
                output_node = node

        if output_node == None:
            output_node = nodes.new(BLENDER_SHADERNODES.SHADERNODE_OUTPUTMATERIAL)

        output_node.location = (300, 0)

        mix_shader_node = nodes.new(BLENDER_SHADERNODES.SHADERNODE_MIXSHADER)
        mix_shader_node.location = (100, 0)
        links.new(
            mix_shader_node.outputs[BLENDER_SHADERNODES.OUTPUT_MIXSHADER_SHADER],
            output_node.inputs[BLENDER_SHADERNODES.INPUT_OUTPUTMATERIAL_SURFACE],
        )

        transparent_bsdf_node = nodes.new(
            BLENDER_SHADERNODES.SHADERNODE_BSDFTRANSPARENT
        )
        transparent_bsdf_node.location = (-200, 100)
        links.new(
            transparent_bsdf_node.outputs[
                BLENDER_SHADERNODES.OUTPUT_BSDFTRANSPARENT_BSDF
            ],
            mix_shader_node.inputs[BLENDER_SHADERNODES.INPUT_MIXSHADER_SHADER1],
        )

        principled_bsdf_node = nodes.new(BLENDER_SHADERNODES.SHADERNODE_BSDFPRINCIPLED)
        principled_bsdf_node.location = (-200, 0)
        principled_bsdf_node.width = 200
        links.new(
            principled_bsdf_node.outputs[
                BLENDER_SHADERNODES.OUTPUT_BSDFTRANSPARENT_BSDF
            ],
            mix_shader_node.inputs[BLENDER_SHADERNODES.INPUT_MIXSHADER_SHADER2],
        )

        loaded_textures = loaded_material.textures()
        for i, t in enumerate(loaded_textures):
            loaded_texture = loaded_textures[t]
            loaded_texture_type = loaded_texture.texture_type()

            texture_node = nodes.new(BLENDER_SHADERNODES.SHADERNODE_TEXIMAGE)
            texture_node.label = loaded_texture.texture_type()
            texture_node.location = (-700, -255 * i)
            texture_node.image = loaded_texture.data()

            if loaded_texture_type == TEXTURE_TYPES.COLORMAP:
                links.new(
                    texture_node.outputs[BLENDER_SHADERNODES.OUTPUT_TEXIMAGE_COLOR],
                    principled_bsdf_node.inputs[
                        BLENDER_SHADERNODES.INPUT_BSDFPRINCIPLED_BASECOLOR
                    ],
                )
                links.new(
                    texture_node.outputs[BLENDER_SHADERNODES.OUTPUT_TEXIMAGE_ALPHA],
                    mix_shader_node.inputs[BLENDER_SHADERNODES.INPUT_MIXSHADER_FAC],
                )
            elif loaded_texture_type == TEXTURE_TYPES.SPECULARMAP:
                links.new(
                    texture_node.outputs[BLENDER_SHADERNODES.OUTPUT_TEXIMAGE_COLOR],
                    principled_bsdf_node.inputs[
                        BLENDER_SHADERNODES.INPUT_BSDFPRINCIPLED_SPECULAR
                    ],
                )
                texture_node.image.colorspace_settings.name = (
                    BLENDER_SHADERNODES.TEXIMAGE_COLORSPACE_LINEAR
                )
                texture_node.location = (-700, -255)
            elif loaded_texture_type == TEXTURE_TYPES.NORMALMAP:
                texture_node.image.colorspace_settings.name = (
                    BLENDER_SHADERNODES.TEXIMAGE_COLORSPACE_LINEAR
                )
                texture_node.location = (-1900, -655)

                normal_map_node = nodes.new(BLENDER_SHADERNODES.SHADERNODE_NORMALMAP)
                normal_map_node.location = (-450, -650)
                normal_map_node.space = BLENDER_SHADERNODES.NORMALMAP_SPACE_TANGENT
                normal_map_node.inputs[
                    BLENDER_SHADERNODES.INPUT_NORMALMAP_STRENGTH
                ].default_value = 0.3
                links.new(
                    normal_map_node.outputs[
                        BLENDER_SHADERNODES.OUTPUT_NORMALMAP_NORMAL
                    ],
                    principled_bsdf_node.inputs[
                        BLENDER_SHADERNODES.INPUT_BSDFPRINCIPLED_NORMAL
                    ],
                )

                combine_rgb_node = nodes.new(BLENDER_SHADERNODES.SHADERNODE_COMBINERGB)
                combine_rgb_node.location = (-650, -750)
                links.new(
                    combine_rgb_node.outputs[
                        BLENDER_SHADERNODES.OUTPUT_COMBINERGB_IMAGE
                    ],
                    normal_map_node.inputs[BLENDER_SHADERNODES.INPUT_NORMALMAP_COLOR],
                )

                math_sqrt_node = nodes.new(BLENDER_SHADERNODES.SHADERNODE_MATH)
                math_sqrt_node.location = (-850, -850)
                math_sqrt_node.operation = BLENDER_SHADERNODES.OPERATION_MATH_SQRT
                links.new(
                    math_sqrt_node.outputs[BLENDER_SHADERNODES.OUTPUT_MATH_VALUE],
                    combine_rgb_node.inputs[BLENDER_SHADERNODES.INPUT_COMBINERGB_B],
                )

                math_subtract_node = nodes.new(BLENDER_SHADERNODES.SHADERNODE_MATH)
                math_subtract_node.location = (-1050, -850)
                math_subtract_node.operation = (
                    BLENDER_SHADERNODES.OPERATION_MATH_SUBTRACT
                )
                links.new(
                    math_subtract_node.outputs[BLENDER_SHADERNODES.OUTPUT_MATH_VALUE],
                    math_sqrt_node.inputs[BLENDER_SHADERNODES.INPUT_MATH_SQRT_VALUE],
                )

                math_subtract_node2 = nodes.new(BLENDER_SHADERNODES.SHADERNODE_MATH)
                math_subtract_node2.location = (-1250, -950)
                math_subtract_node2.operation = (
                    BLENDER_SHADERNODES.OPERATION_MATH_SUBTRACT
                )
                math_subtract_node2.inputs[
                    BLENDER_SHADERNODES.INPUT_MATH_SUBTRACT_VALUE1
                ].default_value = 1.0
                links.new(
                    math_subtract_node2.outputs[BLENDER_SHADERNODES.OUTPUT_MATH_VALUE],
                    math_subtract_node.inputs[
                        BLENDER_SHADERNODES.INPUT_MATH_SUBTRACT_VALUE1
                    ],
                )

                math_power_node = nodes.new(BLENDER_SHADERNODES.SHADERNODE_MATH)
                math_power_node.location = (-1250, -750)
                math_power_node.operation = BLENDER_SHADERNODES.OPERATION_MATH_POWER
                math_power_node.inputs[
                    BLENDER_SHADERNODES.INPUT_MATH_POWER_EXPONENT
                ].default_value = 2.0
                links.new(
                    math_power_node.outputs[BLENDER_SHADERNODES.OUTPUT_MATH_VALUE],
                    math_subtract_node.inputs[
                        BLENDER_SHADERNODES.INPUT_MATH_SUBTRACT_VALUE2
                    ],
                )

                math_power_node2 = nodes.new(BLENDER_SHADERNODES.SHADERNODE_MATH)
                math_power_node2.location = (-1500, -950)
                math_power_node2.operation = BLENDER_SHADERNODES.OPERATION_MATH_POWER
                math_power_node2.inputs[
                    BLENDER_SHADERNODES.INPUT_MATH_POWER_EXPONENT
                ].default_value = 2.0
                links.new(
                    math_power_node2.outputs[BLENDER_SHADERNODES.OUTPUT_MATH_VALUE],
                    math_subtract_node2.inputs[
                        BLENDER_SHADERNODES.INPUT_MATH_SUBTRACT_VALUE2
                    ],
                )
                links.new(
                    texture_node.outputs[BLENDER_SHADERNODES.OUTPUT_TEXIMAGE_ALPHA],
                    math_power_node2.inputs[BLENDER_SHADERNODES.INPUT_MATH_POWER_BASE],
                )

                separate_rgb_node = nodes.new(
                    BLENDER_SHADERNODES.SHADERNODE_SEPARATERGB
                )
                separate_rgb_node.location = (-1500, -450)
                links.new(
                    separate_rgb_node.outputs[BLENDER_SHADERNODES.OUTPUT_SEPARATERGB_G],
                    combine_rgb_node.inputs[BLENDER_SHADERNODES.INPUT_COMBINERGB_G],
                )
                links.new(
                    separate_rgb_node.outputs[BLENDER_SHADERNODES.OUTPUT_SEPARATERGB_G],
                    math_power_node.inputs[BLENDER_SHADERNODES.INPUT_MATH_POWER_BASE],
                )
                links.new(
                    texture_node.outputs[BLENDER_SHADERNODES.OUTPUT_TEXIMAGE_COLOR],
                    separate_rgb_node.inputs[
                        BLENDER_SHADERNODES.INPUT_SEPARATERGB_IMAGE
                    ],
                )
                links.new(
                    texture_node.outputs[BLENDER_SHADERNODES.OUTPUT_TEXIMAGE_ALPHA],
                    math_power_node2.inputs[BLENDER_SHADERNODES.INPUT_MATH_POWER_BASE],
                )
                links.new(
                    texture_node.outputs[BLENDER_SHADERNODES.OUTPUT_TEXIMAGE_ALPHA],
                    combine_rgb_node.inputs[BLENDER_SHADERNODES.INPUT_COMBINERGB_R],
                )


class TEXTURE_TYPES(metaclass=base_enum.BaseEnum):
    COLORMAP = "colorMap"
    DETAILMAP = "detailMap"
    NORMALMAP = "normalMap"
    SPECULARMAP = "specularMap"


def import_ibsp(asset_path: str, file_path: str) -> None:
    importer = Importer()
    loader = Loader(importer=importer)
    try:
        loader.import_bsp(asset_path=asset_path, file_path=file_path)
    except:
        error_log(traceback.print_exc())


def import_xmodel(asset_path: str, file_path: str) -> bpy.types.Object | bool:
    importer = Importer()
    loader = Loader(importer=importer)
    try:
        loader.import_xmodel(
            asset_path=asset_path,
            file_path=file_path,
            angles=(0.0, 0.0, 0.0),
            origin=(0.0, 0.0, 0.0),
            scale=(1.0, 1.0, 1.0),
        )
    except:
        error_log(traceback.print_exc())
