import bpy
import numpy
from bpy.types import Operator
from bpy.props import *

from .. import layer_utils

#
class LAYER_OT_img_icon_update(Operator):
    """img_icon_update"""

    bl_idname = 'layer_list.img_icon_update'
    bl_label = "Update Image Icon"


    def execute(self, context):
        # image icon update
        obj = bpy.context.object
        mat = obj.active_material

        # for i in bpy.data.images:
        for img in mat.texture_paint_images:
            if img.preview:
                img.preview.reload()

        self.report({'INFO'}, "Update Image Icon")
        return{'FINISHED'}


class LAYER_img_invert_color(Operator):
    bl_idname = "layer_list.img_invert_color"
    bl_label = "Invert Color"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}

    # @classmethod
    # def poll(cls, context):
    #     if 'edit_image' in dir(context):
    #         if context.edit_image:
    #             if len(context.edit_image.pixels):
    #                 return True
                # return False

    def execute(self, context):
        # if bpy.context.area.type == "VIEW_3D" and bpy.context.mode == "PAINT_TEXTURE":
        if bpy.context.area.type == "IMAGE_EDITOR":
            img = context.edit_image
        else:
            obj = bpy.context.object
            mat = obj.active_material
            img = mat.texture_paint_images[mat.paint_active_slot]
            # self.report({'INFO'}, "Cannot Run Now Editor and Mode")
            # return{'FINISHED'}

        img_width, img_height, img_channel = img.size[0], img.size[1], img.channels
        pixels = numpy.array(img.pixels).reshape(img_height * img_width, img_channel)
        pixels[:,0] = 1 - pixels[:,0]
        pixels[:,1] = 1 - pixels[:,1]
        pixels[:,2] = 1 - pixels[:,2]
        img.pixels = pixels.flatten()
        img.gl_free()



        # update
        if img:
            img.preview.reload()
        for area in context.screen.areas:
            area.tag_redraw()

        if bpy.context.area.type == "VIEW_3D" and bpy.context.mode == "PAINT_TEXTURE":
            mat.node_tree.update_tag()
        return {'FINISHED'}


class LAYER_Decolorization(Operator):
    bl_idname = "layer_list.decolorization"
    bl_label = "Decolorize"
    bl_description = "This decolor active image"
    bl_options = {'REGISTER', 'UNDO'}

    # @classmethod
    # def poll(cls, context):
    #     if 'edit_image' in dir(context):
    #         if context.edit_image:
    #             if len(context.edit_image.pixels):
    #                 return True
    #             return False

    def execute(self, context):
        img = context.edit_image
        img_width, img_height, img_channel = img.size[0], img.size[1], img.channels
        pixels = numpy.array(img.pixels).reshape(img_height * img_width, img_channel)
        # values = (pixels[:,0] + pixels[:,1] + pixels[:,2]) / 3
        # pixels[:,0] = values.copy()
        pixels[:,0] = 1 - pixels[:,0]
        pixels[:,1] = 1 - pixels[:,1]
        pixels[:,2] = 1 - pixels[:,2]
        # pixels[:,1] = values.copy()
        # pixels[:,2] = values.copy()
        img.pixels = pixels.flatten()
        img.gl_free()
        for area in context.screen.areas:
            area.tag_redraw()
        return {'FINISHED'}
