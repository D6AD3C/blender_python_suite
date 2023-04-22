import bpy

def are_two_armas_selected():
    selected_objects = bpy.context.selected_objects
    for obj in selected_objects:
        print(obj)

    b_failed = False
    if(len(selected_objects)!=2):
        print("Exactly 2 objects must be selected")    
        b_failed = True
    else:
        for obj in selected_objects:
            if obj.type != "ARMATURE":
                print("Selected object was not an armature")
                b_failed = True
    if b_failed:
        return   None

def get_posebone_children(posebone):
    arma = posebone.id_data
    arma_posebones = arma.pose.bones
    children = []
    for arma_posebone in arma_posebones:
        if(arma_posebone.parent == posebone):
            children.append(arma_posebone)
    return children
                 

class Doc():

    def __init__(self):
        self.lines:list[str] = []

    def write_l(self,txt):
        self.lines.append(txt)

    def print(self):
        for l in self.lines:
            print(l)

class PoseboneHierarchyComparison():
    def __init__(self,source_posebone,target_posebone):
        self.source_posebone = source_posebone
        self.target_posebone = target_posebone
        self.source_name = source_posebone.name
        self.target_name = target_posebone.name
        self.match = False
        self.complaints = []

    def is_match(self):
        return self.match

    def get_name(self):
        return self.source_name

    def run(self):
        b_failed = False
        pb1 = self.source_posebone
        pb2 = self.target_posebone

        children = get_posebone_children(pb1)
        match_children = get_posebone_children(pb2)
        match_children_names = []
        for match_child in match_children:
            match_children_names.append(match_child.name)
        
        b_all_children_match = True
        for child in children:                    
            if child.name in match_children_names:
                break
            complaints.append("Missing child bone: "+child.name)
            b_all_children_match = False
        if b_all_children_match:
            self.match = True
        else:
            self.match = False

    def report_to_console(self):
        print("\nHierarchy Comparison ----------------- ")
        print("Name: "+self.source_name)
        print("ExactMatch: "+str(self.match))
        print("Complaints: ")
        for c in self.complaints:
            print("     "+c)

class PoseboneDetailsComparison():

    def __init__(self,source_posebone,target_posebone):
        self.source_posebone = source_posebone
        self.target_posebone = target_posebone
        self.source_name = source_posebone.name
        self.target_name = target_posebone.name
        self.match = False
        self.complaints = []
        self.fail_happend = False

    def is_match(self):
        return self.match

    def get_name(self):
        return self.source_name

    def fail_run(self,complaint):
        self.complaints.append(complaint)
        self.fail_happened = True


    def run(self):
        pb1 = self.source_posebone
        pb2 = self.target_posebone

        if pb1.rotation_mode != pb2.rotation_mode:
            self.fail_run("parent should be: "+pb1.parent.name)

        if pb1.rotation_mode != pb2.rotation_mode:
            self.fail_run("rotation mode should be:"+pb1.rotation_mode)
        if pb1.lock_location != pb2.lock_location:
            self.fail_run("lock_location")
        if pb1.lock_rotation != pb2.lock_rotation:
            self.fail_run("lock_rotation")
        if pb1.lock_rotation_w != pb2.lock_rotation_w:
            self.fail_run("lock_rotation_w")
        if pb1.lock_scale!= pb2.lock_scale:
            self.fail_run("lock_scale")

        self.match = not self.fail_happened

    def report_to_console(self):
        print("\nDetailsComparison ----------------- ")
        print("Name: "+self.source_name)
        print("ExactMatch: "+str(self.match))
        print("Complaints: ")
        for c in self.complaints:
            print("     "+c)

class CompareTwoArma():

    def __init__(self,armas:list):
        self.armas = armas
        self.bones_checked:list[str] = []
        self.bones_shared:list[str] = []
        self.bones_unshared:list[str] = []
        self.hierarchy_comparisons:list = []
        self.detail_comparisons:list[PoseboneDetailsComparison] = []
        pass      

    def run_fail(self):
        return False

    def run(self):

        if are_two_armas_selected():
            return self.run_fail()

        bpy.ops.object.mode_set(mode="POSE")
        arma1 = self.armas[0]
        arma2 = self.armas[1]

        for posebone in arma1.pose.bones:
            self.bones_checked.append(posebone.name)
            posebone_match = arma2.pose.bones.get(posebone.name)
            if posebone_match:
                self.bones_shared.append(posebone.name)
                
                hierarchy_comparison = PoseboneHierarchyComparison(posebone,posebone_match)
                hierarchy_comparison.run()
                self.hierarchy_comparisons.append(hierarchy_comparison)

                detail_comparison = PoseboneDetailsComparison(posebone,posebone_match)
                detail_comparison.run()
                self.detail_comparisons.append(detail_comparison)

            else:
                self.bones_unshared.append(posebone.name)


    def report(self):

        log = Doc()
        log.write_l("\n------------------------------------")
        log.write_l("Rig Compare All Report:")
        log.write_l("Source Arma: "+self.armas[0].name)
        log.write_l("Target Arma: "+self.armas[1].name)
        log.write_l("Bone hits: "+str(len(self.bones_shared)))
        log.write_l("Bone misses: "+str(len(self.bones_unshared)))
        #log.write_l("Bone hierarchy hits: "+str(len(self.bones_children_shared)))
        #log.write_l("Bone hierarchy misses: "+str(len(self.bones_children_unshared)))
        #log.write_l("Bone detail hits: "+str(len(self.bones_details_match)))
        #log.write_l("Bone detail misses: "+str(len(self.bones_details_nomatch)))

        report_shared = False
        report_show_empty_categories = False

        if report_shared:
            log.write_l("Shared Bones:")
            for b in self.bones_shared:
                log.write_l(" > "+b)

        def print_category(log,category,txt,b_show_empty):
            if(len(category)>0 or b_show_empty):
                log.write_l(txt+":")
                for bone_name in category:
                    log.write_l(" > "+bone_name)

        print_category(log,self.bones_unshared,"Unshared Bones",report_show_empty_categories)
       
        #for comparison in self.hierarchy_comparisons:
        #    if not comparison.is_match():
        #        comparison.report_to_console()

        for comparison in self.detail_comparisons:
            if not comparison.is_match():
                comparison.report_to_console()         


