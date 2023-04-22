import bpy
from mathutils import Matrix
import json

def matrix_to_data(matrix,size):
    matrix_array = []
    for row in range(size):
        matrix_array.append([])
        for col in range(size):
             matrix_array[row].append(matrix[row][col])
    return matrix_array

def matrix_from_data(data,size):
    matrix_rebuild = Matrix()
    for ix in range(size):
        for iy in range(size):
            matrix_rebuild[ix][iy] = data[ix][iy]
    return matrix_rebuild

def get_pose_data(arma):
    pose_data = dict()
    for pb in arma.pose.bones:
        pose_data[pb.name] = matrix_to_data(pb.matrix,4)  
    return pose_data

def load_pose_data(arma,pose_data): 
    for k,v in pose_data.items():
        bone_matrix = v
        bone_id = k
        print("Doing bone: "+bone_id)
        matrix_rebuild = matrix_from_data(bone_matrix,4)
        pb = arma.pose.bones.get(bone_id)
        pb.matrix = matrix_rebuild   
        
        #without this the armature explodes since matrices don't get updated after each change
        #makes the op take x10000 longer but I see no work around currently  
        bpy.context.view_layer.update()