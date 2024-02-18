from . import base_enum


class BLENDER_SHADERNODES(metaclass=base_enum.BaseEnum):
    SHADERNODE_OUTPUTMATERIAL = "ShaderNodeOutputMaterial"
    INPUT_OUTPUTMATERIAL_SURFACE = "Surface"
    # ------------------------------------------------
    SHADERNODE_MIXSHADER = "ShaderNodeMixShader"
    INPUT_MIXSHADER_FAC = "Fac"
    INPUT_MIXSHADER_SHADER1 = 1 # Shader
    INPUT_MIXSHADER_SHADER2 = 2 # Shader
    OUTPUT_MIXSHADER_SHADER = "Shader"
    # ------------------------------------------------
    SHADERNODE_BSDFTRANSPARENT = "ShaderNodeBsdfTransparent"
    OUTPUT_BSDFTRANSPARENT_BSDF = "BSDF"
    # ------------------------------------------------
    SHADERNODE_BSDFPRINCIPLED = "ShaderNodeBsdfPrincipled"
    INPUT_BSDFPRINCIPLED_BASECOLOR = "Base Color"
    INPUT_BSDFPRINCIPLED_ROUGHNESS = "Roughness"
    INPUT_BSDFPRINCIPLED_SPECULAR = "Specular IOR Level"
    INPUT_BSDFPRINCIPLED_NORMAL = "Normal"
    OUTPUT_BSDFPRINCIPLED_BSDF = "BSDF"
    # ------------------------------------------------
    SHADERNODE_TEXIMAGE = "ShaderNodeTexImage"
    OUTPUT_TEXIMAGE_COLOR = "Color"
    OUTPUT_TEXIMAGE_ALPHA = "Alpha"
    TEXIMAGE_COLORSPACE_SRGB = "sRGB"
    # ------------------------------------------------
    SHADERNODE_NORMALMAP = "ShaderNodeNormalMap"
    INPUT_NORMALMAP_STRENGTH = "Strength"
    INPUT_NORMALMAP_COLOR = "Color"
    OUTPUT_NORMALMAP_NORMAL = "Normal"
    NORMALMAP_SPACE_OBJECT = "OBJECT"
    # ------------------------------------------------
    SHADERNODE_COMBINECOLOR = "ShaderNodeCombineColor"
    INPUT_COMBINECOLOR_R = "Red"
    INPUT_COMBINECOLOR_G = "Green"
    INPUT_COMBINECOLOR_B = "Blue"
    OUTPUT_COMBINECOLOR_COLOR = "Color"
    # ------------------------------------------------
    SHADERNODE_MATH = "ShaderNodeMath"
    OUTPUT_MATH_VALUE = "Value"
    OPERATION_MATH_SQRT = "SQRT"
    INPUT_MATH_SQRT_VALUE = "Value"
    # ------------------------------------------------
    OPERATION_MATH_SUBTRACT = "SUBTRACT"
    INPUT_MATH_SUBTRACT_VALUE1 = 0 # Value
    INPUT_MATH_SUBTRACT_VALUE2 = 1 # Value
    # ------------------------------------------------
    OPERATION_MATH_POWER = "POWER"
    INPUT_MATH_POWER_BASE = 0 # Value
    INPUT_MATH_POWER_EXPONENT = 1 # Value
    # ------------------------------------------------
    SHADERNODE_SEPARATECOLOR = "ShaderNodeSeparateColor"
    INPUT_SEPARATECOLOR_COLOR = "Color"
    OUTPUT_SEPARATECOLOR_R = "Red"
    OUTPUT_SEPARATECOLOR_G = "Green"
    OUTPUT_SEPARATECOLOR_B = "Blue"
    # ------------------------------------------------
    SHADERNODE_INVERT = "ShaderNodeInvert"
    INPUT_INVERT_FAC = "Fac"
    INPUT_INVERT_COLOR = "Color"
    OUTPUT_INVERT_COLOR = "Color"
