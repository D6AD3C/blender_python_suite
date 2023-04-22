import bpy
import zeka.utils as utils
from mathutils import Matrix
from math import pi,radians,degrees

def get_pole_vector(shoulder_editbone, elbow_editbone, distance = 1.0):
    lo_vector = elbow_editbone.vector
    tot_vector = elbow_editbone.tail - shoulder_editbone.head
    return (lo_vector.project(tot_vector) - lo_vector).normalized() * distance

def get_pole_angle(shoulder_editbone, elbow_editbone,elbow_vector,axis_letter):
        vector = getattr(shoulder_editbone, axis_letter+'_axis') + getattr(elbow_editbone, axis_letter+'_axis')

        if elbow_vector.angle(vector) > pi/2:
            return -pi/2
        else:
            return pi/2

def align_editbone_to_global_axis(editbone,axis):
    length = editbone.length
    #incomplete,needs other axis
    if axis=='Z+':
        editbone.tail = editbone.head
        editbone.tail.z += length
        editbone.roll = 0

def rotate_editbone_on_axis(editbone,axis,degrees):
    old_head = editbone.head.copy() 
    if axis == 'X':
        axis_output = editbone.z_axis.normalized()
    R = Matrix.Rotation(radians(degrees), 4, axis_output)   
    editbone.transform(R, roll=True) 
    offset_vec = -(editbone.head - old_head)
    editbone.head += offset_vec
    editbone.tail += offset_vec 

def lock_all_bone_transforms(posebone):
    posebone.lock_location = [True,True,True]
    posebone.lock_rotation_w = True
    posebone.lock_rotation = [True,True,True]
    posebone.lock_scale = [True,True,True]

def reflect_editbone(editbone):
    head = editbone.head.copy()
    tail = editbone.tail.copy()
    editbone.tail = editbone.head
    editbone.tail -= (tail-head)

def reverse_editbone(editbone):      
    head = editbone.head.copy()
    tail = editbone.tail.copy()
    editbone.head = tail
    editbone.tail = head
    
def move_editbone(editbone,position):
    difference = position-editbone.head
    editbone.head+=difference
    editbone.tail+=difference

def editbone_flatten_axis(editbone,axis):
    if axis=='Z':
        length = editbone.length
        editbone.tail.z = editbone.head.z
        editbone.length = length

def align_editbone_to_world_space(editbone):
    length = editbone.length
    editbone.tail = editbone.head
    editbone.tail.y+=length
    editbone.roll = 0

def create_editbone(arma,name):
    if bpy.context.object.mode != "EDIT":
        bpy.ops.object.mode_set(mode="EDIT")    
    if arma.data.edit_bones.get(name):
        raise Exception("Bone already exists: "+name) 
    new_editbone = arma.data.edit_bones.new(name)
    return new_editbone

def match_editbone(editbone,target_editbone):
    if bpy.context.object.mode != "EDIT":
        bpy.ops.object.mode_set(mode="EDIT")
    editbone.head = target_editbone.head.copy()
    editbone.tail = target_editbone.tail.copy()
    editbone.roll = target_editbone.roll        
    return editbone

def ensure_bone_in_arma(arma, required):
    if(type(required)==list):
        for r in required:
            ensure_bone_in_arma(arma,r)
    else:
        get_bone(arma,required)

def get_bone(arma,name):
    bb = None
    if bpy.context.object.mode == "EDIT":
        bb = arma.data.edit_bones.get(name)
    elif bpy.context.object.mode=='POSE':
        bb =  arma.pose.bones.get(name)
    elif bpy.context.object.mode=='OBJECT':
        bb =  arma.data.bones.get(name)

    if bb == None:
        raise Exception("Bone was not found: "+name) 
    return bb
           
       

def ensure_blender_mode(mode):
    if bpy.context.object.mode != mode:
        bpy.ops.object.mode_set(mode=mode)
        
def activate_arma(arma):
    bpy.context.view_layer.objects.active = arma

def get_bone_adaptive(arma,name):
    if bpy.context.object.mode == "EDIT":
        return arma.data.edit_bones.get(name)
    elif(bpy.context.object.mode=='POSE'):
        posebone = arma.pose.bones.get(name)
        if posebone != None:
            return posebone
        else:
            print("utils: Missing pose bone -> "+name) 

def write_posebone_datapath(bone_id,key):
    return 'pose.bones["'+bone_id+'"]["'+key+'"]'  

def add_custom_property(obj,id,description,value,default=1.0,min=0.0,max=1.0,soft_min=0.0,soft_max=1.0,overridable_library=True):
        obj[id] = value
        id_props = obj.id_properties_ui(id)
        obj.property_overridable_library_set('["'+id+'"]', overridable_library)
        id_props.update(default=default,min=min,max=max,description=description,soft_min=soft_min,soft_max=soft_max)

def add_custom_int_property(obj,id,description,value,default=1,min=0,max=1,soft_min=0,soft_max=1,overridable_library=True):
        obj[id] = value
        id_props = obj.id_properties_ui(id)
        obj.property_overridable_library_set('["'+id+'"]', overridable_library)
        id_props.update(default=default,min=min,max=max,description=description,soft_min=soft_min,soft_max=soft_max)


class CustomProperty2():

    def __init__(self,type,prop_id,description):
        self.type = type
        self.prop_id = prop_id
        self.object_name = None
        self.arma = None
        self.overridable_library = True
        self.description = description
        if type=='INT':
            self.min = 0
            self.max = 1
            self.soft_min=0
            self.soft_max=1
            self.default = None

        if type=="FLOAT":
            self.min = 0.0
            self.max = 1.0
            self.soft_min=0.0
            self.soft_max=1.0       
            self.default = None

    def create(self,arma,object,value):
        self.arma = arma
        if self.default==None:
            self.default = value

        self.object_name = object.name
        object[self.prop_id] = value
        id_props = object.id_properties_ui(self.prop_id)
        object.property_overridable_library_set('["'+self.prop_id+'"]', self.overridable_library)
        id_props.update(default=self.default,min=self.min,max=self.max,description=self.description,soft_min=self.soft_min,soft_max=self.soft_max)



    def write_path(self):
        return write_posebone_datapath(self.object_name,self.prop_id,)
    
class CustomProperty():

    def __init__(self,obj_name,prop_id,type):
        self.obj_name = obj_name
        self.prop_id, = prop_id,
        self.type = type
       
    def write_path(self):
        return write_posebone_datapath(self.obj_name,self.prop_id,)

class CustomPropertyWriter():

    def __init__(self,obj,id,value,type_override=None):
        self.obj = obj
        self.id = id
        self.description = ""
        self.default = value
        self.value = value
        self.overridable_library = True

        if type(value) == float:
            self.type = 'float'
        elif type(value) == int:
            self.type = 'int'

        if self.type=='float':
            self.min = 0.0
            self.max = 1.0
            self.soft_min=0.0
            self.soft_max=1.0
        elif self.type=='int':
            self.min = 0
            self.max = 1
            self.soft_min=0
            self.soft_max=1

    def create(self):
        self.obj[self.id] = self.value
        id_props = self.obj.id_properties_ui(self.id)
        self.obj.property_overridable_library_set('["'+self.id+'"]', self.overridable_library)
        id_props.update(default=self.default,min=self.min,max=self.max,description=self.description,soft_min=self.soft_min,soft_max=self.soft_max)
        return CustomProperty(self.obj.name,self.id,self.type)

class EditboneData():

    def __init__(self,eb):
        self.head = eb.head.copy()
        self.tail = eb.tail.copy()
        self.roll = eb.roll
        self.length = eb.length

class AffixData():

    def __init__(self):
        self.type = 'NONE'
        self.tag = ""

    def set_suffix(self,tag):
        self.type = 'SUFFIX'
        self.tag = tag
        return self

    def apply(self,name):
        return name+self.tag