import bpy
from mathutils import Matrix,Vector,Euler
from math import pi,radians,degrees
import mathutils

import zeka.utilities.pose_saver as pose_saver
import importlib
importlib.reload(pose_saver)

#loc, rot, scale = pb.matrix.decompose()
#ploc, prot, pscale = (pb.parent.matrix.inverted() @ pb.matrix).decompose()

#matrix_world = bpy.context.scene.objects['gamma'].matrix_world @ pb.matrix
#mwloc,mwrot,mwscale = matrix_world.decompose()
#matrix_world = matrix_world @ rot_euler
#pb.matrix = matrix_world.inverted() @ pb.matrix

#if 'QUATERNION' == pb.rotation_mode:
#    pb.rotation_quaternion = mwrot
#else:
#    pb.rotation_euler = mwrot.to_euler(pb.rotation_mode)
#pb.scale = scale


#R = mathutils.Matrix.Rotation(0, 4, 'X')
#mat = Matrix.Translation(loc) @ R @ smat


#mat = Matrix.Translation(loc) @ euler.to_matrix().to_4x4() @ smat


#pb.matrix = matrix_for_bone_from_parent(pb) @ mat
#print(str(loc))
#print(str(rot))

#print(pb.parent.name)
#matrix_for_bone_from_parent(pb)

#location = Vector([0,0,0]).to_matrix().to_4x4()
#rotation = Vector([0,0,0]).to_matrix().to_4x4()
#scale = Vector([1,1,1]).to_matrix().to_4x4()




def align_pose_bone_OLD(pb,rots:list[float],invert=False):
    
    rot1 = rots[0]
    rot2 = rots[1]
    roll = rots[2]
    Vector
    if invert_x==True:
        roll*=-1
        rot2*=-1
        
    smat = Matrix()
    for i in range(3):
        smat[i][i] = 1
   
    euler_roll = Euler(map(radians, (0,roll,0)), 'XYZ')
    rot_euler_roll = euler_roll.to_matrix().to_4x4()

    euler_x = Euler(map(radians, (rot1,0,rot2)), 'XYZ')
    rot_euler_x = euler_x.to_matrix().to_4x4()


    rot_euler_final = rot_euler_x @ rot_euler_roll
    ploc,prot,pscale = (bpy.context.scene.objects['hu_f_m_body_arma'].matrix_world @ pb.matrix).decompose()
    #print(ploc)
    mat = Matrix.Translation(ploc) @  rot_euler_final @ smat

    pb.matrix = mat
    bpy.context.view_layer.update()

def align_pose_bone(pb,rots:list[float],invert=None):
    
    rot_x = rots[0]
    rot_y = rots[1]
    roll = rots[2]
    
    vector = Vector([rot_x,rot_y,roll])

    if type(invert) == str:

        if invert=="X":
            vector.x*=1
            vector.y*=-1
            vector.z*=-1

        
    smat = Matrix()
    for i in range(3):
        smat[i][i] = 1
   
    euler_roll = Euler(map(radians, (0,vector.z,0)), 'XYZ')
    rot_euler_roll = euler_roll.to_matrix().to_4x4()
    
    euler_rot = Euler(map(radians, (vector.x,vector.y,0)), 'XYZ')
    rot_euler_rot = euler_rot.to_matrix().to_4x4()


    rot_euler_final = rot_euler_rot @ rot_euler_roll
    ploc,prot,pscale = (pb.id_data.matrix_world @ pb.matrix).decompose()
    #print(ploc)
    mat = Matrix.Translation(ploc) @  rot_euler_final @ smat

    pb.matrix = mat
    bpy.context.view_layer.update()
    
def tpose():
    affix_list = ["_l","_r"]
    arma = bpy.context.scene.objects['hu_f_m_body_arma']
    for i in range(2):
        affix = affix_list[i]
        invert = 'NONE'
        if i==1:
            invert = 'X'        
        arm_rot1 = [80,120,0]
        arm_rot2 = [110,120,0]
        leg_rot = [-90,-20,0]

        pbs = arma.pose.bones
        align_pose_bone(pbs.get('upperarm'+affix),[90,90,0],invert=invert)
        align_pose_bone(pbs.get('forearm'+affix),[90,90,0],invert=invert)
        align_pose_bone(pbs.get('hand'+affix),[90,90,0],invert=invert)
        align_pose_bone(pbs.get('thigh'+affix),[-90,0,0],invert=invert)
        align_pose_bone(pbs.get('shin'+affix),[-90,0,0],invert=invert)
            
        fingerlabels = ['index','middle','ring','pinky']
        for finger in range(4):
            for joint in range(2):
                finger_name = "finger_"+fingerlabels[finger]+str(joint+1)+affix
                print(finger_name)
                align_pose_bone(arma.pose.bones.get(finger_name),[90,90,0],invert=invert)
        
        thumb_rotation = [180,0,90]
        align_pose_bone(pbs.get('finger_thumb1'+affix),thumb_rotation,invert=invert)
        align_pose_bone(pbs.get('finger_thumb2'+affix),thumb_rotation,invert=invert)
        align_pose_bone(pbs.get('finger_thumb3'+affix),thumb_rotation,invert=invert)

def apose():

    affix_list = ["_l","_r"]
    arma = bpy.context.scene.objects['hu_f_m_body_arma']
    for i in range(2):
        affix = affix_list[i]
        invert = 'NONE'
        if i==1:
            invert = 'X'        
        arm_rot1 = [80,120,0]
        arm_rot2 = [110,120,0]
        leg_rot = [-90,-20,0]
        align_pose_bone(arma.pose.bones.get('upperarm'+affix),[80,120,0],invert=invert)
        align_pose_bone(arma.pose.bones.get('forearm'+affix),[110,120,0],invert=invert)
        align_pose_bone(arma.pose.bones.get('hand'+affix),[90,120,0],invert=invert)
        align_pose_bone(arma.pose.bones.get('thigh'+affix),leg_rot,invert=invert)
        align_pose_bone(arma.pose.bones.get('shin'+affix),leg_rot,invert=invert)

#tpose()

def matrix_to_data(matrix,size):
    row_array = []
    for row in range(size):
        row_array.append([])
        for col in range(size):
             row_array[row].append(matrix[row][col])
    return row_array
        
import json
def save_all_matrix(arma):
    matrix_array = []
    for pb in arma.pose.bones:
        data = dict()
        data['id'] = pb.name
        data['matrix'] = matrix_to_data(pb.matrix,4)
        matrix_array.append(data)
    bpy.context.scene.objects['hu_f_m_body_arma'].data['pose_save'] =  json.dumps(matrix_array)

def load_all_matrix(arma):
    json_string = bpy.context.scene.objects['hu_f_m_body_arma'].data['pose_save']
    bone_data = json.loads(json_string)
    
    for bone in bone_data:
        bone_matrix = bone['matrix']
        bone_id = bone['id']
        print("Doing bone: "+bone_id)
        matrix_rebuild = Matrix()
        for ix in range(4):
            for iy in range(4):
                matrix_rebuild[ix][iy] = bone_matrix[ix][iy]
        pb = arma.pose.bones.get(bone_id)
        pb.matrix = matrix_rebuild    
        bpy.context.view_layer.update()

def save_matrix(bone):
    matrix =  bpy.context.scene.objects['hu_f_m_body_arma'].pose.bones.get(bone).matrix
    bpy.context.scene.objects['hu_f_m_body_arma'].data['pose_save'] = matrix
    print(str(matrix))
    matrix_rebuild = Matrix()
    for ix in range(4):
        for iy in range(4):
            matrix_rebuild[ix][iy] = matrix[ix][iy]
    print(str(matrix_rebuild))

def load_matrix(bone):
    matrix = bpy.context.scene.objects['hu_f_m_body_arma'].data['pose_save']
    matrix_rebuild = Matrix()
    for ix in range(4):
        for iy in range(4):
            matrix_rebuild[ix][iy] = matrix[ix][iy]
    bpy.context.scene.objects['hu_f_m_body_arma'].pose.bones.get(bone).matrix = matrix_rebuild
    print(str(matrix_rebuild))   


arma =  bpy.context.scene.objects['hu_f_m_body_arma']


is_save = True
if is_save:
    arma.data['pose_save'] = json.dumps(pose_saver.get_pose_data(arma))
else:
    pose_saver.load_pose_data(arma,json.loads(arma.data['pose_save']))

#save_all_matrix(arma)
#load_all_matrix(arma)

#save_matrix('forearm_l')
#load_matrix('forearm_l')