import bpy
from bpy.props import *
from bpy.types import PropertyGroup

from .. import layer_utils


def update_multiply_slider(self,context):
    sc = context.scene
    props = sc.texpaint_layers
    obj = bpy.context.object
    if not obj:
        return
    mat = obj.active_material
    if not mat:
        return
    layer_list = mat.layer_list
    if not layer_list:
        return

    tgt_layer = layer_list[mat.layer_index]
    if props.multiply_slider == 0:
        fac = props.multiply_slider
    else:
        fac = (props.multiply_slider/100)

    ntree = layer_utils.get_item_node_tree(tgt_layer)
    if tgt_layer.multiply in ntree.nodes:
        ntree.nodes[tgt_layer.multiply].inputs[1].default_value = fac


class LAYER_PR_ui(PropertyGroup):
    toggle_layer_option : BoolProperty(name="Option")
    toggle_node_group : BoolProperty(name="Show Belong Node Group")
    toggle_node_setting : BoolProperty(name="Node Setting")
    only_active_group : BoolProperty(name="Show Only Active Node Group",default=True)
    display_panel_other_than_texture_paint_mode : BoolProperty(name="Display the panel menu even in modes other than texture paint mode")

class LAYER_PR_texpaint_layers(PropertyGroup):
    offset : FloatProperty(name="Node Position Offset X",default=180)
    multiply_slider : FloatProperty(name="Opacity", default=100,soft_min=0, soft_max=100,update=update_multiply_slider)
    texture_coord_index : IntProperty(name="texture_coord_index",min=0,max=6)
