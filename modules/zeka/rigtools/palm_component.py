import bpy
from math import radians
import zeka.utils as utils
from . import shared, environment

class Component():

    def __init__(self,arma,id,env=environment.get_default()):
        self.id = id
        self.arma = arma
        self.env = env
        self.palm_label = "palm"
        self.affix = shared.AffixData()
        self.source_labels = ["palm1","palm2","palm3","palm4"]
        self.outer_bone_name = None

        self.total_digits = None
        self.layer_mech = self.env.get_layer('mech')
        self.layer_control = self.env.get_layer('control')

        self.feature_inner_control = True
        self.feature_fk_controls = True        

        self.custom_shape_control_fk_name = 'staff'
        self.custom_shape_control_edge_name = 'sleeve'

        self.bone_group_control_fk_name = "fk"
        self.bone_group_control_edge_name = "special"

        self.bones_source = []
        self.bone_outside_control = None
        self.bone_inside_control = None

    def get_source_bone(self,index):
        return self.bones_source[index]
    
    def init(self,bone_outer):
        self.bone_outer = bone_outer
        self.total_digits = len(self.source_labels)

    def begin_editmode(self):
        
        ARMA = self.arma
        AFFIX = self.affix.apply

        shared.activate_arma(self.arma)        
        shared.ensure_blender_mode('EDIT')

        for label in self.source_labels:
            self.bones_source.append(AFFIX(label))

        ebs_source = []
        for bone in self.bones_source:
            ebs_source.append(shared.get_bone(ARMA,bone))
        
        eb_outer = shared.get_bone(ARMA,self.bone_outer)
                

        self.bone_outside_control = AFFIX(self.palm_label+"_outer_control")
        eb_outside_control = shared.create_editbone(ARMA,self.bone_outside_control)  
        shared.match_editbone(eb_outside_control,ebs_source[-1])
        eb_outside_control.parent = eb_outer
        eb_outside_control.layers = self.layer_control

        if self.feature_inner_control:

            self.bone_inside_control = AFFIX(self.palm_label+"_inside_control")
            eb_inside_control = shared.create_editbone(ARMA,self.bone_inside_control)  
            shared.match_editbone(eb_inside_control,ebs_source[0])
            eb_inside_control.parent = eb_outer
            eb_inside_control.layers = self.layer_control

        self.bones_mech = []
        self.bones_fk = []
        self.bones_cap = []

        ebs_mech = []
        ebs_fk = []
        ebs_cap = []

        for i in range(self.total_digits):
            if self.feature_fk_controls:
                name_mech = AFFIX(self.source_labels[i]+"_mech")
                self.bones_mech.append(name_mech)
                eb_mech = shared.create_editbone(ARMA,name_mech)
                ebs_mech.append(eb_mech)
                shared.match_editbone(eb_mech,ebs_source[i])
                eb_mech.parent = eb_outer
                eb_mech.inherit_scale = 'NONE'
                eb_mech.layers = self.layer_mech
            
                name_fk = AFFIX(self.source_labels[i]+"_fk_control")
                self.bones_fk.append(name_fk)
                eb_fk = shared.create_editbone(ARMA,name_fk)
                ebs_fk.append(eb_fk)
                shared.match_editbone(eb_fk,ebs_source[i])
                eb_fk.parent = eb_mech
                eb_fk.inherit_scale = 'ALIGNED'
                eb_fk.layers = self.layer_control

            name_cap = AFFIX(self.source_labels[i]+"_cap")
            self.bones_cap.append(name_cap)
            eb_cap = shared.create_editbone(ARMA,name_cap)
            ebs_cap.append(eb_cap)
            shared.match_editbone(eb_cap,ebs_source[i])
            eb_cap.layers = self.layer_mech

            if not self.feature_fk_controls :
                eb_cap.parent = eb_outer
                eb_cap.inherit_scale = 'NONE'
            else:
                eb_cap.parent = eb_fk
        
    def begin_posemode(self):

        ARMA = self.arma
        AFFIX = self.affix.apply

        bone_group_control_fk = self.env.get_bone_group(ARMA,self.bone_group_control_fk_name)
        bone_group_control_edge = self.env.get_bone_group(ARMA,self.bone_group_control_edge_name)

        shared.activate_arma(self.arma)        
        shared.ensure_blender_mode('POSE')
        
        pb = shared.get_bone(ARMA,self.bone_outside_control)
        pb.rotation_mode = "YXZ"
        pb.lock_scale = [True,True,True]
        pb.custom_shape = self.env.get_custom_shape(self.custom_shape_control_edge_name)
        pb.bone_group = bone_group_control_edge

        pb = shared.get_bone(ARMA,self.bone_inside_control)
        pb.rotation_mode = "YXZ"
        pb.lock_scale = [True,True,True]
        pb.custom_shape = self.env.get_custom_shape(self.custom_shape_control_edge_name)
        pb.bone_group = bone_group_control_edge
        
        if self.feature_fk_controls :
            for bone in self.bones_mech:
                pb = shared.get_bone(ARMA,bone)
                utils.lock_all_bone_transforms(pb)
                cns = pb.constraints.new('COPY_SCALE')
                cns.target = ARMA
                cns.subtarget = self.bone_outer

            for bone in self.bones_fk:
                pb = shared.get_bone(ARMA,bone)
                pb.bone_group = bone_group_control_fk
                pb.rotation_mode = "YXZ"
                pb.custom_shape = self.env.get_custom_shape(self.custom_shape_control_fk_name)

        for bone in self.bones_cap:
            pb = shared.get_bone(ARMA,bone)
            pb.rotation_mode = "YXZ"
            utils.lock_all_bone_transforms(pb)


        bone_chain_that_gets_constraints = self.bones_mech
        influence_diminisher = 1.0/(self.total_digits-1)
        for i in range(self.total_digits-1):
            pb = shared.get_bone(ARMA,bone_chain_that_gets_constraints[-(i+1)])
            cns = pb.constraints.new('COPY_TRANSFORMS')
            cns.target = ARMA
            cns.subtarget = self.bone_outside_control            
            cns.target_space = 'LOCAL'
            cns.owner_space = 'LOCAL'
            cns.influence = 1.0 - (i*influence_diminisher)
            
            if self.feature_inner_control:
                pb = shared.get_bone(ARMA,bone_chain_that_gets_constraints[i])
                cns = pb.constraints.new('COPY_TRANSFORMS')
                cns.target = ARMA
                cns.subtarget = self.bone_inside_control            
                cns.target_space = 'LOCAL'
                cns.owner_space = 'LOCAL'
                cns.influence = 1.0 - (i*influence_diminisher)

        for i in range(self.total_digits):
            pb = shared.get_bone(ARMA,self.bones_source[i])
            cns = pb.constraints.new('COPY_TRANSFORMS')
            cns.target = ARMA
            cns.subtarget = self.bones_cap[i]

