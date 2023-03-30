import bpy
from bpy.types import Operator
from bpy.props import *

from .. import layer_utils

# 使ってない？
def is_layer_node(node, name):
    return node.name[:len(name)] == name



#  ビューシェーディングをマテリアルにする
def set_view_shading(self):
    for area in bpy.context.workspace.screens[0].areas:
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                if space.shading.type != 'MATERIAL' or 'RENDERED':
                    space.shading.type = 'MATERIAL'


# 対象画像を作成・取得
def add_new_img(self):
    obj = bpy.context.object
    mat = obj.active_material
    layer_list = mat.layer_list
    img_data = mat.layer_img_data

    col = (0, 0, 0, 0)
    if self.img_type == "FILL" and self.is_first_add:
        col = (1, 1, 1, 1)
    elif self.img_type == "FILL":
        col = (0, 0, 0, 1)
    else:
        if not layer_list:
            col = img_data.base_color
            new_col_l = []
            if bpy.context.scene.display_settings.display_device == 'sRGB':
                col_l = list(col)
                for val in col_l:
                    new_col_l += [layer_utils.srgb_to_rgb(val, quantum_max=1.0)]

            else:
                new_col_l = list(col)

            col =  new_col_l


    bpy.ops.paint.add_texture_paint_slot(name='Layer.000', width=img_data.width, height=img_data.height,
                                         color=col, alpha=True, float=img_data.bit_depth)

    mat.node_tree.nodes.remove(mat.node_tree.nodes.active)

    img = mat.texture_paint_images[mat.paint_active_slot]

    return img

#
def get_target_image(self):
    obj = bpy.context.object
    mat = obj.active_material
    layer_list = mat.layer_list
    layer_index = mat.layer_index
    img = None
    if self.img_type == "LOAD":
        img = bpy.data.images[self.load_image_name]

    elif self.img_type == "DUPLICATE":
        if not layer_list[layer_index].texture:
            self.report({'INFO'}, " Layer Texture Name is Blank")
            return{'FINISHED'}

        if not self.old_item.layer_type in {"ADJUSTMENT","PROCEDURAL"}:
            img = bpy.data.images[layer_list[layer_index].texture].copy()

    elif self.img_type in {"FILL","NEW"}:
        img = add_new_img(self)

    return img


# 塗りつぶしレイヤーの色を取得
def get_fill_color(self):
    tool_set = bpy.context.tool_settings
    if tool_set.unified_paint_settings.use_unified_color:
        tgt_col = tool_set.unified_paint_settings.color
    else:
        tgt_col = tool_set.image_paint.brush.color

    new_col_l = []
    if bpy.context.scene.display_settings.display_device == 'sRGB':
        col_l = list(tgt_col)
        for val in col_l:
            new_col_l += [layer_utils.srgb_to_rgb(val, quantum_max=1.0)]

    else:
        new_col_l = list(tgt_col)

    return new_col_l


def get_adjustment_name(self):
    if self.adjustment_type == "ShaderNodeRGBCurve":
        return "RGB Curves"
    elif self.adjustment_type == "ShaderNodeValToRGB":
        return "Color Ramp"
    elif self.adjustment_type == "ShaderNodeHueSaturation":
        return "Hue/Saturation"
    elif self.adjustment_type == "ShaderNodeBrightContrast":
        return "Bright Contrast"
    elif self.adjustment_type == "ShaderNodeGamma":
        return "Gamma"
    elif self.adjustment_type == "ShaderNodeRGBToBW":
        return "RGB To BW"
    elif self.adjustment_type == "ShaderNodeInvert":
        return "Invert"


def get_adjustment_shader_name(tgt_nd):
    if tgt_nd.type == "CURVE_RGB":
        return "ShaderNodeRGBCurve"
    elif tgt_nd.type == "VALTORGB":
        return "ShaderNodeValToRGB"
    elif tgt_nd.type == "HUE_SAT":
        return "ShaderNodeHueSaturation"
    elif tgt_nd.type == "BRIGHTCONTRAST":
        return "ShaderNodeBrightContrast"
    elif tgt_nd.type == "GAMMA":
        return "ShaderNodeGamma"
    elif tgt_nd.type == "RGBTOBW":
        return "ShaderNodeRGBToBW"
    elif tgt_nd.type == "INVERT":
        return "ShaderNodeInvert"


def get_procedural_name(self):
    if self.procedural_type == "ShaderNodeTexNoise":
        return "Noise"
    elif self.procedural_type == "ShaderNodeTexVoronoi":
        return "Voronoi"
    elif self.procedural_type == "ShaderNodeTexWave":
        return "Wave"
    elif self.procedural_type == "ShaderNodeTexMagic":
        return "Magic"
    elif self.procedural_type == "ShaderNodeTexMusgrave":
        return "Musgrave"
    elif self.procedural_type == "ShaderNodeTexBrick":
        return "Brick"
    elif self.procedural_type == "ShaderNodeTexGradient":
        return "Gradient"
    elif self.procedural_type == "ShaderNodeTexChecker":
        return "Checker"
