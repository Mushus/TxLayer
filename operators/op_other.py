import bpy, ast
from bpy.types import Operator
from bpy.props import *
from bpy_extras.io_utils import (
    ImportHelper,
    )
from .. import layer_utils

# from ..utils import set_module_path_to_sys
# set_module_path_to_sys()
# import psd_tools


class LAYER_OT_node_viewer(Operator):
    """node_viewer"""

    bl_idname = 'layer_list.node_viewer'
    bl_label = "Node Viewer"
    bl_options = {'REGISTER', 'UNDO'}

    items = [
    ("ShaderNodeEmission","Emission",""),
    ("ShaderNodeBsdfDiffuse","Diffuse",""),
    ]
    shader_type : EnumProperty(default="ShaderNodeEmission",name="Type",items= items)

    @classmethod
    def poll(cls, context):
        obj = bpy.context.active_object
        if obj:
            mat = obj.active_material
            return mat


    def execute(self, context):
        obj = bpy.context.object
        mat = obj.active_material
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links


        # get target node
        tgt_node = get_target_node(mat, nodes)

        # get output node
        out_node = get_output_node(nodes)


        # 接続を元に戻す
        is_fini = restore_link_outout_to_viewer(self, mat, nodes, links, out_node, tgt_node)
        if is_fini:
            return{'FINISHED'}


        # ビューアーに接続
        link_outout_to_viewer(self, nodes, links, out_node, tgt_node)
        return{'FINISHED'}


# get target node
def get_target_node(mat, nodes):
    if mat.layer_active_node_group_name:
        tgt_node = [nd for nd in nodes if  nd.type == "GROUP" and nd.node_tree and nd.node_tree.name == mat.layer_active_node_group_name][0]
    else:
        tgt_node = nodes[mat.layer_list[0].mix]

    return tgt_node

# get output node
def get_output_node(nodes):
    return [nd for nd in nodes if nd.type == "OUTPUT_MATERIAL" and nd.is_active_output][0]

# 接続を元に戻す
def restore_link_outout_to_viewer(self, mat, nodes, links, out_node, tgt_node):
    l_shader = mat.layer_shaders
    if "Viewer" in nodes:
        em_node = nodes["Viewer"]
        if out_node.inputs[0].links[0].from_node == em_node:
            nodes.remove(em_node)
            if l_shader.mix in nodes:
                mix_node = nodes[l_shader.mix]
                links.new(mix_node.outputs[0], out_node.inputs[0])

        return {'FINISHED'}


# ビューアーに接続
def link_outout_to_viewer(self, nodes, links, out_node, tgt_node):
    if "Viewer" in nodes:
        em_node = nodes["Viewer"]
    else:
        em_node = nodes.new(self.shader_type)
        em_node.hide = True
        em_node.location = [out_node.location.x, (out_node.location.y + 40)]
        em_node.label = "Viewer"
        em_node.name = "Viewer"
        em_node.select = False

    links.new(em_node.outputs[0], out_node.inputs[0])
    links.new(tgt_node.outputs[0], em_node.inputs[0])


class LAYER_OT_change_shadernode(Operator):
    """change_shadernode"""

    bl_idname = 'layer_list.change_shadernode'
    bl_label = "Toggle Shader Node Type"
    bl_options = {'REGISTER', 'UNDO'}

    items = [
    ("ShaderNodeBsdfDiffuse","Diffuse",""),
    ("ShaderNodeBsdfPrincipled","Principled BSDF",""),
    ("ShaderNodeEmission","Emission",""),
    ]
    shader_type : EnumProperty(default="ShaderNodeBsdfDiffuse",name="Type",items= items)

    @classmethod
    def poll(cls, context):
        obj = bpy.context.active_object
        if obj:
            mat = obj.active_material
            return mat


    def execute(self, context):
        obj = bpy.context.object
        mat = obj.active_material
        nodes = mat.node_tree.nodes
        l_shader = mat.layer_shaders
        links = mat.node_tree.links

        if l_shader.diffuse in nodes:
            old_node = nodes[l_shader.diffuse]
            # if old_node.type == self.shader_type:
            #     return{'FINISHED'}

            new_shader_node = nodes.new(type=self.shader_type)
            new_shader_node.location = old_node.location
            new_shader_node.name = "LAYER_" + self.shader_type


            # ふくげん
            if l_shader.backup_connect_socket:
                dic = ast.literal_eval(l_shader.backup_connect_socket)
                for lk in dic.keys():
                    if lk in nodes:
                        tgt_nd = nodes[lk]
                        tgt_output_sk = dic[lk][0]
                        tgt_shader_input_sk = dic[lk][1]
                        if tgt_output_sk in tgt_nd.outputs:
                            if tgt_shader_input_sk in new_shader_node.inputs:
                                links.new(tgt_nd.outputs[tgt_output_sk],new_shader_node.inputs[tgt_shader_input_sk])


            # ばっくあっぷ
            if old_node.type == "BSDF_PRINCIPLED":
                backup_connect_socket = {}
                for inp in old_node.inputs:
                    if inp.links:
                        for lk in inp.links:
                            backup_connect_socket[lk.from_node.name] = (lk.from_socket.name,inp.name)

                l_shader.backup_connect_socket = str(backup_connect_socket)


            if old_node.outputs[0].links:
                links.new(old_node.outputs[0].links[0].to_socket,new_shader_node.outputs[0])
            if old_node.inputs[0].links:
                links.new(old_node.inputs[0].links[0].from_socket,new_shader_node.inputs[0])

            l_shader.diffuse = new_shader_node.name
            nodes.remove(old_node)

        return{'FINISHED'}


class LAYER_OT_mat_new(Operator):
    """"""

    bl_idname = 'layer_list.mat_new'
    bl_label = "Add New Empty Material"
    bl_options = {'REGISTER', 'UNDO'}

    remove_principled_bsdf : BoolProperty(name="Remove Principled BSDF",default=True)
    def execute(self, context):
        mat = bpy.data.materials.new(name="Material")
        mat.use_nodes = True
        if self.remove_principled_bsdf:
            mat.node_tree.nodes.remove(mat.node_tree.nodes[0]) # プリンシプルノードを削除

        obj = bpy.context.object
        obj.data.materials.append(mat)
        return{'FINISHED'}


class LAYER_OT_node_change_texture_coord(Operator):
    """"""

    bl_idname = 'layer_list.node_change_texture_coord'
    bl_label = "Change Texture Coord"
    bl_options = {'REGISTER', 'UNDO'}

    index : IntProperty(name="Index",min=0,max=6)

    def execute(self, context):
        sc = bpy.context.scene
        props = sc.texpaint_layers
        obj = bpy.context.object
        mat = obj.active_material
        layer = mat.layer_list[mat.layer_index]
        ntree = layer_utils.get_item_node_tree(layer)
        if layer.texcoord in ntree.nodes:
            ntree.links.new(
            ntree.nodes[layer.texcoord].outputs[self.index],
            ntree.nodes[layer.mapping].inputs[0]
            )


        props.texture_coord_index = self.index

        if self.index == 0:
          text = "Generated"
        elif self.index == 1:
          text = "Normal"
        elif self.index == 2:
          text = "UV"
        elif self.index == 3:
          text = "Object"
        elif self.index == 4:
          text = "Camera"
        elif self.index == 5:
          text = "Window"
        elif self.index == 6:
          text = "Refrection"
        self.report({'INFO'}, "Chanege Texture Coord to [%s]" % text)
        return{'FINISHED'}


class LAYER_OT_layer_setting_resize_2x(Operator):
    """"""

    bl_idname = 'layer_list.layer_setting_resize_2x'
    bl_label = "Resize Layer Default Setting 2x"

    up : BoolProperty(name="Up")

    def execute(self, context):
        old_act = bpy.context.object
        mat = old_act.active_material
        if self.up:
            mat.layer_img_data.width *= 2
            mat.layer_img_data.height *= 2
        else:
            mat.layer_img_data.width = int(mat.layer_img_data.width * 0.5)
            mat.layer_img_data.height = int(mat.layer_img_data.height * 0.5)
        return{'FINISHED'}


class LAYER_OT_layer_add_folder(Operator):
    """layer_add_folder"""

    bl_idname = 'layer_list.layer_add_folder'
    bl_label = "Add Folder"


    def execute(self, context):
        obj = bpy.context.object
        mat = obj.active_material
        act_index = mat.layer_index
        layer_list = mat.layer_list


         # add item
        tgt_name = "Group"
        if tgt_name in layer_list:
            count = [i for i in layer_list if not i.name.find(tgt_name + ".00") == -1]
            tgt_name += ".00" + str(len(count + [1]))

        item = layer_list.add()
        item.name = tgt_name
        item.node_tree = mat.layer_active_node_group_name
        item.layer_type = "FOLDER"


        # get index
        layer_index = mat.layer_index
        mat.layer_index = len(layer_list) - 1


        # sort list
        move_up_count = len(layer_list) - max(layer_index, 0) - 1
        for i in range(move_up_count):
            bpy.ops.layer_list.move_layer(direction='UP')

        return{'FINISHED'}


class LAYER_OT_layer_toggle_solo(Operator):
    bl_idname = "layer_list.layer_toggle_solo"
    bl_label = "Toggle Solo Layer"
    bl_description = "Solo view the active layer. \nRerun to restore the saved opacity value"

    index : IntProperty()

    @classmethod
    def poll(cls, context):
        obj = bpy.context.object
        if obj:
            mat = obj.active_material
            if mat:
                return mat.layer_list


    def execute(self, context):
        obj = bpy.context.object
        mat = obj.active_material
        layer_l = mat.layer_list
        act_item = layer_l[mat.layer_index]

        # 履歴がない場合(ソロビューの開始)
        if not mat.layer_solo_backup_hide_dic:
            # 表示状態をバックアップ
            backup_hide_dic = {}
            for item in layer_l:
                if item.node_tree == act_item.node_tree:
                    ntree = layer_utils.get_item_node_tree(item)
                    if item.multiply in ntree.nodes:
                        backup_hide_dic[item.name] = ntree.nodes[item.multiply].inputs[1].default_value
            mat.layer_solo_backup_hide_dic = str(backup_hide_dic)

            # アクティブ以外を非表示
            act_item = layer_l[self.index]
            # ntree = layer_utils.get_item_node_tree(act_item)
            # if act_item.multiply in ntree.nodes:
            #     ntree.nodes[item.multiply] = 0

            for item in layer_l:
                if item.node_tree == act_item.node_tree:
                    if not item == act_item:
                        ntree = layer_utils.get_item_node_tree(item)
                        if item.multiply in ntree.nodes:
                            ntree.nodes[item.multiply].inputs[1].default_value = 0

                mat.layer_solo_index = self.index


        # 別のレイヤーをソロビューにする場合
        # (インデックスがあって、インデックスが同じでない場合)は、不透明度切り替えのみする
        elif (not mat.layer_solo_index == -1) and (not mat.layer_solo_index == self.index):
            # アクティブ以外を非表示
            act_item = layer_l[self.index]
            # ntree = layer_utils.get_item_node_tree(act_item)
            # if act_item.multiply in ntree.nodes:
            #     ntree.nodes[item.multiply] = 0

            for item in layer_l:
                if item.node_tree == act_item.node_tree:
                    if not item == act_item:
                        ntree = layer_utils.get_item_node_tree(item)
                        if item.multiply in ntree.nodes:
                            ntree.nodes[item.multiply].inputs[1].default_value = 0

            mat.layer_solo_index = self.index


        # 履歴があり、インデックスが同じの場合は復元
        elif mat.layer_solo_backup_hide_dic and mat.layer_solo_index == self.index:
            # 表示状態を復元
            try:
                dic = ast.literal_eval(mat.layer_solo_backup_hide_dic)
            except Exception as e:
                mat.layer_solo_backup_hide_dic = ""
                self.report({'INFO'}, str(e))
                return{'FINISHED'}
            for item in layer_l:
                ntree = layer_utils.get_item_node_tree(item)
                if item.multiply in ntree.nodes:
                    if item.name in dic:
                        ntree.nodes[item.multiply].inputs[1].default_value = dic[item.name]

            mat.layer_solo_backup_hide_dic = ""
            mat.layer_solo_index = -1

        return {'FINISHED'}


# 外部画像をレイヤーとして読み込み
class LAYER_OT_layer_load_external_image(Operator, ImportHelper):
    bl_idname = "layer_list.layer_load_external_image"
    bl_label = "Load External Image"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}

    node_name : StringProperty()
    use_filter : BoolProperty(default=True, options={'HIDDEN'},)
    use_filter_image : BoolProperty(default=True, options={'HIDDEN'},)

    filename_ext = ".png"
    filter_glob : StringProperty( default="*.bmp;*.rgb;*.png;*.jpg;*.jp2;*.tga;*.cin;*.dpx;*.exr;*.hdr;*.ti;", options={'HIDDEN'}, )


    @classmethod
    def poll(cls, context):
        obj = bpy.context.object
        if obj:
            mat = obj.active_material
            if mat:
                return mat.layer_list

    def execute(self, context):
        img = bpy.data.images.load(self.filepath, check_existing=False)
        bpy.ops.layer_list.new_layer('INVOKE_DEFAULT',img_type="LOAD",load_image_name=img.name)

        return{'FINISHED'}


class LAYER_OT_layer_read_psd(Operator):
    bl_idname = "layer_list.layer_read_psd"
    bl_label = "layer_read_psd"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        obj = bpy.context.object
        return obj
        # if obj:
        #     return obj.active_material

    def execute(self, context):
        psd = psd_tools.PSDImage.open(r"C:\Users\sdt\Desktop\layer_test\sample_psd.psd")

        for layer in list(psd.descendants()):
            print("layer_name: ", layer.name)
            print("is_group(): ", layer.is_group())

        if not layer.is_group():
            pil_img = layer.topil()
            pil_img.save(layer.name + ".png")


        return{'FINISHED'}
