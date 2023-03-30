import bpy
from .. import layer_utils


class LAYER_OT_movelayer(bpy.types.Operator):
    """Move the active layer up or down in the list to change the configuration order of the nodes.\nIf the layers to be replaced are not in the same node group, only the list items will be moved"""

    bl_idname = 'layer_list.move_layer'
    bl_label = 'Move Layer'
    bl_options = {'REGISTER', 'UNDO'}

    direction: bpy.props.EnumProperty(items=(('UP', 'Up', ""), ('DOWN', 'Down', ""),))

    @classmethod
    def poll(cls, context):
        obj = bpy.context.active_object
        if obj:
            mat = obj.active_material
            return mat and mat.layer_list


    # 対象ノード群同士の位置を入れ替える
    def swap_loc(self, layer1, layer2):
        ntree = layer_utils.get_item_node_tree(layer1)
        nodes = ntree.nodes
        layer1_pos = nodes[layer1.mix].location.x
        layer2_pos = nodes[layer2.mix].location.x

        if layer1.mix in nodes:
            nodes[layer1.mix].location.x = layer2_pos
        if layer2.mix in nodes:
            nodes[layer2.mix].location.x = layer1_pos
        if layer1.multiply in nodes:
            nodes[layer1.multiply].location.x = layer2_pos
        if layer2.multiply in nodes:
            nodes[layer2.multiply].location.x = layer1_pos
        if layer1.img_tex in nodes:
            nodes[layer1.img_tex].location.x = layer2_pos
        if layer2.img_tex in nodes:
            nodes[layer2.img_tex].location.x = layer1_pos
        if layer1.add in nodes:
            nodes[layer1.add].location.x = layer2_pos
        if layer2.add in nodes:
            nodes[layer2.add].location.x = layer1_pos
        if layer1.mask in nodes:
            nodes[layer1.mask].location.x = layer2_pos
        if layer2.mask in nodes:
            nodes[layer2.mask].location.x = layer1_pos
        if layer1.mapping in nodes:
            nodes[layer1.mapping].location.x = layer2_pos
        if layer2.mapping in nodes:
            nodes[layer2.mapping].location.x = layer1_pos
        if layer1.texcoord in nodes:
            nodes[layer1.texcoord].location.x = layer2_pos
        if layer2.texcoord in nodes:
            nodes[layer2.texcoord].location.x = layer1_pos


    def move_nodes(self, index, neighbor):
        """Move nodes that correspond to layer."""
        mat = bpy.context.object.active_material
        list = mat.layer_list
        ntree = layer_utils.get_item_node_tree(list[index])
        nodes = ntree.nodes

        if neighbor < 0 or neighbor >= len(list):
            return

        higher_index = index
        lower_index = neighbor
        if neighbor > index:
            higher_index = neighbor
            lower_index = index


        # Make references and remove links
        to_higher = list[lower_index]
        to_lower = list[higher_index]
        # 同じノードツリー内での並び替えでなければ、ノードの並び替えせずリスト入れ替えだけする
        if (not to_lower.node_tree == to_higher.node_tree) or (to_lower.layer_type == "FOLDER") or (to_higher.layer_type == "FOLDER"):
            list.move(neighbor, index)
            return

        to_higher_node = nodes[to_higher.mix]
        to_lower_node = nodes[to_lower.mix]


        # 一旦リンクを除去する
        if nodes[to_lower.mix].outputs[0].links:
            for lk in nodes[to_lower.mix].outputs[0].links:
                if lk.from_node.type == "MIX_RGB":
                    ntree.links.remove(lk)
                    break
        if nodes[to_higher.add].outputs[0].links:
            ntree.links.remove(nodes[to_higher.add].outputs[0].links[0])
        if nodes[to_lower.add].outputs[0].links:
            ntree.links.remove(nodes[to_lower.add].outputs[0].links[0])

        higher = layer_utils.get_input_node(to_lower)
        lower = layer_utils.get_output_node(to_higher)
        higher_add = None
        try:
            higher_add = nodes[to_lower.add].inputs[0].links[0].from_node
        except IndexError:
            higher_add = None

        self.swap_loc(to_higher, to_lower)

        # 新しいリンクを作成する
        if higher is not None:
            col_input = layer_utils.get_input_of_type(to_higher_node, 'RGBA')
            ntree.links.new(higher.outputs[0], to_higher_node.inputs[col_input])
        col_input = layer_utils.get_input_of_type(lower, 'RGBA')
        if not col_input:
            col_input = 0
        ntree.links.new(to_lower_node.outputs[0], lower.inputs[col_input])
        ntree.links.new(to_higher_node.outputs[0], to_lower_node.inputs[1])


        self.link_adjustment_node_input(mat, nodes, ntree, list, to_higher, to_lower)

        list.move(neighbor, index)
        self.link_add_nodes(lower_index, higher_index, higher_add)


    def link_adjustment_node_input(self, mat, nodes, ntree, list, to_higher, to_lower):
        # 1つ上のミックスノードと、調整ノードのリンクを作成する
        if to_higher.layer_type == "ADJUSTMENT":
            adj_node = nodes[to_higher.img_tex]

            target_socket = "Color"
            if adj_node.type == "VALTORGB":
                target_socket = "Fac"

            if nodes[to_higher.mix].inputs[1].links:
                bottom_mix_node = nodes[to_higher.mix].inputs[1].links[0].from_node
                new_link = ntree.links.new(bottom_mix_node.outputs[0], adj_node.inputs[target_socket])
                # print("form_node",new_link.from_node)
                # print("self_mix",nodes[to_higher.mix])
                # if not new_link.is_valid: # 循環しているリンクになってしまっているなら除去
                # if new_link.from_node == nodes[to_higher.mix]:
                #     ntree.links.remove(lk)
            else:
                for lk in adj_node.inputs[target_socket].links:
                    if not lk.is_valid:
                        ntree.links.remove(lk)


        if to_lower.layer_type == "ADJUSTMENT":
            adj_node = nodes[to_lower.img_tex]

            target_socket = "Color"
            if adj_node.type == "VALTORGB":
                target_socket = "Fac"

            if nodes[to_lower.mix].inputs[1].links:
                bottom_mix_node = nodes[to_lower.mix].inputs[1].links[0].from_node
                new_link = ntree.links.new(bottom_mix_node.outputs[0], adj_node.inputs[target_socket])
            else:
                for lk in adj_node.inputs[target_socket].links:
                    if not lk.is_valid:
                        ntree.links.remove(lk)



    def link_add_nodes(self, low_index, high_index, higher):
        layer_list = bpy.context.object.active_material.layer_list
        ntree = layer_utils.get_item_node_tree(layer_list[low_index])

        nodes = ntree.nodes
        low_out = layer_utils.get_alpha_output(bpy.context, low_index)
        # print("low_out",low_index,low_out.id_data.name)
        high_out = layer_utils.get_alpha_output(bpy.context, high_index)
        low_index_node = nodes[layer_list[low_index].add]
        high_index_node = nodes[layer_list[high_index].add]

        ntree.links.new(low_index_node.outputs[0], low_out)
        ntree.links.new(high_index_node.outputs[0], high_out)
        if higher is not None:
            ntree.links.new(higher.outputs[0], high_index_node.inputs[0])


    def move_index(self, index):
        """Move index of a layer render que while clamping it."""

        list = bpy.context.object.active_material.layer_list

        list_length = len(list) - 1  # (index starts at 0)
        new_index = index + (-1 if self.direction == 'UP' else 1)

        bpy.context.object.active_material.layer_index = max(0, min(new_index, list_length))


    def execute(self, context):
        mat = bpy.context.object.active_material
        index = mat.layer_index

        old_link_socket = layer_utils.temp_link_root_top_layer(self)


        neighbor = index + (-1 if self.direction == 'UP' else 1)
        self.move_nodes(index, neighbor)

        self.move_index(index)


        if old_link_socket:
            mat.node_tree.links.new(mat.node_tree.nodes[mat.layer_shaders.diffuse].inputs[0],old_link_socket)
        return {'FINISHED'}
