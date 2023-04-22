import bpy
from math import radians
from . import limb_component, shared, environment
import zeka.utils as utils

import importlib
importlib.reload(limb_component)

class Component():

    def __init__(self,arma,id,env=environment.get_default()):
        self.id = id
        self.arma = arma
        self.env = env
        self.affix = shared.AffixData()
        self.arm_label = "arm"
        self.upperarm_label = "upperarm"
        self.forearm_label = "forearm"
        self.hand_label = "hand"
        self.outer_name = None       

        self.parent_switch_ik_hand_bones = []
        self.parent_switch_ik_pole_bones = []

    def add_parent_switch_ik_hand_bones(self,bones):
        self.parent_switch_ik_hand_bones += bones
    
    def add_parent_switch_ik_pole_bones(self,bones):
        self.parent_switch_ik_pole_bones += bones

    def get_hand_source_bone(self):
        return self.affix.apply(self.hand_label)
    
    def get_ik_end_control_bone(self):
        return self.limb.get_ik_end_control_bone()
    
    def init(self,bone_outer):
        self.outer_name = bone_outer
    def begin_all(self):
        self.begin_editmode()
        self.begin_posemode()

    def begin_editmode(self):

        ARMA = self.arma
        AFFIX = self.affix.apply
        self.limb = limb_component.Component(self.arma,"limb",self.env)
        self.limb.affix = self.affix
        self.limb.type = 'ARM'
        self.limb.add_parent_switch_ik_end_bones(self.parent_switch_ik_hand_bones)
        self.limb.add_parent_switch_ik_pole_bones(self.parent_switch_ik_pole_bones)
        self.limb.init(self.arm_label,self.outer_name,self.upperarm_label,self.forearm_label,self.hand_label)
        self.limb.begin_editmode()
        

    def begin_posemode(self):
        self.limb.begin_posemode()
        pass