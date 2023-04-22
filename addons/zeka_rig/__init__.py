# ----------------------------------------------------------
# File __init__.py
# ----------------------------------------------------------
#
# zeka_rig - Copyright (C) 2023 Alex Zeka
#
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
#
# ----------------------------------------------------------

bl_info = {
    "name": "Zeka Rig",
    "description": "When you got no buddies to help, make your own, BlenderBuddy",
    "author": "Alex Zeka",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "Various Menus on the View3D",    
    "warning": "This is used primarily for my own pipeline, not thoroughly tested in a million different use cases, this is an early version so large changes might be made.",
    "wiki_url": "",    
    "category": 'Mesh'}


import bpy
from bpy.types import (Menu,Panel,Operator)
import importlib
from . import ops
importlib.reload(ops)

#menufunction
def menufunc_rig_ik3_swing(self, context):
    self.layout.operator(ops.ZEKARIG_OT_rig_ik3.bl_idname)

def menu_func2(self, context):
    self.layout.menu(VIEW3D_MT_blenderbuddy_armature.bl_idname)
    # bl_idname should be in form of "something.something"
    # or YourClass.bl_idname

class VIEW3D_MT_blenderbuddy_armature(Menu):
    bl_label = "Blender Buddy"
    bl_idname = "blenderbuddy.armature_menu"

    def draw(self, context):
        layout = self.layout

class ZEKARIG_PT_View3D(Panel):
    """Shape Key Tools Panel layout"""
    bl_label = "Zeka Rig"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    #bl_context = 'objectmode'
    #bl_category = "Tools"    
    bl_category = "Zeka Rig" 


    @classmethod
    def poll(self,context):        
        return True

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        #layout.row().prop(context.scene.zekarig_globals, 'arma_1') # Layout.prop(data, 'prop') # show data.prop
        #layout.row().prop(context.scene.zekarig_globals, 'csv_1')

        self.layout.label(text="Hello")
        #if 1==2:
        if context.object.type == 'ARMATURE':
            layout.operator(ops.ZEKARIG_OT_rig_ik3.bl_idname, icon='BONE_DATA')


 

class ZekaRigGlobalSettings(bpy.types.PropertyGroup):
    arma_1: bpy.props.PointerProperty(type=bpy.types.Armature
      #update= lambda self, context: weightUpdate(self, context, 1)
    )

classes = (
    ZekaRigGlobalSettings,
    ZEKARIG_PT_View3D,
    VIEW3D_MT_blenderbuddy_armature,
    ops.ZEKARIG_OT_rig_ik3
)







def register():

    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.Scene.zekarig_globals = bpy.props.PointerProperty(type=ZekaRigGlobalSettings)

    bpy.types.VIEW3D_MT_pose.append(menufunc_rig_ik3_swing)


def unregister():    

    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.zekarig_globals