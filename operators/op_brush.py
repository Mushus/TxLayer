import bpy
from bpy.types import Operator
from bpy.props import *

from .. import layer_utils


#
class LAYER_OT_brush_set_eraser(Operator):
    """"""
    bl_idname = 'layer_list.brush_set_eraser'
    bl_label = "Set Eraser Brush"
    bl_options = {'REGISTER', 'UNDO'}

    switch : BoolProperty(name="Switch",default=True)

    def execute(self, context):
        if "Eraser" in bpy.data.brushes:
            brs = bpy.data.brushes["Eraser"]
        else:
            brs = bpy.data.brushes.new("Eraser",mode="TEXTURE_PAINT")
            brs.blend = 'ERASE_ALPHA'

        if self.switch:
            if bpy.context.scene.tool_settings.image_paint.brush == brs:
                bpy.context.scene.tool_settings.image_paint.brush = bpy.data.brushes["TexDraw"]
            else:
                bpy.context.scene.tool_settings.image_paint.brush = brs
        else:
            bpy.context.scene.tool_settings.image_paint.brush = brs

        return{'FINISHED'}


class LAYER_OT_brush_set_gradient(Operator):
    """"""
    bl_idname = 'layer_list.brush_set_gradient'
    bl_label = "Set Gradient Brush"
    bl_options = {'REGISTER', 'UNDO'}

    switch : BoolProperty(name="Switch",default=True)

    def execute(self, context):
        sc_tool = bpy.context.scene.tool_settings
        if "Gradient" in bpy.data.brushes:
            brs = bpy.data.brushes["Gradient"]
        else:
            brs = bpy.data.brushes.new("Gradient",mode="TEXTURE_PAINT")
            brs.image_tool = "FILL"
            brs.color_type = 'GRADIENT'

        bpy.ops.wm.tool_set_by_id(name="builtin_brush.Fill")
        if self.switch:
            if sc_tool.image_paint.brush == brs:
                sc_tool.image_paint.brush = bpy.data.brushes["Fill"]
            else:
                sc_tool.image_paint.brush = brs
        else:
            sc_tool.image_paint.brush = brs
            # print(len(brs.gradient.elements))
            # brs.gradient.elements[0] = sc_tool.unified_paint_settings.color
            # brs.gradient.elements[1] = (0,0,0,0)

        return{'FINISHED'}
