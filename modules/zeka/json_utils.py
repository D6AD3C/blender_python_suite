import bpy
import json
import zeka.utils as utils

def bool_to_int(boolvalue:bool)->int:
    if boolvalue :
        return 1
    return 0

def bone_to_json_object(bone,recursive=True):

    bone_name = bone.name
    arma = bone.id_data

    bpy.ops.object.mode_set(mode='EDIT')
    eb = arma.data.edit_bones[bone_name]
    inherit_scale = eb.inherit_scale

    parent_name = ""
    if eb.parent!=None :
        parent_name = eb.parent.name

    bpy.ops.object.mode_set(mode='POSE')
    bone = arma.pose.bones.get(bone_name)

    j = dict()
    j["name"] = bone.name
    j["rotation_mode"] = bone.rotation_mode
    j["inherit_scale"] = inherit_scale
    j["ik_stretch"] = bone.ik_stretch
    j["parent"] = parent_name 

    save_rotation_mode = bone.rotation_mode
    xform = j["transforms"] = dict()  
    xform["location"] = [bone.location[0],bone.location[1],bone.location[2]]
    bone_rotation_mode = 'XYZ'
    xform["rotation"] = [bone.rotation_euler[0],bone.rotation_euler[1],bone.rotation_euler[2]]
    bone_rotation_mode = save_rotation_mode
    xform["scale"] = [bone.scale[0],bone.scale[1],bone.scale[2]]


    b_nonzero_xforms = False
    for l_ in xform["location"]:
        if l_ != 0.0:
            b_nonzero_xforms = True
            print("FOUND LOC!!!!!!!"+ str(l_))
    for r_ in xform["rotation"]:
        if r_ != 0.0:
            b_nonzero_xforms = True
    for s_ in xform["scale"]:
        if s_ != 1.0:
            b_nonzero_xforms = True

    j["nonzero_xforms"] = bool_to_int(b_nonzero_xforms)

    xform_lock = j["transform_locks"] = dict()   
    lock_loc = xform_lock["location"] = dict()
    lock_loc ["x"] = bool_to_int(bone.lock_location[0])
    lock_loc ["y"] = bool_to_int(bone.lock_location[1])
    lock_loc ["z"] = bool_to_int(bone.lock_location[2])
    lock_rot = xform_lock["rotation"] = dict()
    lock_rot["w"] = bool_to_int(bone.lock_rotation_w)
    lock_rot["x"] = bool_to_int(bone.lock_rotation[0])
    lock_rot["y"] = bool_to_int(bone.lock_rotation[1])
    lock_rot["z"] = bool_to_int(bone.lock_rotation[2])
    lock_scale = xform_lock["scale"] = dict()
    lock_scale["x"] = bool_to_int(bone.lock_scale[0])
    lock_scale["y"] = bool_to_int(bone.lock_scale[1])
    lock_scale["z"] = bool_to_int(bone.lock_scale[2])
    j["transform_locks"] = xform_lock

    bone_children = utils.get_bone_children(bone)
    j["children"] = []
    for c in bone_children:
        j["children"].append(bone_to_json_object(c,recursive))
    return j

def arma_to_json_object(arma):
    j = dict()
    j["id"] = arma.name
    j["bones"] = [] 
    bpy.ops.object.mode_set(mode='POSE')
    j["bones"].append(bone_to_json_object(arma.pose.bones[0],recursive=True))
    return j


def json_object_to_pretty_string(json_object,indent=1, sort_keys=False):
    return json.dumps(json_object,indent=indent,sort_keys=sort_keys)