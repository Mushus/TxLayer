import bpy
from bpy.types import Operator
from bpy.props import *

from .new_layer_node import setup_output
from .. import layer_utils


class LAYER_OT_node_group_rename_active_ng(Operator):
    bl_idname = 'layer_list.node_group_rename_active_ng'
    bl_label = "Rename Node Group"
    bl_options = {'REGISTER', 'UNDO'}

    new_name : StringProperty(name="New Name",default="")

    @classmethod
    def poll(cls, context):
        obj = bpy.context.active_object
        if obj:
            mat = obj.active_material
            return mat


    def invoke(self, context, event):
        mat = bpy.context.object.active_material
        act_ngp = mat.layer_active_node_group_name
        self.new_name = act_ngp

        dpi_value = bpy.context.preferences.system.dpi
        return context.window_manager.invoke_props_dialog(self, width=dpi_value*3)

    def execute(self, context):
        mat = bpy.context.object.active_material
        act_ngp = mat.layer_active_node_group_name

        # update layer node tree name
        for ly in mat.layer_list:
            if ly.node_tree == act_ngp:
                ly.node_tree = self.new_name

        # rename node group
        if act_ngp in bpy.data.node_groups:
            bpy.data.node_groups[act_ngp].name = self.new_name

        mat.layer_active_node_group_name = self.new_name
        return{'FINISHED'}


class LAYER_OT_node_group_create(Operator):
    bl_idname = 'layer_list.node_group_create'
    bl_label = "Create Node Group"
    bl_description = "Create a node group and connect it to the socket of the Principle BSDF.\nCreate a BG fill layer/Simple layer in the node group"
    bl_options = {'REGISTER', 'UNDO'}

    name : StringProperty(name="Name",default="")
    items = [
    ("Base Color","Base Color",""),
    ("Metallic","Metallic",""),
    ("Roughness","Roughness",""),
    ("Emission","Emission",""),
    ("Normal","Normal",""),
    ("Alpha","Alpha",""),
    ("No Link","No Link",""),
    ("Other","Other",""),
    ]
    principled_input_socket_type : EnumProperty(default="Base Color",name="Principled Input Socket Type",items= items)
    items = [
    ("Subsurface","Subsurface",""),
    ("Subsurface Color","Subsurface Color",""),
    ("Subsurface IOR","Subsurface IOR",""),
    ("Subsurface Anisotropy","Subsurface Anisotropy",""),
    ("Specular","Specular",""),
    ("Specular Tint","Specular Tint",""),
    ("Anisotropic","Anisotropic",""),
    ("Anisotropic Rotation","Anisotropic Rotation",""),
    ("Sheen","Sheen",""),
    ("Sheen Tint","Sheen Tint",""),
    ("Clearcoat","Clearcoat",""),
    ("Clearcoat Roughness","Clearcoat Roughness",""),
    ("IOR","IOR",""),
    ("Transmission","Transmission",""),
    ("Transmission Roughness","Transmission Roughness",""),
    ("Emission Strength","Emission Strength",""),
    ]
    principled_input_socket_other_type : EnumProperty(default="Subsurface",name="Principled Input Socket Other Type",items= items)

    @classmethod
    def poll(cls, context):
        obj = bpy.context.active_object
        if obj:
            mat = obj.active_material
            return mat


    def invoke(self, context, event):
        dpi_value = bpy.context.preferences.system.dpi

        return context.window_manager.invoke_props_dialog(self, width=dpi_value*3)

    def draw(self, context):
        layout = self.layout
        layout.prop(self,"name")
        row = layout.row(align=True)
        row.active = False
        socket_name, ng_name = self.get_ngp_name()
        row.label(text=ng_name,icon="FORWARD",translate=False)

        if self.principled_input_socket_type == "Alpha":
            layout.label(text="Alpha Blend & Off [Show Backface]",icon="NONE")
        elif self.principled_input_socket_type == "Normal":
            layout.label(text="Create Bump Node & Layer",icon="NONE")
        else:
            layout.label(text="",icon="NONE")

        col = layout.column(align=True)
        col.prop(self,"principled_input_socket_type",expand=True)
        if self.principled_input_socket_type == "Other":
            layout.separator()
            col = layout.column(align=True)
            col.prop(self,"principled_input_socket_other_type",expand=True)

    def execute(self, context):
        props = bpy.context.scene.texpaint_layers
        obj = bpy.context.object
        mat = obj.active_material
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        l_shader = mat.layer_shaders

        # 名前を決定
        socket_name, ng_name = self.get_ngp_name()


        ngp = bpy.data.node_groups.new(name="Node Group",type="ShaderNodeTree")
        ngp.name = ng_name
        inp_nd = ngp.nodes.new(type="NodeGroupInput")
        inp_nd.location.y = 300

        out_nd = ngp.nodes.new(type="NodeGroupOutput")
        inp_col = ngp.inputs.new("NodeSocketColor","Color")
        if self.principled_input_socket_type == "Base Color":
            inp_col.default_value = (1,1,1,1)
        elif self.principled_input_socket_type == "Normal":
            inp_col.default_value = (0.5,0.5,0.5,1)
        inp_fac = ngp.inputs.new("NodeSocketFloatFactor","Alpha")
        inp_col = ngp.outputs.new("NodeSocketColor","Color")
        inp_fac = ngp.outputs.new("NodeSocketFloatFactor","Alpha")

        loc_x = -190 * (1 + len([i for i in nodes if i.type == "GROUP"]))
        gp_node = mat.node_tree.nodes.new(type="ShaderNodeGroup")
        gp_node.node_tree = ngp
        gp_node.name = gp_node.node_tree.name
        gp_node.location = (-40 + loc_x,530)
        mat.node_tree.nodes.active = gp_node

        mat.layer_active_node_group_name = gp_node.node_tree.name
        # bpy.ops.layer_list.new_layer("INVOKE_DEFAULT",img_type="FILL")


        # レイヤーのシェーダーが無いなら追加
        if not l_shader.diffuse or not l_shader.transparent or not l_shader.mix:
            offset_x = props.offset
            diffuse, transparent, mix = setup_output(mat, mat.node_tree, offset_x)
            # gp_l = [i for i in mat.node_tree.nodes if i.type == "GROUP" if i.node_tree == ntree]
            # links.new(gp_node.outputs[0],mat.node_tree.nodes[l_shader.diffuse].inputs[0])
            links.new(gp_node.outputs[1],mat.node_tree.nodes[l_shader.mix].inputs[0])
        else:
            if not l_shader.diffuse in nodes:
                return{'FINISHED'}

            diffuse = nodes[l_shader.diffuse]


        # リンク
        if diffuse.type == "BSDF_PRINCIPLED":

            tgt_inputs = diffuse.inputs[socket_name]

            if socket_name == "Alpha":
                mat.blend_method = 'BLEND'
                mat.show_transparent_back = False
                bpy.ops.layer_list.new_layer("INVOKE_DEFAULT",layer_name="Layer 1",img_type="FILL",fill_color_mode="CUSTOM",fill_color=(1,1,1,1))

            elif socket_name == "Normal":
                gp_node.node_tree.layer_is_bump = True
                bump_node = nodes.new(type="ShaderNodeBump")
                bump_node.location = (-320,-420)
                links.new(bump_node.outputs[0], tgt_inputs)
                tgt_inputs = bump_node.inputs["Height"]
                bpy.ops.layer_list.new_layer("INVOKE_DEFAULT",layer_name="BG",img_type="FILL",fill_color_mode="CUSTOM",fill_color=(0.5,0.5,0.5,1))
                bpy.ops.layer_list.new_layer("INVOKE_DEFAULT",layer_name="Down",img_type="FILL",fill_color_mode="CUSTOM",fill_color=(0,0,0,1))
                bpy.ops.layer_list.new_layer("INVOKE_DEFAULT",layer_name="Up",img_type="FILL",fill_color_mode="CUSTOM",fill_color=(1,1,1,1))
            else:
                bpy.ops.layer_list.new_layer("INVOKE_DEFAULT",layer_name="BG",img_type="FILL",fill_color_mode="CUSTOM",fill_color=(1,1,1,1))
                bpy.ops.layer_list.new_layer("INVOKE_DEFAULT",layer_name="Layer 1",img_type="NEW")

            # if not tgt_inputs.links:
            if not socket_name == "No Link":
                links.new( gp_node.outputs[0], tgt_inputs)

        return{'FINISHED'}


    def get_ngp_name(self):
        if self.principled_input_socket_type == "Other":
            socket_name = self.principled_input_socket_other_type
        else:
            socket_name = self.principled_input_socket_type

        if self.name:
            ng_name = self.name
        else:
            ng_name = socket_name
        if ng_name in bpy.data.node_groups:
            count = [i for i in bpy.data.node_groups if not i.name.find(ng_name + ".00") == -1]
            if len(count):
                ng_name += ".00" + str(len(count))
            else:
                ng_name += ".001"

        return socket_name, ng_name


class LAYER_OT_node_group_set_active(Operator):
    """Set the node group to which the new layer will be added"""

    bl_idname = 'layer_list.node_group_set_active'
    bl_label = "Set Active Node Group"
    bl_options = {'REGISTER', 'UNDO'}

    target_node_gp : StringProperty()

    @classmethod
    def poll(cls, context):
        obj = bpy.context.active_object
        if obj:
            mat = obj.active_material
            return mat

    def execute(self, context):
        obj = bpy.context.object
        mat = obj.active_material
        mat.layer_active_node_group_name = self.target_node_gp
        for nd in mat.node_tree.nodes:
            if nd.type == "GROUP":
                if nd.node_tree and nd.node_tree.name == self.target_node_gp:
                    mat.node_tree.nodes.active = nd
                    break


        # mat.update_tag()
        # mat.node_tree.update_tag()
        # bpy.context.view_layer.update()
        for a in bpy.context.screen.areas:
            a.tag_redraw()

        return{'FINISHED'}


class LAYER_OT_node_group_remove_layer_input_socket(Operator):
    """"""

    bl_idname = 'layer_list.node_group_remove_layer_socket'
    bl_label = "Remove Layer Input Socket in Node Group"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        obj = bpy.context.active_object
        if obj:
            mat = obj.active_material
            if mat and mat.layer_list:
                act_item = mat.layer_list[mat.layer_index]

                return act_item.node_tree

    def execute(self, context):
        obj = bpy.context.object
        mat = obj.active_material
        act_item = mat.layer_list[mat.layer_index]
        ntree = layer_utils.get_item_node_tree(act_item)

        gp_out_node = [i for i in ntree.nodes if i.type == "GROUP_OUTPUT"][0]

        if act_item.name in [inp.name for inp in gp_out_node.inputs]:
            gp_out_node.outputs.remove(gp_out_node.inputs[act_item.name])
            self.report({'INFO'}, "Remove Socket [%s]" % act_item.name)


        return{'FINISHED'}


class LAYER_OT_node_group_create_layer_input_socket(Operator):
    """"""

    bl_idname = 'layer_list.node_group_create_layer_socket'
    bl_label = "Create an active layer output socket in a node group"
    bl_options = {'REGISTER', 'UNDO'}

    target_node_gp : StringProperty()
    # items = [
    # ("img_tex","img_tex",""),
    # ("mix","mix",""),
    # ("multiply","multiply",""),
    # ]
    # target_node_type : EnumProperty(default="",name="Type",items= items)
    @classmethod
    def poll(cls, context):
        obj = bpy.context.active_object
        if obj:
            mat = obj.active_material
            if mat and mat.layer_list:
                act_item = mat.layer_list[mat.layer_index]

                return act_item.node_tree

    def execute(self, context):
        obj = bpy.context.object
        mat = obj.active_material
        act_item = mat.layer_list[mat.layer_index]
        ntree = layer_utils.get_item_node_tree(act_item)
        gp_out_node = [i for i in ntree.nodes if i.type == "GROUP_OUTPUT"][0]

        if act_item.name in [inp.name for inp in gp_out_node.inputs]:
            self.report({'INFO'}, "There is a group input socket with the same name as the layer name")
            return {'CANCELLED'}

        for ngp in bpy.data.node_groups:
            if act_item.node_tree == ngp.name:
                if act_item.img_tex in ntree.nodes:
                    inp_col = ngp.outputs.new("NodeSocketColor",act_item.name)
                    out_sk = gp_out_node.inputs[act_item.name]

                    ngp.links.new(
                        out_sk,
                        ntree.nodes[act_item.img_tex].outputs[0]
                    )
                    self.report({'INFO'}, "Add Socket [%s]" % act_item.name)



        return{'FINISHED'}


class LAYER_OT_node_group_create_select_root_nodes(Operator):
    """"""

    bl_idname = 'layer_list.node_group_create_select_root_nodes'
    bl_label = "Create Node Group from Select Root Nodes"

    target_node_gp : StringProperty()

    @classmethod
    def poll(cls, context):
        obj = bpy.context.active_object
        if obj:
            mat = obj.active_material
            return mat and mat.layer_list

    def execute(self, context):
        obj = bpy.context.object
        mat = obj.active_material
        act_item = mat.layer_list[mat.layer_index]
        ntree = layer_utils.get_item_node_tree(act_item)
        sel_nd_l = [nd for nd in mat.node_tree.nodes if nd.select]
        if not sel_nd_l:
            self.report({'WARNING'}, "No Select Nodes")
            return {'CANCELLED'}
            return{'FINISHED'}

        bpy.ops.node.group_make()

        for item in mat.layer_list:
            if item.node_tree:
                item.node_tree = mat.node_tree.nodes.active.node_tree

        return{'FINISHED'}
