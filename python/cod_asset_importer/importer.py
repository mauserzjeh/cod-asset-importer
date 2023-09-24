import bpy
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
        debug_log(loaded_model.name())

    def ibsp(self, loaded_ibsp: LoadedIbsp) -> None:
        debug_log(loaded_ibsp.name())

    def material(self, loaded_material: LoadedMaterial) -> None:
        pass

    def _import_material_v14(loaded_material: LoadedMaterial) -> None:
        pass

    def _import_material_v20_v25(loaded_material: LoadedMaterial) -> None:
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

            texture_node = nodes.new(BLENDER_SHADERNODES.SHADERNODE_TEXIMAGE)
            texture_node.label = loaded_texture.texture_type()
            texture_node.location = (-700, -255 * i)
            texture_node.image = loaded_texture.data()

            if t.type == TEXTURE_TYPES.COLORMAP:
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
            elif t.type == TEXTURE_TYPES.SPECULARMAP:
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
            elif t.type == TEXTURE_TYPES.NORMALMAP:
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
