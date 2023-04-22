import bpy
from mathutils import Matrix,Vector,Euler
from math import radians

def posebone_magic_rotate(pb,rots:list[float],invert=None):
    
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
    #Transforms don't update without calling update, unfortunately this makes it take FOREVER
    bpy.context.view_layer.update()



def snap_editbone_to_editbone(bone,target):
    if type(bone) == list:
        for b in bone:
            snap_editbone_to_editbone(b,target)
    else:  
        bone.matrix = target.matrix


def space_bone_along_bone(bones,target):
    target_vector = target.tail.copy() - target.head.copy()
    target_head = target.head.copy()

    for i,b in enumerate(reversed(bones)):
        b.head = (((target_vector.copy()/(len(bones)+1))*(i+1)) + target_head)
        b.tail = target.tail.copy()
        b.roll = target.roll

def apply_all_targeting_arma_modifiers(arma,ForcePreserveVolume=True):
    bpy.ops.object.mode_set(mode='OBJECT')
    for obj in bpy.context.scene.objects:        
        for modifier in obj.modifiers:
            if modifier.type == "ARMATURE":
                if modifier.object == arma:
                    print("Applying Armature Modifier: "+obj.name)
                    if ForcePreserveVolume==True:
                        modifier.use_deform_preserve_volume = True
                    bpy.context.view_layer.objects.active = obj
                    bpy.ops.object.modifier_apply(modifier=modifier.name)
                


connect_prop_id = "connected | ZEKA"

def write_all_editbones_connect_property(arma):   
    for eb in arma.data.edit_bones:
        if eb.use_connect == True:        
            eb[connect_prop_id] = 1
        else:
            eb[connect_prop_id] = 0 
        id_props = eb.id_properties_ui(connect_prop_id)
        eb.property_overridable_library_set('["'+connect_prop_id+'"]', True)
        id_props.update(default=0,min=0,max=1,description="Emulate a connection (ZEKA)",soft_min=0,soft_max=1)    
    
def update_magic_connect(arma):
    for eb in arma.data.edit_bones:
        if eb[connect_prop_id]==1:  
            eb.head.x = eb.parent.tail.x
            eb.head.y = eb.parent.tail.y
            eb.head.z = eb.parent.tail.z



def apply_pose_with_all_objects(arma,force_preserve_volume=True):

    bpy.ops.object.mode_set(mode='OBJECT')
    for obj in bpy.context.scene.objects: 
        bpy.context.view_layer.objects.active = obj       
        for i, modifier in zip(range(len(obj.modifiers)),obj.modifiers):
            if modifier.type == "ARMATURE":
                if modifier.object == arma:
                    new_modifier = obj.modifiers.new(modifier.name, 'ARMATURE')
                    new_modifier.object = arma
                    new_modifier.use_deform_preserve_volume = modifier.use_deform_preserve_volume
                    new_modifier.use_multi_modifier = modifier.use_multi_modifier
                    new_modifier.vertex_group = modifier.vertex_group
                    new_modifier.use_vertex_groups = modifier.use_vertex_groups
                    new_modifier.invert_vertex_group = modifier.invert_vertex_group
                    new_modifier.use_bone_envelopes = modifier.use_bone_envelopes
                    new_modifier.show_in_editmode = modifier.show_in_editmode
                    new_modifier.show_viewport = modifier.show_viewport
                    new_modifier.show_render = modifier.show_render             

                    index = i
                    name = modifier.name
                    if force_preserve_volume==True:
                        modifier.use_deform_preserve_volume = True
                    bpy.ops.object.modifier_apply(modifier=name)
                    new_modifier.name = name
                    
                    for i, other_modifier in zip(range(len(obj.modifiers)),obj.modifiers):   
                        if other_modifier == new_modifier:
                            new_index = i    

                    while new_index != index:
                        if(new_index>index):
                            bpy.ops.object.modifier_move_up(modifier=name)
                            new_index-=1
                        else:
                            bpy.ops.object.modifier_move_down(modifier=name)
                            new_index+=1

        for constraint in obj.constraints:
            if constraint.type == "ARMATURE":
                for target in constraint.targets:
                    if target.target == arma:
                        new_constraint = obj.constraints.new('ARMATURE') 
                        new_constraint.influence = constraint.influence
                        new_constraint.use_deform_preserve_volume = constraint.use_deform_preserve_volume
                        if force_preserve_volume:
                            new_constraint.use_deform_preserve_volume = True    
                        new_target = new_constraint.targets.new()
                        new_target.target = target.target
                        new_target.subtarget = target.subtarget
                        new_target.weight = target.weight
                        bpy.ops.constraint.apply(constraint=new_constraint.name,owner='OBJECT')

    bpy.context.view_layer.objects.active = arma
    bpy.ops.object.mode_set(mode='POSE')       
    bpy.ops.pose.armature_apply(selected=False)