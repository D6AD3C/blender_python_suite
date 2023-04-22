import bpy
import json
import zeka.utils as utils


class HierarchicalBone():

    def __init__(self,bone):
        self.bone_id = bone.name
        self.arma = bone.id_data
        arma_posebones = self.arma.pose.bones
        self.children = []
        for arma_posebone in arma_posebones:
            if(arma_posebone.parent == bone):
                self.children.append(HierarchicalBone(arma_posebone))

    def print(self,depth):
        indent = ""
        for d in range(depth):
            indent+="   "
        print(indent+self.bone_id)        
        for c in self.children:
            c.print(depth+1)
        
    def to_json(self):
        j = dict()
        j["name"] = self.bone_id
        j["children"] = []
        for c in self.children:
            j["children"].append(c.to_json())
        return j




class BoneHierarchyPrinter():

    def __init__(self):
        pass


    def print_loop(bone):
        pass
    def print(self,arma):
        bpy.ops.object.mode_set(mode='POSE')
        hb = HierarchicalBone(arma.pose.bones[0])
        hb.print(0)
        pass
    

