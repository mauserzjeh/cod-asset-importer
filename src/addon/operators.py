
import bpy
import os

from . import importer

class D3DBSPImporter(bpy.types.Operator):
    bl_idname = 'cod_asset_importer.d3dbsp_importer'
    bl_label = 'Import'
    bl_options = {'UNDO'}

    filepath : bpy.props.StringProperty(subtype='FILE_PATH')
    filename_ext = '.d3dbsp'
    filter_glob : bpy.props.StringProperty(default='*.d3dbsp', options={'HIDDEN'})

    def execute(self, context):
        assetpath = os.path.abspath(os.path.join(os.path.join(self.filepath, os.pardir), os.pardir))
        importer.import_d3dbsp(assetpath, self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        bpy.context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class XModelImporter(bpy.types.Operator):
    bl_idname = 'cod_asset_importer.xmodel_importer'
    bl_label = 'Import'
    bl_options = {'UNDO'}

    filepath : bpy.props.StringProperty(subtype='FILE_PATH')
    def execute(self, context):
        assetpath = os.path.abspath(os.path.join(os.path.join(self.filepath, os.pardir), os.pardir))
        importer.import_xmodel(assetpath, self.filepath, True)
        return {'FINISHED'}

    def invoke(self, context, event):
        bpy.context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class IWiImporter(bpy.types.Operator):
    bl_idname = 'cod_asset_importer.iwi_importer'
    bl_label = 'Import'
    bl_options = {'UNDO'}

    filepath : bpy.props.StringProperty(subtype='FILE_PATH')
    filename_ext = '.iwi'
    filter_glob : bpy.props.StringProperty(default='*.iwi', options={'HIDDEN'})
    normalmap : bpy.props.BoolProperty(
        name = 'Normal map',
        description = 'Whether the texture is a normal map or not.',
        default = False
    )

    def execute(self, context ):
        assetpath = os.path.abspath(os.path.join(os.path.join(self.filepath, os.pardir), os.pardir))
        importer.import_texture(assetpath, self.filepath, self.normalmap)
        return {'FINISHED'}

    def invoke(self, context, event):
        bpy.context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}