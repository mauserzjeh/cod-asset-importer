import glob
import bpy
import mathutils
import os
import math
import traceback
from .cod_asset_importer import (
    XMODEL_VERSION,
    GAME_VERSION,
    TEXTURE_TYPE,
    LoadedModel,
    LoadedIbsp,
    LoadedMaterial,
    Loader,
    LoadedTexture,
)
from .blender_shadernodes import (
    BLENDER_SHADERNODES,
)


class Importer:
    def __init__(self, asset_path: str) -> None:
        self.asset_path = asset_path
        self.ibsp_entities_null = None

    def xmodel(self, loaded_model: LoadedModel) -> None:
        model_name = loaded_model.name()
        model_version = loaded_model.version()

        xmodel_null = bpy.data.objects.new(model_name, None)
        bpy.context.scene.collection.objects.link(xmodel_null)

        mesh_objects = []

        materials = loaded_model.materials()
        for _, material in materials.items():
            append_asset_path = ""
            if model_version == XMODEL_VERSION.V14:
                append_asset_path = "skins"

            self.material(loaded_material=material, append_asset_path=append_asset_path)

        loaded_bones = loaded_model.bones()
        for i, surface in enumerate(loaded_model.surfaces()):
            mesh = bpy.data.meshes.new(model_name)
            vertices = surface.vertices()
            mesh.vertices.add(len(vertices) // 3)
            mesh.loops.add(surface.loops_len())
            polygons_len = surface.polygons_len()
            mesh.polygons.add(polygons_len)
            mesh.vertices.foreach_set("co", vertices)
            mesh.polygons.foreach_set("loop_total", surface.polygon_loop_totals())
            mesh.polygons.foreach_set("loop_start", surface.polygon_loop_starts())
            mesh.polygons.foreach_set("vertices", surface.polygon_vertices())
            mesh.polygons.foreach_set("use_smooth", [True] * polygons_len)
            mesh.update(calc_edges=True)
            mesh.validate()

            mesh.normals_split_custom_set_from_vertices(surface.normals())

            uv_layer = mesh.uv_layers.new()
            uv_layer.data.foreach_set("uv", surface.uvs())

            vertex_color_layer = mesh.color_attributes.new(
                name="VertexColor", type="FLOAT_COLOR", domain="POINT"
            )
            vertex_color_layer.data.foreach_set("color", surface.colors())

            obj = bpy.data.objects.new(model_name, mesh)
            active_material_name = surface.material()
            if model_version == XMODEL_VERSION.V14:
                active_material_name = os.path.splitext(active_material_name)[0]
            obj.active_material = bpy.data.materials.get(active_material_name)

            bpy.context.scene.collection.objects.link(obj)

            if len(loaded_bones) > 1:
                for bone_index, weights in surface.weight_groups().items():
                    bone_name = loaded_bones[bone_index].name()
                    vg = obj.vertex_groups.new(name=bone_name)
                    for vertex_index, weight in weights.items():
                        vg.add(index=[vertex_index], weight=weight, type="REPLACE")

            mesh_objects.append(obj)

        skeleton = None
        if len(loaded_bones) > 1:
            armature = bpy.data.armatures.new(f"{model_name}_armature")
            armature.display_type = "STICK"

            skeleton = bpy.data.objects.new(f"{model_name}_skeleton", armature)
            skeleton.parent = xmodel_null
            skeleton.show_in_front = True
            bpy.context.scene.collection.objects.link(skeleton)
            bpy.context.view_layer.objects.active = skeleton
            bpy.ops.object.mode_set(mode="EDIT")

            bone_matrices = {}

            for loaded_bone in loaded_bones:
                bone_name = loaded_bone.name()

                new_bone = armature.edit_bones.new(bone_name)
                new_bone.tail = (0, 0.05, 0)

                matrix_rotation = (
                    mathutils.Quaternion(loaded_bone.rotation()).to_matrix().to_4x4()
                )
                matrix_transform = mathutils.Matrix.Translation(
                    mathutils.Vector(loaded_bone.position())
                )

                matrix = matrix_transform @ matrix_rotation
                bone_matrices[bone_name] = matrix

                bone_parent = loaded_bone.parent()
                if bone_parent > -1:
                    new_bone.parent = armature.edit_bones[bone_parent]

            bpy.context.view_layer.objects.active = skeleton
            bpy.ops.object.mode_set(mode="POSE")

            for bone in skeleton.pose.bones:
                bone.matrix_basis.identity()
                bone.matrix = bone_matrices[bone.name]

            bpy.ops.pose.armature_apply()
            bpy.context.view_layer.objects.active = skeleton

            maxs = [0, 0, 0]
            mins = [0, 0, 0]

            for bone in armature.bones:
                for i in range(3):
                    maxs[i] = max(maxs[i], bone.head_local[i])
                    mins[i] = min(mins[i], bone.head_local[i])

            dimensions = []
            for i in range(3):
                dimensions.append(maxs[i] - mins[i])

            length = max(0.001, (dimensions[0] + dimensions[1] + dimensions[2]) / 600)
            bpy.ops.object.mode_set(mode="EDIT")
            for bone in [armature.edit_bones[lb.name()] for lb in loaded_bones]:
                bone.tail = bone.head + (bone.tail - bone.head).normalized() * length

            bpy.ops.object.mode_set(mode="OBJECT")
            bpy.ops.object.select_all(action="DESELECT")

        for mesh_object in mesh_objects:
            if skeleton == None:
                mesh_object.parent = xmodel_null
                continue

            for loaded_bone in loaded_bones:
                mesh_object.vertex_groups.new(name=loaded_bone.name())

            mesh_object.parent = skeleton
            modifier = mesh_object.modifiers.new("armature_rig", "ARMATURE")
            modifier.object = skeleton
            modifier.use_bone_envelopes = False
            modifier.use_vertex_groups = True

        if self.ibsp_entities_null != None:
            xmodel_null.parent = self.ibsp_entities_null
            xmodel_null.location = loaded_model.origin()
            xmodel_null.scale = loaded_model.scale()
            angles = loaded_model.angles()
            xmodel_null.rotation_euler = (
                math.radians(angles[2]),
                math.radians(angles[0]),
                math.radians(angles[1]),
            )

    def ibsp(self, loaded_ibsp: LoadedIbsp) -> None:
        ibsp_name = loaded_ibsp.name()

        ibsp_null = bpy.data.objects.new(ibsp_name, None)
        bpy.context.scene.collection.objects.link(ibsp_null)

        ibsp_geometry_null = bpy.data.objects.new(f"{ibsp_name}_geometry", None)
        bpy.context.scene.collection.objects.link(ibsp_geometry_null)
        ibsp_geometry_null.parent = ibsp_null

        ibsp_entities_null = bpy.data.objects.new(f"{ibsp_name}_entities", None)
        bpy.context.scene.collection.objects.link(ibsp_entities_null)
        ibsp_entities_null.parent = ibsp_null

        self.ibsp_entities_null = ibsp_entities_null

        surfaces = loaded_ibsp.surfaces()
        for surface in surfaces:
            name = f"{ibsp_name}_geometry"

            mesh = bpy.data.meshes.new(name)
            vertices = surface.vertices()
            mesh.vertices.add(len(vertices) // 3)
            mesh.loops.add(surface.loops_len())
            polygons_len = surface.polygons_len()
            mesh.polygons.add(polygons_len)
            mesh.vertices.foreach_set("co", vertices)
            mesh.polygons.foreach_set("loop_total", surface.polygon_loop_totals())
            mesh.polygons.foreach_set("loop_start", surface.polygon_loop_starts())
            mesh.polygons.foreach_set("vertices", surface.polygon_vertices())
            mesh.polygons.foreach_set("use_smooth", [True] * polygons_len)
            mesh.update(calc_edges=True)
            mesh.validate()

            mesh.normals_split_custom_set_from_vertices(surface.normals())

            uv_layer = mesh.uv_layers.new()
            uv_layer.data.foreach_set("uv", surface.uvs())

            vertex_color_layer = mesh.color_attributes.new(
                name="VertexColor", type="FLOAT_COLOR", domain="POINT"
            )
            vertex_color_layer.data.foreach_set("color", surface.colors())

            obj = bpy.data.objects.new(name, mesh)
            obj.parent = ibsp_geometry_null

            active_material_name = surface.material()
            obj.active_material = bpy.data.materials.get(active_material_name)

            bpy.context.scene.collection.objects.link(obj)

    def material(
        self,
        loaded_material: LoadedMaterial,
        has_ext: bool = True,
        append_asset_path: str = "",
    ) -> None:
        version = loaded_material.version()
        if version == XMODEL_VERSION.V14:
            self._import_material_v14(
                loaded_material=loaded_material,
                has_ext=has_ext,
                append_asset_path=append_asset_path,
            )
        elif version == XMODEL_VERSION.V62:
            self._import_material_v62(loaded_material=loaded_material)
        else:
            self._import_material_v20_v25(loaded_material=loaded_material)

    def _import_material_v14(
        self, loaded_material: LoadedMaterial, has_ext: bool, append_asset_path: str
    ) -> None:
        material_name = loaded_material.name()

        texture_file = os.path.join(
            self.asset_path, append_asset_path, os.path.join(*material_name.split("/"))
        )
        if not has_ext:
            for tex in glob.iglob(texture_file + ".*"):
                texture_file = tex
                break

        material_name = os.path.splitext(material_name)[0]

        if bpy.data.materials.get(material_name):
            return

        try:
            texture_image = bpy.data.images.load(texture_file, check_existing=True)
            material = bpy.data.materials.new(material_name)
            material.use_nodes = True
            material.blend_method = "HASHED"

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

            principled_bsdf_node = nodes.new(
                BLENDER_SHADERNODES.SHADERNODE_BSDFPRINCIPLED
            )
            principled_bsdf_node.location = (-200, 0)
            principled_bsdf_node.width = 200
            links.new(
                principled_bsdf_node.outputs[
                    BLENDER_SHADERNODES.OUTPUT_BSDFTRANSPARENT_BSDF
                ],
                mix_shader_node.inputs[BLENDER_SHADERNODES.INPUT_MIXSHADER_SHADER2],
            )

            texture_node = nodes.new(BLENDER_SHADERNODES.SHADERNODE_TEXIMAGE)
            texture_node.label = str(TEXTURE_TYPE.Color)
            texture_node.location = (-700, 0)
            texture_node.image = texture_image
            links.new(
                texture_node.outputs[BLENDER_SHADERNODES.OUTPUT_TEXIMAGE_COLOR],
                principled_bsdf_node.inputs[
                    BLENDER_SHADERNODES.INPUT_BSDFPRINCIPLED_BASECOLOR
                ],
            )

            invert_node = nodes.new(BLENDER_SHADERNODES.SHADERNODE_INVERT)
            invert_node.location = (-400, 0)

            invert_fac_default_value = 0.0
            transparent_textures = ["foliage_masked", "foliage_detail"]
            for tt in transparent_textures:
                if tt in material_name.lower():
                    invert_fac_default_value = 1.0
                    break

            invert_node.inputs[BLENDER_SHADERNODES.INPUT_INVERT_FAC].default_value = (
                invert_fac_default_value
            )

            links.new(
                invert_node.outputs[BLENDER_SHADERNODES.OUTPUT_INVERT_COLOR],
                mix_shader_node.inputs[BLENDER_SHADERNODES.INPUT_MIXSHADER_FAC],
            )
            links.new(
                texture_node.outputs[BLENDER_SHADERNODES.OUTPUT_TEXIMAGE_ALPHA],
                invert_node.inputs[BLENDER_SHADERNODES.INPUT_INVERT_COLOR],
            )
        except:
            return

    def _import_material_v20_v25(self, loaded_material: LoadedMaterial) -> None:
        material_name = loaded_material.name()

        if bpy.data.materials.get(material_name):
            return

        material = bpy.data.materials.new(material_name)
        material.use_nodes = True
        material.blend_method = "HASHED"

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
        for i, loaded_texture in enumerate(loaded_textures):
            texture_image = self._import_texture(loaded_texture=loaded_texture)
            if texture_image == None:
                continue

            loaded_texture_type = loaded_texture.texture_type()

            texture_node = nodes.new(BLENDER_SHADERNODES.SHADERNODE_TEXIMAGE)
            texture_node.label = str(loaded_texture_type)
            texture_node.location = (-900, 600 - (255 * i))
            texture_node.image = texture_image

            if loaded_texture_type == TEXTURE_TYPE.Color:
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
            elif loaded_texture_type == TEXTURE_TYPE.Specular:
                links.new(
                    texture_node.outputs[BLENDER_SHADERNODES.OUTPUT_TEXIMAGE_COLOR],
                    principled_bsdf_node.inputs[
                        BLENDER_SHADERNODES.INPUT_BSDFPRINCIPLED_SPECULAR
                    ],
                )
                texture_node.image.colorspace_settings.name = (
                    BLENDER_SHADERNODES.TEXIMAGE_COLORSPACE_SRGB
                )
            elif loaded_texture_type == TEXTURE_TYPE.Roughness:
                links.new(
                    texture_node.outputs[BLENDER_SHADERNODES.OUTPUT_TEXIMAGE_COLOR],
                    principled_bsdf_node.inputs[
                        BLENDER_SHADERNODES.INPUT_BSDFPRINCIPLED_ROUGHNESS
                    ],
                )
                texture_node.image.colorspace_settings.name = (
                    BLENDER_SHADERNODES.TEXIMAGE_COLORSPACE_SRGB
                )
            elif loaded_texture_type == TEXTURE_TYPE.Normal:
                texture_node.image.colorspace_settings.name = (
                    BLENDER_SHADERNODES.TEXIMAGE_COLORSPACE_SRGB
                )
                texture_node.location = (-1900, -655)

                normal_map_node = nodes.new(BLENDER_SHADERNODES.SHADERNODE_NORMALMAP)
                normal_map_node.location = (-450, -650)
                normal_map_node.space = BLENDER_SHADERNODES.NORMALMAP_SPACE_OBJECT
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

                combine_rgb_node = nodes.new(
                    BLENDER_SHADERNODES.SHADERNODE_COMBINECOLOR
                )
                combine_rgb_node.location = (-650, -750)
                links.new(
                    combine_rgb_node.outputs[
                        BLENDER_SHADERNODES.OUTPUT_COMBINECOLOR_COLOR
                    ],
                    normal_map_node.inputs[BLENDER_SHADERNODES.INPUT_NORMALMAP_COLOR],
                )

                math_sqrt_node = nodes.new(BLENDER_SHADERNODES.SHADERNODE_MATH)
                math_sqrt_node.location = (-850, -850)
                math_sqrt_node.operation = BLENDER_SHADERNODES.OPERATION_MATH_SQRT
                links.new(
                    math_sqrt_node.outputs[BLENDER_SHADERNODES.OUTPUT_MATH_VALUE],
                    combine_rgb_node.inputs[BLENDER_SHADERNODES.INPUT_COMBINECOLOR_B],
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
                    BLENDER_SHADERNODES.SHADERNODE_SEPARATECOLOR
                )
                separate_rgb_node.location = (-1500, -450)
                links.new(
                    separate_rgb_node.outputs[
                        BLENDER_SHADERNODES.OUTPUT_SEPARATECOLOR_G
                    ],
                    combine_rgb_node.inputs[BLENDER_SHADERNODES.INPUT_COMBINECOLOR_G],
                )
                links.new(
                    separate_rgb_node.outputs[
                        BLENDER_SHADERNODES.OUTPUT_SEPARATECOLOR_G
                    ],
                    math_power_node.inputs[BLENDER_SHADERNODES.INPUT_MATH_POWER_BASE],
                )
                links.new(
                    texture_node.outputs[BLENDER_SHADERNODES.OUTPUT_TEXIMAGE_COLOR],
                    separate_rgb_node.inputs[
                        BLENDER_SHADERNODES.INPUT_SEPARATECOLOR_COLOR
                    ],
                )
                links.new(
                    texture_node.outputs[BLENDER_SHADERNODES.OUTPUT_TEXIMAGE_ALPHA],
                    math_power_node2.inputs[BLENDER_SHADERNODES.INPUT_MATH_POWER_BASE],
                )
                links.new(
                    texture_node.outputs[BLENDER_SHADERNODES.OUTPUT_TEXIMAGE_ALPHA],
                    combine_rgb_node.inputs[BLENDER_SHADERNODES.INPUT_COMBINECOLOR_R],
                )

    def _import_material_v62(self, loaded_material: LoadedMaterial) -> None:
        material_name = loaded_material.name()

        if bpy.data.materials.get(material_name):
            return

        material = bpy.data.materials.new(material_name)
        material.use_nodes = True
        material.blend_method = "HASHED"

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
        for i, loaded_texture in enumerate(loaded_textures):
            texture_image = self._import_texture(loaded_texture=loaded_texture)
            if texture_image == None:
                continue

            loaded_texture_type = loaded_texture.texture_type()

            texture_node = nodes.new(BLENDER_SHADERNODES.SHADERNODE_TEXIMAGE)
            texture_node.label = str(loaded_texture_type)
            texture_node.location = (-900, 600 - (255 * i))
            texture_node.image = texture_image

            if loaded_texture_type == TEXTURE_TYPE.Color:
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
            elif loaded_texture_type == TEXTURE_TYPE.Specular:
                links.new(
                    texture_node.outputs[BLENDER_SHADERNODES.OUTPUT_TEXIMAGE_COLOR],
                    principled_bsdf_node.inputs[
                        BLENDER_SHADERNODES.INPUT_BSDFPRINCIPLED_SPECULAR
                    ],
                )
                texture_node.image.colorspace_settings.name = (
                    BLENDER_SHADERNODES.TEXIMAGE_COLORSPACE_SRGB
                )
            elif loaded_texture_type == TEXTURE_TYPE.Roughness:
                links.new(
                    texture_node.outputs[BLENDER_SHADERNODES.OUTPUT_TEXIMAGE_COLOR],
                    principled_bsdf_node.inputs[
                        BLENDER_SHADERNODES.INPUT_BSDFPRINCIPLED_ROUGHNESS
                    ],
                )
                texture_node.image.colorspace_settings.name = (
                    BLENDER_SHADERNODES.TEXIMAGE_COLORSPACE_SRGB
                )
            elif loaded_texture_type == TEXTURE_TYPE.Normal:
                texture_node.image.colorspace_settings.name = (
                    BLENDER_SHADERNODES.TEXIMAGE_COLORSPACE_SRGB
                )
                texture_node.location = (-1900, -655)

                normal_map_node = nodes.new(BLENDER_SHADERNODES.SHADERNODE_NORMALMAP)
                normal_map_node.location = (-450, -650)
                normal_map_node.space = BLENDER_SHADERNODES.NORMALMAP_SPACE_OBJECT
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

                combine_rgb_node = nodes.new(
                    BLENDER_SHADERNODES.SHADERNODE_COMBINECOLOR
                )
                combine_rgb_node.location = (-650, -750)
                links.new(
                    combine_rgb_node.outputs[
                        BLENDER_SHADERNODES.OUTPUT_COMBINECOLOR_COLOR
                    ],
                    normal_map_node.inputs[BLENDER_SHADERNODES.INPUT_NORMALMAP_COLOR],
                )

                math_sqrt_node = nodes.new(BLENDER_SHADERNODES.SHADERNODE_MATH)
                math_sqrt_node.location = (-850, -850)
                math_sqrt_node.operation = BLENDER_SHADERNODES.OPERATION_MATH_SQRT
                links.new(
                    math_sqrt_node.outputs[BLENDER_SHADERNODES.OUTPUT_MATH_VALUE],
                    combine_rgb_node.inputs[BLENDER_SHADERNODES.INPUT_COMBINECOLOR_B],
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
                    BLENDER_SHADERNODES.SHADERNODE_SEPARATECOLOR
                )
                separate_rgb_node.location = (-1500, -450)
                links.new(
                    separate_rgb_node.outputs[
                        BLENDER_SHADERNODES.OUTPUT_SEPARATECOLOR_G
                    ],
                    combine_rgb_node.inputs[BLENDER_SHADERNODES.INPUT_COMBINECOLOR_G],
                )
                links.new(
                    separate_rgb_node.outputs[
                        BLENDER_SHADERNODES.OUTPUT_SEPARATECOLOR_G
                    ],
                    math_power_node.inputs[BLENDER_SHADERNODES.INPUT_MATH_POWER_BASE],
                )
                links.new(
                    texture_node.outputs[BLENDER_SHADERNODES.OUTPUT_TEXIMAGE_COLOR],
                    separate_rgb_node.inputs[
                        BLENDER_SHADERNODES.INPUT_SEPARATECOLOR_COLOR
                    ],
                )
                links.new(
                    texture_node.outputs[BLENDER_SHADERNODES.OUTPUT_TEXIMAGE_ALPHA],
                    math_power_node2.inputs[BLENDER_SHADERNODES.INPUT_MATH_POWER_BASE],
                )
                links.new(
                    texture_node.outputs[BLENDER_SHADERNODES.OUTPUT_TEXIMAGE_ALPHA],
                    combine_rgb_node.inputs[BLENDER_SHADERNODES.INPUT_COMBINECOLOR_R],
                )

    def _import_texture(
        self, loaded_texture: LoadedTexture
    ) -> bpy.types.Texture | None:
        texture_name = loaded_texture.name()
        texture_image = bpy.data.images.get(texture_name)
        if texture_image != None:
            return texture_image

        texture_image = bpy.data.images.new(
            name=texture_name,
            width=loaded_texture.width(),
            height=loaded_texture.height(),
            alpha=True,
        )
        texture_image.pixels = loaded_texture.data()
        texture_image.file_format = "TARGA"
        texture_image.alpha_mode = "CHANNEL_PACKED"

        return texture_image


def import_ibsp(asset_path: str, file_path: str) -> None:
    importer = Importer(asset_path=asset_path)
    loader = Loader(importer=importer)
    try:
        loader.import_bsp(asset_path=asset_path, file_path=file_path)
    except:
        traceback.print_exc()


def import_xmodel(
    asset_path: str, file_path: str, selected_version: GAME_VERSION
) -> bpy.types.Object | bool:
    importer = Importer(asset_path=asset_path)
    loader = Loader(importer=importer)
    try:
        loader.import_xmodel(
            asset_path=asset_path,
            file_path=file_path,
            selected_version=selected_version,
            angles=(0.0, 0.0, 0.0),
            origin=(0.0, 0.0, 0.0),
            scale=(1.0, 1.0, 1.0),
        )
    except:
        traceback.print_exc()
