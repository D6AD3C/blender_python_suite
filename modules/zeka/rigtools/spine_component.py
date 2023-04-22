import bpy
from math import radians
import zeka.utils as utils
from . import shared, environment

class Component():

    def __init__(self,arma,id,env=environment.get_default()):
        self.id = id
        self.arma = arma
        self.env = env
        self.affix = shared.AffixData()
        self.labels_source = None
        self.label_spine = "spine"
        self.label_torso = "torso"
        self.label_hips = "hips"
        self.label_chest = "chest"
        
        self.layer_tweak = self.env.get_layer("tweak")
        self.layer_mech = self.env.get_layer("mech")
        self.layer_control_fk = self.env.get_layer("control")
        self.layer_control_special = self.env.get_layer("control")


        self.custom_shape_box = self.env.get_custom_shape("box")
        self.custom_shape_sphere = self.env.get_custom_shape("sphere")
        
        self.custom_shape_tweak_name = "sphere"
        self.custom_shape_torso_control_name = "box"
        self.custom_shape_hips_control_name = "humanhips"
        self.custom_shape_chest_control_name = "humanchest"
        self.custom_shape_fk_control_name = "circle"

        self.bone_group_control_special_name = "control"
        self.bone_group_control_fk_name = "control"
        self.bone_group_control_tweak_name = "tweak"

        self.layer_control_special = self.env.get_layer('control')
        self.total_joints = None
        self.spine_pivot_index = 2
        self.labels_source = []
        self.bones_source = []

        self.bone_root = 'root'
        self._bone_head_connector = None
        self.propid_torso_parent = "Torso Parent"

    def get_torso_control_bone(self):
        return self.bone_torso_control
    
    def get_head_connector_bone(self):
        return self._bone_head_connector
    
    def get_attribute_hub_bone(self):
        return self.bone_torso_control
    
    def init(self,labels_source):
        self.labels_source = labels_source
        for label in self.labels_source:
            self.bones_source.append(self.affix.apply(label))
        self.total_joints = len(self.labels_source)

        self.scale_modifier_bone_count_adaptive = self.total_joints/4

    def begin_editmode(self):

        ARMA = self.arma
        AFFIX = self.affix.apply

        shared.activate_arma(self.arma)        
        shared.ensure_blender_mode('EDIT')
    

        ebs_source = []
        self.source_bone_lengths = []
        for i in range(self.total_joints):
            eb = shared.get_bone(ARMA,self.bones_source[i])
            ebs_source.append(eb)
            self.source_bone_lengths.append(eb.length)

        self.bone_half_coordinates = []
        for i in range(self.total_joints-1):
            eb1 = ebs_source[i]
            eb2 = ebs_source[i+1]
            self.source_bone_lengths.append(eb1.length)
            halfway = utils.linear_interpolate_between_vectors(eb1.head,eb2.head,0.5)
            self.bone_half_coordinates.append(halfway)

        self.bone_torso_parent = AFFIX(self.label_torso+"_parent")
        eb_torso_parent = shared.create_editbone(ARMA,self.bone_torso_parent)
        eb_torso_parent.parent = None
        shared.match_editbone(eb_torso_parent,ebs_source[0])
        utils.align_editbone_to_worldspace(eb_torso_parent)
        utils.move_editbone(eb_torso_parent,self.bone_half_coordinates[0])
        eb_torso_parent.layers = self.layer_mech

        self.bone_torso_control = AFFIX(self.label_torso+"_control")
        eb_torso_control = shared.create_editbone(ARMA,self.bone_torso_control)
        shared.match_editbone(eb_torso_control,eb_torso_parent)
        eb_torso_control.parent = eb_torso_parent
        eb_torso_control.inherit_scale = 'AVERAGE'
        eb_torso_control.length *=2
        eb_torso_control.layers = self.layer_control_special


        self.bone_hips_control = AFFIX(self.label_hips+"_control")
        eb_hips_control = shared.create_editbone(ARMA,self.bone_hips_control)
        shared.match_editbone(eb_hips_control,ebs_source[self.spine_pivot_index])
        eb_hips_control.parent = eb_torso_control
        utils.align_editbone_to_worldspace(eb_hips_control)
        eb_hips_control.layers = self.layer_control_special 
      
        self.bone_chest_control = AFFIX(self.label_chest+"_control")
        eb_chest_control = shared.create_editbone(ARMA,self.bone_chest_control)
        shared.match_editbone(eb_chest_control,ebs_source[self.spine_pivot_index])
        utils.align_editbone_to_worldspace(eb_chest_control)
        eb_chest_control.parent = eb_torso_control
        eb_chest_control.length *=1.2
        eb_chest_control.layers = self.layer_control_special


        #BUILD LOWER MOVEMENT!
        #BUILD LOWER MOVEMENT!
        #BUILD LOWER MOVEMENT!
        #BUILD LOWER MOVEMENT!


        hips_pivot_bones = self.spine_pivot_index+1
        self.bones_downward_control = []
        self.bones_downward_mech = []
        self.bones_downward_tweak = []
        ebs_downward_control = []
        ebs_downward_mech = []
        ebs_downward_tweak = []
        

        for i in reversed(range(hips_pivot_bones)):
            str_index = str(i)

            is_first = False
            if i==hips_pivot_bones-1:
                is_first = True
                
            is_last = False
            if i == 0:
                is_last = True

            if is_last != True:
                name_mech = AFFIX(self.labels_source[i-1]+"_mech")
                self.bones_downward_mech.append(name_mech)
                eb_mech = shared.create_editbone(ARMA,name_mech)
                ebs_downward_mech.append(eb_mech)
                shared.match_editbone(eb_mech,ebs_source[i])
                eb_mech.layers = self.layer_mech
                utils.align_editbone_to_worldspace(eb_mech)
                if is_first :
                    eb_mech.parent =  eb_torso_control
                else:
                    eb_mech.parent = ebs_downward_control[i-1]
                
                name_control = AFFIX(self.labels_source[i-1]+"_fk_control")
                self.bones_downward_control.append(name_control)
                eb_control = shared.create_editbone(ARMA,name_control)
                ebs_downward_control.append(eb_control)
                shared.match_editbone(eb_control,ebs_source[i-1])
                utils.move_editbone(eb_control,ebs_source[i].head)
                eb_control.parent = eb_mech
                eb_control.layers = self.layer_control_fk
                

                if not is_first:
                    name_tweak = AFFIX(self.labels_source[i]+"_tweak_control")
                    self.bones_downward_tweak.append(name_tweak)
                    eb_tweak = shared.create_editbone(ARMA,name_tweak)
                    ebs_downward_tweak.append(eb_tweak)
                    shared.match_editbone(eb_tweak,ebs_source[i])
                    eb_tweak.parent = eb_control
                    eb_tweak.length *= .5
                    eb_tweak.layers = self.layer_tweak
            else:            
                name_final_downward_tweak = AFFIX(self.labels_source[0]+"_tweak_control")
                self.bones_downward_tweak.append(name_final_downward_tweak) 
                eb_final_downward_tweak = shared.create_editbone(ARMA,name_final_downward_tweak)
                ebs_downward_tweak.append(eb_final_downward_tweak)
                shared.match_editbone(eb_final_downward_tweak,ebs_source[0])
                eb_final_downward_tweak.parent = ebs_downward_control[-1]
                eb_final_downward_tweak.length *=.5
                eb_final_downward_tweak.layers = self.layer_tweak

                self.bone_hips_widget_guide = AFFIX(self.label_hips+"_widget_guide")
                eb_hips_widget_guide = shared.create_editbone(ARMA,self.bone_hips_widget_guide)
                shared.match_editbone(eb_hips_widget_guide,ebs_source[0])
                eb_hips_widget_guide.parent = ebs_downward_control[-1]
                eb_hips_widget_guide.layers = self.layer_mech

        self.bones_hip_pivot_mechs = self.bones_downward_mech
        self.bones_fk_controls = self.bones_downward_control
        self.bones_tweaks = self.bones_downward_tweak
        self.bones_hip_pivot_mechs.reverse()
        self.bones_fk_controls.reverse()
        self.bones_tweaks.reverse()

        #END OF LOWER MOVEMENT!
        #END OF LOWER MOVEMENT!
        #END OF LOWER MOVEMENT!



        #UPPER MOVEMENT
        #UPPER MOVEMENT
        #UPPER MOVEMENT
        
        upper_movement_bones = self.total_joints - self.spine_pivot_index

        self.bones_upward_mech = []
        self.bones_upward_control = []
        self.bones_upward_tweak = []
        ebs_upward_mech = []
        ebs_upward_control = []
        ebs_upward_tweak = []

        for i in range(upper_movement_bones):
            actual_index = self.spine_pivot_index+i
            str_index = str(actual_index)
            
            is_first = False
            if(i==0):
                is_first = True

            is_last = False
            if i == upper_movement_bones-1:
                is_last = True

            name_mech = AFFIX(self.labels_source[actual_index]+"_mech")
            self.bones_upward_mech.append(name_mech)
            eb_mech = shared.create_editbone(ARMA,name_mech)
            ebs_upward_mech.append(eb_mech)
            shared.match_editbone(eb_mech,ebs_source[actual_index])
            eb_mech.layers = self.layer_mech
            utils.align_editbone_to_worldspace(eb_mech)

            if is_first:
                eb_mech.parent = eb_torso_control
            else:
                eb_mech.parent = ebs_upward_control[i-1]

            name_control = AFFIX(self.labels_source[actual_index]+"_fk_control")
            self.bones_upward_control.append(name_control)
            eb_control = shared.create_editbone(ARMA,name_control)
            shared.match_editbone(eb_control,ebs_source[actual_index])
            ebs_upward_control.append(eb_control)
            eb_control.parent = eb_mech
            eb_control.layers = self.layer_control_fk
            

            if is_first:
                self.bone_mech_pivot = AFFIX(self.label_spine+"_pivot_mech")
                eb_mech_pivot = shared.create_editbone(ARMA,self.bone_mech_pivot)
                shared.match_editbone(eb_mech_pivot,shared.get_bone(ARMA,self.bones_fk_controls[self.spine_pivot_index-1]))
                eb_mech_pivot.parent = eb_control
                eb_mech_pivot.layers = self.layer_mech
                eb_dynamic_tweak_parent = eb_mech_pivot
            else:
                eb_dynamic_tweak_parent = eb_control 

            name_tweak = AFFIX(self.labels_source[actual_index]+"_tweak_control")            
            self.bones_upward_tweak.append(name_tweak)
            eb_tweak = shared.create_editbone(ARMA,name_tweak)
            ebs_upward_tweak.append(eb_tweak)
            shared.match_editbone(eb_tweak,eb_control)
            eb_tweak.parent = eb_dynamic_tweak_parent
            eb_tweak.length *= .5
            eb_tweak.layers = self.layer_tweak

            if is_last:
                self.bone_chest_widget_guide = AFFIX(self.label_chest+"_widget_guide")
                eb_chest_widget_guide = shared.create_editbone(ARMA,self.bone_chest_widget_guide)
                shared.match_editbone(eb_chest_widget_guide,eb_control)
                eb_chest_widget_guide.parent = eb_control
                eb_chest_widget_guide.layers = self.layer_mech

                name_final_tweak = AFFIX(self.label_spine+"_top_tweak_control")
                self.bones_upward_tweak.append(name_final_tweak)
                eb_final_tweak = shared.create_editbone(ARMA,name_final_tweak)
                ebs_upward_tweak.append(eb_final_tweak)
                shared.match_editbone(eb_final_tweak,ebs_source[-1])
                utils.move_editbone(eb_final_tweak,ebs_source[-1].tail)
                eb_final_tweak.parent = eb_control
                eb_final_tweak.length *= .5
                eb_final_tweak.layers = self.layer_tweak

        self.bones_tweaks = []
        self.bones_tweaks+= self.bones_downward_tweak
        self.bones_tweaks+= self.bones_upward_tweak

        self.bones_fk_controls = []
        self.bones_fk_controls+= self.bones_downward_control
        self.bones_fk_controls+= self.bones_upward_control

        self.bones_tweaks = []
        self.bones_tweaks+= self.bones_downward_tweak
        self.bones_tweaks+= self.bones_upward_tweak

        #END UPPER MOVEMENT
        #END UPPER MOVEMENT
        #END UPPER MOVEMENT

        self._bone_head_connector = self.bones_fk_controls[-1]
        

    def begin_posemode(self):
        
        ARMA = self.arma
        AFFIX = self.affix.apply       
        shared.ensure_blender_mode('POSE')

        bone_group_control_special = self.env.get_bone_group(ARMA,self.bone_group_control_special_name)
        bone_group_control_fk = self.env.get_bone_group(ARMA, self.bone_group_control_fk_name)
        bone_group_control_tweak = self.env.get_bone_group(ARMA, self.bone_group_control_tweak_name)

        

        pb_torso_parent = shared.get_bone(ARMA, self.bone_torso_parent)
        utils.lock_all_bone_transforms(pb_torso_parent)
        cns = pb_torso_parent.constraints.new('ARMATURE')
        cns.name = "switch_parent"
        target = cns.targets.new()
        target.target = ARMA
        target.subtarget = self.bone_root
        
        


        pb_torso_control = shared.get_bone(ARMA,self.bone_torso_control)
        pb_torso_control.bone_group = bone_group_control_special
        pb_torso_control.custom_shape = self.env.get_custom_shape(self.custom_shape_torso_control_name)
        pb_torso_control.custom_shape_scale_xyz = [1.25,1.25,0.75]
        pb_torso_control.custom_shape_scale_xyz *= self.scale_modifier_bone_count_adaptive

        shared.add_custom_int_property(pb_torso_control,self.propid_torso_parent,"Toggle between IK and FK mode",1)

        pb_hips_control = shared.get_bone(ARMA,self.bone_hips_control)
        pb_hips_control.bone_group = bone_group_control_special
        pb_hips_control.custom_shape = self.env.get_custom_shape(self.custom_shape_hips_control_name)
        pb_hips_control.custom_shape_scale_xyz = [3.0,3.0,3.0]
        pb_hips_control.custom_shape_transform = shared.get_bone(ARMA,self.bone_hips_widget_guide)
        pb_hips_control.custom_shape_scale_xyz *= self.scale_modifier_bone_count_adaptive

        pb_chest_control = shared.get_bone(ARMA,self.bone_chest_control)
        pb_chest_control.bone_group = bone_group_control_special
        pb_chest_control.custom_shape = self.env.get_custom_shape(self.custom_shape_chest_control_name)
        pb_chest_control.custom_shape_scale_xyz = [3.0,3.0,3.0]
        pb_chest_control.custom_shape_transform = shared.get_bone(ARMA,self.bone_chest_widget_guide)
        pb_chest_control.custom_shape_scale_xyz *= self.scale_modifier_bone_count_adaptive

        for bone in self.bones_downward_mech:

            pb = shared.get_bone(ARMA,bone)
            utils.lock_all_bone_transforms(pb)
            cns = pb.constraints.new('COPY_TRANSFORMS')
            cns.name = "Copy Transforms"
            cns.target = ARMA
            cns.subtarget = self.bone_hips_control
            cns.target_space = 'LOCAL'
            cns.owner_space = 'LOCAL'
            cns.influence = 1/self.spine_pivot_index
            
        for bone in self.bones_upward_mech:
            pb = shared.get_bone(ARMA,bone)
            utils.lock_all_bone_transforms(pb)
            cns = pb.constraints.new('COPY_TRANSFORMS')
            cns.name = "Copy Transforms"
            cns.target = ARMA
            cns.subtarget = self.bone_chest_control
            cns.target_space = 'LOCAL'
            cns.owner_space = 'LOCAL'
            cns.influence = 1/(self.total_joints-self.spine_pivot_index)

        for i in range(len(self.bones_fk_controls)):
            bone = self.bones_fk_controls[i]
            pb = shared.get_bone(ARMA,bone)
            pb.bone_group = bone_group_control_fk
            pb.custom_shape = self.env.get_custom_shape(self.custom_shape_fk_control_name)
            if i < self.spine_pivot_index:
                pb.custom_shape_translation.y = -self.source_bone_lengths[i]/2
            else:
                pb.custom_shape_translation.y = self.source_bone_lengths[i]/2        

        for bone in self.bones_tweaks:
            pb = shared.get_bone(ARMA,bone)
            pb.bone_group = bone_group_control_tweak
            pb.custom_shape = self.env.get_custom_shape(self.custom_shape_tweak_name)
            pb.rotation_mode = 'ZXY'
            pb.lock_rotation = [True,False,True]
            pb.lock_scale = [False,True,False]

        pb = shared.get_bone(ARMA,self.bone_hips_widget_guide)
        utils.lock_all_bone_transforms(pb)

        pb = shared.get_bone(ARMA,self.bone_chest_widget_guide)
        utils.lock_all_bone_transforms(pb)
    
        pb = shared.get_bone(ARMA,self.bone_mech_pivot)
        utils.lock_all_bone_transforms(pb)
        cns = pb.constraints.new('COPY_TRANSFORMS')
        cns.name = "Copy Transforms"
        cns.target = ARMA
        cns.subtarget = self.bones_fk_controls[self.spine_pivot_index-1]
        cns.target_space = 'WORLD'
        cns.owner_space = 'WORLD'
        cns.influence = 1/(self.total_joints-self.spine_pivot_index)
        
        number_of_tweaks = len(self.bones_tweaks)
        for i in range(number_of_tweaks-1):
            pb = shared.get_bone(ARMA,self.bones_source[i])
            utils.lock_all_bone_transforms(pb)
            cns = pb.constraints.new('COPY_TRANSFORMS')
            cns.name = "Copy Transforms"
            cns.target = ARMA
            cns.subtarget = self.bones_tweaks[i]

            if i < number_of_tweaks-1:
                cns = pb.constraints.new('STRETCH_TO')
                cns.target = self.arma
                cns.subtarget = self.bones_tweaks[i+1]