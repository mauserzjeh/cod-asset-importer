from __future__ import annotations
import bpy
from . import base_enum

"""
Selects an object and all of its children
"""
def select_hierarchy(obj: bpy.types.Object) -> None:
    obj.select_set(True)
    for children in obj.children:
        select_hierarchy(children)


"""
Copies the selected objects
"""
def copy_object_hierarchy(obj: bpy.types.Object) -> list[bpy.types.Object]:
    select_hierarchy(obj)
    bpy.ops.object.duplicate()
    return bpy.context.selected_objects


"""
Blender shader node constants to make node setup a bit more readable
and manageable
"""
class BLENDER_SHADERNODES(metaclass=base_enum.BaseEnum):
    SHADERNODE_OUTPUTMATERIAL = "ShaderNodeOutputMaterial"
    INPUT_OUTPUTMATERIAL_SURFACE = 0
    # ------------------------------------------------
    SHADERNODE_MIXSHADER = "ShaderNodeMixShader"
    INPUT_MIXSHADER_FAC = 0
    INPUT_MIXSHADER_SHADER1 = 1
    INPUT_MIXSHADER_SHADER2 = 2
    OUTPUT_MIXSHADER_SHADER = 0
    # ------------------------------------------------
    SHADERNODE_BSDFTRANSPARENT = "ShaderNodeBsdfTransparent"
    OUTPUT_BSDFTRANSPARENT_BSDF = 0
    # ------------------------------------------------
    SHADERNODE_BSDFPRINCIPLED = "ShaderNodeBsdfPrincipled"
    INPUT_BSDFPRINCIPLED_BASECOLOR = 0
    INPUT_BSDFPRINCIPLED_SPECULAR = 7
    INPUT_BSDFPRINCIPLED_NORMAL = 22
    OUTPUT_BSDFPRINCIPLED_BSDF = 0
    # ------------------------------------------------
    SHADERNODE_TEXIMAGE = "ShaderNodeTexImage"
    OUTPUT_TEXIMAGE_COLOR = 0
    OUTPUT_TEXIMAGE_ALPHA = 1
    TEXIMAGE_COLORSPACE_LINEAR = "Linear"
    # ------------------------------------------------
    SHADERNODE_NORMALMAP = "ShaderNodeNormalMap"
    INPUT_NORMALMAP_STRENGTH = 0
    INPUT_NORMALMAP_COLOR = 1
    OUTPUT_NORMALMAP_NORMAL = 0
    NORMALMAP_SPACE_TANGENT = "TANGENT"
    # ------------------------------------------------
    SHADERNODE_COMBINERGB = "ShaderNodeCombineRGB"
    INPUT_COMBINERGB_R = 0
    INPUT_COMBINERGB_G = 1
    INPUT_COMBINERGB_B = 2
    OUTPUT_COMBINERGB_IMAGE = 0
    # ------------------------------------------------
    SHADERNODE_MATH = "ShaderNodeMath"
    OUTPUT_MATH_VALUE = 0
    OPERATION_MATH_SQRT = "SQRT"
    INPUT_MATH_SQRT_VALUE = 0
    # ------------------------------------------------
    OPERATION_MATH_SUBTRACT = "SUBTRACT"
    INPUT_MATH_SUBTRACT_VALUE1 = 0
    INPUT_MATH_SUBTRACT_VALUE2 = 1
    # ------------------------------------------------
    OPERATION_MATH_POWER = "POWER"
    INPUT_MATH_POWER_BASE = 0
    INPUT_MATH_POWER_EXPONENT = 1
    # ------------------------------------------------
    SHADERNODE_SEPARATERGB = "ShaderNodeSeparateRGB"
    INPUT_SEPARATERGB_IMAGE = 0
    OUTPUT_SEPARATERGB_R = 0
    OUTPUT_SEPARATERGB_G = 1
    OUTPUT_SEPARATERGB_B = 2
    # ------------------------------------------------
    SHADERNODE_INVERT = "ShaderNodeInvert"
    INPUT_INVERT_FAC = 0
    INPUT_INVERT_COLOR = 1
    OUTPUT_INVERT_COLOR = 0
