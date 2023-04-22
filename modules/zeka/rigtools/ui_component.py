import bpy
from . import shared, environment
import zeka.utils as utils
from mathutils import Vector


class Slider():

    def __init__(self,arma,id,env=environment.get_default()):
        self.id = id
        self.arma = arma
        self.env = env
        self.custom_shape='panelbutton'
        self.bone_group = env.get_bone_group(self.arma,'control')
        self.layer = env.get_layer('control')

    def get_data_path(self):
        return shared.write_posebone_datapath(self.name,"prop_value") 

    def run_editmode(self,name,custom_shape='panelbutton',location=Vector([0,0,0])):
        ARMA = self.arma
        self.name = name

        bpy.ops.object.mode_set(mode='EDIT')

        b = shared.Bone("slide")\
            .set_name(name)\
            .create(self.arma)
        eb = b.get_blenderbone()
        eb.head = location
        eb.head[0] = location[0]
        eb.head[1] = location[1]
        eb.head[2] = location[2]
        eb.tail[0] = location[0]
        eb.tail[1] = location[1]+.025
        eb.tail[2] = location[2]
        eb.layers = self.layer

        bpy.ops.object.mode_set(mode='POSE')
        pb = b.get_blenderbone()
        pb.bone_group = self.bone_group
        pb.custom_shape = self.env.get_custom_shape("panelbutton") 
        utils.lock_all_bone_transforms(pb)
        pb.lock_location = [True,True,False]
        cns = pb.constraints.new('LIMIT_LOCATION')
        cns.use_min_x = True
        cns.use_min_y = True
        cns.use_min_z = True
        cns.use_max_x = True
        cns.use_max_y = True
        cns.use_max_z = True
        cns.max_z = 0.1
        cns.use_transform_limit = True
        cns.owner_space = 'LOCAL'
#bpy.data.objects["rig_proxy"].pose.bones["arm_ik_fk_l"]["prop_value"]
        shared.add_custom_property(pb,"prop_value","VALUE",0.0)
        driver = pb.driver_add('["prop_value"]').driver
        driver.type = 'SCRIPTED'
        driver.expression = '(y*10)'
        var = driver.variables.new()
        var.type = 'TRANSFORMS'
        var.name = 'y' 
        var.targets[0].id = self.arma 
        var.targets[0].bone_target = name
        var.targets[0].transform_space = 'LOCAL_SPACE'
        var.targets[0].transform_type = 'LOC_Z'

                


