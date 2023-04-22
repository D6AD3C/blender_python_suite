
#developer extras might need to be enabled to have these work

import bpy
from bpy.types import (Operator,IntProperty)
import bmesh

import zeka.utilities.general_utils as general_utils

def MeshPartsTraitDetection_enumer(scene, context):
    items = []
    index = 0
    items.append((str(index),'No Report',''))
    index+=1
    items.append((str(index),'New TextDoc',''))
    index+=1
    for i, obj in enumerate(bpy.data.texts):
            items.append((str(index+1),obj.name,''))
            index+=1
    return items

class ZEKA_OT_MeshAnalysis(Operator):
    """Rotate a posebone to an exact angle magically"""
    bl_idname = "zeka.mesh_analysis"
    bl_label = "ZEKA: Mesh Analysis"
    bl_description = "Rotate a posebone to an exact angle magically"
    bl_options = {'REGISTER','UNDO'}


    selection_only: bpy.props.BoolProperty(name = 'In Selection Only', default=False)
    report_enum: bpy.props.EnumProperty(items = MeshPartsTraitDetection_enumer, name="Report")

    select_tri: bpy.props.BoolProperty(name = 'Select Tris', default=False)
    select_quad: bpy.props.BoolProperty(name = 'Select Quads', default=False)
    select_ngon: bpy.props.BoolProperty(name = 'Select Ngons', default=False)
    select_concave: bpy.props.BoolProperty(name = 'Select Concave', default=False)
    select_nearzero: bpy.props.BoolProperty(name = 'Select NearZero', default=False)
    nearzero_x_only: bpy.props.BoolProperty(name = 'Near Zero on X only', default=True)

    @classmethod
    def poll(cls, context):
        if(bpy.context.object.type == 'MESH' and context.active_object.mode =='EDIT'):
            return True
        else:
            return False

    def execute(self, context):

        obj = context.edit_object
        mesh = obj.data
        bm = bmesh.from_edit_mesh(mesh)
        bm.faces.active = None

        total = 0
        selection_total = 0
        tri_total = 0
        quad_total = 0
        ngon_total = 0
        concave_total = 0

        for face in bm.faces:
            total+=1
            face.select_set(False)
            if len(face.verts) == 3:
                if(self.select_tri==True):
                    face.select_set(True)
                    selection_total+=1
                    tri_total+=1                    
            if len(face.verts) == 4:
                print("OK!")
                if(self.select_quad==True):
                    face.select_set(True)
                    selection_total+=1
                    quad_total+=1 
                    print("OK!")
            if len(face.verts) > 4:
                if(self.select_ngon==True):
                    face.select_set(True)
                    selection_total+=1
                    ngon_total+=1 

            for loop in face.loops:
                if not loop.is_convex:
                    if(self.select_concave==True):
                        face.select_set(True)
                        selection_total+=1
                        concave_total+=1
                    break

        output = 'Total: '+str(total)+" | "
        output += 'Selected: '+str(selection_total)+" | "

        self.report({'INFO'}, output)
        return{'FINISHED'}

        if(self.selection_only==True):
            for face in bm.faces:
                if(face.select):
                    faces.append(faces)
        else:
            faces = bm.faces

        bm.faces.active = None
        for face in bm.faces:
            face.select_set(False)


        for face in faces:
            for loop in face.loops:
                if not loop.is_convex:
                    if(self.select_concave==True):
                        face.select_set(True)
                break

        bmesh.update_edit_mesh(mesh)
        return{'FINISHED'}


class ZEKA_OT_MirrorVertexGroupNames(Operator):
    """Mirror vertex groups names (will delete )"""
    bl_idname = "zeka.mirror_vertex_group_names"
    bl_label = "ZEKA: Mirror Vertex Groups"
    bl_description = "Mirror vertex group names"
    bl_options = {'REGISTER','UNDO'}


    suffix_from: bpy.props.StringProperty(name = 'From', default="_l")
    suffix_to: bpy.props.StringProperty(name = 'To', default="_r")

    @classmethod
    def poll(cls, context):
        if(bpy.context.object.type == 'MESH' and context.active_object.mode =='OBJECT'):
            return True
        else:
            return False

    def execute(self, context):

        obj = bpy.context.view_layer.objects.active
        general_utils.mirror_vertex_group_names(obj,suffix=self.suffix_from, mirrored_suffix=self.suffix_to)
        return{'FINISHED'}


classes = [
    ZEKA_OT_MeshAnalysis,
    ZEKA_OT_MirrorVertexGroupNames
]




from bpy.utils import register_class
for cls in classes:
    register_class(cls)