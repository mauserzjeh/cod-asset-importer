from typing import Set
import bpy
import os
from . import importer
from .cod_asset_importer import (
    GAME_VERSIONS,
)


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
    version: bpy.props.EnumProperty(
        name="Version",
        description="Version of the model",
        items=[
            ("cod1", "CoD1 (v14)", "Call of Duty & Call of Duty UO"),
            ("cod2", "CoD2 (v20)", "Call of Duty 2"),
            ("cod4", "CoD4 (v25)", "Call of Duty: Modern Warfare"),
            ("cod5", "CoD5 (v25)", "Call of Duty: World at War"),
        ],
    )

    version_options = {
        "cod1": GAME_VERSIONS.CoD1,
        "cod2": GAME_VERSIONS.CoD2,
        "cod4": GAME_VERSIONS.CoD4,
        "cod5": GAME_VERSIONS.CoD5,
    }

    def execute(self, context: bpy.types.Context) -> Set[int] | Set[str]:
        assetpath = os.path.abspath(
            os.path.join(os.path.dirname(self.filepath), os.pardir)
        )

        importer.import_xmodel(
            asset_path=assetpath,
            file_path=self.filepath,
            selected_version=self.version_options[self.version],
        )
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
