import bpy
from bpy.types import Operator
from bpy.props import *

from .. import layer_utils
from .. import utils


# シェーダーノードをセットアップ
def setup_output(mat, ntree, offset):
    mat_output = None
    for node in ntree.nodes:
        if node.type == 'OUTPUT_MATERIAL':
            mat_output = node
            break
    if not mat_output:
        mat_output = ntree.nodes.new('ShaderNodeOutputMaterial')

    # Make shaders

    diffuse = ntree.nodes.new(utils.preference().default_shader_type)
    diffuse.name = "LAYER_DIFFUSE"
    mat.layer_shaders.diffuse = diffuse.name
    if diffuse.type == "BSDF_PRINCIPLED":
        # diffuse.inputs["Specular"].default_value = 0
        diffuse.inputs["Base Color"].default_value = mat.layer_img_data.base_color
        diffuse.inputs["Metallic"].default_value = mat.layer_img_data.metallic
        diffuse.inputs["Roughness"].default_value = mat.layer_img_data.roughness

    transparent = ntree.nodes.new('ShaderNodeBsdfTransparent')
    transparent.name = "LAYER_TRANSPARENT"
    mat.layer_shaders.transparent = transparent.name

    mix = ntree.nodes.new('ShaderNodeMixShader')
    mix.name = "LAYER_MIX_SHADER"
    mix.inputs[0].default_value = 1
    mat.layer_shaders.mix = mix.name

    # Link shaders
    ntree.links.new(transparent.outputs[0], mix.inputs[1])
    ntree.links.new(diffuse.outputs[0], mix.inputs[2])
    ntree.links.new(mix.outputs[0], mat_output.inputs[0])

    # Position shaders
    mix.location.x = mat_output.location.x - offset
    mix.location.y = mat_output.location.y
    transparent.location.x = mix.location.x - offset
    transparent.location.y = mix.location.y
    diffuse.location.x = transparent.location.x
    diffuse.location.y = transparent.location.y - 75

    # dummy lock image
    # ロック用のダミー画像を作成
    add_dummy_image_node(mat)
    return diffuse, transparent, mix


def add_dummy_image_node(mat):
    img_node = mat.node_tree.nodes.new('ShaderNodeTexImage')
    img_node.name = "LAYER_DUMMY"
    img_node.label = "Dummy Image"
    img_node.hide = True
    img_node.mute = True
    if "LAYER_DUMMY" in bpy.data.images:
        img_node.image = bpy.data.images["LAYER_DUMMY"]
    else:
        img_node.image = bpy.data.images.new("LAYER_DUMMY", 4, 4)

    img_node.location.x = -60
    img_node.location.y = -600


#
def get_current_node(current_node,col_input):
    if current_node.inputs[col_input].is_linked:
        if not current_node.inputs[col_input].links[0].from_node.type == "GROUP_INPUT":
            current_node = current_node.inputs[col_input].links[0].from_node
            col_input = layer_utils.get_input_of_type(current_node, 'RGBA')
            get_current_node(current_node,col_input)

    return current_node, col_input


# レイヤーのノードをセットアップ
def make_nodes(self, context, layer, img):
    props = bpy.context.scene.texpaint_layers
    offset_x = props.offset

    mat = context.object.active_material
    ntree = layer_utils.get_target_node_tree()
    layer_list = mat.layer_list
    img_data = mat.layer_img_data

    if ntree.name == "Shader Nodetree":
        if not mat.layer_shaders.diffuse or not mat.layer_shaders.transparent or not mat.layer_shaders.mix:
            setup_output(mat, ntree, offset_x)
        else:
            if mat.layer_shaders.diffuse in ntree.nodes:
                ntree.nodes[mat.layer_shaders.diffuse]
            else:
                setup_output(mat, ntree, offset_x)

        if len([i for i in layer_list if i.node_tree == ""]) == 1:
            offset_x += 150


        current_node = ntree.nodes[mat.layer_shaders.diffuse]
    else:
        current_node = [i for i in ntree.nodes if i.type == "GROUP_OUTPUT"][0]

    # Find first node in layer ntree that has no connected input
    # current_node, col_input = get_current_node(current_node,0)
    col_input = 0

    try:
        while current_node.inputs[col_input].is_linked and not current_node.inputs[col_input].links[0].from_node.type == "GROUP_INPUT":
            current_node = current_node.inputs[col_input].links[0].from_node
            col_input = layer_utils.get_input_of_type(current_node, 'RGBA')
    except TypeError as e:
        print("Node in chain has no color input. Try deleting extra nodes you've added to the chain.")
        print("Error: " + str(e))


    mix_node = add_node_mix(self, ntree, layer, current_node, col_input, offset_x)
    mult_node = add_node_multiply(self, ntree, layer, current_node, mix_node)
    mask_node = add_node_mask(self, ntree, layer, current_node, mix_node, mult_node)
    if self.img_type in {"ADJUSTMENT"} or (self.img_type == "DUPLICATE" and self.old_item.layer_type == "ADJUSTMENT"):
        adj_node = add_node_adjustment(self, ntree, layer, current_node, img, mix_node, mult_node, mask_node)
    elif self.img_type in {"PROCEDURAL"} or (self.img_type == "DUPLICATE" and self.old_item.layer_type == "PROCEDURAL"):
        adj_node = add_node_procedural(self, ntree, layer, current_node, img, mix_node, mult_node, mask_node)
    else:
        img_node = add_node_img(self, ntree, layer, current_node, img, mix_node, mult_node, mask_node)
    add_node = add_node_add(self, context, ntree, layer, current_node, mix_node, mult_node)


# Adjustment
def add_node_procedural(self, ntree, layer, current_node, img, mix_node, mult_node, mask_node):
    sc = bpy.context.scene
    props = sc.texpaint_layers

    if self.img_type == "DUPLICATE":
        old_node = ntree.nodes[self.old_item.img_tex]
        pros_node = ntree.nodes.new(get_adjustment_shader_name(old_node))
    else:
        pros_node = ntree.nodes.new(self.procedural_type)
    pros_node.name = "LAYER_PROCEDURAL"
    layer.layer_type = "PROCEDURAL"
    layer.img_tex = pros_node.name
    layer.is_procedural_layer = True


    nd_map = ntree.nodes.new("ShaderNodeMapping")
    nd_map.name = "LAYER_MAPPING"
    nd_map.location.x = mult_node.location.x
    nd_map.location.y = mask_node.location.y - 600
    layer.mapping = nd_map.name
    nd_coord = ntree.nodes.new("ShaderNodeTexCoord")
    nd_coord.name = "LAYER_TEXCOORD"
    nd_coord.location.x = mult_node.location.x
    nd_coord.location.y = mask_node.location.y - 950
    layer.texcoord = nd_coord.name


    ntree.links.new(nd_map.outputs[0], pros_node.inputs[0])
    ntree.links.new(nd_coord.outputs[props.texture_coord_index], nd_map.inputs[0])
    ntree.links.new(pros_node.outputs[0], mask_node.inputs[0])

    # ntree.links.new(pros_node.outputs[0], mask_node.inputs[0])

    pros_node.location.x = mult_node.location.x
    pros_node.location.y = mask_node.location.y - 153

    return pros_node


# Adjustment
def add_node_adjustment(self, ntree, layer, current_node, img, mix_node, mult_node, mask_node):
    if self.img_type == "DUPLICATE":
        old_node = ntree.nodes[self.old_item.img_tex]
        adj_node = ntree.nodes.new(get_adjustment_shader_name(old_node))

        # key
        for ky in old_node.keys():
            fac = getattr(old_node, ky)
            setattr(adj_node[ky].default_value, ky, fac)

        # default_value
        for ky in old_node.inputs.keys():
            fac = old_node.inputs[ky].default_value
            adj_node.inputs[ky].default_value = fac

        if adj_node.type == "VALTORGB":
            fac = getattr(old_node.color_ramp, "hue_interpolation")
            setattr(adj_node.color_ramp, "hue_interpolation", fac)
            fac = getattr(old_node.color_ramp, "color_mode")
            setattr(adj_node.color_ramp, "color_mode", fac)

            # 足りない分を作成
            old_num = len(old_node.color_ramp.elements) - 2
            if old_num > 0:
                for i in range(old_num):
                    adj_node.color_ramp.elements.new(position=0)

            # 色・位置を合わせる
            for i,el in enumerate(adj_node.color_ramp.elements):
                el.color = old_node.color_ramp.elements[i].color
                el.position = old_node.color_ramp.elements[i].position


        elif adj_node.type == "CURVE_RGB":
            data_name_l = ["black_level", "clip_max_x", "clip_max_y", "clip_min_x", "clip_min_y", "extend", "tone", "use_clip", "white_level"]
            for nm in data_name_l:
                fac = getattr(old_node.mapping, nm)
                setattr(adj_node.mapping, nm, fac)

            # 足りない分を作成
            for cv_i,cv in enumerate(old_node.mapping.curves):
                old_num = len(cv.points) - 2
                if old_num > 0:
                    for i in range(old_num):
                        adj_node.mapping.curves[cv_i].points.new(position=0,value=0)

            # 色・位置を合わせる
            for cv_i,cv in enumerate(adj_node.mapping.curves):
                for pt_i,el in enumerate(cv.points):
                    el.handle_type = old_node.mapping.curves[cv_i].points[pt_i].handle_type
                    el.location = old_node.mapping.curves[cv_i].points[pt_i].location


            adj_node.mapping.curves.update()
            adj_node.mapping.update()



    else:
        adj_node = ntree.nodes.new(self.adjustment_type)
    adj_node.name = "LAYER_ADJUSTMENT"
    layer.img_tex = adj_node.name
    layer.layer_type = "ADJUSTMENT"
    ntree.links.new(adj_node.outputs[0], mix_node.inputs[2])

    adj_node.location.x = mult_node.location.x
    adj_node.location.y = mask_node.location.y - 153

    return adj_node


# Mix
def add_node_mix(self, ntree, layer, current_node, col_input, offset_x):
    mix_node = ntree.nodes.new('ShaderNodeMixRGB')
    mix_node.blend_type = self.blend_type
    if self.img_type == "DUPLICATE":
        old_mix = ntree.nodes[self.old_item.mix]
        mix_node.blend_type = old_mix.blend_type
        mix_node.inputs[2].default_value = old_mix.inputs[2].default_value
        mix_node.mute = old_mix.mute

    if self.img_type == "FILL" and not layer.id_data.layer_list:
        mix_node.inputs[1].default_value[1] = img_data.base_color
        mix_node.inputs[1].default_value[2] = img_data.base_color

    if self.img_type in {"FILL"}:
        mix_node.inputs[2].default_value = self.fill_color
    elif self.img_type in {"PROCEDURAL"}:
        mix_node.inputs[2].default_value = (0,0,0,1)

    mix_node.name = "LAYER_MIX"
    layer.mix = mix_node.name

    ntree.links.new(mix_node.outputs[0], current_node.inputs[col_input])
    if layer.node_tree:
        group_input_node = [i for i in ntree.nodes if i.type == "GROUP_INPUT"][0]
        ntree.links.new(group_input_node.outputs["Color"],mix_node.inputs[1])


    mix_node.location.x = current_node.location.x - offset_x
    mix_node.location.y = current_node.location.y

    return mix_node


# Multiply
def add_node_multiply(self, ntree, layer, current_node, mix_node):
    mult_node = ntree.nodes.new('ShaderNodeMath')
    mult_node.operation = 'MULTIPLY'
    if self.img_type == "DUPLICATE":
        old_mult= ntree.nodes[self.old_item.multiply]
        mult_node.inputs[1].default_value = old_mult.inputs[1].default_value
    else:
        mult_node.inputs[1].default_value = 1
    mult_node.name = "LAYER_MULT"

    layer.multiply = mult_node.name

    ntree.links.new(mult_node.outputs[0], mix_node.inputs[0])
    mult_node.location.x = mix_node.location.x
    mult_node.location.y = mix_node.location.y - 170

    return mult_node


# Mask
def add_node_mask(self, ntree, layer, current_node, mix_node, mult_node):
    mask_node = ntree.nodes.new('ShaderNodeMath')
    mask_node.operation = 'MULTIPLY'
    mask_node.inputs[1].default_value = 1
    if self.img_type in {"ADJUSTMENT","PROCEDURAL"}:
        mask_node.inputs[0].default_value = 1

    mask_node.name = "LAYER_MASK"
    mask_node.label = "Mask"
    mask_node.hide = True
    if self.img_type == "DUPLICATE":
        old_mask = ntree.nodes[self.old_item.mask]
        if self.old_item.mask and old_mask.inputs[1].links:
            mk_src_mult_name = old_mask.inputs[1].links[0].from_node.name
            for ly in layer.id_data.layer_list:
                if ly.multiply == mk_src_mult_name:
                    ntree.links.new(tree.nodes[ly.multiply].outputs[0], mask_node.inputs[1])
                    break

    layer.mask = mask_node.name
    ntree.links.new(mask_node.outputs[0], mult_node.inputs[0])
    mask_node.location.x = mix_node.location.x
    mask_node.location.y = mult_node.location.y - 150

    return mask_node


# Image Texture
def add_node_img(self, ntree, layer, current_node, img, mix_node, mult_node, mask_node):
    img_node = ntree.nodes.new('ShaderNodeTexImage')
    img_node.name = "LAYER_IMG"
    img_node.image = img
    layer.img_tex = img_node.name

    if self.img_type == "DUPLICATE":
        if ntree.nodes[self.old_item.mix].inputs[2].links:
            ntree.links.new(img_node.outputs[0], mix_node.inputs[2])
            ntree.links.new(img_node.outputs[1], mask_node.inputs[0])
        else:
            ntree.links.new(img_node.outputs[0], mask_node.inputs[0])
    else:
        if self.img_type == "FILL":
            ntree.links.new(img_node.outputs[0], mask_node.inputs[0])
        else:
            ntree.links.new(img_node.outputs[0], mix_node.inputs[2])
            ntree.links.new(img_node.outputs[1], mask_node.inputs[0])

    img_node.location.x = mult_node.location.x
    img_node.location.y = mask_node.location.y - 153


    mat = bpy.context.object.active_material
    img_node.interpolation = mat.layer_img_data.interpolation
    
    if mat.layer_active_node_group_name in bpy.data.node_groups:
        if bpy.data.node_groups[mat.layer_active_node_group_name].layer_is_bump:
            img_node.interpolation = "Cubic"

    return img_node


# Add
def add_node_add(self, context, ntree, layer, current_node, mix_node, mult_node):
    add_node = ntree.nodes.new('ShaderNodeMath')
    add_node.operation = 'ADD'
    add_node.inputs[0].default_value = 0
    add_node.use_clamp = True
    add_node.name = "LAYER_ADD"
    layer.add = add_node.name

    add_output = layer_utils.get_alpha_output(context, len(layer.id_data.layer_list) - 1)
    ntree.links.new(add_node.outputs[0], add_output)
    ntree.links.new(mult_node.outputs[0], add_node.inputs[1])
    add_node.location.x = mix_node.location.x
    add_node.location.y = mix_node.location.y + 155

    if layer.node_tree:
        group_input_node = [i for i in ntree.nodes if i.type == "GROUP_INPUT"][0]
        ntree.links.new(group_input_node.outputs["Alpha"],add_node.inputs[0])
