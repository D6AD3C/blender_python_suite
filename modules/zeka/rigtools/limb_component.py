import bpy
from . import shared, environment
from mathutils import Vector
from math import radians, degrees



class Component():

    def __init__(self,arma,id,env=environment.get_default()):
        self.id = id
        self.env = env
        self.arma = arma
        self.type = 'ARM'
        self._init = False

        self.affix = shared.AffixData()
        self.root_name = "root"
        self.outer_name = None
        self.limb_label = None
        self.labels_source = None
        self.limb_length = None

        self.layer_control = self.env.get_layer('control')
        self.layer_mech = self.env.get_layer('mech')
        self.layer_tweak = self.env.get_layer('tweak')
        self.layer_control_hub = self.env.get_layer('control')
        self.layer_control_fk = self.env.get_layer('control')
        self.layer_control_ik = self.env.get_layer('control')

        self.bone_group_special_name = 'special'
        self.bone_group_control_fk_name = 'fk'
        self.bone_group_control_ik_name = 'ik'        
        self.bone_group_tweak_name = 'tweak'
        self.bone_group_visualizer_name = 'visualizer'

        self.custom_shape_sphere = self.env.get_custom_shape("sphere")
        self.custom_shape_circle = self.env.get_custom_shape("circle")
        self.custom_shape_circlewave = self.env.get_custom_shape("circlewave")
        self.custom_shape_gear = self.env.get_custom_shape("gear")
        self.custom_shape_ik_swing_name = "swing"
        self.custom_shape_pivot_name = "pivot"
        self.custom_shape_ik_end_control_name = 'square'
        self.custom_shape_pole_name = "pole"
        self.property_ikfk_switch = shared.CustomProperty2('FLOAT', "IKFK Switch","Slide Between IK and FK mode.")
        self.property_show_ik = shared.CustomProperty2('INT', "Show IK","Show IK controls.")

        self.propid_ik_pole = "IK Pole-Vector"
        self.propid_ik_stretch = "IK Strech"
        self.propid_fk_follow = "FK Follow"
        self.propid_ik_visibility = "Show IK"
        self.propid_fk_visibility = "Show FK"
        self.propid_end_parent = "Parent End"
        self.propid_pole_parent = "Parent Pole"
        self.propid_tweak_visibility = "Show Tweak"
        self.feature_ik = True
        self.feature_fk = True

        self._b_no_ik_end_control = False

        self.custom_shape_scale_modifier = 1

        self._x_positive = None
        self._invert_x_applicator = 1
        
        self.invert_x = None

        self.limb_length = None
        self.source_bone_head_location = []
        self.distance_mid_to_pole = None
        self.distance_end_to_down = None
        self.magic_number_visualizer_length_multiplier = .069


        self.bone_root = "root"
        self.bone_outer = None
        self.bones_source = []
        self.bone_limb_parent = None
        self.bone_limb_parent_mech = None
        self.bone_ik_swing = None
        self.bone_ik_swing_control = None
        self.bone_ik_mid = None
        self.bone_ik_target = None
        self.bone_ik_end_control_parent = None
        self.bone_ik_end_control = None
        self.bone_ik_end_control_parent = None
        self.bone_ik_pole_control = None
        self.bone_ik_pole_parent = None
        self.bone_ik_pole_visualizer = None
        self.bone_ik_end_scale = None
        self.bone_ik_pivot_control = None
        self.bone_ik_end_pivot_mech = None
        self.bone_ik_dynamic_pre_end_target = None
        self.bone_fk_controls = []
        self.bone_fk_hand_mech = None   
        self.bone_switches = []
        self.bone_tweaks = []
        self.bone_tweak_mechs = []

        self.bone_ik_target_dynamic_parent = None

        self.parent_switch_ik_end_bones = []
        self.parent_switch_ik_pole_bones = []
        self.parent_switch_pole_add_ik_target = True



    def get_hub_bone(self):
        return self.bone_limb_parent

    def get_property_show_ik(self):
        return self.property_show_ik

    def get_property_ikfk_switch(self):
        return self.property_ikfk_switch
    
    def add_parent_switch_ik_end_bones(self,bones):
        self.parent_switch_ik_end_bones += bones
    
    def add_parent_switch_ik_pole_bones(self,bones):
        self.parent_switch_ik_pole_bones += bones

    def get_ik_target_bone(self):
        return self.bone_ik_target
    
    def get_ik_end_control_bone(self):
        return self.bone_ik_end_control

    def get_end_fk_control_bone(self):
        return self.bone_fk_controls[-1]
    
    def get_ik_target_name(self):
        return self.bone_ik_target

    def get_end_switch_bone(self):
        return self.bone_switches[-1]
    
    def init(self,limb_label,bone_outer,start,mid,end):
        AFFIX = self.affix.apply
        self.bone_outer = bone_outer
        self.limb_label = limb_label
        self.labels_source = [start,mid,end]
        self.bones_source = [AFFIX(self.labels_source[0]),AFFIX(self.labels_source[1]),AFFIX(self.labels_source[2])]

        if self.type=='LEG':
            self._b_no_ik_end_control = True

        self._init = True

    def ensure_init(self):
         if self._init == False:
            raise Exception("Component was not init() before run()")   
             
    def begin_editmode(self):
        self.ensure_init()
        self.limb_editmode()

    def begin_posemode(self):
        self.ensure_init()
        self.limb_posemode()
              
    def limb_editmode(self):
        self.limb_base_editmode()
        self.limb_ik_editmode()
        self.limb_fk_editmode()
        self.limb_switch_editmode()
        self.limb_tweak_editmode()
        
    def limb_posemode(self): 

        self.limb_base_posemode()
        self.limb_ik_posemode()
        self.limb_fk_posemode()
        self.limb_switch_posemode()
        self.limb_tweak_posemode()
        self.posemode_bind_source_bones()

    def limb_base_editmode(self):

        AFFIX = self.affix.apply
        ARMA = self.arma
        shared.activate_arma(self.arma)        
        shared.ensure_blender_mode('EDIT')
        
        eb_outer = shared.get_bone(ARMA,self.bone_outer)

        ebs_source = []
        for i in range(3):
            eb = shared.get_bone(ARMA,self.bones_source[i])
            self.source_bone_head_location.append(eb.head.copy())
            ebs_source.append(eb)
 
        self.limb_length = ebs_source[0].length+ebs_source[1].length

        
        self._x_positive = ebs_source[0].head[0] - ebs_source[1].head[0] < 0

        #ignore if the user overrides invert_x        
        if self.invert_x == None :
 
            if self._x_positive == False:
                self.invert_x = True
            else:
                self.invert_x = False
        
        if self.invert_x == True:
            self.invert_x_applicator = 1
        else:
            self.invert_x_applicator = -1

        if self.distance_end_to_down == None:
            self.distance_end_to_down = ebs_source[2].head.z


        self.bone_limb_parent = AFFIX(self.labels_source[0]+"_hub_control")
        eb_hub = shared.create_editbone(ARMA,self.bone_limb_parent)
        shared.match_editbone(eb_hub,ebs_source[0])
        eb_hub.parent = eb_outer
        eb_hub.inherit_scale = 'NONE'
        eb_hub.length*=.15
        eb_hub.layers = self.layer_control

        self.bone_limb_parent_mech = AFFIX(self.labels_source[0]+"_hub_mech")
        eb_hub_mech = shared.create_editbone(ARMA,self.bone_limb_parent_mech)
        shared.match_editbone(eb_hub_mech,ebs_source[0])
        eb_hub_mech.parent = eb_outer
        shared.align_editbone_to_world_space(eb_hub_mech)
        eb_hub_mech.inherit_scale = 'FIX_SHEAR'
        eb_hub_mech.length *= .3
        eb_hub_mech.layers = self.layer_mech


    def limb_base_posemode(self):

        ARMA = self.arma
        shared.ensure_blender_mode('POSE')

        bone_group_special = self.env.get_bone_group(ARMA,self.bone_group_special_name)
        pb_hub = shared.get_bone(ARMA,self.bone_limb_parent)
        shared.lock_all_bone_transforms(pb_hub)
        pb_hub.lock_scale = [False,False,False]
        pb_hub.custom_shape = self.custom_shape_gear
        pb_hub.custom_shape_translation[0] = (0.15*self.invert_x_applicator)
        pb_hub.custom_shape_rotation_euler[0] = radians(90)
        pb_hub.bone_group = bone_group_special



        self.property_ikfk_switch.create(self.arma,pb_hub,0.0)
        self.property_show_ik.create(self.arma,pb_hub,1)

        shared.add_custom_property(pb_hub,self.propid_ik_pole,"Use IK PoleVector instead of Swing",0.0)
        shared.add_custom_property(pb_hub,self.propid_ik_stretch,"Enable IK Stretch",0.0)
        shared.add_custom_property(pb_hub,self.propid_fk_follow,"FK Follow",0.0)

        shared.add_custom_int_property(pb_hub,self.propid_fk_visibility,"Show FK controls",1)
        shared.add_custom_int_property(pb_hub,self.propid_tweak_visibility,"Show Tweak Controls",1)



        pb_hub_mech = shared.get_bone(ARMA,self.bone_limb_parent_mech)
        shared.lock_all_bone_transforms(pb_hub_mech)
        cns = pb_hub_mech.constraints.new('COPY_SCALE')
        cns.name = "Copy Root Scale"
        cns.target = ARMA
        cns.subtarget = self.bone_root
        cns.use_make_uniform = True
        cns = pb_hub_mech.constraints.new('COPY_SCALE')
        cns.name = "Copy Arm Scale"
        cns.target = ARMA
        cns.subtarget = self.bone_limb_parent
        cns.use_offset = True
        cns.use_make_uniform = True
        cns.target_space = 'LOCAL'
        cns.owner_space = 'LOCAL'
        cns = pb_hub_mech.constraints.new('COPY_ROTATION')
        cns.target = ARMA
        cns.subtarget = self.bone_root
        cns.influence = 0.0
        driver = cns.driver_add("influence").driver
        driver.type = 'SUM'
        var = driver.variables.new()
        var.type = 'SINGLE_PROP'
        var.targets[0].id = self.arma                
        var.targets[0].data_path = shared.write_posebone_datapath(self.bone_limb_parent,self.propid_fk_follow)



    def limb_ik_editmode(self):


        ARMA = self.arma
        AFFIX = self.affix.apply

        shared.activate_arma(self.arma)        
        shared.ensure_blender_mode('EDIT')

        eb_hub = shared.get_bone(ARMA,self.bone_limb_parent)

        ebs_source = []
        for i in range(3):
            eb = shared.get_bone(ARMA,self.bones_source[i])
            ebs_source.append(eb)


 

        self.bone_ik_pole_parent = AFFIX(self.labels_source[0]+"_ik_pole_parent")
        eb_bone_ik_pole_parent = shared.create_editbone(ARMA,self.bone_ik_pole_parent)
        shared.match_editbone(eb_bone_ik_pole_parent,ebs_source[2])
        eb_bone_ik_pole_parent.parent = None
        eb_bone_ik_pole_parent.layers = self.layer_mech


        self.bone_ik_pole_control = AFFIX(self.labels_source[0]+"_ik_pole_control")     
        eb_bone_ik_pole_control = shared.create_editbone(ARMA,self.bone_ik_pole_control)
        shared.match_editbone(eb_bone_ik_pole_control,ebs_source[2])
        eb_bone_ik_pole_control.parent = eb_bone_ik_pole_parent
        eb_bone_ik_pole_control.use_local_location = False
        eb_bone_ik_pole_control.inherit_scale = 'AVERAGE'
        eb_bone_ik_pole_control .layers = self.layer_control
        

        bpy.context.view_layer.update()
        eb_pole_start = ebs_source[0]
        eb_pole_end = ebs_source[1]


        pole_bone_length = .075
        pole_distance = 1.5
        pole_vector = shared.get_pole_vector(eb_pole_start,eb_pole_end)
        eb_bone_ik_pole_control.head = eb_pole_start.tail + (pole_vector.normalized()*pole_distance)
        eb_bone_ik_pole_control.tail = eb_bone_ik_pole_control.head + (pole_vector.normalized()*pole_bone_length)
        #eb_bone_ik_pole_control.head = eb_bone_ik_pole_control.tail - (pole_vector.normalized()*5)
        eb_bone_ik_pole_control.roll = 0
        pole_angle = shared.get_pole_angle(eb_pole_start,eb_pole_end,pole_vector,"y")
        shared.align_editbone_to_world_space(eb_bone_ik_pole_control)

        shared.match_editbone(eb_bone_ik_pole_parent,eb_bone_ik_pole_control)
        eb_bone_ik_pole_parent.length *=.5

        #pole_angle = get_pole_angle(self.bones_source[0].get(), self.bones_source[1].get(), pole_vector)
        #pole_angle = round(180*pole_angle/3.141592, 3)#convert radians to degrees
        #print("POLE_ANGLE: "+str(degrees(pole_angle)))
        #print("GOAL: -85.8547)")
        

        self.bone_ik_swing = AFFIX(self.labels_source[0]+"_ik_swing")
        eb_ik_swing = shared.create_editbone(ARMA,self.bone_ik_swing)
        shared.match_editbone(eb_ik_swing,ebs_source[0])
        eb_ik_swing.parent = eb_hub
        #eb_ik_swing.length = eb.length*.4
        eb_ik_swing.layers = self.layer_mech

        self.bone_ik_swing_control = AFFIX(self.labels_source[0]+"_ik_end_control")
        eb_ik_swing_control = shared.create_editbone(ARMA,self.bone_ik_swing_control)
        shared.match_editbone(eb_ik_swing_control,ebs_source[0])
        eb_ik_swing_control.parent = eb_ik_swing
        eb_ik_swing_control.layers = self.layer_control


        
        self.bone_ik_mid = AFFIX(self.labels_source[1]+"_ik")
        eb_ik_mid = shared.create_editbone(ARMA,self.bone_ik_mid)
        shared.match_editbone(eb_ik_mid,ebs_source[1])
        eb_ik_mid.parent = eb_ik_swing_control
        eb_ik_mid.layers = self.layer_mech


        self.bone_ik_pole_visualizer = AFFIX(self.labels_source[0]+"_ik_pole_visualizer")
        eb_bone_ik_pole_visualizer = shared.create_editbone(ARMA,self.bone_ik_pole_visualizer)
        shared.match_editbone(eb_bone_ik_pole_visualizer,ebs_source[1])
        eb_bone_ik_pole_visualizer.parent = eb_ik_mid
        shared.align_editbone_to_global_axis(eb_bone_ik_pole_visualizer,'Z+')
        eb_bone_ik_pole_visualizer.length = .1
        eb_bone_ik_pole_visualizer.layers = self.layer_control
        self.distance_mid_to_pole = (ebs_source[1].head - eb_bone_ik_pole_control.head).length



        eb_dynamic_parent = None

        if not self._b_no_ik_end_control:


            self.bone_ik_end_control_parent = AFFIX(self.labels_source[2]+"_ik_parent")
            eb_ik_end_control_parent = shared.create_editbone(ARMA,self.bone_ik_end_control_parent)
            shared.match_editbone(eb_ik_end_control_parent,ebs_source[2])
            shared.align_editbone_to_world_space(eb_ik_end_control_parent)
            eb_ik_end_control_parent.parent = None
            eb_ik_end_control_parent.layers = self.layer_mech


            self.bone_ik_end_control = AFFIX(self.labels_source[2]+"_ik_end_control")
            eb_ik_end_control = shared.create_editbone(ARMA,self.bone_ik_end_control)
            shared.match_editbone(eb_ik_end_control,ebs_source[2])
            if self.type == 'ARM':
                pass
            if self.type == 'LEG':
                shared.reflect_editbone(eb_ik_end_control)
                shared.editbone_flatten_axis(eb_ik_end_control,"Z")
            eb_ik_end_control.parent = eb_ik_end_control_parent 
            eb_ik_end_control.use_local_location = False
            eb_ik_end_control.inherit_scale = 'AVERAGE'
            eb_ik_end_control.layers = self.layer_control

            eb_dynamic_parent = eb_ik_end_control


            self.bone_ik_end_scale = AFFIX(self.labels_source[2]+"_ik_scale")
            eb_bone_ik_end_scale = shared.create_editbone(ARMA,self.bone_ik_end_scale)
            shared.match_editbone(eb_bone_ik_end_scale,eb_ik_end_control)
            eb_bone_ik_end_scale.parent = eb_dynamic_parent 
            eb.layers = self.layer_mech
            eb_dynamic_parent = eb_bone_ik_end_scale


            self.bone_ik_pivot_control = AFFIX(self.labels_source[2]+"_ik_pivot_control")
            eb_ik_pivot_control = shared.create_editbone(ARMA,self.bone_ik_pivot_control)
            shared.match_editbone(eb_ik_pivot_control,eb_ik_end_control)
            eb_ik_pivot_control.parent = eb_dynamic_parent
            eb_ik_pivot_control.layers =self.layer_control
            eb_dynamic_parent = eb_ik_pivot_control


            self.bone_ik_end_pivot_mech = AFFIX(self.labels_source[2]+"_ik_pivot_mech")
            eb_bone_ik_end_pivot_mech = shared.create_editbone(ARMA, self.bone_ik_end_pivot_mech)
            shared.match_editbone(eb_bone_ik_end_pivot_mech,eb_ik_end_control)
            eb_bone_ik_end_pivot_mech.parent = eb_dynamic_parent
            eb_bone_ik_end_pivot_mech.layers = self.layer_mech
            eb_dynamic_parent = eb_bone_ik_end_pivot_mech  

        self.bone_ik_target = AFFIX(self.labels_source[2]+"_ik_target")
        eb_bone_ik_target = shared.create_editbone(ARMA,self.bone_ik_target)
        shared.match_editbone(eb_bone_ik_target,ebs_source[2])
        eb_bone_ik_target.parent = eb_dynamic_parent
        eb_bone_ik_target.layers = self.layer_mech        

        




    def limb_ik_posemode(self):

        ARMA = self.arma

        ik_end_controls = [self.bone_ik_swing_control,self.bone_ik_pole_control]
        if self._b_no_ik_end_control == False:
            ik_end_controls.append(self.bone_ik_end_control)
            ik_end_controls.append(self.bone_ik_pivot_control)

            
        shared.ensure_blender_mode('POSE')

        bone_group_visualizer = self.env.get_bone_group(ARMA,self.bone_group_visualizer_name)
        bone_group_control_ik = self.env.get_bone_group(ARMA,self.bone_group_control_ik_name)

        pb_hub = shared.get_bone(ARMA,self.bone_limb_parent)
        
        if self.parent_switch_pole_add_ik_target:
             self.parent_switch_ik_pole_bones.append(self.bone_ik_target)

        total_ik_end_parent_switches = len(self.parent_switch_ik_end_bones)
        total_pole_parent_switches = len(self.parent_switch_ik_pole_bones)

        cpw = shared.CustomPropertyWriter(pb_hub,self.propid_end_parent,0)
        cpw.description = "end control parent"
        cpw.max = total_ik_end_parent_switches
        cpw.soft_max = total_ik_end_parent_switches
        self.customprop_ik_end_parent = cpw.create()

        cpw = shared.CustomPropertyWriter(pb_hub,self.propid_pole_parent,0)
        cpw.description = "pole control parent"
        cpw.max = total_pole_parent_switches
        cpw.soft_max = total_pole_parent_switches
        self.customprop_ik_pole_parent = cpw.create()

             
        pb_ik_pole_parent = shared.get_bone(ARMA,self.bone_ik_pole_parent)
        shared.lock_all_bone_transforms(pb_ik_pole_parent)
        cns = pb_ik_pole_parent.constraints.new('ARMATURE')
        cns.name = "parent_switch"        
        for i in range(len(self.parent_switch_ik_pole_bones)): 
            target = cns.targets.new()
            target.target = ARMA
            target.subtarget = self.parent_switch_ik_pole_bones[i]
            target.weight = 0.0
            drv = target.driver_add("weight")
            driver = drv.driver
            driver.type = 'SCRIPTED'
            driver.expression = "v=="+str(i)
            var = driver.variables.new()
            var.type = 'SINGLE_PROP'
            var.name = 'v'
            var.targets[0].id = self.arma                
            var.targets[0].data_path = self.customprop_ik_pole_parent.write_path()

        pb_ik_mid = shared.get_bone(ARMA,self.bone_ik_mid)
        pb_ik_mid.ik_stretch = 0.1
        pb_ik_mid.lock_ik_y = True
        pb_ik_mid.lock_ik_z = True
        shared.lock_all_bone_transforms(pb_ik_mid)
        cns = pb_ik_mid.constraints.new('IK')
        cns.name = "IK Track"
        cns.target = ARMA
        cns.subtarget = self.bone_ik_target
        cns.chain_count = 2
        drv = cns.driver_add("influence")
        driver = drv.driver
        driver.type = 'SUM'
        var = driver.variables.new()
        var.type = 'SINGLE_PROP'
        var.targets[0].id = ARMA                
        #var.targets[0].data_path = self.uiprop_ik_pole.get_data_path() self.bone_limb_parent
        var.targets[0].data_path = shared.write_posebone_datapath(self.bone_limb_parent,self.propid_ik_pole)
        drv_modifier = drv.modifiers.new('GENERATOR')
        drv_modifier.mode = 'POLYNOMIAL'
        polynomial = [1.0, -1.0]
        drv_modifier.poly_order = len(polynomial)-1            
        for pn_i,v in enumerate(polynomial):
            drv_modifier.coefficients[pn_i] = v 

        cns = pb_ik_mid.constraints.new('IK')
        cns.name = "IK Pole"
        cns.target = ARMA
        cns.subtarget = self.bone_ik_target
        cns.pole_target = ARMA
        cns.pole_subtarget = self.bone_ik_pole_control
        cns.chain_count = 2
        cns.pole_angle = radians(-90)
        driver = cns.driver_add("influence").driver
        driver.type = 'SUM'
        var = driver.variables.new()
        var.type = 'SINGLE_PROP'
        var.targets[0].id = ARMA               
        var.targets[0].data_path = shared.write_posebone_datapath(self.bone_limb_parent,self.propid_ik_pole) 


        pb_ik_swing = shared.get_bone(ARMA,self.bone_ik_swing)
        shared.lock_all_bone_transforms(pb_ik_swing)
        cns = pb_ik_swing.constraints.new('DAMPED_TRACK')
        cns.target = ARMA
        cns.subtarget = self.bone_ik_target

        pb_ik_swing_control = shared.get_bone(ARMA,self.bone_ik_swing_control)
        pb_ik_swing_control.ik_stretch = 0.1
        pb_ik_swing_control.rotation_mode = "ZXY"
        pb_ik_swing_control.lock_rotation = [True,False,True]
        pb_ik_swing_control.bone_group = bone_group_control_ik
        pb_ik_swing_control.custom_shape = self.env.get_custom_shape(self.custom_shape_ik_swing_name)
        pb_ik_swing_control.custom_shape_translation[1] = .03 



        pb_ik_target = shared.get_bone(ARMA,self.bone_ik_target)
        shared.lock_all_bone_transforms(pb_ik_target)
        cns = pb_ik_target.constraints.new('LIMIT_DISTANCE')
        cns.name = "Limit distance for stretch toggle"
        cns.target = ARMA
        cns.subtarget = self.bone_limb_parent_mech
        cns.distance = self.limb_length
        cns.target_space = 'CUSTOM'
        cns.owner_space = 'CUSTOM'
        cns.space_object = ARMA
        cns.space_subtarget = self.bone_limb_parent_mech
        drv = cns.driver_add("influence")
        driver = drv.driver
        driver.type = 'SUM'
        var = driver.variables.new()
        var.type = 'SINGLE_PROP'
        var.targets[0].id = self.arma                
        var.targets[0].data_path = shared.write_posebone_datapath(self.bone_limb_parent,self.propid_ik_stretch)
        drv_modifier = drv.modifiers.new('GENERATOR')
        drv_modifier.mode = 'POLYNOMIAL'
        polynomial = [1.0, -1.0]
        drv_modifier.poly_order = len(polynomial)-1            
        for pn_i,v in enumerate(polynomial):
            drv_modifier.coefficients[pn_i] = v 

        pb_ik_pole_control = shared.get_bone(ARMA,self.bone_ik_pole_control)
        pb_ik_pole_control.bone_group = bone_group_control_ik
        pb_ik_pole_control.custom_shape = self.env.get_custom_shape(self.custom_shape_pole_name)


        for control in ik_end_controls:
            print(control)
            pb = shared.get_bone(ARMA,control)
            drv = self.arma.data.bones[pb.name].driver_add("hide")
            driver = drv.driver
            driver.type = 'SCRIPTED'
            driver.expression = "v==0"
            var = driver.variables.new()
            var.type = 'SINGLE_PROP'
            var.name = 'v'
            var.targets[0].id = self.arma                
            var.targets[0].data_path = self.property_show_ik.write_path()


        pb_ik_pole_visualizer = shared.get_bone(ARMA,self.bone_ik_pole_visualizer)
        shared.lock_all_bone_transforms(pb_ik_pole_visualizer)
        pb_ik_pole_visualizer.custom_shape = self.env.get_custom_shape('line')
        pb_ik_pole_visualizer.bone_group = bone_group_visualizer        
        cns = pb_ik_pole_visualizer.constraints.new('COPY_TRANSFORMS')
        cns.target = ARMA
        cns.subtarget = self.bone_ik_mid
        cns = pb_ik_pole_visualizer.constraints.new('STRETCH_TO')
        cns.rest_length = self.distance_mid_to_pole*self.magic_number_visualizer_length_multiplier
        cns.target = ARMA
        cns.subtarget = self.bone_ik_pole_control
        cns.volume = 'NO_VOLUME'

        
        if not self._b_no_ik_end_control:

            
            pb = shared.get_bone(ARMA,self.bone_ik_end_control_parent)
            shared.lock_all_bone_transforms(pb)
            cns = pb.constraints.new('ARMATURE')
            cns.name = "switch_parent"
            for i in range(len(self.parent_switch_ik_end_bones)): 
                target = cns.targets.new()
                target.target = ARMA
                target.subtarget = self.parent_switch_ik_pole_bones[i]
                target.weight = 0.0
                drv = target.driver_add("weight")
                driver = drv.driver
                driver.type = 'SCRIPTED'
                driver.expression = "v=="+str(i)
                var = driver.variables.new()
                var.type = 'SINGLE_PROP'
                var.name = 'v'
                var.targets[0].id = self.arma                
                var.targets[0].data_path = self.customprop_ik_end_parent.write_path()

            pb_ik_end_control = shared.get_bone(ARMA,self.bone_ik_end_control)
            pb_ik_end_control.bone_group = bone_group_control_ik
            pb_ik_end_control.custom_shape = self.env.get_custom_shape(self.custom_shape_ik_end_control_name)


            pb = shared.get_bone(ARMA, self.bone_ik_end_scale)
            shared.lock_all_bone_transforms(pb)
            cns = pb.constraints.new('COPY_SCALE')
            cns.target = ARMA
            cns.subtarget = self.bone_limb_parent
            cns.target_space = 'LOCAL'
            cns.owner_space = 'LOCAL'
            cns.use_make_uniform = True
            cns.use_offset = True

            pb = shared.get_bone(ARMA,self.bone_ik_pivot_control)
            pb.custom_shape = self.env.get_custom_shape(self.custom_shape_pivot_name)
            pb.bone_group = bone_group_control_ik

            pb = shared.get_bone(ARMA,self.bone_ik_end_pivot_mech)
            shared.lock_all_bone_transforms(pb)
            cns = pb.constraints.new('COPY_LOCATION')
            cns.target = ARMA
            cns.subtarget = self.bone_ik_pivot_control
            cns.target_space = 'LOCAL'
            cns.owner_space = 'LOCAL'
            cns.invert_x = True
            cns.invert_y = True
            cns.invert_z = True

    def limb_fk_editmode(self):

        ARMA = self.arma
        AFFIX = self.affix.apply

        shared.activate_arma(self.arma)        
        shared.ensure_blender_mode('EDIT')

        eb_hub = shared.get_bone(ARMA,self.bone_limb_parent)
        eb_outer = shared.get_bone(ARMA,self.bone_outer)

        ebs_source = []
        for i in range(3):
            eb = shared.get_bone(ARMA,self.bones_source[i])
            ebs_source.append(eb)


        ebs_fk_chain = []
        for i in range(3):
            
            name = AFFIX(self.labels_source[i]+"_fk_control")
            self.bone_fk_controls.append(name)    
            eb = shared.create_editbone(ARMA,name)
            eb.layers = self.layer_control
            shared.match_editbone(eb,ebs_source[i])
            ebs_fk_chain.append(eb)

            if i == 0:
                eb.inherit_scale = 'AVERAGE'
                eb.parent = shared.get_bone(ARMA,self.bone_limb_parent)
            if i == 1:
                eb.use_connect = True
                eb.inherit_scale = 'ALIGNED'
                eb.parent = ebs_fk_chain[i-1]
            if i == 2:

                self.bone_fk_hand_mech = AFFIX(self.labels_source[2]+"_fk_mech")
                eb_bone_fk_hand_mech = shared.create_editbone(ARMA,self.bone_fk_hand_mech)
                shared.match_editbone(eb_bone_fk_hand_mech,ebs_source[2])
                eb_bone_fk_hand_mech.inherit_scale = 'NONE'
                eb_bone_fk_hand_mech.use_connect = True
                eb_bone_fk_hand_mech.layers = self.layer_mech
                eb_bone_fk_hand_mech.parent = ebs_fk_chain[i-1]

                eb.parent = eb_bone_fk_hand_mech





    def limb_fk_posemode(self):

        ARMA = self.arma

        shared.ensure_blender_mode('POSE')
        CUSTOM_SHAPE_CIRCLE = self.custom_shape_circle

        bone_group_control_fk = self.env.get_bone_group(ARMA,self.bone_group_control_fk_name)
        scale_array = [.8,.6,1.5]

        for i in range(3):
            pb = shared.get_bone(ARMA,self.bone_fk_controls[i])
            pb.bone_group = bone_group_control_fk
            pb.custom_shape = CUSTOM_SHAPE_CIRCLE
            pb.custom_shape_scale_xyz *= scale_array[i]
            pb.custom_shape_scale_xyz *= self.custom_shape_scale_modifier
            self.arma.data.bones[pb.name].hide = True     
            drv = self.arma.data.bones[pb.name].driver_add("hide")
            driver = drv.driver
            driver.type = 'SCRIPTED'
            driver.expression = "v==0"
            var = driver.variables.new()
            var.type = 'SINGLE_PROP'
            var.name = 'v'
            var.targets[0].id = ARMA               
            var.targets[0].data_path = shared.write_posebone_datapath(self.bone_limb_parent,self.propid_fk_visibility)

            is_last = i==2
            if is_last:
                pb.lock_location=[True,True,True]

        pb_bone_fk_hand_mech = shared.get_bone(ARMA,self.bone_fk_hand_mech)
        shared.lock_all_bone_transforms(pb_bone_fk_hand_mech)
        cns = pb_bone_fk_hand_mech.constraints.new('COPY_SCALE')
        cns.target = ARMA
        cns.subtarget = self.bone_limb_parent_mech
        cns.use_make_uniform = True
        


    def limb_switch_editmode(self):

        ARMA = self.arma
        AFFIX = self.affix.apply

        shared.activate_arma(self.arma)        
        shared.ensure_blender_mode('EDIT')

        eb_hub = shared.get_bone(ARMA,self.bone_limb_parent)
        eb_outer = shared.get_bone(ARMA,self.bone_outer)

        ebs_source = []
        ebs_switches = []
        
        for i in range(3):
            eb = shared.get_bone(ARMA,self.bones_source[i])
            ebs_source.append(eb)
            
        for i in range(3):
            name = AFFIX(self.labels_source[i]+"_switch")
            self.bone_switches.append(name)
            str_i = str(i)
            eb = shared.create_editbone(ARMA,name)
            ebs_switches.append(eb)
            shared.match_editbone(eb,ebs_source[i])
            if i == 0:
                eb.parent = eb_outer
            else:
                eb.parent = ebs_switches[i-1]
            eb.layers = self.layer_mech
            


    def limb_switch_posemode(self):

        ARMA = self.arma
        shared.ensure_blender_mode('POSE')
        
        ik_array = [self.bone_ik_swing_control,self.bone_ik_mid,self.bone_ik_target]
        for i in range(3):
            name = self.bone_switches[i]
            pb = shared.get_bone(ARMA,name)
            shared.lock_all_bone_transforms(pb)
            cns = pb.constraints.new('COPY_TRANSFORMS')
            cns.name = "Copy Transforms FK"
            cns.target = ARMA
            cns.subtarget = self.bone_fk_controls[i]
 
            cns = pb.constraints.new('COPY_TRANSFORMS')
            cns.name = "Copy Transforms IK"
            cns.target = ARMA
            cns.subtarget = ik_array[i]
            driver = cns.driver_add("influence").driver
            driver.type = 'SUM'
            var = driver.variables.new()
            var.type = 'SINGLE_PROP'
            var.name = "vartest"
            var.targets[0].id = ARMA             
            var.targets[0].data_path = self.property_ikfk_switch.write_path()      


        
    def limb_tweak_editmode(self):

        ARMA = self.arma
        AFFIX = self.affix.apply

        shared.activate_arma(self.arma)        
        shared.ensure_blender_mode('EDIT')

        eb_hub = shared.get_bone(ARMA,self.bone_limb_parent)
        eb_outer = shared.get_bone(ARMA,self.bone_outer)

        ebs_source = []
        ebs_switches = []
        for i in range(3):
            ebs_source.append(shared.get_bone(ARMA,self.bones_source[i]))
            ebs_switches.append(shared.get_bone(ARMA,self.bone_switches[i]))

        self.length_adjustments = [.3,.2,.5]

        ebs_tweak_mechs = []
        ebs_tweaks = []
        for i in range(3):
            name_mech = AFFIX(self.labels_source[i]+"_tweak_mech")
            self.bone_tweak_mechs.append(name_mech)
            eb_mech = shared.create_editbone(ARMA,name_mech)
            ebs_tweak_mechs.append(eb_mech)
            shared.match_editbone(eb_mech,ebs_source[i])

            if i==0:
                eb_mech.parent = eb_outer
            else:
                eb_mech.parent = ebs_switches[i]
            if i==0:
                eb_mech.inherit_scale = 'FIX_SHEAR'
            eb_mech.layers = self.layer_mech
            

            name_tweak = AFFIX(self.labels_source[i]+"_tweak")
            self.bone_tweaks.append(name_tweak)
            eb_tweak = shared.create_editbone(ARMA,name_tweak)
            ebs_tweaks.append(eb_tweak)
            shared.match_editbone(eb_tweak,ebs_source[i])
            eb_tweak.parent = eb_mech
            eb_tweak.layers = self.layer_tweak
            eb_tweak.length *= self.length_adjustments[i]
            





    def limb_tweak_posemode(self):

        ARMA = self.arma
        CUSTOM_SHAPE_SPHERE = self.custom_shape_sphere
        BONEGROUP_TWEAK = self.env.get_bone_group(ARMA,self.bone_group_tweak_name)

        shared.ensure_blender_mode('POSE')


        for i in range(3):
            pb = shared.get_bone(ARMA,self.bone_tweaks[i])
            pb.rotation_mode = 'ZXY'
            pb.lock_rotation = [True,False,True]
            pb.lock_scale = [False,True,False]
            pb.bone_group = BONEGROUP_TWEAK
            pb.custom_shape = CUSTOM_SHAPE_SPHERE
            drv = self.arma.data.bones[pb.name].driver_add("hide")
            driver = drv.driver
            driver.type = 'SCRIPTED'
            driver.expression = "v==0"
            var = driver.variables.new()
            var.type = 'SINGLE_PROP'
            var.name = 'v'
            var.targets[0].id = ARMA                
            var.targets[0].data_path = shared.write_posebone_datapath(self.bone_limb_parent,self.propid_tweak_visibility)
                                                                      

        pb = shared.get_bone(ARMA,self.bone_tweak_mechs[0])
        shared.lock_all_bone_transforms(pb)
        cns = pb.constraints.new('COPY_SCALE')
        cns.use_make_uniform = True
        cns.target = ARMA
        cns.subtarget = self.bone_limb_parent_mech
        cns = pb.constraints.new('COPY_LOCATION')
        cns.target = ARMA
        cns.subtarget = self.bone_switches[0]
        cns = pb.constraints.new('DAMPED_TRACK')
        cns.target = ARMA
        cns.subtarget = self.bone_switches[0]
        cns.head_tail = 1

        pb = shared.get_bone(ARMA,self.bone_tweak_mechs[1])
        shared.lock_all_bone_transforms(pb)
        cns = pb.constraints.new('COPY_SCALE')
        cns.use_make_uniform = True
        cns.target = ARMA
        cns.subtarget = self.bone_limb_parent

        pb = shared.get_bone(ARMA,self.bone_tweak_mechs[2])
        shared.lock_all_bone_transforms(pb)


    def posemode_bind_source_bones(self):
        
        ARMA = self.arma

        shared.ensure_blender_mode('POSE')

        for i in range(3):
            pb = shared.get_bone(ARMA,self.bones_source[i])
            shared.lock_all_bone_transforms(pb)
            cns = pb.constraints.new('COPY_TRANSFORMS')
            cns.name = "Copy Transforms"
            cns.target = ARMA
            cns.subtarget = self.bone_tweaks[i]