import bpy
from . import shared, environment
from . import node_component, spine_component, neck_component, arm_component, palm_component, finger_component, leg_biped_component


import importlib
importlib.reload(environment)
importlib.reload(node_component)
importlib.reload(spine_component)
importlib.reload(neck_component)
importlib.reload(arm_component)
importlib.reload(leg_biped_component)
importlib.reload(palm_component)
importlib.reload(finger_component)

from math import radians

class Component():

    def __init__(self,arma,id,env=environment.get_default()):
        self.id = id
        self.env = env
        self.arma = arma

        self.root = "root"      
        self.spine_labels = ["pelvis","spine1","spine2","spine3","spine4","spine5"]  
        self.shoulder_label = "shoulder"
        self.arm_label = "arm"
        self.upperarm_label = "upperarm"
        self.forearm_label = "forearm"
        self.hand_label = "hand"
        self.palm_labels = ["palm1","palm2","palm3","palm4"] 
        self.finger_labels = ["finger_thumb","finger_index","finger_middle","finger_ring","finger_pinky"]
        self.leg_label = "leg"
        self.heel_label = "heel"
        self.pelvis_label = "pelvis"
        self.thigh_label = "thigh"
        self.shin_label = "shin"
        self.foot_label = "foot"
        self.ball_label = "ball"
        
    
    def run(self):

        print("Building Humanoid Component...")
        ARMA = self.arma
        shared.activate_arma(self.arma)
        ENV = self.env

        self.affix = shared.AffixData().set_suffix("_l")

        #take some measurements
        shared.activate_arma(self.arma)
        bpy.ops.object.mode_set(mode='EDIT')        
        eb_shoulder = shared.get_bone_adaptive(self.arma,self.affix.apply(self.shoulder_label))
        eb_upperarm = shared.get_bone_adaptive(self.arma,self.affix.apply(self.upperarm_label))
        distance_shoulder_to_upperarm = (eb_shoulder.head - eb_upperarm.head).length

        ROOT = node_component.Component(ARMA,"root",env=ENV)
        ROOT.affix = shared.AffixData()
        ROOT.custom_shape = self.env.get_custom_shape("humanroot")
        ROOT.custom_shape_scale_xyz = [4,4,4]
        ROOT.init(self.root)
        ROOT.begin_editmode()

        SPINE = self.spine_component = spine_component.Component(ARMA,"spine",env=ENV)   
        SPINE.init(self.spine_labels)     
        SPINE.begin_editmode()
        SPINE.begin_posemode()
         
        NECK = self.neck_component = neck_component.Component(ARMA,"neck",env=ENV)   
        NECK.init(['neck1','neck2','head'])    
        NECK.enable_connection_with_spine(
            SPINE.get_torso_control_bone(),
            SPINE.get_attribute_hub_bone(),
            SPINE.get_head_connector_bone()
        )
        NECK.begin_editmode()

        ROOT.begin_posemode()
        NECK.begin_posemode()

        for i in range(2):
            if i == 1:
                self.affix = shared.AffixData().set_suffix("_r")

            AFFIX = self.affix.apply
   
            SHOULDER = node_component.Component(self.arma,AFFIX("shoulder"),env=ENV)
            SHOULDER.affix = self.affix
            SHOULDER.custom_shape = self.env.get_custom_shape("square")
            SHOULDER.custom_shape_scale_xyz = [0.6,1,1]
            SHOULDER.custom_shape_rotation_euler = [radians(90),0,0]
            SHOULDER.custom_shape_translation = [0,distance_shoulder_to_upperarm,distance_shoulder_to_upperarm/2]
            SHOULDER.init(self.shoulder_label)
            SHOULDER.begin_editmode()

            ARM = self.arm_component = arm_component.Component(self.arma,AFFIX(self.arm_label+"_limb"),env=ENV)
            ARM.affix = self.affix
            ARM.arm_label = self.arm_label
            ARM.upperarm_label = self.upperarm_label
            ARM.forearm_label = self.forearm_label
            ARM.hand_label = self.hand_label
            ARM.add_parent_switch_ik_hand_bones([self.root,SPINE.get_torso_control_bone(),SHOULDER.get_source_bone()])
            ARM.add_parent_switch_ik_pole_bones([self.root,SPINE.get_torso_control_bone(),SHOULDER.get_source_bone()])
            ARM.init(SHOULDER.get_source_bone())
            ARM.begin_editmode()

            
            PALM = self.palm_component = palm_component.Component(self.arma,AFFIX("palm"),env=ENV)
            PALM.affix = self.affix
            PALM.source_labels = self.palm_labels
            PALM.init(ARM.get_hand_source_bone())
            PALM.begin_editmode()
            

            finger_components = []
            for i in range(len(self.finger_labels)):
                
                FINGER = finger_component.Component(self.arma,self.finger_labels[i],env=self.env)
                FINGER.affix = self.affix
                FINGER.enable_feature_ik(AFFIX(self.hand_label))

                #IS THUMB
                finger_array = [self.finger_labels[i]+"1",self.finger_labels[i]+"2",self.finger_labels[i]+"3"]
                if i==0 :
                    FINGER.init(self.finger_labels[i],finger_array, AFFIX("hand"))
                else:
                    FINGER.init(self.finger_labels[i], finger_array, PALM.get_source_bone(i-1)) 
                FINGER.begin_editmode()
                finger_components.append(FINGER)


            LEG = self.arm_component = leg_biped_component.Component(self.arma,AFFIX(self.leg_label),env=ENV)
            LEG.affix = self.affix
            LEG.leg_label = self.leg_label
            LEG.heel_label = self.heel_label
            LEG.thigh_label = self.thigh_label
            LEG.shin_label = self.shin_label
            LEG.foot_label = self.foot_label
            LEG.ball_label = self.ball_label            
            LEG.run_editmode(self.pelvis_label)

        
            SHOULDER.begin_posemode()
            ARM.begin_posemode()
            PALM.begin_posemode()
            LEG.run_posemode()
            for finger in finger_components:
                finger.begin_posemode()
            

