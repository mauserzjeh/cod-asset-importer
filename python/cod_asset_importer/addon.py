import bpy
from . import operators


class CodAssetImporterMenu(bpy.types.Menu):
    bl_idname = "IMPORT_MT_cod_asset_importer"
    bl_label = "CoD Asset Importer"

    def draw(self: bpy.types.Menu, context: bpy.types.Context):
        self.layout.operator(
            operator=operators.MapImporter.bl_idname, text="Import map",
        )
        self.layout.operator(
            operator=operators.ModelImporter.bl_idname, text="Import model"
        )


def menu_func(self: bpy.types.Menu, context: bpy.types.Context):
    self.layout.menu(CodAssetImporterMenu.bl_idname)


def register():
    bpy.utils.register_class(CodAssetImporterMenu)
    bpy.types.TOPBAR_MT_file_import.append(menu_func)


def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func)
    bpy.utils.unregister_class(CodAssetImporterMenu)
