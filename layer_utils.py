import bpy



def preference():
    preference = bpy.context.preferences.addons[__name__.partition('.')[0]].preferences
    return preference


def get_input_of_type(node, type):
    for index, input in enumerate(node.inputs):
        if input.type == type:
            return index

def get_input_node(layer):
    ntree = get_item_node_tree(layer)
    nodes = ntree.nodes
    layer_input = None
    try:
        if len(nodes[layer.mix].inputs[1].links) >= 2:
            l = nodes[layer.mix].inputs[1].links[1]
        else:
            l = nodes[layer.mix].inputs[1].links[0]
        layer_input = l.from_node
        ntree.links.remove(l)
    except IndexError as e:
        layer_input = None
    return layer_input


def get_output_node(layer):
    layer_output = None
    ntree = get_item_node_tree(layer)
    if ntree.name == "Shader Nodetree":
        nt_name = ""
    else:
        nt_name = ntree.name

    if layer.node_tree == nt_name:
        if layer.mix in ntree.nodes:
            if len(ntree.nodes[layer.mix].outputs[0].links) >= 2:
                l = ntree.nodes[layer.mix].outputs[0].links[1]
            if len(ntree.nodes[layer.mix].outputs[0].links) == 0:
                return None
            else:
                l = ntree.nodes[layer.mix].outputs[0].links[0]
            layer_output = l.to_node
            ntree.links.remove(l)
    # except IndexError as e:
    #     print("Layer has no output. This should not occur unless user changed nodes directly.")
    #     print("Error: " + str(e))
    return layer_output


def offset_layer(layer, offset):
    ntree = get_item_node_tree(layer)
    nodes = ntree.nodes
    nodes[layer.mix].location.x += offset
    nodes[layer.multiply].location.x += offset
    nodes[layer.mask].location.x += offset
    nodes[layer.img_tex].location.x += offset
    try:
        nodes[layer.add].location.x += offset
    except:
        pass


def get_alpha_output(context, index):
    mat = context.object.active_material
    ntree = get_item_node_tree(mat.layer_list[index])
    nodes = ntree.nodes
    if ntree.name == "Shader Nodetree":
        nt_name = ""
    else:
        nt_name = ntree.name

    # indexが指定位置以下であり、対象ノードツリー内にある
    valid_layers = [x
        for i, x in enumerate(mat.layer_list)
        if i < index
        if x.node_tree == nt_name
        ]


    for i, lay in reversed(list(enumerate(valid_layers))):
        if lay.add in nodes:
            return nodes[lay.add].inputs[0]

    # 対象ソケットがなかった場合は、ミックスシェーダーまたはグループ出力に接続する
    if ntree.name == "Shader Nodetree":
        return nodes[mat.layer_shaders.mix].inputs[0]
    else:
        out_node_l = [i for i in ntree.nodes if i.type == "GROUP_OUTPUT"]
        return out_node_l[0].inputs[1]


#
def rgb_to_srgb(value, quantum_max=1.0):
  if value <= 0.0031308:
    return value * 12.92
  value = float(value) / quantum_max
  value = (value ** (1.0 / 2.4)) * 1.055 - 0.055
  return value * quantum_max


# sRGB空間で画像処理するべからず - 豪鬼メモ
# https://mikio.hatenablog.com/entry/2018/09/10/213756
def srgb_to_rgb(value, quantum_max=1.0):
  value = float(value) / quantum_max
  if value <= 0.04045:
    return value / 12.92
  value = ((value + 0.055) / 1.055) ** 2.4
  return value * quantum_max


def get_target_node_tree():
    mat = bpy.context.object.active_material
    tgt_ntree = mat.node_tree
    if mat.layer_active_node_group_name:
        for nd in mat.node_tree.nodes:
            if nd.type == "GROUP":
                if mat.node_tree:
                    if nd.node_tree.name == mat.layer_active_node_group_name:
                        tgt_ntree = nd.node_tree
                        break

    return tgt_ntree


def get_item_node_tree(item):
    mat = bpy.context.object.active_material
    ntree = mat.node_tree
    if item:
        if item.node_tree in bpy.data.node_groups:
            ntree = bpy.data.node_groups[item.node_tree]
    else:
        if mat.layer_list and len(mat.layer_list)-1 <= mat.layer_index:
            item = mat.layer_list[mat.layer_index]
            if item.node_tree in bpy.data.node_groups:
                ntree = bpy.data.node_groups[item.node_tree]

    return ntree


#
def get_using_index(mat,ntree):
    if ntree.name == "Shader Nodetree":
        nt_name = ""
    else:
        nt_name = ntree.name

    if mat.layer_list[mat.layer_index].node_tree == nt_name:
        return mat.layer_index
    else:
        ly_l = [(i,ly) for i,ly in enumerate(mat.layer_list) if ly.node_tree == nt_name]
        return ly_l[0][0]


# ベースカラーにノードグループが接続されていると、ルートで新規レイヤー作成で起こる問題の回避
# 一時的にルートのMixノードとベースカラーを接続する
def temp_link_root_top_layer(self):
    mat = bpy.context.object.active_material
    ntree = mat.node_tree
    nodes = ntree.nodes
    layer_list = mat.layer_list

    old_link_socket = None
    if layer_list and not mat.layer_active_node_group_name and mat.layer_shaders.diffuse:
        if nodes[mat.layer_shaders.diffuse].inputs[0].links:
            old_link = nodes[mat.layer_shaders.diffuse].inputs[0].links[0]
            if not old_link.from_node.type == "MIX_RGB":
                old_link_socket = old_link.from_socket
                ntree.links.remove(old_link)

        for i in layer_list:
            if not i.node_tree:
                ntree.links.new(nodes[mat.layer_shaders.diffuse].inputs[0], nodes[i.mix].outputs[0])
                break

    return old_link_socket
