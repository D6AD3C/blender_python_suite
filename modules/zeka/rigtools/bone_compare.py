import bpy

class Bone():

    def __init__(self,arma,name):
        self.arma = arma
        self.name = name
        self.keys = dict() 

    def gather_editmode(self):
        bpy.context.view_layer.objects.active = self.arma
        bpy.ops.object.mode_set(mode='EDIT')
        eb = self.arma.data.edit_bones.get(self.name)
        if eb==None:
            raise Exception("Bone missing: "+self.name)
        self.keys['inherit_scale'] = eb.inherit_scale
        self.keys['use_connect'] = eb.use_connect
        self.keys['use_local_location'] = eb.use_local_location
        self.keys['use_inherit_rotation'] = eb.use_inherit_rotation
        self.keys['use_relative_parent'] = eb.use_relative_parent

        parent = eb.parent
        if parent != None:
            parent = eb.parent.name
        self.keys['parent'] = parent

    def gather_posemode(self):
        bpy.context.view_layer.objects.active = self.arma
        bpy.ops.object.mode_set(mode='POSE')
        pb = self.arma.pose.bones.get(self.name)
        self.keys['rotation_mode'] = pb.rotation_mode
        self.keys['ik_stretch'] = pb.ik_stretch
        self.keys['lock_ik_x'] = pb.lock_ik_x
        self.keys['lock_ik_y'] = pb.lock_ik_y
        self.keys['lock_ik_z'] = pb.lock_ik_z
        self.keys['ik_stiffness_x'] = pb.ik_stiffness_x
        self.keys['ik_stiffness_y'] = pb.ik_stiffness_y
        self.keys['ik_stiffness_z'] = pb.ik_stiffness_z
        self.keys['lock_location'] = pb.lock_location
        self.keys['lock_rotation'] = pb.lock_rotation
        self.keys['lock_scale'] = pb.lock_scale
        self.keys['constraints'] = len(pb.constraints)
        pass

    def compare_dict(self,bone,key):

        if(key=='lock_location' or key=="lock_rotation" or key=="lock_scale"):
            if(self.keys[key][0]!=bone.keys[key][0] or\
                self.keys[key][1]!=bone.keys[key][1] or\
                self.keys[key][2]!=bone.keys[key][2]):
                print(self.name+": key does not match-"+key)

        elif self.keys[key]!=bone.keys[key]:
           print(self.name+": key does not match-"+key+" should be "+str(bone.keys[key]))

    def compare(self,bone):
        CB = self.compare_dict
        CB(bone,'use_connect')
        CB(bone,'inherit_scale')
        CB(bone,'rotation_mode')
        CB(bone,'ik_stretch')
        CB(bone,'lock_ik_x')
        CB(bone,'lock_ik_y')
        CB(bone,'lock_ik_z')
        CB(bone,'ik_stiffness_x')
        CB(bone,'ik_stiffness_y')
        CB(bone,'ik_stiffness_z')
        CB(bone,'use_local_location')
        CB(bone,'use_inherit_rotation')
        CB(bone,'use_relative_parent')
        CB(bone,'lock_location')
        CB(bone,'lock_rotation')
        CB(bone,'lock_scale')
        CB(bone,'constraints')
        #CB(bone,'parent')

class BoneComparer():

    def __init__(self,arma1,arma2):
        self.arma1 = arma1
        self.arma2 = arma2
        self.bone_key_11 = dict()
        self.bone_key_12 = dict()
        self.bone_key_21 = dict()
        self.bones = []

    def add(self,bone1,bone2):
        b1 = Bone(self.arma1,bone1)
        b2 = Bone(self.arma2,bone2)

        self.bones.append(b1)
        self.bones.append(b2)
        self.bone_key_11[b1.name] = b1
        self.bone_key_12[b1.name] = b2
        self.bone_key_21[b2.name] = b1

    def compare(self):
        for bone in self.bones:
            bone.gather_editmode()
        for bone in self.bones:
            bone.gather_posemode()

        for k,v in self.bone_key_12.items():
            self.bone_key_11[k].compare(v)

ARMA1 = bpy.context.scene.objects['rig_proxy']
ARMA2 = bpy.context.scene.objects['rig.002']    
bc = BoneComparer(ARMA1,ARMA2)


bc.add("upperarm_hub_control_l","upper_arm_parent.L")
bc.add("upperarm_hub_mech_l","MCH-upper_arm_parent.L")
bc.add("upperarm_switch_l","ORG-upper_arm.L")
bc.add("shin_switch_l","ORG-shin.L")
bc.add("foot_switch_l","ORG-foot.L")
bc.add("toe_switch_l","ORG-toe.L")
bc.add("upperarm_tweak_mech_l","MCH-upper_arm_tweak.L")
bc.add("upperarm_tweak_l","upper_arm_tweak.L")
bc.add("upperarm_l","DEF-upper_arm.L")
bc.add("shin_l","DEF-shin.L")
bc.add("foot_l","DEF-foot.L")
bc.add("toe_l","DEF-toe.L")
bc.add("upperarm_fk_control_l","upper_arm_fk.L")
bc.add("shin_fk_control_l","shin_fk.L")
bc.add("foot_fk_mech_l","MCH-foot_fk.L")
bc.add("foot_fk_control_l","foot_fk.L")
#bc.add("ball_fk_mech_l","MCH-toe_fk.L")
#bc.add("ball_fk_control_l","toe_fk.L")
bc.add("thigh_ik_end_control_l","thigh_ik.L")
bc.add("thigh_ik_swing_l","MCH-thigh_ik_swing.L")
bc.add("shin_ik_l","MCH-shin_ik.L")
bc.add("foot_ik_target_l","MCH-thigh_ik_target.L")
bc.add("foot_l_ik_control_parent_l","MCH-foot_ik.parent.L")
bc.add("foot_l_ik_control_l","foot_ik.L")

#bc.add("","VIS_thigh_ik_pole_l")
bc.add("thigh_hub_control_l","thigh_parent.L")
bc.add("thigh_hub_mech_l","MCH-thigh_parent.L")
bc.add("thigh_switch_l","ORG-thigh.L")
bc.add("shin_switch_l","ORG-shin.L")
bc.add("foot_switch_l","ORG-foot.L")
bc.add("toe_switch_l","ORG-toe.L")
bc.add("thigh_tweak_mech_l","MCH-thigh_tweak.L")
bc.add("thigh_tweak_l","thigh_tweak.L")
bc.add("thigh_l","DEF-thigh.L")
bc.add("shin_l","DEF-shin.L")
bc.add("foot_l","DEF-foot.L")
bc.add("toe_l","DEF-toe.L")
bc.add("thigh_fk_control_l","thigh_fk.L")
bc.add("shin_fk_control_l","shin_fk.L")
bc.add("foot_fk_mech_l","MCH-foot_fk.L")
bc.add("foot_fk_control_l","foot_fk.L")
#bc.add("ball_fk_mech_l","MCH-toe_fk.L")
#bc.add("ball_fk_control_l","toe_fk.L")
bc.add("thigh_ik_end_control_l","thigh_ik.L")
bc.add("thigh_ik_swing_l","MCH-thigh_ik_swing.L")
bc.add("shin_ik_l","MCH-shin_ik.L")
bc.add("foot_ik_target_l","MCH-thigh_ik_target.L")
bc.add("foot_l_ik_control_parent_l","MCH-foot_ik.parent.L")
bc.add("foot_l_ik_control_l","foot_ik.L")
bc.add("foot_l_ik_scale_l","MCH-foot_ik_scale.L")
bc.add("foot_l_ik_pivot_control_l","foot_ik_pivot.L")
bc.add("foot_ik_spin_l","foot_spin_ik.L")
bc.add("foot_heel_control_l","foot_heel_ik.L")
bc.add("foot_heel_rock2_l","MCH-heel.02_rock2.L")
bc.add("foot_heel_rock1_l","MCH-heel.02_rock1.L")
bc.add("foot_heel_roll2_l","MCH-heel.02_roll2.L")
bc.add("foot_heel_roll1_l","MCH-heel.02_roll1.L")
bc.add("foot_roll_l","MCH-foot_roll.L")
bc.add("foot_toe_ik_parent_l","MCH-toe_ik_parent.L")
bc.add("foot_toe_ik_control_l","toe_ik.L")
print("starting")
bc.compare()