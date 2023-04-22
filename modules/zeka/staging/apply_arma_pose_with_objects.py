import bpy


def apply_arma_pose_with_objects(arma,force_preserve_volume=True):

    found_modifier_data_array = []

    class found_modifier_data:

        def __init__(self):
            self.object = None
            self.modifier = None
            self.index = None
            self.name = None
            self.use_deform_preserve_volume = None
            self.use_multi_modifier = None
            self.vertex_group = None
            self.use_vertex_groups = None
            self.invert_vertex_groups = None
            self.use_bone_envelopes = None
            self.show_in_editmode = None
            self.show_viewport = None
            self.show_render = None

    bpy.ops.object.mode_set(mode='OBJECT')
    for obj in bpy.context.scene.objects:        
        for i, modifier in zip(range(len(obj.modifiers)),obj.modifiers):
            if modifier.type == "ARMATURE":
                if modifier.object == arma:
                    data = found_modifier_data()
                    data.object = obj
                    data.name = modifier.name
                    data.modifier = modifier
                    data.index = i
                    data.use_deform_preserve_volume = modifier.use_deform_preserve_volume
                    data.use_multi_modifier = modifier.use_multi_modifier
                    data.vertex_group = modifier.vertex_group
                    data.use_vertex_groups = modifier.use_vertex_groups
                    data.invert_vertex_group = modifier.invert_vertex_group
                    data.use_bone_envelopes = modifier.use_bone_envelopes
                    data.show_in_editmode = modifier.show_in_editmode
                    data.show_viewport = modifier.show_viewport
                    data.show_render = modifier.show_render
                    found_modifier_data_array.append(data)

    for data in found_modifier_data_array:
        if force_preserve_volume==True:
            data.modifier.use_deform_preserve_volume = True
        bpy.context.view_layer.objects.active = data.object
        bpy.ops.object.modifier_apply(modifier=data.modifier.name)
    
    #bpy.context.view_layer.update()

    bpy.context.view_layer.objects.active = arma
    bpy.ops.object.mode_set(mode='POSE')       
    bpy.ops.pose.armature_apply(selected=False)
    #bpy.context.view_layer.update()
    
    bpy.ops.object.mode_set(mode='OBJECT')

    for data in found_modifier_data_array:
        bpy.context.view_layer.objects.active = data.object
        new_modifier = data.object.modifiers.new(data.name, 'ARMATURE')
        new_modifier.name = data.name
        new_modifier.object = arma
        new_modifier.use_deform_preserve_volume = data.use_deform_preserve_volume
        new_modifier.use_multi_modifier = data.use_multi_modifier
        new_modifier.vertex_group = data.vertex_group
        new_modifier.use_vertex_groups = data.use_vertex_groups
        new_modifier.invert_vertex_group = data.invert_vertex_group
        new_modifier.use_bone_envelopes = data.use_bone_envelopes
        new_modifier.show_in_editmode = data.show_in_editmode
        new_modifier.show_viewport = data.show_viewport
        new_modifier.show_render = data.show_render
        

        index = -1
        for i, modifier in zip(range(len(data.object.modifiers)),data.object.modifiers):   
            if modifier == new_modifier:
                index = i    

        while index != data.index:
            if(index>data.index):
                bpy.ops.object.modifier_move_up(modifier=data.name)
                index-=1
                print(str(index))
                print(str(data.index))
                print("MOVED DOWN")
            else:
                bpy.ops.object.modifier_move_down(modifier=data.name)
                print("MOVED UP")
                index+=1


apply_arma_pose_with_objects(bpy.context.view_layer.objects.active)