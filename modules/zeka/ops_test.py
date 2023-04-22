import bpy
from math import pi,radians,degrees
from mathutils import Matrix, Vector
import math
import mathutils
arma = bpy.context.scene.objects['hu_f_m_body_arma']

pb = bpy.context.selected_pose_bones[-1]
print(pb.name)
#lo_vector.project(tot_vector)


mw = arma.convert_space(
        pose_bone=pb,
        matrix=pb.matrix,
        from_space='POSE',
        to_space='WORLD',
        )

#axis_output = pb.z_axis.normalized()
#t = pb.matrix.to_translation().resize_4d()
#s = pb.matrix.to_scale().resize_4x4()
#r = Matrix.Rotation(radians(.001), 4, 'Z').resize_4d()
#R = mathutils.Matrix.LocRotScale(t,r,s).resize_4d()   
#q = pb.matrix.toQuat()
#pb.matrix = mathutils.Matrix.Rotation(180, 4, 'X')
#pb.location = [0,0,0]
#pb.matrix = R

#print(str(q))


def matrix_scale(scale_vec):
    return Matrix([[scale_vec[0],0,0,0],
                   [0,scale_vec[1],0,0],
                   [0,0,scale_vec[2],0],
                   [0,0,0,1]
    ])

def matrix_for_bone_from_parent(bone, ao):
    eb1 = ao.data.bones[bone.name]
    E = eb1.matrix_local # * Matrix.Scale(eb1.length,4)
    ebp = ao.data.bones[bone.name].parent
    E_p = ebp.matrix_local # * Matrix.Scale(ebp.length,4)
    return E_p.inverted() * E

def matrix_for_bone_from_parent2(bone, ao):
    eb1 = ao.data.bones[bone.name]
    E = eb1.matrix # * Matrix.Scale(eb1.length,4)
    ebp = ao.data.bones[bone.name].parent
    E_p = ebp.matrix # * Matrix.Scale(ebp.length,4)
    return E_p.inverted() * E

matrix = matrix_for_bone_from_parent2(pb,arma)
pb.matrix = matrix.to_4x4()

def outcome():
    target_rotation = Vector([0,0,0])
    target_vector = Vector([0,0,1])
    target_roll = 0
    bone = bpy.context.object.data.bones.active
    name = bone.name
    bpy.ops.object.mode_set(mode='EDIT')
    eb = bpy.context.object.data.edit_bones[name]
    head = eb.head.copy()
    tail = eb.tail.copy()
    length = eb.length
    eb = bpy.context.object.data.edit_bones.new(name+"TEMP_ALIGN_ASSIST")
    temp_name = eb.name

    eb.head = head.copy()
    eb.tail = head.copy()
    eb.tail[0]+=target_vector.x
    eb.tail[1]+=target_vector.y
    eb.tail[2]+=target_vector.z
    eb.length = length
    eb.roll = radians(target_roll)

    #bpy.context.scene.update()

    matrix = eb.matrix
    #context.object.data.edit_bones.remove(eb)

    bpy.ops.object.mode_set(mode='POSE')
    pb = bpy.context.object.pose.bones.get(name)
    tpb = bpy.context.object.pose.bones[temp_name]   
    tpb.rotation_mode = 'XYZ'
    tpb.rotation_euler[0] = radians(target_rotation.x)
    tpb.rotation_euler[1] = radians(target_rotation.y)
    tpb.rotation_euler[2] = radians(target_rotation.z)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.mode_set(mode='POSE')
    pb.matrix = tpb.matrix

    pb.location[0] = 0
    pb.location[1] = 0
    pb.location[2] = 0

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.context.object.data.edit_bones.remove(bpy.context.object.data.edit_bones[temp_name])
    bpy.ops.object.mode_set(mode='POSE')

    #seemed clean, would look but roll could not be adjusted correctly, maybe revist.
    #bv = pb.tail-pb.head
    #rd = bv.rotation_difference(v)

    #M = (
    #Matrix.Translation(pb.head) @
    #rd.to_matrix().to_4x4() @
    #Matrix.Translation(-pb.head)
    #)
    #pb.matrix = M @ pb.matrix