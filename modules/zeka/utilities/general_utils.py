import bpy

def rename_custom_property(name, new_name, anything_array):

    for anything in anything_array:
        
        renames = []
        for k in anything.keys():
            if k ==name:
                renames.append(k)
                
        for k in renames:
            anything[new_name] = anything[k]
            id_props = anything.id_properties_ui(name)
            anything.property_overridable_library_set('["'+name+'"]', True)
            del anything[k]
            #eb[k].id = "WTF"
            #del eb[k]
    
def delete_custom_property(name, anything_array):

    for anything in anything_array:
        
        deletes = []
        for k in anything.keys():
            if k ==name:
                deletes.append(k)
                
        for k in deletes:
            del anything[k]

def update_custom_property(name, anything_array, description,default,  min,max,soft_min,soft_max,library_overridable):

    for anything in anything_array:
        
        deletes = []
        for k in anything.keys():
            if k ==name:
                id_props = anything.id_properties_ui(name)
                anything.property_overridable_library_set('["'+name+'"]',library_overridable)
                id_props.update(default=default)   
                id_props.update(description=description)
                id_props.update(min=min,max=max,soft_min=soft_min,soft_max=soft_max)


def mirror_vertex_group_names(object, type='SUFFIX', suffix="_l", mirrored_suffix="_r"):
    suffix_map = [suffix,mirrored_suffix]

    for group in object.vertex_groups:
        
        suffix = group.name[-2:]
        name = group.name[:-2]
        
        if suffix == suffix_map[0]:
                
            b_found = False
            goal_name = name+suffix_map[1]
            for other_group in object.vertex_groups:
                if other_group.name == goal_name:
                    b_found = True
                    
            if b_found == True:
                object.vertex_groups.remove(other_group)
                
            if b_found == False:
                object.vertex_groups.new(name=goal_name)