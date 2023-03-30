import bpy
from bpy.types import Operator
from bpy.props import *

from .. import layer_utils


class LAYER_OT_dellayer(Operator):
    """Delete selected layer"""

    bl_idname = 'layer_list.delete_layer'
    bl_label = "Remove Layer"
    bl_description = "Delete selected layer\nCtrl : Remove Only list item"
    bl_options = {'REGISTER', 'UNDO'}


    only_list_item_remove : BoolProperty()


    @classmethod
    def poll(cls, context):
        obj = bpy.context.active_object
        if obj:
            mat = obj.active_material
            return mat and mat.layer_list and mat.layer_index >= 0 and mat.layer_index < len(mat.layer_list)


    def invoke(self, context, event):
        if event.ctrl:
            self.only_list_item_remove = True
        else:
            self.only_list_item_remove = False
        return self.execute(context)


    def delete_nodes(self, context):
        props = context.scene.texpaint_layers
        mat = context.object.active_material
        list = mat.layer_list
        index = mat.layer_index
        layer = list[index]
        # is_adjustment_layer = False
        # if layer.layer_type == "ADJUSTMENT":
        #     is_adjustment_layer = True
        ntree = layer_utils.get_item_node_tree(layer)
        nodes = ntree.nodes
        get_input = layer_utils.get_input_node
        get_output = layer_utils.get_output_node

        # Delete links and make references
        try:
            mix_node = nodes[layer.mix]
            higher = get_input(layer)
            lower = get_output(layer)
        except KeyError as e:
            return
        try:
            add_node = nodes[layer.add]
        except KeyError as e:
            add_node = None
        try:
            higher_add = add_node.inputs[0].links[0].from_node
        except IndexError as e:
            higher_add = None

        # Delete nodes
        nodes.remove(mix_node)
        if layer.multiply in nodes:
            nodes.remove(nodes[layer.multiply])
        if layer.mask in nodes:
            nodes.remove(nodes[layer.mask])
        if layer.img_tex in nodes:
            nodes.remove(nodes[layer.img_tex])

        if layer.layer_type == "PROCEDURAL":
            if layer.mapping in nodes:
                nodes.remove(nodes[layer.mapping])
            if layer.texcoord in nodes:
                nodes.remove(nodes[layer.texcoord])

        if add_node is not None:
            nodes.remove(add_node)

        for i, lay in enumerate(list):
            if i > index:
                layer_utils.offset_layer(lay, props.offset)

        if higher is not None:
            col_input = layer_utils.get_input_of_type(lower, 'RGBA')
            if not col_input == None:
            # if col_input or is_adjustment_layer:
                ntree.links.new(higher.outputs[0], lower.inputs[col_input])
        if higher_add is not None:
            add_out = layer_utils.get_alpha_output(context, index)
            if not add_out == None:
                ntree.links.new(higher_add.outputs[0], add_out)


    def execute(self, context):
        mat = context.object.active_material
        layer_list = mat.layer_list
        index = mat.layer_index

        old_link_socket = layer_utils.temp_link_root_top_layer(self)


        if not self.only_list_item_remove:
            self.delete_nodes(context)

        layer_list.remove(index)
        mat.layer_index = min(max(0, index - 1), len(layer_list) - 1)

        if old_link_socket:
            mat.node_tree.links.new(mat.node_tree.nodes[mat.layer_shaders.diffuse].inputs[0],old_link_socket)

        return{'FINISHED'}
