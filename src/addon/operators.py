
import bpy

from . import importer

class D3DBSPImporter(bpy.types.Operator):
    bl_idname = 'cod_asset_importer.d3dbsp_importer'
    bl_label = 'Import'
    bl_options = {'UNDO'}

    filepath : bpy.props.StringProperty(subtype='FILE_PATH')
    filename_ext = '.d3dbsp'
    filter_glob : bpy.props.StringProperty(default='*.d3dbsp', options={'HIDDEN'})

    assetpath : bpy.props.StringProperty(
        name = 'Asset path',
        description = 'Directory containing extracted assets'
    )

    def execute(self, context):
        importer.import_d3dbsp(self.assetpath, self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        bpy.context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class XModelImporter(bpy.types.Operator):
    bl_idname = 'cod_asset_importer.xmodel_importer'
    bl_label = 'Import'
    bl_options = {'UNDO'}

    def execute(self, context):
        print('xmodel')
        return {'FINISHED'}

    def invoke(self, context, event):
        bpy.context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}