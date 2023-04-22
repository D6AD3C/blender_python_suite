import bpy
import json
import os
from mathutils import Matrix
from math import pi
from math import radians
from mathutils import Vector


def turn_off_all_arma_layers(arma):
    arma.data.layers = [False] * 32

def copy_object(obj:bpy.types.Object,new_id,delete_if_exists:bool=False)->bpy.types.Object:
    if delete_if_exists:
        remove_and_unlink_object(new_id)
    copied_data = obj.data.copy()
    copied_data.name = new_id
    new_object = bpy.data.objects.new(new_id, copied_data)
    bpy.context.scene.collection.objects.link(new_object) 
    return new_object

def remove_and_unlink_object(obj):
    if type(obj)==str:
        if bpy.data.objects.get(obj) != None:
            remove_and_unlink_object(bpy.data.objects[obj])
    if type(obj)==bpy.types.Object:
        obj.data.name = obj.data.name+"_UNLINKED"
        bpy.data.objects.remove(obj, do_unlink=True)

def get_selected_bones():
    if bpy.context.object.mode == "EDIT":
        return bpy.context.selected_bones
    elif bpy.context.object.mode == "POSE":
        return  bpy.context.selected_pose_bones
    else:
        return []
    
def get_arma_from_bone(bone):
    if(type(bone)==list):
        if(len(bone)==0):
            return False
        return get_arma_from_bone(bone[0])    
    if bpy.context.object.mode == "EDIT":
        return bpy.context.object
    elif bpy.context.object.mode == "POSE":
        return  bone.id_data
    else:
        return None
    
def set_mode(mode:str):
    bpy.ops.object.mode_set(mode=mode)

def get_bone(arma,id):
    if bpy.context.object.mode == "EDIT":
        return arma.data.edit_bones.get(id)
    elif(bpy.context.object.mode=='POSE'):
        posebone = arma.pose.bones.get(id)
        if posebone != None:
            return posebone
        else:
            print("utils: Missing pose bone -> "+id) 

def new_editbone(arma,new_editbone_id):
    if bpy.context.object.mode != "EDIT":
        bpy.ops.object.mode_set(mode="EDIT")
    new_editbone = arma.data.edit_bones.new(new_editbone_id)
    return new_editbone

def match_editbone(editbone,target_editbone):
    if bpy.context.object.mode != "EDIT":
        bpy.ops.object.mode_set(mode="EDIT")
    editbone.head = target_editbone.head.copy()
    editbone.tail = target_editbone.tail.copy()
    editbone.roll = target_editbone.roll        
    return editbone

#Aligns a bone so it's local pivot matches the world.
#It will maintain it's current length but it's tail will point directly down the y+ axis.
def align_editbone_to_worldspace(editbone):
    length = editbone.length
    editbone.tail = editbone.head
    editbone.tail.y+=length
    editbone.roll = 0


def align_editbone_to_global_axis(editbone,axis):
    length = editbone.length
    if axis=='Z+':
        editbone.tail = editbone.head
        editbone.tail.z += length
        editbone.roll = 0

def set_parent(editbone,parent_editbone):
    editbone.parent = parent_editbone      
    return editbone


def lock_all_bone_transforms(posebone):
    posebone.lock_location = [True,True,True]
    posebone.lock_rotation_w = True
    posebone.lock_rotation = [True,True,True]
    posebone.lock_scale = [True,True,True]

#get a point between two vectors normalize within the range of 0.0 - 1.0 equalling 0 to 100% of it's length
def linear_interpolate_between_vectors(v1,v2,amount):
    #0.0-1.0 
    return v1+((v2-v1)*amount)

def move_editbone(editbone,position):
    difference = position-editbone.head
    editbone.head+=difference
    editbone.tail+=difference

#Move an Editbone bone along it's current heading.
def slide_editbone(editbone,distance_to_slide):
    start_length = editbone.length
    editbone.length = distance_to_slide
    result_tail = editbone.tail.copy()
    editbone.length = distance_to_slide+.1
    editbone.head = result_tail
    editbone.length = start_length   


def rotate_editbone_on_axis(editbone,axis,degrees):
    old_head = editbone.head.copy() 
    if axis == 'X':
        axis_output = editbone.z_axis.normalized()
    R = Matrix.Rotation(radians(degrees), 4, editbone.z_axis.normalized())   
    editbone.transform(R, roll=True) 
    offset_vec = -(editbone.head - old_head)
    editbone.head += offset_vec
    editbone.tail += offset_vec 


def make_editbone_perpendicular_on_x(editbone,flip):
    old_head = editbone.head.copy()    
    angle = -90
    R = Matrix.Rotation(radians(angle), 4, editbone.z_axis.normalized())   
    editbone.transform(R, roll=True) 
    offset_vec = -(editbone.head - old_head)
    editbone.head += offset_vec
    editbone.tail += offset_vec 

def reverse_editbone(editbone):      
    head = editbone.head.copy()
    tail = editbone.tail.copy()
    editbone.head = tail
    editbone.tail = head
    
#Reflects the bone on it's head in the opposite direction    
def reflect_editbone(editbone):
    head = editbone.head.copy()
    tail = editbone.tail.copy()
    editbone.tail = editbone.head
    editbone.tail -= (tail-head)

def get_pole_vector(shoulder_editbone, elbow_editbone):
    lo_vector = elbow_editbone.vector
    tot_vector = elbow_editbone.tail - shoulder_editbone.head
    return (lo_vector.project(tot_vector) - lo_vector).normalized() * .5

def get_pole_angle(shoulder_editbone, elbow_editbone,elbow_vector,axis_letter):
        vector = getattr(shoulder_editbone, axis_letter+'_axis') + getattr(elbow_editbone, axis_letter+'_axis')

        if elbow_vector.angle(vector) > pi/2:
            return -pi/2
        else:
            return pi/2
        
def delete_bones_on_axis(armature,axis,tolerance=-0.00001):
    bpy.ops.object.mode_set(mode='EDIT')
    #bpy.context.view_layer.objects.active = armature
    del_count = 0
    if axis == 'X-':
        for editbone in armature.data.edit_bones:
            if editbone.head.x < tolerance:
                del_count+=1
                armature.data.edit_bones.remove(editbone)
    print("zeka.utils.delete_bones_on_axis | deleted bone count: "+str(del_count))

def get_bone_children(bone): 
    if bpy.context.object.mode=='POSE':
        arma = bone.id_data
        arma_posebones = arma.pose.bones
        children = []
        for arma_posebone in arma_posebones:
            if(arma_posebone.parent == bone):
                children.append(arma_posebone)
        return children
    
def enumclass_to_str_list(enum_class):
    str_array = []
    for e in enum_class:
        str_array.append(e.value)
    return str_array



def set_armature_modifier_target(object,new_arma):
    modifier = get_armature_modifier(object);
    modifier.object = new_arma;

def set_armature_target_for_all_objects_in_collection(collection,armature):    
    for ob in collection.all_objects:
        set_armature_modifier_target(ob,armature)

def get_armature_modifier(obj):
    for modifier in obj.modifiers:
        if modifier.type == "ARMATURE":
            return modifier
    return None

def make_proxy_arma(source_arma,new_name,modifier_id="Copy Transforms"):
    remove_all_bone_constraints_in_arma(source_arma)
    bpy.ops.object.mode_set(mode='POSE')
    proxy = copy_object(source_arma,new_name,True)
    transform_constraint_all_bones_to_armature(source_arma,proxy,modifier_id)
    return proxy

def transform_constraint_all_bones_to_armature(source_arma,target_arma,modifier_id="Copy Transforms"):
    
    bpy.ops.object.mode_set(mode='POSE')

    for pb in source_arma.pose.bones:
        crc = pb.constraints.new('COPY_TRANSFORMS')
        crc.name = "Copy Transforms"
        crc.target = target_arma
        crc.subtarget = pb.name

def remove_all_bone_constraints(posebone):
    for constraint in posebone.constraints:
        posebone.constraints.remove(constraint)

def remove_all_bone_constraints_in_arma(arma):    
    arma.select_set(True)
    bpy.context.view_layer.objects.active = arma
    bpy.ops.object.mode_set(mode='POSE')
    for posebone in arma.pose.bones:
        remove_all_bone_constraints(posebone)



def load_object_from_blendfile(file_path,inner_path,object_name): 
    #file_path = 'D:/11.blend'
    #inner_path = 'Object'
    #object_name = 'Suzanne'

    bpy.ops.wm.append(
        filepath=os.path.join(file_path, inner_path, object_name),
        directory=os.path.join(file_path, inner_path),
        filename=object_name
        )