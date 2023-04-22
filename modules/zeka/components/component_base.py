import bpy
from enum import Enum
import zeka.utils as utils
import zeka.shared.bone_adaptive as bone_adaptive
import importlib
importlib.reload(bone_adaptive)




class Affixer():

    def __init__(self):
        self.type = 'NONE'
        self.affix = None
        
    def get_affix(self)->str:
        return self.affix
     
    def add_affix(self,name)->str:
        if(self.affix!=None):
            if self.type=='SUFFIX':
                name+=self.affix
        return name

    def remove_affix(self,name:str)->str:
        if(self.affix!=None):
            if self.type=='SUFFIX':
                return name[:len(self.affix)*-1]
        
    def detect_affix(self,bone_name)->str:   
        last2 = bone_name[-2:]
        known_suffix = ["_l","_L",".l",".L","_r","_R",".r",".R"]
        for suffix in known_suffix:
            if last2 == suffix:
                self.affix = suffix
                self.type = 'SUFFIX'
        return self




class Tagger():

    def __init__(self):
        self.mech = "mech"
        self.parent = "parent"
        self.switch = "switch"
        self.control = "control"
        self.tweak = "tweak"
        self.ik = "ik"
        self.fk = "fk"
        self.tweak = "tweak"
        self.affix = ""

    def tag(self,name,tags)->str:
        if 'IK' in tags:
            name = name+"_"+self.ik
        if 'FK' in tags:
            name = name+"_"+self.fk
        if 'MECH' in tags:
            name = name+"_"+self.mech
        if 'PARENT' in tags:
            name = name+"_"+self.parent
        if 'SWITCH' in tags:
            name = name+"_"+self.switch
        if 'CONTROL' in tags:
            name = name+"_"+self.control
        if 'TWEAK' in tags:
            name = name+"_"+self.tweak
        if 'AFFIX' in tags:
            name = name+self.affix

        return name
    






class LogF():

    class Entry():
        
        def __init__(self,flag,text):
            self.flag = flag
            self.text = text

    def __init__(self,id):
        self.id = self.set_id(id)
        self.entries = []

    def div(self):
        print("\n--------------------------------------")
        
    def set_id(self,id):
        self.id = id
        return id
    
    def write(self,flag,text):
        print(self.id+" | "+text)
        self.entries.append(self.Entry(flag,text))
    



class TagCommand():

    def __init__(self,id:str,order:int,func:callable):
        self.id = id
        self.order = order
        self.func = func

class TaggerAdvanced():

    def __init__(self):
        self.tags = []
        

    def update(self):
        self.tags.sort(key=lambda x: x.order, reverse=False)

    def set_tag(self,id,order,func):
        self.tags.append(TagCommand(id,order,func))

    def register_cmds(self):
        pass
    
    def tag(self,name,tags):
        for tag_cmd in self.tags:
            for tag in tags:
                if tag_cmd.id == tag:
                    name = tag_cmd.func(name,tags)
        return name
    
class BoneTagger(Tagger):

    def __init__(self):   
        super().__init__()
        def MECH(name,tags):
            return name+"_m"
        def CONTROL(name,tags):
            return name+"_control" 
        def TWEAK(name,tags):
            return name+"_tweak"  
        def PARENT(name,tags):
            return name+"_parent" 
        def SWITCH(name,tags):
            return name+"_switch" 
               
        
        self.set_tag('PARENT',0,PARENT)
        self.set_tag('MECH',4,MECH)
        self.set_tag('CONTROL',5,CONTROL)
        self.set_tag('TWEAK',6,TWEAK)
        self.set_tag('SWITCH',7,SWITCH)

        self.update()


class BoneDict():

    def __init__(self):
        self.bones = dict()

    def add(self,id):
        if type(id) == list:
            for i in id:
                self.add(i)
        else:
            self.bones[id] = bone_adaptive.BoneWithData()

    def set_all_arma(self,arma):
        for key,value in self.bones.items():
            value.set_arma(arma)

    def get_bone(self,id):
        return self.bones[id]
    
    def print_all_bones(self):
        for bone_id,bone in self.bones.items():
            if bone :
                print("     "+bone_id+" : "+bone.get_name())  
    
class ComponentBase():

    def __init__(self):
        b_failed:bool = False
        pass

    def fail(self):
        b_failed=True
        return False

        