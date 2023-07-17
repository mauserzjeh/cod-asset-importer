import bpy

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

version = bl_info["version"]
version_str = ".".join(map(str, version))