import bpy
from math import radians
from . import shared, environment




class Component():

    def __init__(self,arma,id,env=environment.get_default()):
        self.id = id
        self.arma = arma
        self.env = env
        self.affix = shared.AffixData()
        self.label = None
        self.rotation_mode = 'YXZ'
        self.layer_name = 'control'
        self.bone_group_control_name = "fk"
        self.custom_shape = None
        self.custom_shape_scale_xyz = [1,1,1]
        self.custom_shape_translation = [0,0,0]
        self.custom_shape_rotation_euler = [0,0,0]
        self.bone_source = None
        self.bone_control = None
        

    def get_source_bone(self): 
        return self.bone_source

    def init(self,label):
        self.label = label

    def begin_editmode(self):

        AFFIX = self.affix.apply
        ARMA = self.arma
        shared.activate_arma(self.arma)        
        shared.ensure_blender_mode('EDIT')

        AFFIX = self.affix.apply

        self.bone_source = AFFIX(self.label)
        eb_bone = shared.get_bone(ARMA,self.bone_source)
        eb_bone.use_connect = False
        eb_ref_parent = eb_bone.parent

        self.bone_control = AFFIX(self.label+"_control")
        eb_control = shared.create_editbone(ARMA,self.bone_control)
        shared.match_editbone(eb_control,eb_bone)
        eb_control.parent = eb_ref_parent
        eb_control.layers = self.env.get_layer(self.layer_name)


    def begin_posemode(self):
        
        ARMA = self.arma      
        AFFIX = self.affix.apply
        shared.ensure_blender_mode('POSE')

        bone_group_control = self.env.get_bone_group(ARMA,self.bone_group_control_name)

        pb = shared.get_bone(ARMA,self.bone_control)
        pb.bone_group = bone_group_control
        pb.rotation_mode = self.rotation_mode
        pb.custom_shape = self.custom_shape
        pb.custom_shape_translation = self.custom_shape_translation
        pb.custom_shape_rotation_euler = self.custom_shape_rotation_euler
        pb.custom_shape_scale_xyz = self.custom_shape_scale_xyz

        pb = shared.get_bone(ARMA,self.bone_source)
        cns = pb.constraints.new('COPY_TRANSFORMS')
        cns.target = ARMA
        cns.subtarget = self.bone_control
        