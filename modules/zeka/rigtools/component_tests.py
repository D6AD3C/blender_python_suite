import bpy
import zeka.utils as utils
from zeka.rigtools import environment, spine_component, neck_component, palm_component, arm_component, leg_biped_component, shared
import time
import importlib
importlib.reload(utils)
importlib.reload(shared)
importlib.reload(spine_component)
importlib.reload(neck_component)
importlib.reload(arm_component)
importlib.reload(leg_biped_component)
importlib.reload(palm_component)

class Stopwatch():

    def __init__(self):
        self.start()
        pass
    
    def start(self):
        self.time_start = time.time()
    
    def stop_str(self):
        return str(round(time.time()-self.time_start,3))

def shared_conclusion_settings(arma,env=environment.get_default()):
    arma.display_type = "WIRE"
    arma.data.show_axes = True
    arma.show_in_front = True
    utils.turn_off_all_arma_layers(arma)
    arma.data.layers[31] = False
    env.solo_layers(arma,['mech','tweak','control'])

def arm_compoment_test(default_pose='t_pose'):

    print("---------------------------------------------------------")
    print("Testing Component: arm_component - "+default_pose)
    stopwatch = Stopwatch()
    
    arma_name = "arm_component_tpose"
    if default_pose==default_pose=='a_pose':
        arma_name = "arm_component_apose"

    copyed_arma = utils.copy_object(bpy.context.scene.objects[arma_name], arma_name+"_proxy",True)
    
    arm = arm_component.Component(copyed_arma,"arm_test")
    arm.affix = shared.AffixData().set_suffix("_l")       
    arm.init("shoulder_l")
    arm.begin_editmode()
    arm.begin_posemode()

    shared_conclusion_settings(copyed_arma)
    print("     completed in: "+stopwatch.stop_str())

def leg_compoment_test(default_pose='t_pose'):

    print("---------------------------------------------------------")
    print("Testing Component: leg_biped - "+default_pose)
    stopwatch = Stopwatch()
    
    arma_name = "leg_biped_component_tpose"
    if default_pose==default_pose=='a_pose':
        arma_name = "leg_biped_component_apose"

    copyed_arma = utils.copy_object(bpy.context.scene.objects[arma_name], arma_name+"_proxy",True)

    leg = leg_biped_component.Component(copyed_arma,"leg_test")
    leg.affix = shared.AffixData().set_suffix("_l")
    leg.shin_label = "shin"         
    leg.run_editmode("pelvis")
    leg.run_posemode()

    shared_conclusion_settings(copyed_arma)
    print("     completed in: "+stopwatch.stop_str())


def palm_compoment_test():

    print("---------------------------------------------------------")
    print("Testing Component: palm")
    stopwatch = Stopwatch()
    
    arma_name = "palm_component"
    
    copyed_arma = utils.copy_object(bpy.context.scene.objects[arma_name], arma_name+"_proxy",True)

    palm = palm_component.Component(copyed_arma,"palm")
    palm.affix = shared.AffixData().set_suffix("_l")
    palm.init('hand_l')
    palm.begin_editmode()
    palm.begin_posemode()

    shared_conclusion_settings(copyed_arma)
    print("     completed in: "+stopwatch.stop_str())


def spine_component_test(test_type):

    test = '4 bones'
    arma_name = "spine_component"
    bones_spine = ['pelvis','spine1','spine2','spine3']
    if test_type=="6_bones":
        arma_name+="_6_bones"
        bones_spine += ['spine4','spine5']
        test = '6 bones'
        
    print("---------------------------------------------------------")
    print("Testing Component: spine_component "+test)
    stopwatch = Stopwatch()
    

    copyed_arma = utils.copy_object(bpy.context.scene.objects[arma_name], arma_name+"_proxy",True)
    copyed_arma.display_type = "WIRE"
    copyed_arma.data.show_axes = True
    copyed_arma.show_in_front = True

    spine = spine_component.Component(copyed_arma,"spine")
    spine.init(bones_spine)
    spine.begin_editmode()
    spine.begin_posemode()

    shared_conclusion_settings(copyed_arma)
    print("     completed in: "+stopwatch.stop_str())



def spine6_and_neck3_test():
        
    print("\n---------------------------------------------------------")
    print("Running Test: Spine(6B) and Neck(3B)")
    arma_name = "spine6_neck3_component"

    copyed_arma = utils.copy_object(bpy.context.scene.objects[arma_name], arma_name+"_proxy",True)
    stopwatch = Stopwatch()
    print("     starting spine(6B)...")
    stopwatch_single = Stopwatch()
    spine = spine_component.Component(copyed_arma,"spine")
    spine.init(['pelvis','spine1','spine2','spine3','spine4','spine5'])
    spine.begin_editmode()
    spine.begin_posemode()
    print("         spine(6B) completed in: "+stopwatch_single.stop_str())

    print("     starting neck(3B)...")
    stopwatch_single.start()
    
    neck = neck_component.Component(copyed_arma,"neck")
    neck.enable_connection_with_spine(
        spine.get_torso_control_bone(),
        spine.get_attribute_hub_bone(),
        spine.get_head_connector_bone()
        )
    neck.init(['neck1','neck2','head'])
    neck.begin_editmode()
    neck.begin_posemode()

    print("         neck(3B) completed in: "+stopwatch_single.stop_str())
    print("     total operation completed in: "+stopwatch.stop_str())
    shared_conclusion_settings(copyed_arma)
    

def spine6_and_neck5_test():
        
    print("\n---------------------------------------------------------")
    print("Running Test: Spine(6B) and Neck(5B)")
    arma_name = "spine6_neck5_component"

    copyed_arma = utils.copy_object(bpy.context.scene.objects[arma_name], arma_name+"_proxy",True)
    stopwatch = Stopwatch()
    print("     starting spine(6B)...")
    stopwatch_single = Stopwatch()
    spine = spine_component.Component(copyed_arma,"spine")
    spine.init(['pelvis','spine1','spine2','spine3','spine4','spine5'])
    spine.begin_editmode()
    spine.begin_posemode()
    print("         spine(6B) completed in: "+stopwatch_single.stop_str())

    print("     starting neck(5B)...")
    stopwatch_single.start()
    
    neck = neck_component.Component(copyed_arma,"neck")
    neck.enable_connection_with_spine(
        spine.get_torso_control_bone(),
        spine.get_attribute_hub_bone(),
        spine.get_head_connector_bone()
        )
    neck.init(['neck1','neck2','neck3','neck4','head'])
    neck.begin_editmode()
    neck.begin_posemode()

    print("         neck(5B) completed in: "+stopwatch_single.stop_str())
    print("     total operation completed in: "+stopwatch.stop_str())
    shared_conclusion_settings(copyed_arma)
    

#utils.remove_all_bone_constraints_in_arma(bpy.context.scene.objects["leg_biped_component"])
#spine_component_test("4_bones")
#spine_component_test('6_bones')
#spine6_and_neck3_test()
#spine6_and_neck5_test()
#arm_compoment_test("a_pose")

arm_compoment_test('a_pose')

#palm_compoment_test()
#leg_compoment_test()
#leg_compoment_test('a_pose')
