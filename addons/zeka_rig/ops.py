import bpy
from bpy.types import (Operator,IntProperty)



class ZEKARIG_OT_rig_ik3(bpy.types.Operator):
    """Copy all Shape Key names to Clipboard"""
    bl_idname = "zekarig.rig_ik3_swing"
    bl_label = "ZekaRig: Rig IK3-Swing"
    bl_description = "Creates an IK3 type rig mechanism. You may enter bone names manually or fill them in via selected (1:root,2:parent,3:chain1,4:chain2,5:chainr3."
    bl_options = {'REGISTER', 'UNDO'}

    check_to_run: bpy.props.BoolProperty(name="Click this to run",default=False)
    first_time_run: bpy.props.BoolProperty(options={'HIDDEN'},default=True)

    ik3_style: bpy.props.EnumProperty(items=(
            ("1","C3-IKSwing","",1),
            ("2","C3-IKPole","",3),
            ("3","C3-FK","",2),
            ("4","C3-Super","",8)
            )
    )

    component_name: bpy.props.StringProperty(default="")
    root_name: bpy.props.StringProperty(default="")
    parent_name: bpy.props.StringProperty(default="")
    bone1_name: bpy.props.StringProperty(default="")
    bone2_name: bpy.props.StringProperty(default="")
    bone3_name: bpy.props.StringProperty(default="")
    
    @classmethod
    def poll(cls, context):
        if(bpy.context.object==None or bpy.context.object.type != 'ARMATURE'):
            return False
        else:
            return True

    def execute(self, context):

        if self.first_time_run:
           self.first_time_run = False
           print("WTF: "+str(len(context.selected_pose_bones)))
           if len(context.selected_pose_bones) == 5:
                self.root_name = context.selected_pose_bones[0].name 
                self.parent_name = context.selected_pose_bones[1].name 
                self.bone1_name = context.selected_pose_bones[2].name 
                self.bone2_name = context.selected_pose_bones[3].name 
                self.bone3_name = context.selected_pose_bones[4].name 

        if self.check_to_run:
            self.check_to_run = False
            bpy.ops.object.mode_set(mode="OBJECT")
            arma = context.object
            root_bone = arma.pose.bones.get(self.root_name)
            parent_bone = arma.pose.bones.get(self.parent_name)   
            bone1 = arma.pose.bones.get(self.bone1_name) 
            bone2 = arma.pose.bones.get(self.bone2_name) 
            bone3 = arma.pose.bones.get(self.bone3_name) 

            if self.component_name=="":
                print("Fail: Component name empty.")
                return{'FINISHED'}            
            if root_bone==None:
                print("Fail: Root bone incorrect.")
                return{'FINISHED'}
            if parent_bone==None:
                print("Fail: Parent bone incorrect.")
                return{'FINISHED'}
            if bone1==None:
                print("Fail: bone1 incorrect.")
                return{'FINISHED'}
            if bone2==None:
                print("Fail: bone2 incorrect.")
                return{'FINISHED'}
            if bone3==None:
                print("Fail: bone3 incorrect.")
                return{'FINISHED'}
            
            component = ik3_swing.new_component(arma,self.component_name,[bone1.name,bone2.name,bone3.name])
            component.init()
            component.build()
            print("WE COMPLETED")
        else: 
            print("KWQEKL:QWEKLQEWhkkjh")

        return{'FINISHED'}