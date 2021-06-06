bl_info = {
 'name': ' Pre-bake setup',
 'Version': 'v0.1 alpha',
 "blender": (2, 80, 0),
 'Author': 'Sould3mon / soul-d3',
 'Category' : 'All'
}

import bpy

preview_is_set = False
revert_nodes = []

    #execute

class  Pre_bake(bpy.types.Operator):
   
    bl_idname="node.add_pre_bake_nodes"
    bl_label= "Add Bake Nodes"
    bl_options = {"REGISTER","UNDO"}
    
    action : bpy.props.EnumProperty(
        items=[
        ('Add_nodes','add nodes','add nodes'),
        ('Preview','Preview bake','Preview bake'),
        ('Revert','Revert to bake','Revert to bake'),
        ('Del_nodes','delete nodes','delete nodes')
        ]
    
    )
    #nodes_added = False
    #preview_is_set = False
    #revert_nodes = []
    
    
    def execute(self,context):
        
        
          
        #bakeobject = 
        Object = bpy.context.scene.ScriptVariables.Object.name
        myobj = bpy.data.objects[Object]  #script variable

        mymat = myobj.material_slots.items()
        #print(bpy.context.scene.ScriptVariables.TEXTarget)
        
        UVMapMat = bpy.context.scene.ScriptVariables.UVMapMat
        UVMapTarget = bpy.context.scene.ScriptVariables.UVMapTarget
        TEXTarget = bpy.context.scene.ScriptVariables.TEXTarget #placeholder
        Location = [-600,100]
        #Added_nodes =  bpy.context.scene.ScriptVariables.Add_nodes 
        Vars = bpy.context.scene.ScriptVariables
        

        # finds the most left node in the node tree to add nodes
        def findLocation(nodes):
            nodeitems =nodes.items()
            newloc = 1000.0 #default to the right
            for name in nodeitems:
                print( name[0], nodes[name[0]].location[0])
                if newloc > nodes[name[0]].location[0]:
                    newloc = nodes[name[0]].location[0]
            print(newloc)
            Location[0] = newloc - 400
            
            return
        
        def select_node(matname):
            nodes = bpy.data.materials[matname].node_tree.nodes
            nodeitems =nodes.items()
            for i in nodeitems:
                if "Bake Target Image" in i[0]:
                    i[1].select = True
                    nodes.active = i[1]
                else:
                    i[1].select = False
            return
            

        def CreateUVNode(matname,nodename,valuename,loc):
            nodes = bpy.data.materials[matname].node_tree.nodes
            if nodename in nodes:
                print("already exists")
                return
            findLocation(nodes)
            newnode = nodes.new('ShaderNodeUVMap')
            newnode.uv_map = valuename  #script variable
            newnode.location = loc #location
            newnode.name =  nodename
            newnode.label = nodename
            return newnode
            
        def CreateTEXNode(matname,nodename,valuename,loc):
            nodes = bpy.data.materials[matname].node_tree.nodes
            if nodename in nodes:
                print("already exists")
                
                for i in nodes.items():
                    
                    if "Bake Target Image" in i[0]:
                        i[1].select = True
                        nodes.active = i[1]
                        
                        if i[1].image == bpy.data.images[valuename] :
                            print("name is the same")
                        else:
                            print("update name")
                            i[1].image = bpy.data.images[valuename]
                    
                return
            findLocation(nodes)
            newnode = nodes.new("ShaderNodeTexImage")
            
            newnode.location = loc #location
            newnode.name =  nodename
            newnode.label = nodename
            newnode.image = bpy.data.images[valuename] #script variable
            return newnode
        
        def ConnectNewNodes(matname,nodeout,nodein,outputv ='UV',inputv = 'Vector' ):
            if nodeout == None or nodein == None:
                print("no new material node returned")
            else:
                
                tree = bpy.data.materials[matname].node_tree
                tree.links.new(nodeout.outputs[outputv],nodein.inputs[inputv])
            return
        
        
        def ConnectTexNodes(matname,nodeout):
            #find all image textures and connect vector
            
            tree = bpy.data.materials[matname].node_tree
            nodeitems = tree.nodes.items()
            if nodeout == None:
                print("no material node passed")
            else:
                
                for i in nodeitems:
                    if "Image Texture" in i[0]:
                        print(i[0])
                        tree.links.new(nodeout.outputs['UV'],i[1].inputs['Vector'])
            return
        
        def Checkmetal(matname):
            nodes = bpy.data.materials[matname].node_tree.nodes
            for i in nodes.items():
                if "Principled BSDF" in i[0]:
                    if i[1].inputs['Metallic'].default_value > 0.0 :
                        msg= "material has metallic > 0 baking might not get expected result"
                        
                        self.report({'ERROR'}, msg)
                        if bpy.context.scene.ScriptVariables.SkipMetal == True :
                            self.report({'ERROR'}, 'skipped Material ' + matname )
                            return True
                    
            
            
            return False
        #bpy.ops.node.add_node(type="ShaderNodeBsdfDiffuse", use_transform=True)
        def Create_P_Node(matname,nodename,loc):
            nodes = bpy.data.materials[matname].node_tree.nodes
            if nodename in nodes:
                print("already exists")
                return
            #findLocation(nodes)
            newnode = nodes.new('ShaderNodeBsdfDiffuse')
            #newnode.uv_map = valuename  #script variable
            newnode.location = loc #location
            newnode.name =  nodename
            newnode.label = nodename
            #newnode.select = False
            return newnode
                    
  
        def addnodes():
            for matname in mymat:
                if Checkmetal(matname[0]) :
                    pass
                else:
                    
                    Location = [-600,100]
                    uvmatnode = CreateUVNode(matname[0],'UV Map Mat' ,UVMapMat, Location)
                    Location[1] +=  300
                    texnode = CreateTEXNode(matname[0],'Bake Target Image',TEXTarget , Location)
                    uvbakenode = CreateUVNode(matname[0],'UV Map Bake',UVMapTarget , Location)
                    ConnectNewNodes(matname[0],uvbakenode,texnode)
                    
                    if bpy.context.scene.ScriptVariables.ConnectMaterial == True :
                        ConnectTexNodes(matname[0],uvmatnode)
                        
                    select_node(matname[0])
            Vars.Added_nodes = True        
            return
        
        def add_preview():
            global revert_nodes , preview_is_set
            #revert_nodes.append(1)
            if Vars.Added_nodes == False :
                print('nothing to do ')
                return
            
            for matname in mymat:
                if Checkmetal(matname[0]) :
                    pass
                else:
                    nodes = bpy.data.materials[matname[0]].node_tree.nodes
                    
                    if preview_is_set == False:
                        
                        for items in nodes.items():
                            if items[0] == "Material Output":
                                print("output found")
                                revert_nodes.append((bpy.data.materials[matname[0]].node_tree,items[1].inputs['Surface'].links[0].from_socket,items[1]))
                            else:
                                print("not found")
                        
                        #    print("output not found")
                    texnode =bpy.data.materials[matname[0]].node_tree.nodes['Bake Target Image']
                    #outputnode = bpy.data.materials[matname[0]].node_tree.nodes['Material Output']
                    Location = list(texnode.location)
                    Location[0] +=  800
                    
                    previewnode = Create_P_Node(matname[0],'Preview', Location)
                    ConnectNewNodes(matname[0],texnode,previewnode,'Color','Color')
                    pnode = bpy.data.materials[matname[0]].node_tree.nodes['Preview']
                    #ConnectNewNodes(matname[0],previewnode,revert_nodes[-1][-1],'BSDF','Surface')
                    revert_nodes[-1][0].links.new(pnode.outputs['BSDF'],revert_nodes[-1][2].inputs['Surface'])
                    select_node(matname[0])
                    
                  
            print(revert_nodes)
            print(preview_is_set)
            preview_is_set = True    
            return
        
        def revert_con():
            global revert_nodes , preview_is_set
            #tree = bpy.data.materials[matname[0]].node_tree.nodes
            for revert in  revert_nodes:
                #revert[0]
                #tree.links.new(revert[0],nodes['Material Output'].inputs['Surface'])
                revert[0].links.new(revert[1],revert[2].inputs['Surface'])
            preview_is_set = False
            revert_nodes = [] 
            return
        
        
        
        
        #main part of script
        
        if self.action == 'Add_nodes':
            print('adding nodes')
            addnodes()
        elif self.action == 'Preview':
            add_preview()
            print('preview bake')
        elif self.action == 'Revert':
            print('reverting from preview')
            revert_con()
        elif self.action == 'Del_nodes':
            if Vars.Added_nodes == True:
                print('deleting nodes')
    
            
        return {'FINISHED'}


    
class Pre_bake_panel(bpy.types.Panel):
    bl_idname = "panel.Pre-bake"
    bl_label = "Pre-bake"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    def draw(self, context):
        #scene =
        
        #self.layout.prop(bpy.context.scene.ScriptVariables, 'Test')
        #self.layout.prop(bpy.context.scene.ScriptVariables, 'Test2')
        self.layout.prop(bpy.context.scene.ScriptVariables, 'Object')
        self.layout.prop(bpy.context.scene.ScriptVariables, 'UVMapMat')
        self.layout.prop(bpy.context.scene.ScriptVariables, 'UVMapTarget')
        self.layout.prop(bpy.context.scene.ScriptVariables, 'TEXTarget')
        row = self.layout.row()
        row.prop(bpy.context.scene.ScriptVariables, 'ConnectMaterial')
        row.prop(bpy.context.scene.ScriptVariables, 'SkipMetal')
        self.layout.operator("node.add_pre_bake_nodes", icon='NODETREE', text="Add Nodes").action ='Add_nodes'

        row = self.layout.row()
        row.operator("node.add_pre_bake_nodes", icon='MESH_CUBE', text="Preview").action = 'Preview'
        row.operator("node.add_pre_bake_nodes", icon='LOOP_BACK', text="Revert",).action = 'Revert'
        self.layout.operator("node.add_pre_bake_nodes", icon='NODETREE', text="delete Nodes").action ='Del_nodes'   
        
class ScriptVariables(bpy.types.PropertyGroup):
    
    def cbuv(self,context):
        l =[]
        if bpy.context.scene.ScriptVariables.Object == None :
            l = [('None','None','',0)]
            return l
        else:
            myobj = bpy.data.objects[bpy.context.scene.ScriptVariables.Object.name]
            for items in myobj.data.uv_layers.data.uv_layers.items():
                #print(items[0])
                l.append((items[0],items[0],'uvmap name'))
            
        return l
    
    def cbtex(self,context):
        
        l =[]
        if bpy.context.scene.ScriptVariables.Object == None :
            l = [('None','None','',0)]
            return l
        else:
           
            for items in bpy.data.images.items():
                #print(items[0])
                l.append((items[0],items[0],'texture name'))
            
        return l


    Object: bpy.props.PointerProperty(
        name = 'Object',
        description = "select the object to bake",
        type=bpy.types.Object
    )
    UVMapMat  : bpy.props.EnumProperty(
        name ='UVMap Material',
        description = " select UVMap used on material Default UVMap",
        items = cbuv
        )
    UVMapTarget : bpy.props.EnumProperty(
        name ='UVMap Target',
        description = "select UVMap BakeTarget Default UVMap.bake",
        items = cbuv
        )
    '''    
    UVMapMat : bpy.props.StringProperty(
        name = "UVMap Material",
        description=" select UVMap used on material Default UVMap",
        default = "UVMap"
        
    )
    '''
    
    TEXTarget : bpy.props.EnumProperty(
        name = "TextureTarget",
        description=" select texture",
        items = cbtex
        #default = "TextureName"
        )
    ConnectMaterial : bpy.props.BoolProperty(
        name = 'connect uvmap',
        description = "connect material map to ALL image Texture vector nodes",
        default = False
        )
    SkipMetal : bpy.props.BoolProperty(
        name = 'skip metallic',
        description = "check material for metallic, values > 0 might not result in expected baking behavior skip material if checked",
        default = False
        )
    Added_nodes :  bpy.props.BoolProperty(
        name = 'added_nodes',
        description = "",
        default = False
        )

def register():
    bpy.utils.register_class(ScriptVariables)
    bpy.utils.register_class(Pre_bake)
    bpy.utils.register_class(Pre_bake_panel)
    bpy.types.Scene.ScriptVariables = bpy.props.PointerProperty(type=ScriptVariables)
def unregister():
    del bpy.types.Scene.ScriptVariables
    bpy.utils.unregister_class(ScriptVariables)
    bpy.utils.unregister_class(Pre_bake)
    bpy.utils.unregister_class(Pre_bake_panel)


#if __name__ == "__main__" :
#    register()
