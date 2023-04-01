import os, bpy
from .._vendor import pytoshop
from .._vendor.pytoshop.layers import LayerRecord, ChannelImageData
import numpy as np
from . import get_layer_list

class LAYER_OT_layer_import_psd(bpy.types.Operator):
    bl_idname = "layer_list.import_psd"
    bl_label = "Import PSD"
    bl_description = "Import PSD(Paint Layer Only)"
    bl_options = {"REGISTER"}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filename: bpy.props.StringProperty()
    directory: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(
        default="*.psd",
        options={'HIDDEN'},
    )

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)

        return {'RUNNING_MODAL'}

    def execute(self, context):
        filepath_folder, filepath_name = os.path.split(self.filepath)
        filepath_nameonly, filepath_ext = os.path.splitext(filepath_name)
        if(filepath_ext != '.psd'):
            self.report({'ERROR'}, "'%s' is not PSD file." % self.filepath)
            return {'CANCELLED'}

        with open(self.filepath, 'rb') as fd:
            psd = pytoshop.read(fd)
            width = psd.width
            height = psd.height

            blender_layers = get_layer_list(context)

            layers = psd.layer_and_mask_info.layer_info
            for i in layers.layer_records:
                overrided_index = -1
                for k, blender_layer in enumerate(blender_layers):
                    if blender_layer.name == i.name:
                        overrided_index = k
                        break

            if overrided_index != -1:
                None
                # del blender_layers[overrided_index]
                # blender_layers.insert(overrided_index, i)
            else:
                img = bpy.data.images.new(name = i.name, width = width, height = height)
                write_image(img, i)
                
        return {"FINISHED"}

def write_image(img: bpy.types.Image, layer_info: LayerRecord) -> None:
    channels = 4
    dw = int(img.size[0])
    dh = int(img.size[1])
    np_channels = [
        layer_info.channels[0].image.ravel().tolist(),
        layer_info.channels[1].image.ravel().tolist(),
        layer_info.channels[2].image.ravel().tolist(),
        layer_info.channels[-1].image.ravel().tolist()
    ]
    st = layer_info.top
    sl = layer_info.left
    sw = layer_info.width
    sh = layer_info.height
    # Direct editing of image.pixels is very slow
    pixels = [0] * len(img.pixels)
    for (i, channel) in enumerate(np_channels):
        for k in range(dw * dh):
            dx = int(k % dw)
            dy = int(k / dw)
            sx = dx - sl
            sy = dy - st
            if sx < 0 or sy < 0 or sx >= sw or sy >= sh:
                pixels[i + channels * k] = 0.0
            else:
                pixels[i + channels * k] = channel[sx + (sh - sy - 1) * sw] / 255.0
    img.pixels = pixels