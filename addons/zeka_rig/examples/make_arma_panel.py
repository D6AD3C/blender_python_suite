import bpy
from bpy.types import Operator, Menu, Panel
from bl_operators.presets import AddPresetBase

class DATA_PT_test(bpy.types.Panel):
    bl_label = "Zeka"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        obj = context.object
        if not context.object:
            return False
        return obj.type == 'ARMATURE'

    def draw(self, context):
        C = context
        layout = self.layout
        obj = C.object



classes = (
    DATA_PT_test,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
        #bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()