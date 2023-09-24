import bpy
from . import operators

bl_info = {
    "name": "Call of Duty Asset Importer",
    "description": "Import Call of Duty assets",
    "author": "Soma Rádóczi",
    "version": (3, 0, 0),
    "blender": (3, 0, 0),
    "location": "File > Import/Export",
    "category": "Import-Export",
    "warning": "This addon is still in development",
}

operators_list = (
    {"class": operators.MapImporter, "text": "Call of Duty map", "function": None},
    {"class": operators.ModelImporter, "text": "Call of Duty model", "function": None},
)


def menu_function(cls: object, text: str) -> callable:
    def menu_func(self, context):
        self.layout.operator(cls.bl_idname, text=text)

    return menu_func


def register():
    for operator in operators_list:
        bpy.utils.register_class(operator["class"])
        operator["function"] = menu_function(operator["class"], operator["text"])
        bpy.types.TOPBAR_MT_file_import.append(operator["function"])


def unregister():
    for operator in reversed(operators_list):
        bpy.utils.unregister_class(operator["class"])
        bpy.types.TOPBAR_MT_file_import.remove(operator["function"])
