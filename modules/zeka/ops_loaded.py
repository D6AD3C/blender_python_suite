import bpy
from bpy.types import (Operator,IntProperty)


import bpy
from bpy.types import (Operator)


class RIGBUDDY_OT_AttachHead(Operator):
    """Copy all Shape Key names to Clipboard"""
    bl_idname = "rigbuddy.attachhead"
    bl_label = "Attach Head"
    bl_description = "Snap selected bones to the active bone."
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if(context.object.type == 'OBJECT'):
            return False
        else:
            return True

    def execute(self, context):
        print("WE FUCK")
        return{'FINISHED'}
    

classes = (
    RIGBUDDY_OT_AttachHead
)

from bpy.utils import register_class
register_class(RIGBUDDY_OT_AttachHead)
print("ok!")