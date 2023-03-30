import bpy
from bpy.types import Operator
from bpy.props import *

from .. import layer_utils

class LAYER_OT_set_mask(Operator):
    """Masks the active layer in the transparency of the image on another layer"""

    bl_idname = 'layer_list.set_mask'
    bl_label = "Set Clipping Mask"
    bl_options = {'REGISTER', 'UNDO'}

    source_layer_name : StringProperty(name="Source Layer Name")
    # items = [
    # ("1","Alpha",""),
    # ("0","Color",""),
    # ]
    # channel_type : EnumProperty(default="1",name="Channel Type",items= items)
    is_unlink : BoolProperty(name="Unlink")

    @classmethod
    def poll(cls, context):
        obj = bpy.context.active_object
        if obj:
            mat = obj.active_material
            return mat and mat.layer_list and mat.layer_index >= 0 and mat.layer_index < len(mat.layer_list)

    def execute(self, context):
        obj = bpy.context.object
        mat = obj.active_material
        layer_list = mat.layer_list
        tgt_layer = layer_list[mat.layer_index]
        ntree = layer_utils.get_item_node_tree(tgt_layer)



        if self.is_unlink:
            if ntree.nodes[tgt_layer.mask].inputs[1].links:
                ntree.links.remove(
                    ntree.nodes[tgt_layer.mask].inputs[1].links[0]
                 )

        else:
            src_layer = layer_list[self.source_layer_name]
            ntree.links.new(
                ntree.nodes[src_layer.multiply].outputs[0],
                ntree.nodes[tgt_layer.mask].inputs[1]
            )


        # 画面とノードを更新して最新状態にする
        mat.update_tag()
        ntree.update_tag()
        bpy.context.view_layer.update()
        bpy.context.area.tag_redraw()
        return{'FINISHED'}
