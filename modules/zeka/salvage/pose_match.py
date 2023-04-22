__author__ = 'thoth'

# http://blender.stackexchange.com/questions/63878/how-to-map-a-pose-to-the-restpose-of-another-rig-with-same-topology


import bpy
from mathutils import *

def explore_matrices(arm):
    for bone in arm.data.bones:
        #print ( [ bone.name, bone.head_local, bone.matrix_local*Vector([0,0,0])])
        print ( [ bone.name, bone.tail_local, bone.matrix_local@Vector([0,bone.length,0])])


def scene_link(obj, scn):
    try:
        scn.objects.link(obj)
    except:
        pass


def check1(arm):
    bone = arm.pose.bones[2]

    e1 = bpy.data.objects.get("head")
    if e1 is None:
        e1 = bpy.data.objects.new("head", None)
    scn = bpy.context.scene
    scene_link(e1, scn)
    e2 = bpy.data.objects.get("tail")
    if e2 is None:
        e2 = bpy.data.objects.new("tail", None)
    scene_link(e2, scn)
    e1.location = arm.matrix_world @ bone.matrix @ Vector([0,0,0])
    e2.location = arm.matrix_world @ bone.matrix @ Vector([0,arm.data.bones[bone.name].length,0])


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
    return E_p.inverted() @ E

def matrix_the_hard_way(pose_bone, ao):
    if pose_bone.rotation_mode == 'QUATERNION':
        mr = pose_bone.rotation_quaternion.to_matrix().to_4x4()
    else:
        mr = pose_bone.rotation_euler.to_matrix().to_4x4()
    m1 = Matrix.Translation(pose_bone.location) @ mr @ matrix_scale(pose_bone.scale)

    E = ao.data.bones[pose_bone.name].matrix_local
    if pose_bone.parent is None:
        return E @ m1
    else:
        m2 = matrix_the_hard_way(pose_bone.parent, ao)
        E_p = ao.data.bones[pose_bone.parent.name].matrix_local
        return m2 @ E_p.inverted() @ E @ m1

def pose_to_match(arm, goal):
    """
    pose arm so that its bones line up with the REST pose of goal
    """

    matrix_os= {}
    for to_match in goal.data.bones:
        matrix_os[to_match.name] = to_match.matrix_local
        #print([ "matrix", to_match.name, matrix_os[to_match.name] ] )

    #xyz' = s * m * m(parent) * xyz

    for to_pose in arm.pose.bones:
        if to_pose.parent is None:
            len2 = arm.data.bones[to_pose.name].length
            len1 = goal.data.bones[to_pose.name].length
            to_pose.matrix = matrix_os[to_pose.name] @ Matrix.Scale(len1/len2, 4)
        else:
            # we can not set .matrix, because a lot of stuff behind the scenes has not yet
            # caught up with our alterations, and it ends up doing math on outdated numbers
            mp = matrix_the_hard_way(to_pose.parent, arm) @ matrix_for_bone_from_parent(to_pose, arm)
            m2 = mp.inverted()* matrix_os[to_pose.name] @ Matrix.Scale(goal.data.bones[to_pose.name].length, 4)
            loc,rot,scale = m2.decompose()
            to_pose.location = loc
            if 'QUATERNION' == to_pose.rotation_mode:
                to_pose.rotation_quaternion = rot
            else:
                to_pose.rotation_euler = rot.to_euler(to_pose.rotation_mode)
            to_pose.scale = scale / arm.data.bones[to_pose.name].length



#
#
#

#explore_matrices(bpy.data.objects['beta'])

#pose_to_match(bpy.data.objects['Armature.001'], bpy.data.objects['Armature'])

pose_to_match(bpy.data.objects['gamma'], bpy.data.objects['beta'])


#check1(bpy.data.objects['gamma'])