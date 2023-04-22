import bpy
from mathutils import Matrix,Vector,Euler
from math import pi,radians,degrees
import mathutils


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
    e1.location = arm.matrix_world * bone.matrix * Vector([0,0,0])
    e2.location = arm.matrix_world * bone.matrix * Vector([0,arm.data.bones[bone.name].length,0])


#arma = bpy.context.scene.objects['a1']

#m1 = arma.pose.bones.get('bone').matrix

#print(m1)
print(degrees(.7071))
#M = Matrix()
#v = Vector()
#M @ v
#Vector((0.0, 0.0, 0.0))

def matrix_for_bone_from_parent(pb):
    m = pb.matrix # * Matrix.Scale(eb1.length,4)
    pm = pb.parent.matrix
    return pm.inverted() @ m

pb = bpy.context.selected_pose_bones[-1]
euler = Euler(map(radians, (0,0,90)), 'ZYX')
#pb.matrix = euler.to_matrix().to_4x4()

loc, rot, scale = pb.matrix.decompose()

smat = Matrix()
for i in range(3):
    smat[i][i] = scale[i]

#R = mathutils.Matrix.Rotation(0, 4, 'X')
#mat = Matrix.Translation(loc) @ R @ smat


#mat = Matrix.Translation(loc) @ euler.to_matrix().to_4x4() @ smat
#pb.matrix = mat

def matrix_scale(scale_vec):
    return Matrix([[scale_vec[0],0,0,0],
                   [0,scale_vec[1],0,0],
                   [0,0,scale_vec[2],0],
                   [0,0,0,1]
    ])



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
    
#pb.matrix = matrix_the_hard_way(pb,bpy.data.objects['gamma'])




pb = bpy.context.selected_pose_bones[-1]
euler = Euler(map(radians, (0,0,90)), 'ZYX')
loc, rot, scale = pb.matrix.decompose()
smat = Matrix()
for i in range(3):
    smat[i][i] = scale[i]
pb.location = loc

#rot = mathutils.Matrix.Rotation(-90, 4, 'X')
euler = Euler(map(radians, (0,0,90)), 'ZYX')
rot_euler = euler.to_matrix().to_4x4()
#loc, rot, scale = pb.matrix.decompose()

#result_m = rot.to_matrix().to_4x4().inverted() @ rot_euler
#ploc,prot,pscale = result_m.decompose()
#prot = rot

loc, rot, scale = pb.matrix.decompose()
ploc, prot, pscale = (pb.parent.matrix.inverted() @ pb.matrix).decompose()

if 'QUATERNION' == pb.rotation_mode:
    pb.rotation_quaternion = prot
else:
    pb.rotation_euler = prot.to_euler(pb.rotation_mode)
#pb.scale = scale


#R = mathutils.Matrix.Rotation(0, 4, 'X')
#mat = Matrix.Translation(loc) @ R @ smat


#mat = Matrix.Translation(loc) @ euler.to_matrix().to_4x4() @ smat


#pb.matrix = matrix_for_bone_from_parent(pb) @ mat
#print(str(loc))
#print(str(rot))

#print(pb.parent.name)
#matrix_for_bone_from_parent(pb)
#pb.matrix = matrix_for_bone_from_parent(pb).inverted() @ euler.to_matrix().to_4x4()
