
import bpy

class D3DBSPImporter(bpy.types.Operator):
    bl_idname = 'cod_asset_importer.d3dbsp_importer'
    bl_label = 'Import'
    bl_options = {'UNDO'}

    def execute(self, context):
        print("d3dbsp")
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
        return {'RUNNIN_MODAL'}