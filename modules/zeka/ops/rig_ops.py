
#developer extras might need to be enabled to have these work

import bpy
from bpy.types import (Operator,IntProperty)
import zeka.utilities.rig_utils as rig_utils
import importlib
importlib.reload(rig_utils)

class ZEKA_OT_PoseboneMagicRotate(Operator):
    """Rotate a posebone to an exact angle magically"""
    bl_idname = "zeka.posebonemagicrotate"
    bl_label = "ZEKA: Posebone Magic Rotate"
    bl_description = "Rotate a posebone to an exact angle magically"
    bl_options = {'REGISTER','UNDO'}

    rotation_x: bpy.props.IntProperty(name = 'Rotation X', default=0)
    rotation_y: bpy.props.IntProperty(name = 'Rotation Y', default=0)
    roll: bpy.props.IntProperty(name = 'Roll', default=0)

    @classmethod
    def poll(cls, context):
        if(context.object.type != 'ARMATURE' or bpy.context.object.mode != 'POSE'):
            return False
        else:
            return True

    def execute(self, context):
        pb = bpy.context.selected_pose_bones[-1]
        rig_utils.posebone_magic_rotate(pb,[self.rotation_x,self.rotation_y,self.roll])
        return{'FINISHED'}
    

class ZEKA_OT_SelectBonesBySide(Operator):
    """Rotate a posebone to an exact angle magically"""
    bl_idname = "zeka.select_bones_by_side"
    bl_label = "ZEKA: Select Bones By Side"
    bl_description = "Rotate a posebone to an exact angle magically"
    bl_options = {'REGISTER','UNDO'}

    axis_side_enum: bpy.props.EnumProperty(items = [ 
         ('0','X -',''),
         ('1','X +',''),
         ('2','Y -',''),
         ('3','Y +',''),
         ('4','Z -',''),
         ('5','Z +','')],
         name="Axis Side")


    @classmethod
    def poll(cls, context):
        if(context.object.type == 'OBJECT'):
            return False
        else:
            return True

    def execute(self, context):
        arma = bpy.context.view_layer.objects.active
        #bpy.context.selected_pose_bones = []
        for pb in arma.pose.bones:
            pb.bone.select = False
            global_location = arma.matrix_world @ pb.matrix @ pb.location
            if global_location.x < -.0000001:
                pb.bone.select = True


        return{'FINISHED'}



class ZEKA_OT_SnapBoneToBone(Operator):
    """Copy all Shape Key names to Clipboard"""
    bl_idname = "zeka.snap_bone_to_bone"
    bl_label = "Snap selected edit-bones to active edit-bone"
    bl_description = "Snap selected bones to the active bone."
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(cls, context):
        if(bpy.context.object!=None or bpy.context.object.type != 'ARMATURE' or context.active_object.mode!='EDIT'):
            return False
        else:
            return True

    def execute(self, context):
        active = context.object.data.edit_bones.active
        bones = context.selected_editable_bones        
        bones.remove(active)
        rig_utils.snap_editbone_to_editbone(bones,active)
        return{'FINISHED'}


class ZEKA_OT_SpaceBonesAlongBone(Operator):
    """Copy all Shape Key names to Clipboard"""
    bl_idname = "zeka.space_bones_along_bones"
    bl_label = "Space selected bones evenly along the vector of the active bone"
    bl_description = "Snap selected bones to the active bone."
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(cls, context):
        if(bpy.context.object.type != 'ARMATURE' or context.active_object.mode!='EDIT'):
            return False
        else:
            return True

    def execute(self, context):
        active = context.object.data.edit_bones.active
        bones = context.selected_editable_bones        
        bones.remove(active)
        rig_utils.space_bone_along_bone(bones,active)
        return{'FINISHED'}
    
class ZEKA_OT_ApplyAllTargetingArmaModifiers(Operator):
    """Rotate a posebone to an exact angle magically"""
    bl_idname = "zeka.apply_all_targeting_arma_modifiers"
    bl_label = "ZEKA: Apply All Targeting Arma Modifiers"
    bl_description = "Rotate a posebone to an exact angle magically"
    bl_options = {'REGISTER','UNDO'}

    force_preserve: bpy.props.BoolProperty(name="Force Preserve",default=True)


    @classmethod
    def poll(cls, context):
        if(context.object.type != 'ARMATURE'):
            return False
        else:
            return True

    def execute(self, context):
        arma = bpy.context.view_layer.objects.active
        rig_utils.apply_all_targeting_arma_modifiers(arma,self.force_preserve)
        return{'FINISHED'}



class ZEKA_OT_ApplyPoseWithAllObjects(Operator):
    """Rotate a posebone to an exact angle magically"""
    bl_idname = "zeka.apply_pose_with_all_objects"
    bl_label = "ZEKA: Apply Pose With All Objects"
    bl_description = "Apply a pose and also apply and recreate all targeting object armature modifiers"
    bl_options = {'REGISTER','UNDO'}

    force_preserve: bpy.props.BoolProperty(name="Force Preserve",default=True)


    @classmethod
    def poll(cls, context):
        if(context.object.type != 'ARMATURE'):
            return False
        else:
            return True

    def execute(self, context):
        arma = bpy.context.view_layer.objects.active
        rig_utils.apply_pose_with_all_objects(arma,self.force_preserve)
        return{'FINISHED'}
    
classes = [
    ZEKA_OT_PoseboneMagicRotate,
    ZEKA_OT_SelectBonesBySide,
    ZEKA_OT_ApplyAllTargetingArmaModifiers,
    ZEKA_OT_SnapBoneToBone,
    ZEKA_OT_SpaceBonesAlongBone,
    ZEKA_OT_ApplyPoseWithAllObjects
]




from bpy.utils import register_class
for cls in classes:
    register_class(cls)