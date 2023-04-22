import bpy
import bmesh



obj = bpy.context.view_layer.objects.active

shapekeys = obj.data.shape_keys.key_blocks



bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(obj.data)
total=0

for v in bm.verts:
    #MatrixWorld = obj.matrix_world
    #VertexLocalCoords = v.co
    #result = MatrixWorld @ VertexLocalCoords
    #print(result.x)
    
    if(abs(v.co.x)<.0000000000000000000001):
        v.co.x = 0.0;
        total+=1

bmesh.update_edit_mesh(obj.data)
    
print("Total Zero Verts: "+str(total))  

for v in bm.verts:
    
    if(v.co.x<0):
        #print("THIS ONE ON THE OTHER SIDE!")
        v.select = True;

bmesh.update_edit_mesh(obj.data)
    
    
mirrored_shapekeys = []
   
for shapekey in shapekeys:
    shapekey.value = 0
    # rename / translate shape key names by changing shapekey.name
    print(shapekey.name[-2:])
    if(shapekey.name[-2:]=='_l'):
        mirrored_shapekeys.append(shapekey)    
    
    

for shapekey in mirrored_shapekeys:
    bpy.context.object.active_shape_key_index = obj.data.shape_keys.key_blocks.find(shapekey.name)
    shapekey.value = 1
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.blend_from_shape(shape='Basis', blend=1.0, add=False)
    print("OK")
    RightSideName = shapekey.name[:-2]+'_r'
    obj.shape_key_add(name=RightSideName,from_mix=True)
    shapekey.value = 0
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.object.active_shape_key_index = obj.data.shape_keys.key_blocks.find(RightSideName)
    bpy.ops.object.shape_key_mirror(use_topology=True)
    
    
bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.mode_set(mode='EDIT')