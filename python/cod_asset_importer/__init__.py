bl_info = {
    "name": "Call of Duty Asset Importer",
    "description": "Import Call of Duty assets",
    "author": "Soma Rádóczi",
    "version": (3, 2, 0),
    "blender": (3, 0, 0),
    "location": "File > Import -> CoD Asset Importer",
    "category": "Import-Export",
    "warning": "This addon is still in development",
}

version = bl_info["version"]

try:
    from bpy.app import version as bpy_version

    if bpy_version is not None:
        from . import addon, operators

        def register():
            operators.register()
            addon.register()

        def unregister():
            addon.unregister()
            operators.unregister()

except:
    pass
