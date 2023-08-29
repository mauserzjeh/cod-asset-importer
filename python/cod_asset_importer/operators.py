from typing import Set
from bpy.types import Context
import bpy
import os


class XModelImporter(bpy.types.Operator):
    bl_idname = "cod_asset_importer"
    bl_label = "Import"
    bl_options = {"UNDO"}

    file_path: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context: Context) -> Set[int] | Set[str]:
        asset_path = os.path.abspath(
            os.path.join(os.path.dirname(self.file_path), os.pardir)
        )

        return {"FINISHED"}
