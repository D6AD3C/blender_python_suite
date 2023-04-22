import bpy
from . import limb_component, shared, environment, foot_component
import zeka.utils as utils

import importlib

importlib.reload(limb_component)
importlib.reload(foot_component)

class Bones():

    def __init__(self):
        self.root = shared.Bone('root')
        self.hub = shared.Bone('hub')

class Component():

    def __init__(self,arma,id,env=environment.get_default()):
        self.id = id
        self.arma = arma
        self.env = env
        self.outer_name = None
        self.leg_label = "leg"
        self.heel_label = "heel"
        self.thigh_label = "thigh"
        self.shin_label = "shin"
        self.foot_label = "foot"
        self.ball_label = "ball"
        

    def run_all(self,outer_name):
        self.editmode(outer_name)
        self.posemode()

    def run_editmode(self,outer_name):

        self.outer_name = outer_name
        AFFIX = self.affix.apply
        ARMA = self.arma




        self.limb = limb_component.Component(self.arma,"limb",self.env)
        self.limb.affix = self.affix
        self.limb.type = 'LEG'
        self.limb.custom_shape_scale_modifier = 0.7
        self.limb.init(self.leg_label,self.outer_name,self.thigh_label,self.shin_label,self.foot_label)
        self.limb.begin_editmode()


        self.foot = foot_component.Component(self.arma,"foot",self.env)
        self.foot.affix = self.affix
        self.foot.heel_label = self.heel_label
        self.foot.foot_label = self.foot_label
        self.foot.ball_label = self.ball_label
        self.foot.property_show_ik = self.limb.get_property_show_ik()
        self.foot.init(self.limb.get_hub_bone())
        self.foot.begin_editmode()



        eb_ball = shared.get_bone(ARMA,AFFIX(self.ball_label))
        self.bone_ball_switch = AFFIX(self.ball_label+"_switch")
        eb_ball_switch = shared.create_editbone(ARMA,self.bone_ball_switch)
        shared.match_editbone(eb_ball_switch,eb_ball)
        eb_ball_switch.parent = shared.get_bone(ARMA,self.limb.get_end_switch_bone())
        eb_ball_switch.layers = self.env.get_layer('mech')

        self.bone_fk_control_mech = AFFIX(self.ball_label+"_fk_control_mech")
        eb_fk_control_mech = shared.create_editbone(ARMA,self.bone_fk_control_mech)
        shared.match_editbone(eb_fk_control_mech,eb_ball)
        eb_fk_control_mech.parent = shared.get_bone(ARMA,self.limb.get_end_fk_control_bone())
        eb_fk_control_mech.layers = self.env.get_layer('mech')

        self.bone_fk_control = AFFIX(self.ball_label+"_fk_control")
        eb_fk_control = shared.create_editbone(ARMA,self.bone_fk_control)
        shared.match_editbone(eb_fk_control,eb_ball)
        eb_fk_control.parent = eb_fk_control_mech
        eb_fk_control.layers = self.env.get_layer('control')

    def run_posemode(self):

        ARMA = self.arma
        AFFIX = self.affix.apply
        self.limb.begin_posemode()
        self.foot.begin_posemode()

        pb = shared.get_bone(ARMA, self.limb.get_ik_target_bone())
        utils.lock_all_bone_transforms(pb)
        cns = pb.constraints.new('COPY_TRANSFORMS')
        cns.target = ARMA
        cns.subtarget = self.foot.get_ik_target_goal_bone()
    
        pb = shared.get_bone(ARMA, self.bone_ball_switch)
        shared.lock_all_bone_transforms(pb)
        cns = pb.constraints.new('COPY_TRANSFORMS')
        cns.target = ARMA
        cns.subtarget = self.foot.get_ball_result_bone()
    
        pb = shared.get_bone(ARMA,AFFIX(self.ball_label))
        shared.lock_all_bone_transforms(pb)
        cns = pb.constraints.new('COPY_TRANSFORMS')
        cns.target = ARMA
        cns.subtarget = self.bone_fk_control
        cns = pb.constraints.new('COPY_TRANSFORMS')
        cns.target = ARMA
        cns.subtarget = self.foot.get_ik_toe_control_bone()

        return
    
        #pb = shared.get_bone(self.arma,self.limb.get_ik_end_control_bone())
        #pb.bone_group = self.env.get_bone_group(self.arma,"ik")
        #pb.custom_shape = self.env.get_custom_shape('humanfoot')
        #pb.custom_shape_translation[2] = -self.foot.bonedata_source[0].head.z
        #pb.custom_shape_scale_xyz *= 1.8