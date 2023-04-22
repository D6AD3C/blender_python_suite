import bpy


class LayerData():

    layers = []
    index = -1
    
    def __init__(self,layer_index):
        self.layers = [False] * 32
        self.index = layer_index
        self.layers[layer_index] = True

    def get_index(self):
        return self.index
    
    def get_layers(self):
        return self.layers

class BoneGroupData():
    name = "Default"
    color_set = 'CUSTOM'
    active = [1,1,1]
    select = [1,1,1]
    normal = [1,1,1]
    show_colored_constraints = True 

    def get_name(self):
        return self.name
    
    def set_all_rgb(self,rgb):
        self.active = rgb
        self.select = rgb
        self.normal = rgb

    def apply(self,bone_group):
        bone_group.color_set = self.color_set
        bone_group.colors.active = self.active
        bone_group.colors.select = self.select
        bone_group.colors.normal = self.normal
        bone_group.colors.show_colored_constraints = self.show_colored_constraints

     
class CustomShapeGetter():

    def get_custom_shape(self,name):
        return bpy.data.objects["shapelib_"+name]

class Abstract():

    layers = dict()

    def __init__(self):

        self.layers = dict()
        self.bone_groups = dict()
        self.layer_default = LayerData(0)
        self.bone_group_default = BoneGroupData()
        self.custom_shapes = CustomShapeGetter()

    def get_layer(self,name):
        
        if name in self.layers:
            return self.layers[name].get_layers()
        return self.layer_default.get_layers()
    
    def get_bone_group(self,arma,name):        
        if name in self.bone_groups:
            bone_group_style = self.bone_groups[name]
        else:
            bone_group_style = self.bone_group_default

        bone_group = arma.pose.bone_groups.get(bone_group_style.get_name())       
        if bone_group == None:
            arma.pose.bone_groups.new(name=bone_group_style.get_name())
            bone_group = arma.pose.bone_groups.active
            bone_group_style.apply(bone_group)
        return bone_group
        
    def get_custom_shape(self,name):  
        return self.custom_shapes.get_custom_shape(name)

    def solo_layers(self,arma,layer_names):
        indices = []
        for name in layer_names:
            if name in self.layers:
                indices.append(self.layers[name].get_index())

        for run_twice in range(2):
            for i in range(32):
                if i in indices:
                    arma.data.layers[i] = True
                else:
                    arma.data.layers[i] = False


class Default(Abstract):

    def __init__(self):
        super().__init__()
        self.layers['mech'] = LayerData(3)
        self.layers['tweak'] = LayerData(4)
        self.layers['control'] = LayerData(5)
        self.layers['control_ik'] = LayerData(6)
        self.layers['control_fk'] = LayerData(7)

        bone_group_fk = BoneGroupData()
        bone_group_fk.name = "FK"
        bone_group_fk.set_all_rgb([1,1,1])

        bone_group_ik = BoneGroupData()
        bone_group_ik.name = "IK"
        bone_group_ik.set_all_rgb([1,1,.8])

        bone_group_tweak = BoneGroupData()
        bone_group_tweak.name = "Tweak"
        bone_group_tweak.set_all_rgb([.7,.7,.8])

        bone_group_special = BoneGroupData()
        bone_group_special.name = "Special"
        bone_group_special.set_all_rgb([0.9,0.9,1.0])

        bone_group_visualizer = BoneGroupData()
        bone_group_visualizer.name = "Visualizer"
        bone_group_visualizer.set_all_rgb([0.0,1.0,0.0])

        self.bone_groups['fk'] = bone_group_fk
        self.bone_groups['ik'] = bone_group_ik
        self.bone_groups['special'] = bone_group_special
        self.bone_groups['tweak'] = bone_group_tweak
        self.bone_groups['visualizer'] = bone_group_visualizer









DEFAULT_ENVIRONMENT = Default()

def get_default():
    return DEFAULT_ENVIRONMENT

