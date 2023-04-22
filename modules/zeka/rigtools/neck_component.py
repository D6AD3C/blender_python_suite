import bpy
from math import radians
from . import shared, environment

class Component():

    def __init__(self,arma,id,env=environment.get_default()):
        self.id = id
        self.arma = arma
        self.env = env
        self.affix = shared.AffixData()
        self.labels_source = []
        self.label_neck = 'neck'
        self.label_head = 'head'
        self.total_joints = None
        self.scale_modifier_bone_count_adaptive = 1
        
        self.propid_head_follow = "Head Follow"
        self.propid_neck_follow = "Neck Follow"

        self.bones_source = []
        self.bone_neck_control = None
        self.bone_neck_follow = None
        self.bone_head_control = None
        self.bone_head_follow = None
        
        self.bone_group_control_name = 'control'
        self.layer_mech = self.env.get_layer('mech')
        self.layer_control = self.env.get_layer('control')
        self.layer_tweak = self.env.get_layer('tweak')
        self.custom_shape_neck_control_name = 'circle'
        self.custom_shape_head_control_name = 'circle'
        self.custom_shape_bend_control_name = 'plusarrow'
        self.custom_shape_tweak_name = 'tweak'

        self.bone_spine_connection_torso = None
        self.bone_spine_connection_hub = None
        self.bone_spine_connection_stem = None


    def enable_connection_with_spine(self,torso_bone,hub_bone,stem_bone):
        self.bone_spine_connection_torso = torso_bone
        self.bone_spine_connection_hub = hub_bone
        self.bone_spine_connection_stem = stem_bone


    def init(self,labels_source):
        self.labels_source = labels_source
        for label in self.labels_source:
            self.bones_source.append(self.affix.apply(label))
        self.total_joints = len(self.labels_source)

        self.scale_modifier_bone_count_adaptive = (self.total_joints-1)/2

    def begin_editmode(self):

        ARMA = self.arma
        AFFIX = self.affix.apply

        shared.activate_arma(self.arma)        
        shared.ensure_blender_mode('EDIT')

        ebs_source = []
        for bone in self.bones_source:
            ebs_source.append(shared.get_bone(ARMA,bone))

        self._length_head = ebs_source[-1].length

        self.bone_neck_follow = AFFIX(self.label_neck+"_follow") 
        eb_neck_follow = shared.create_editbone(ARMA,self.bone_neck_follow)
        shared.match_editbone(eb_neck_follow,ebs_source[0])
        shared.align_editbone_to_world_space(eb_neck_follow)
        eb_neck_follow.parent = shared.get_bone(ARMA,self.bone_spine_connection_stem)
        eb_neck_follow.layers = self.layer_mech

        self.bone_neck_control = AFFIX(self.label_neck+"_control")
        eb_neck_control = shared.create_editbone(ARMA,self.bone_neck_control)
        shared.match_editbone(eb_neck_control,ebs_source[0])
        eb_neck_control.parent = eb_neck_follow
        eb_neck_control.tail = ebs_source[-1].head
        eb_neck_control.layers = self.layer_control
        self._length_neck_control = eb_neck_control.length

        self.bone_head_follow = AFFIX(self.label_head+"_follow")
        eb_head_follow = shared.create_editbone(ARMA,self.bone_head_follow)
        shared.match_editbone(eb_head_follow,ebs_source[-1])
        shared.align_editbone_to_world_space(eb_head_follow)
        eb_head_follow.parent = eb_neck_control
        eb_head_follow.layers = self.layer_mech
                

        self.bone_head_control = AFFIX(self.label_head+"_control")
        eb_head_control = shared.create_editbone(ARMA,self.bone_head_control)
        shared.match_editbone(eb_head_control,ebs_source[-1])
        eb_head_control.parent = eb_head_follow 
        eb_head_control.layers = self.layer_control

        self.bones_tweak = []
        self.bones_ik = []
        self.bones_mech = []

        ebs_tweak = []
        ebs_ik = []
        ebs_mech = []

        for i in range(self.total_joints-1):
            
            is_first = i==0
            self.bones_tweak.append(AFFIX(self.labels_source[i]+"_tweak_control"))
            self.bones_ik.append(AFFIX(self.labels_source[i]+"_ik"))
            self.bones_mech.append(AFFIX(self.labels_source[i]+"_mech"))
        
            eb_mech = shared.create_editbone(ARMA,self.bones_mech[i])
            ebs_mech.append(eb_mech)
            eb_mech.layers = self.layer_mech

            if is_first:
                shared.match_editbone(eb_mech,eb_neck_control)
                eb_mech.parent = eb_neck_control
            else:
                shared.match_editbone(eb_mech,ebs_source[i])
                eb_mech.length*=.5
                eb_mech.parent = ebs_mech[0]
                eb_mech.inherit_scale = 'NONE'

            eb_tweak = shared.create_editbone(ARMA,self.bones_tweak[i])
            ebs_tweak.append(eb_tweak)
            shared.match_editbone(eb_tweak,ebs_source[i])
            eb_tweak.length*=.5
            eb_tweak.layers = self.layer_tweak

            if is_first:
                eb_tweak.parent = eb_neck_control
            else:
                eb_tweak.parent = ebs_mech[i]

            eb_ik = shared.create_editbone(ARMA,self.bones_ik[i])
            ebs_ik.append(eb_ik)
            shared.match_editbone(eb_ik,ebs_source[i])
            eb_ik.layers = self.layer_mech

            if is_first:
                eb_ik.parent = eb_tweak
            else:
                eb_ik.parent = ebs_ik[i-1]


        if (self.total_joints-1) % 2 == 0:
            bend_location = ebs_source[int((self.total_joints-1)/2)].head.copy()
        else:
            #have to implement this still, finding mid point in case of odd number of bones
            pass
        self.bone_bend_control = AFFIX(self.label_neck+"_bend_control")
        eb_bend = shared.create_editbone(ARMA,self.bone_bend_control)
        shared.match_editbone(eb_bend,eb_neck_control)
        eb_bend.head = bend_location
        eb_bend.parent = ebs_mech[0]
        eb_bend.layers = self.layer_control


        


        

    def begin_posemode(self):
        
        ARMA = self.arma
        AFFIX = self.affix.apply       
        shared.ensure_blender_mode('POSE')

        bone_group_control = self.env.get_bone_group(ARMA,self.bone_group_control_name)
        if self.bone_spine_connection_hub:
            
            pb_hub = shared.get_bone(ARMA,self.bone_spine_connection_hub)
            shared.add_custom_property(pb_hub,self.propid_head_follow,"Head will follow the connected spines rotation",0.0)
            shared.add_custom_property(pb_hub,self.propid_neck_follow,"Toggle between IK and FK mode",0.0)

        _bone_followers = [self.bone_neck_follow,self.bone_head_follow]
        _bone_followers_datapaths = []
        _bone_followers_datapaths.append(shared.write_posebone_datapath(self.bone_spine_connection_hub,self.propid_neck_follow))
        _bone_followers_datapaths.append(shared.write_posebone_datapath(self.bone_spine_connection_hub,self.propid_head_follow))

        for i in range(len(_bone_followers)):
            pb = shared.get_bone(ARMA,_bone_followers[i])
            cns = pb.constraints.new('COPY_ROTATION')
            cns.target = ARMA
            cns.subtarget = self.bone_spine_connection_torso
            driver = cns.driver_add("influence").driver
            driver.type = 'SUM'
            var = driver.variables.new()
            var.type = 'SINGLE_PROP'
            var.targets[0].id = ARMA               
            var.targets[0].data_path = _bone_followers_datapaths[i]

            cns = pb.constraints.new('COPY_SCALE')
            cns.target = ARMA
            cns.subtarget = self.bone_spine_connection_torso

        pb = shared.get_bone(ARMA,self.bone_neck_control)
        pb.custom_shape = self.env.get_custom_shape(self.custom_shape_neck_control_name)
        pb.custom_shape_translation[1] = self._length_neck_control/2
        pb.bone_group = bone_group_control

        pb = shared.get_bone(ARMA,self.bone_head_control)
        pb.custom_shape = self.env.get_custom_shape(self.custom_shape_head_control_name)
        pb.custom_shape_translation[1] = self._length_head*3
        pb.custom_shape_scale_xyz *= 3.5
        pb.bone_group = bone_group_control
        

        #calculate falloff influence of bend bone
        total_neck_bones = self.total_joints-1
        bend_falloffs = []
        
        #print("FALLOFFS:")
        if (total_neck_bones) % 2 == 0:
            half = int(total_neck_bones/2)
            step_falloff = 1.0/total_neck_bones

            falloff_modifer_array = []
            for i in range(total_neck_bones):
                val = (half-1)-i

                if i >= half:
                    val = 0 + (i-(half))

                falloff_modifer_array.append(val)
                #print ("I: "+str(i))
                #print("VAL: "+str(val))

            influence_falloff_array = []
            for i in range(len(falloff_modifer_array)):
                influence_falloff_array.append(1-(falloff_modifer_array[i]*step_falloff))
                #print("FALLOFF: "+str(influence_falloff_array[i]))
            
        else:
            #have to implement this still, finding mid point in case of odd number of bones
            pass

        for i in range(self.total_joints-1):

            is_first = i==0
            is_last = i==self.total_joints-2

            pb_ik = shared.get_bone(ARMA,self.bones_ik[i])
            shared.lock_all_bone_transforms(pb_ik)
            pb_ik.ik_stretch = .1
            if is_last:
                cns = pb_ik.constraints.new('IK')
                cns.target = ARMA
                cns.subtarget = self.bone_head_control
                cns.chain_count = self.total_joints-1 

            pb_mech = shared.get_bone(ARMA,self.bones_mech[i])
            shared.lock_all_bone_transforms(pb_mech)

            if is_first:
                cns = pb_mech.constraints.new('STRETCH_TO')
                cns.target = ARMA
                cns.subtarget = self.bone_head_control
                cns.volume = 'VOLUME_XZX'
            else:
                cns = pb_mech.constraints.new('COPY_LOCATION')
                cns.name = "Copy location from IK chain"
                cns.target = ARMA
                cns.subtarget = self.bones_ik[i]
                cns = pb_mech.constraints.new('COPY_LOCATION')
                cns.name = "Take influence from bend control"
                cns.target = ARMA
                cns.subtarget = self.bone_bend_control
                cns.use_offset = True
                cns.target_space = 'LOCAL'
                cns.owner_space = 'LOCAL'
                cns.influence = influence_falloff_array[i]
                cns = pb_mech.constraints.new('COPY_SCALE')
                cns.target = ARMA
                cns.subtarget = self.bone_neck_control


        pb = shared.get_bone(ARMA,self.bone_bend_control)
        pb.lock_rotation = [True,True,True]
        pb.lock_scale = [True,True,True]
        pb.custom_shape = self.env.get_custom_shape(self.custom_shape_bend_control_name)
        pb.bone_group = bone_group_control

        for i in range(self.total_joints-1):
            is_first = i==0
            is_last = i==self.total_joints-2

            pb = shared.get_bone(ARMA,self.bones_source[i])
            cns = pb.constraints.new('COPY_TRANSFORMS')
            cns.target = ARMA
            cns.subtarget = self.bones_tweak[i]
            cns = pb.constraints.new('STRETCH_TO')
            cns.target = ARMA
            if is_first:
                cns.subtarget = self.bones_tweak[i+1]
            else:
                cns.subtarget = self.bone_head_control
        
        pb = shared.get_bone(ARMA,self.bones_source[-1])
        cns = pb.constraints.new('COPY_TRANSFORMS')
        cns.target = ARMA
        cns.subtarget = self.bone_head_control

