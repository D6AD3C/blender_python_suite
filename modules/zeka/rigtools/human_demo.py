import bpy
import importlib
#import sys
#sys.path.append(r'D:\_python_scripts')
#import zeka.autorig.component.ik3_limb as ik3_limb

#import zeka.components.foot as foot
#import zeka.rig_compare as rig_compare
import zeka.utils as utils
import zeka.rigtools.shared as shared
import zeka.rigtools.environment as environment
import zeka.rigtools.humanoid_component as humanoid_component

import importlib
importlib.reload(humanoid_component)
importlib.reload(utils)
importlib.reload(shared)
importlib.reload(environment)

def rig_test2():

    proxy_arma = utils.make_proxy_arma(bpy.context.scene.objects['hu_f_m_body_arma'],"rig_proxy")
    proxy_arma.display_type = "WIRE"
    #proxy_arma.data.show_axes = True
    proxy_arma.show_in_front = True

    env = environment.Default()


    HU = humanoid_component.Component(proxy_arma,"humanoid")
    HU.shoulder_label = "clavicle"
    HU.ball_label = "toe"
    HU.run()

    utils.turn_off_all_arma_layers(proxy_arma)
    proxy_arma.data.layers[31] = False
    env.solo_layers(proxy_arma,['tweak','control'])

    print("COMPLETE")
    return


rig_test2()