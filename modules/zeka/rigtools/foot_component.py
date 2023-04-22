import bpy
from math import radians
import zeka.utils as utils
from . import shared, environment, limb_component

class Component():

    def __init__(self,arma,id,env=environment.get_default()):
        self.id = id
        self.arma = arma
        self.env = env
        self.affix = shared.AffixData()
        self.bone_root = 'root'
        self.bone_foot = None
        self.bone_ball = None
        
        self.premade_control_name = None
        self.foot_label = "foot"
        self.ball_label = "ball"
        self.toe_label = "toe"
        self.heel_label = "heel"        
        self.rock_label = "rock"
        self.roll_label = "roll"
        
        self.bonedata_source = None

        self.b_invert_x = False
        self.bone_group_control_ik_name = "ik"
        self.bone_group_control_fk_name = "fk"

        self.custom_shape_heel_control_name = "plusarrow"
        self.custom_shape_foot_spin_name = "plusarrow"
        self.custom_shape_foot_ik_control_name = 'humanfoot'
        self.custom_shape_pivot_name = "pivot"
        self.layer_mech = self.env.get_layer('mech')
        self.layer_control_ik = self.env.get_layer('control')
        self.layer_control_fk = self.env.get_layer('control')

        self.property_ikfk_switch = None
        self.property_show_ik = None

        #changes the foot pivot places, naturally will just use Z = 0
        self.floor_override_location = None


    def get_ik_toe_control_bone(self):
        return self.bone_ik_toe_control
    
    def get_ik_target_goal_bone(self):
        return self.bone_foot_roll
    
    def get_ball_result_bone(self):
        return self.bone_ik_toe_control 
    
    def init(self,bone_hub):
        AFFIX = self.affix.apply
        self.bone_hub = bone_hub
        self.bone_foot = AFFIX(self.foot_label)
        self.bone_ball = AFFIX(self.ball_label)

    def begin_editmode(self):

        ARMA = self.arma
        AFFIX = self.affix.apply
        shared.activate_arma(self.arma)
        shared.ensure_blender_mode('EDIT')
 

        eb_root = shared.get_bone(ARMA,self.bone_root)

        eb_foot = shared.get_bone(ARMA,self.bone_foot)
        eb_ball = shared.get_bone(ARMA,self.bone_ball)
        ebs_source = [eb_foot,eb_ball]
        
        self.bonedata_source = []
        self.total_length = 0

        for eb in ebs_source:
            self.bonedata_source.append(shared.EditboneData(eb))
            self.total_length+=eb.length

        foot_z_floor_plane = 0
        self.distance_foot_to_z_floor = eb_foot.head.z
        
        
        self.bone_ik_control_parent = AFFIX(self.bone_foot+"_ik_control_parent")
        eb_ik_control_parent = shared.create_editbone(ARMA,self.bone_ik_control_parent)
        shared.match_editbone(eb_ik_control_parent,eb_foot)
        eb_ik_control_parent.parent = None
        shared.rotate_editbone_on_axis(eb_ik_control_parent,'X',180)
        shared.editbone_flatten_axis(eb_ik_control_parent,'Z')
        eb_ik_control_parent.roll = 0
        eb_ik_control_parent.layers = self.layer_mech


        eb_dynamic_inversed_foot = eb_ik_control_parent


        self.bone_ik_control = AFFIX(self.bone_foot+"_ik_control")
        eb_ik_control = shared.create_editbone(ARMA,self.bone_ik_control)
        shared.match_editbone(eb_ik_control,eb_dynamic_inversed_foot)
        eb_ik_control.length = self.total_length*1.5
        eb_ik_control.parent = eb_ik_control_parent
        eb_ik_control.layers = self.layer_control_ik
        eb_ik_control.inherit_scale = 'AVERAGE'

        self.bone_ik_control_scale = AFFIX(self.bone_foot+"_ik_scale")
        eb_ik_control_scale = shared.create_editbone(ARMA,self.bone_ik_control_scale)
        shared.match_editbone(eb_ik_control_scale,eb_dynamic_inversed_foot)
        eb_ik_control_scale.parent = eb_ik_control
        eb_ik_control_scale.layers = self.layer_mech

        self.bone_ik_pivot_control = AFFIX(self.bone_foot+"_ik_pivot_control")
        eb_ik_pivot_control = shared.create_editbone(ARMA,self.bone_ik_pivot_control )
        shared.match_editbone(eb_ik_pivot_control,eb_dynamic_inversed_foot)
        eb_ik_pivot_control.parent = eb_ik_control_scale
        eb_ik_pivot_control.layers = self.layer_control_fk
        eb_ik_pivot_control.head.z = foot_z_floor_plane
        eb_ik_pivot_control.tail.z = foot_z_floor_plane

        self.bone_ik_pivot_mech = AFFIX(self.bone_foot+"_ik_pivot_mech")
        eb_ik_pivot_mech = shared.create_editbone(ARMA,self.bone_ik_pivot_mech)
        shared.match_editbone(eb_ik_pivot_mech,eb_ik_pivot_control)
        eb_ik_pivot_mech.parent = eb_ik_pivot_control
        eb_ik_pivot_mech.layers = self.layer_mech

        self.bone_ik_foot_spin = AFFIX(self.foot_label+"_ik_spin")
        eb_ik_foot_spin = shared.create_editbone(ARMA,self.bone_ik_foot_spin)
        shared.match_editbone(eb_ik_foot_spin,eb_ball)
        eb_ik_foot_spin.parent = eb_ik_pivot_mech
        shared.rotate_editbone_on_axis(eb_ik_foot_spin,'X',180)
        shared.editbone_flatten_axis(eb_ik_foot_spin,'Z')
        eb_ik_foot_spin.layers = self.layer_control_ik

        self.bone_ik_heel_control = AFFIX(self.foot_label+"_heel_control")
        eb_ik_heel_control = shared.create_editbone(ARMA,self.bone_ik_heel_control)
        shared.match_editbone(eb_ik_heel_control,eb_dynamic_inversed_foot)
        eb_ik_heel_control.parent = eb_ik_foot_spin
        eb_ik_heel_control.layers = self.layer_control_ik
        eb_ik_heel_control.inherit_scale = 'AVERAGE'

        self.bone_heel_finder = AFFIX(self.foot_label+"_heel_finder")
        eb_heel_finder = shared.create_editbone(ARMA,self.bone_heel_finder)
        shared.match_editbone(eb_heel_finder,eb_dynamic_inversed_foot)

        if self.b_invert_x:
            shared.rotate_editbone_on_axis(eb_heel_finder,'X',90)
        else:
            shared.rotate_editbone_on_axis(eb_heel_finder,'X',-90)
        #this is a magic number assuming the heel width is about half the width of the foot
        #can easily add a setting that sets the heel location 
        eb_heel_finder.length *=.5 
        offset = utils.linear_interpolate_between_vectors(eb_heel_finder.head,eb_heel_finder.tail,-.5)
        utils.move_editbone(eb_heel_finder,offset)
        eb_heel_finder.layers = self.layer_mech
        eb_heel_finder.head.z = foot_z_floor_plane
        eb_heel_finder.tail.z = foot_z_floor_plane

        self.bone_heel_rock2 = AFFIX(self.foot_label+"_heel_rock2")
        eb_heel_rock2 =  shared.create_editbone(ARMA,self.bone_heel_rock2)
        shared.match_editbone(eb_heel_rock2,eb_dynamic_inversed_foot)
        eb_heel_rock2.parent = eb_ik_foot_spin
        utils.move_editbone(eb_heel_rock2,eb_heel_finder.head)
        eb_heel_rock2.layers = self.layer_mech


        self.bone_heel_rock1 = AFFIX(self.foot_label+"_heel_rock1")
        eb_heel_rock1 =  shared.create_editbone(ARMA,self.bone_heel_rock1)
        shared.match_editbone(eb_heel_rock1,eb_dynamic_inversed_foot)
        eb_heel_rock1.parent = eb_heel_rock2
        utils.move_editbone(eb_heel_rock1,eb_heel_finder.tail)
        eb_heel_rock1.layers = self.layer_mech

        self.bone_heel_roll2 = AFFIX(self.foot_label+"_heel_roll2")
        eb_heel_roll2 = shared.create_editbone(ARMA,self.bone_heel_roll2)
        shared.match_editbone(eb_heel_roll2,eb_dynamic_inversed_foot)
        eb_heel_roll2.parent = eb_heel_rock1
        utils.move_editbone(eb_heel_roll2,utils.linear_interpolate_between_vectors(eb_heel_finder.head,eb_heel_finder.tail,.5))
        eb_heel_roll2.layers = self.layer_mech


        self.bone_heel_roll1 = AFFIX(self.foot_label+"_heel_roll1")
        eb_heel_roll1 = shared.create_editbone(ARMA,self.bone_heel_roll1)
        shared.match_editbone(eb_heel_roll1,eb_ik_foot_spin)
        eb_heel_roll1.parent = eb_heel_roll2
        eb_heel_roll1.length *= .9
        eb_heel_roll1.layers = self.layer_mech

        self.bone_foot_roll = AFFIX(self.foot_label+"_roll")
        eb_foot_roll = shared.create_editbone(ARMA,self.bone_foot_roll)       
        shared.match_editbone(eb_foot_roll,eb_foot)
        eb_foot_roll.parent = eb_heel_roll1
        eb_foot_roll.layers = self.layer_mech

        #IK_LEG_TARGET GOES HERE

        self.bone_ik_toe_parent = AFFIX(self.foot_label+"_"+self.toe_label+"_ik_parent")
        eb_ik_toe_parent = shared.create_editbone(ARMA,self.bone_ik_toe_parent)
        shared.match_editbone(eb_ik_toe_parent,eb_ik_foot_spin)
        eb_ik_toe_parent.use_connect = True
        eb_ik_toe_parent.length *= .8
        eb_ik_toe_parent.parent = eb_foot_roll
        eb_ik_toe_parent.layers = self.layer_mech

        self.bone_ik_toe_control = AFFIX(self.foot_label+"_"+self.toe_label+"_ik_control")
        eb_ik_toe_control = shared.create_editbone(ARMA,self.bone_ik_toe_control)
        shared.match_editbone(eb_ik_toe_control ,eb_ball)
        eb_ik_toe_control.parent = eb_ik_toe_parent
        eb_ik_toe_control.layers = self.layer_mech

           
    def begin_posemode(self):        
    
        ARMA = self.arma
        shared.activate_arma(self.arma)
        shared.ensure_blender_mode('POSE')
        
        bone_group_control_ik = self.env.get_bone_group(ARMA,self.bone_group_control_ik_name)

        pb = shared.get_bone(ARMA,self.bone_ik_control_parent)
        shared.lock_all_bone_transforms(pb)

        
        pb = shared.get_bone(ARMA,self.bone_ik_control)
        pb.custom_shape = self.env.get_custom_shape(self.custom_shape_foot_ik_control_name)
        pb.custom_shape_translation[2] = -self.distance_foot_to_z_floor
        pb.bone_group = bone_group_control_ik

        pb = shared.get_bone(ARMA, self.bone_ik_control_scale)
        shared.lock_all_bone_transforms(pb)
        cns = pb.constraints.new('COPY_SCALE')
        cns.target = ARMA
        cns.subtarget = self.bone_hub
        cns.use_make_uniform = True
        cns.use_offset = True
        cns.target_space = 'LOCAL'
        cns.owner_space = 'LOCAL'

        pb = shared.get_bone(ARMA, self.bone_ik_pivot_control)
        pb.custom_shape = self.env.get_custom_shape(self.custom_shape_pivot_name)
        pb.bone_group = bone_group_control_ik
        
        pb =  shared.get_bone(ARMA, self.bone_ik_heel_control)
        pb.rotation_mode = 'ZXY'
        pb.bone_group = bone_group_control_ik
        pb.custom_shape = self.env.get_custom_shape(self.custom_shape_heel_control_name)
        pb.custom_shape_translation[1] = self.bonedata_source[0].length/2
        pb.custom_shape_translation[2] -(self.bonedata_source[0].head.z/2)
        if self.b_invert_x:
            pb.custom_shape_scale_xyz[0] = pb.custom_shape_scale_xyz[0]*-1
        pb.lock_location = [True,True,True]
        pb.lock_scale = [True,True,True]
        pb = shared.get_bone(ARMA,self.bone_ik_foot_spin)
        pb.bone_group = bone_group_control_ik
        pb.custom_shape = self.env.get_custom_shape(self.custom_shape_foot_spin_name)
        pb = shared.get_bone(ARMA,self.bone_heel_rock2)
        pb.rotation_mode = 'ZXY'
        utils.lock_all_bone_transforms(pb)
        cns = pb.constraints.new('COPY_ROTATION')
        cns.target = ARMA
        cns.subtarget = self.bone_ik_heel_control
        cns.use_x = False
        cns.use_z = False
        cns.target_space = 'LOCAL'
        cns.owner_space = 'LOCAL'
        cns = pb.constraints.new('LIMIT_ROTATION')
        cns.use_limit_y = True
        cns.min_y = radians(-360)
        cns.owner_space = 'LOCAL'

        pb = shared.get_bone(ARMA,self.bone_heel_rock1)
        pb.rotation_mode = "ZXY"
        utils.lock_all_bone_transforms(pb)
        cns = pb.constraints.new('COPY_ROTATION')
        cns.target = ARMA
        cns.subtarget = self.bone_ik_heel_control
        cns.use_x = False
        cns.use_z = False
        cns.target_space = 'LOCAL'
        cns.owner_space = 'LOCAL'
        cns = pb.constraints.new('LIMIT_ROTATION')
        cns.use_limit_y = True
        cns.max_y = radians(360)
        cns.owner_space = 'LOCAL'

        pb = shared.get_bone(ARMA,self.bone_heel_roll2)
        pb.rotation_mode = "ZXY"
        utils.lock_all_bone_transforms(pb)
        cns = pb.constraints.new('COPY_ROTATION')
        cns.target = ARMA
        cns.subtarget = self.bone_ik_heel_control
        cns.use_y = False
        cns.use_z = False
        cns.target_space = 'LOCAL'
        cns.owner_space = 'LOCAL'
        cns = pb.constraints.new('LIMIT_ROTATION')
        cns.use_limit_x = True
        cns.min_x = radians(-360)
        cns.owner_space = 'LOCAL'
    
        pb = shared.get_bone(ARMA, self.bone_heel_roll1)
        pb.rotation_mode = "ZXY"
        utils.lock_all_bone_transforms(pb)
        cns = pb.constraints.new('COPY_ROTATION')
        cns.target = ARMA
        cns.subtarget = self.bone_ik_heel_control
        cns.target_space = 'POSE'
        cns.owner_space = 'POSE'
    
    
        pb = shared.get_bone(ARMA, self.bone_foot_roll)
        utils.lock_all_bone_transforms(pb)
        pb.rotation_mode = 'ZXY'

        pb = shared.get_bone(ARMA, self.bone_ik_toe_parent)
        utils.lock_all_bone_transforms(pb)
        cns = pb.constraints.new('COPY_TRANSFORMS')
        cns.target = ARMA
        cns.subtarget = self.bone_heel_roll2
        
        if self.property_show_ik != None:
            bones_prop_show_ik_listeners = [self.bone_ik_control,self.bone_ik_heel_control,self.bone_ik_pivot_control,self.bone_ik_toe_control]

            for i in range(len(bones_prop_show_ik_listeners)):
                pb = shared.get_bone(ARMA,bones_prop_show_ik_listeners[i])
                drv = ARMA.data.bones[pb.name].driver_add("hide")
                driver = drv.driver
                driver.type = 'SCRIPTED'
                driver.expression = "v==0"
                var = driver.variables.new()
                var.type = 'SINGLE_PROP'
                var.name = 'v'
                var.targets[0].id = ARMA                
                var.targets[0].data_path = self.property_show_ik.write_path()



