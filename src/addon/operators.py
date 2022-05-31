
import bpy
import os

from . import importer
from .. utils import (
    data as datautils,
    log
)
from .. assets import (
    d3dbsp,
    bsp,
    xmodel,
)

"""
Imports a map file into blender
"""
class MapImporter(bpy.types.Operator):
    bl_idname = 'cod_asset_importer.map_importer'
    bl_label = 'Import'
    bl_options = {'UNDO'}

    filepath : bpy.props.StringProperty(subtype='FILE_PATH')
    filename_ext = '.d3dbsp'
    filter_glob : bpy.props.StringProperty(default='*.d3dbsp;*.bsp', options={'HIDDEN'})

    def execute(self, context):
        assetpath = os.path.abspath(os.path.join(os.path.dirname(self.filepath), os.pardir))
        if os.path.basename(self.filepath).startswith("mp_"):
            assetpath = os.path.abspath(os.path.join(os.path.dirname(self.filepath), os.pardir, os.pardir))

        version = datautils.PeekMapVersion(self.filepath)
        if version == d3dbsp.D3DBSP.VERSION:
            importer.import_d3dbsp(assetpath, self.filepath)
            return {'FINISHED'}

        if version == bsp.BSP.VERSION:
            importer.import_bsp(assetpath, self.filepath)
            return {'FINISHED'}

        log.error_log(f"Unsupported map version {version}")
        return {'FINISHED'}

    def invoke(self, context, event):
        bpy.context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

"""
Imports xmodel file into blender
"""
class XModelImporter(bpy.types.Operator):
    bl_idname = 'cod_asset_importer.xmodel_importer'
    bl_label = 'Import'
    bl_options = {'UNDO'}

    filepath : bpy.props.StringProperty(subtype='FILE_PATH')
    def execute(self, context):
        assetpath = os.path.abspath(os.path.join(os.path.dirname(self.filepath), os.pardir))

        version = datautils.PeekXmodelVersion(self.filepath)
        if version == xmodel.XModelV20.VERSION:
            importer.import_xmodel_v20(assetpath, self.filepath, True)
            return {'FINISHED'}

        if version == xmodel.XModelV14.VERSION:
            importer.import_xmodel_v14(assetpath, self.filepath, True)
            return {'FINISHED'}

        if version == xmodel.XModelV25.VERSION:
            importer.import_xmodel_v25(assetpath, self.filepath, True)
            return {'FINISHED'}

        log.error_log(f"Unsupported xmodel version {version}")
        return {'FINISHED'}

    def invoke(self, context, event):
        bpy.context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}