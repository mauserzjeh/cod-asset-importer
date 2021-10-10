import bpy

def select_hierarchy(obj: bpy.types.Object) -> None:
   obj.select_set(True)
   for children in obj.children:
       select_hierarchy(children)

def copy_object_hierarchy(obj: bpy.types.Object) -> list[bpy.types.Object]:
    select_hierarchy(obj)
    bpy.ops.object.duplicate()
    return bpy.context.selected_objects