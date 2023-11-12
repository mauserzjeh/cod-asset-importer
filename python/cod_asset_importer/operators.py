from typing import Set
import bpy
import os
from . import importer


class MapImporter(bpy.types.Operator):
    bl_idname = "cod_asset_importer.map_importer"
    bl_label = "Import"
    bl_options = {"UNDO"}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filename_ext = ".d3dbsp"
    filter_glob: bpy.props.StringProperty(default="*.d3dbsp;*.bsp", options={"HIDDEN"})

    def execute(self, context: bpy.types.Context) -> Set[int] | Set[str]:
        assetpath = os.path.abspath(
            os.path.join(os.path.dirname(self.filepath), os.pardir)
        )
        if os.path.basename(self.filepath).startswith("mp_"):
            assetpath = os.path.abspath(
                os.path.join(os.path.dirname(self.filepath), os.pardir, os.pardir)
            )

        importer.import_ibsp(asset_path=assetpath, file_path=self.filepath)
        return {"FINISHED"}

    def invoke(self, context, event):
        bpy.context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class ModelImporter(bpy.types.Operator):
    bl_idname = "cod_asset_importer.model_importer"
    bl_label = "Import"
    bl_options = {"UNDO"}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context: bpy.types.Context) -> Set[int] | Set[str]:
        assetpath = os.path.abspath(
            os.path.join(os.path.dirname(self.filepath), os.pardir)
        )

        importer.import_xmodel(asset_path=assetpath, file_path=self.filepath)
        return {"FINISHED"}

    def invoke(self, context, event):
        bpy.context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


OPERATORS = [MapImporter, ModelImporter]


def register():
    for op in OPERATORS:
        bpy.utils.register_class(op)


def unregister():
    for op in OPERATORS:
        bpy.utils.unregister_class(op)
