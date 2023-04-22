import bpy
from math import radians
from . import shared, environment


class Component():

    def __init__(self,arma,id,env=environment.get_default()):
        self.id = id
        self.arma = arma
        self.env = env
        self.affix = shared.AffixData()
        self.bone_outer = None
        self.label_finger = None

        self.layer_mech = self.env.get_layer('mech')
        self.layer_control = self.env.get_layer('control')
        
        self.bone_group_control_fk_name = 'control'
        self.bone_group_control_ik_name = 'control'
        self.bone_group_control_special_name = 'control'
        
        self.custom_shape_ik_control_name = 'sphere'
        self.custom_shape_fk_control_name = 'pyramid'

        self.custom_shape_fk_name = 'pyramid'
        self.custom_shape_master_name = 'tugtab'
        self.finger_bone_count = None
        self._feature_ik = True
        self.propid_ik_fk_switch = "ik_fk"

        self._feature_ik_parent_switch_target_bone = None

    def enable_feature_ik(self,parent_switch_target_bone):
        self._feature_ik_parent_switch_target_bone = parent_switch_target_bone

    def init(self,label,finger_labels,bone_outer):
        self.bone_outer = bone_outer
        self.label_finger = label
        self.finger_labels = finger_labels
        self.finger_bone_count = len(self.finger_labels)

        self.bones_source = []
        for label in finger_labels:
            self.bones_source.append(self.affix.apply(label))

        return self
    
    def begin_all(self):
        self.begin_editmode()
        self.begin_posemode()

    def begin_editmode(self):
        ARMA = self.arma
        AFFIX = self.affix.apply
        shared.activate_arma(self.arma)
        shared.ensure_blender_mode('EDIT')

        eb_outer = shared.get_bone(ARMA,self.bone_outer)
        total_finger_length = 0.0

        ebs_source = []
        for i in range(self.finger_bone_count):
            eb_source = shared.get_bone(ARMA,self.bones_source[i])
            ebs_source.append(eb_source)
            total_finger_length+=eb_source.length

        self.bone_master = AFFIX(self.label_finger+"_master")
        eb_bone_master = shared.create_editbone(ARMA,self.bone_master)
        shared.match_editbone(eb_bone_master,ebs_source[0])
        eb_bone_master.parent = eb_outer
        eb_bone_master.length = total_finger_length
        eb_bone_master.layers = self.layer_control

        self.bones_driver = []
        ebs_driver = []
        self.bones_fk_control = []
        ebs_fk_control = []
        self.bones_switch = []
        ebs_switch = []
        self.bones_mech = []
        ebs_mech = []

        for i in range(self.finger_bone_count):
            name_driver = AFFIX(self.finger_labels[i]+"_driver")
            self.bones_driver.append(name_driver)
            eb_driver = shared.create_editbone(ARMA,name_driver)
            ebs_driver.append(eb_driver)
            shared.match_editbone(eb_driver,ebs_source[i])
            if i==0:
                eb_driver.parent = eb_outer
            else: 
                eb_driver.parent = ebs_fk_control[i-1]
            eb_driver.length*=.5
            eb_driver.layers = self.layer_mech

            name_fk_control = AFFIX(self.finger_labels[i]+"_fk_control")
            self.bones_fk_control.append(name_fk_control)
            eb_fk_control = shared.create_editbone(ARMA,name_fk_control)
            ebs_fk_control.append(eb_fk_control)
            shared.match_editbone(eb_fk_control,ebs_source[i])
            eb_fk_control.parent = eb_driver
            eb_fk_control.layers = self.layer_control

            name_switch = AFFIX(self.finger_labels[i]+"_switch")
            self.bones_switch.append(name_switch)
            eb_switch = shared.create_editbone(ARMA,name_switch)
            ebs_switch.append(eb_switch)
            shared.match_editbone(eb_switch,ebs_source[i])
            if i==0:
                eb_switch.parent = eb_outer
                eb_switch.use_connect = False
            else:
                eb_switch.parent = ebs_switch[i-1]
                eb_switch.use_connect = True
           
            name_mech = AFFIX(self.finger_labels[i]+"_mech")
            self.bones_mech.append(name_mech)
            eb_mech = shared.create_editbone(ARMA,name_mech)
            ebs_mech.append(eb_mech)    
            shared.match_editbone(eb_mech,ebs_source[i])        
            if i==0:
                eb_mech.parent = eb_outer
            else:
                eb_mech.parent = ebs_fk_control[i]
            eb_mech.layers = self.layer_mech



        self.bone_control_tip = AFFIX(self.label_finger+"_fk_control")
        self.bones_fk_control.append(self.bone_control_tip)
        eb_control_tip = shared.create_editbone(ARMA,self.bone_control_tip)
        shared.match_editbone(eb_control_tip,ebs_source[self.finger_bone_count-1])
        eb_control_tip.parent = ebs_fk_control[self.finger_bone_count-1]
        shared.reverse_editbone(eb_control_tip)
        eb_control_tip.layers = self.layer_control
        eb_control_tip.length*=.5


        if self._feature_ik:
            
            self.bone_ik_parent = AFFIX(self.label_finger+"_ik_parent")
            eb_ik_parent = shared.create_editbone(ARMA,self.bone_ik_parent)
            shared.match_editbone(eb_ik_parent,ebs_source[-1])
            eb_ik_parent.parent = None
            shared.move_editbone(eb_ik_parent,eb_ik_parent.tail)
            shared.align_editbone_to_world_space(eb_ik_parent)
            eb_ik_parent.layers = self.layer_mech
        
            self.bone_ik_control = AFFIX(self.label_finger+"_ik_control")
            eb_ik_control = shared.create_editbone(ARMA,self.bone_ik_control)
            shared.match_editbone(eb_ik_control,ebs_source[-1])
            eb_ik_control.parent = eb_ik_parent
            shared.move_editbone(eb_ik_control,eb_ik_control.tail)
            eb_ik_control.layers = self.layer_control
            eb_ik_control.inherit_scale = 'AVERAGE'




    def begin_posemode(self):

        ARMA = self.arma
        shared.ensure_blender_mode('POSE')
        
        bone_group_control_fk = self.env.get_bone_group(ARMA,self.bone_group_control_fk_name)
        bone_group_control_ik = self.env.get_bone_group(ARMA,self.bone_group_control_ik_name)
        bone_group_control_special = self.env.get_bone_group(ARMA,self.bone_group_control_special_name)

        pb = shared.get_bone(ARMA,self.bone_master)
        pb.bone_group = bone_group_control_special
        pb.custom_shape = self.env.get_custom_shape(self.custom_shape_master_name)
        pb.lock_scale = [True,False,True]

        pb = shared.get_bone(ARMA,self.bones_driver[0])
        cns = pb.constraints.new('COPY_LOCATION')
        cns.target = ARMA
        cns.subtarget = self.bone_master
        cns = pb.constraints.new('COPY_ROTATION')
        cns.target = ARMA
        cns.subtarget = self.bone_master
        cns.target_space = 'LOCAL'
        cns.owner_space = 'LOCAL'


        pb = shared.get_bone(ARMA,self.bones_mech[0])
        cns = pb.constraints.new('COPY_LOCATION')
        cns.target = ARMA
        cns.subtarget = self.bones_fk_control[0]
        cns = pb.constraints.new('COPY_SCALE')
        cns.target = ARMA
        cns.subtarget = self.bones_fk_control[0]

        pb = shared.get_bone(ARMA,self.bones_fk_control[-1])
        shared.lock_all_bone_transforms(pb)
        pb.lock_location = [False,False,False]

        for i in range(self.finger_bone_count):
            
            is_first = i==0
            pb = shared.get_bone(ARMA,self.bones_driver[i])
            shared.lock_all_bone_transforms(pb)
            if is_first:
                pass
            else:
                pb.rotation_mode = 'YZX'
                driver = pb.driver_add('rotation_euler',0).driver
                driver.type = 'SCRIPTED'
                driver.expression = '(1-scale_y)*pi'
                var = driver.variables.new()
                var.type = 'SINGLE_PROP'
                var.name = 'scale_y' 
                var.targets[0].id = ARMA 
                var.targets[0].data_path = 'pose.bones["'+self.bone_master+'"].scale.y' 


            pb = shared.get_bone(ARMA,self.bones_fk_control[i])
            pb.custom_shape = self.env.get_custom_shape(self.custom_shape_fk_name)
            pb.custom_shape_transform = shared.get_bone(ARMA,self.bones_switch[i])
            pb.bone_group = bone_group_control_fk
            pb.custom_shape_scale_xyz = [0.25,0.25,0.25]

            pb = shared.get_bone(ARMA,self.bones_switch[i])
            shared.lock_all_bone_transforms(pb)
            cns = pb.constraints.new('COPY_TRANSFORMS')
            cns.target = ARMA
            cns.subtarget = self.bones_mech[i]
            if i!=0:
                pb.ik_stiffness_y = 0.99
                pb.ik_stiffness_z = 0.99

            pb = shared.get_bone(ARMA,self.bones_source[i])
            cns = pb.constraints.new('COPY_TRANSFORMS')
            cns.target = ARMA
            cns.subtarget = self.bones_switch[i]

            pb = shared.get_bone(ARMA,self.bones_mech[i])
            shared.lock_all_bone_transforms(pb)
            cns = pb.constraints.new('STRETCH_TO')
            cns.volume = 'NO_VOLUME'
            cns.target = ARMA
            cns.subtarget = self.bones_fk_control[i+1]


        if self._feature_ik:

            pb = shared.get_bone(ARMA,self.bone_ik_parent)
            shared.lock_all_bone_transforms(pb)

            pb = shared.get_bone(ARMA,self.bone_ik_control)
            shared.lock_all_bone_transforms(pb)
            pb.lock_location=[False,False,False]                
            shared.add_custom_property(pb,self.propid_ik_fk_switch,"IK / FK",0.0)
            shared.add_custom_property(pb,"ik_parent","IK Parent",1.0)
            pb.bone_group = bone_group_control_ik
            pb.custom_shape = self.env.get_custom_shape(self.custom_shape_ik_control_name)

            pb = shared.get_bone(ARMA,self.bones_switch[-1])
            pb.lock_ik_y = True
            pb.lock_ik_z = True
            shared.lock_all_bone_transforms(pb)
            cns = pb.constraints.new('IK')
            cns.name = "IK"
            cns.target = ARMA
            cns.use_tail = True
            cns.use_stretch = False
            cns.subtarget = self.bone_ik_control
            cns.chain_count = self.finger_bone_count
            driver = cns.driver_add('influence').driver
            driver.type = 'SUM'
            var = driver.variables.new()
            var.type = 'SINGLE_PROP'
            var.targets[0].id = self.arma                
            var.targets[0].data_path = shared.write_posebone_datapath(self.bone_ik_control,self.propid_ik_fk_switch)

            pb = shared.get_bone(ARMA,self.bone_ik_parent)
            cns = pb.constraints.new('ARMATURE')
            cns.name = "switch_parent"
            target = cns.targets.new()
            target.target = ARMA
            target.subtarget = self._feature_ik_parent_switch_target_bone