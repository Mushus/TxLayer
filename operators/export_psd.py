import os, bpy
from .. import layer_utils
from .._vendor import pytoshop
import numpy as np

def get_layer_list(context: bpy.types.Context) -> bpy.types.Collection:
    obj = context.object
    mat = obj.active_material
    layer_list = mat.layer_list
    return layer_list

class LAYER_OT_layer_export_psd(bpy.types.Operator):
    bl_idname = "layer_list.export_psd"
    bl_label = "Export PSD"
    bl_description = "Export PSD(Paint Layer Only)"
    bl_options = {"REGISTER"}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filename: bpy.props.StringProperty()
    directory: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(
        default="*.psd",
        options={'HIDDEN'},
    )

    width: bpy.props.IntProperty(
        name="Width",
        description="Horizontal dimension",
        default=1024,
        subtype = "PIXEL",
    )

    height: bpy.props.IntProperty(
        name="Height",
        description="Vertical dimension",
        default=1024,
        subtype = "PIXEL",
    )

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)

        return {'RUNNING_MODAL'}

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        row = col.row()
        col.label(text="Width")
        row.prop(self, "width")
        
        row = col.row()
        col.label(text="Height")
        row.prop(self, "height")

    def execute(self, context):
        filepath_folder, filepath_name = os.path.split(self.filepath)
        filepath_nameonly, filepath_ext = os.path.splitext(filepath_name)
        if(filepath_ext != '.psd'):
            filepath_name += ".psd"
            filepath_nameonly += filepath_ext
            filepath_ext = ".psd"

        w = self.width
        h = self.height
        psd = pytoshop.core.PsdFile(num_channels=1, width=w, height=h, compression=pytoshop.enums.Compression.raw)

        layer_list = get_layer_list(context)
        for i in reversed(layer_list):
            if i.layer_type != "IMAGE":
                continue
                
            ntree = layer_utils.get_item_node_tree(i)
            img = ntree.nodes[i.img_tex].image
            
            channels = resize_pixels(img, w, h)
            mask = np.full((w, h), 255, dtype=np.uint8) if len(channels) < 4 else channels[3]

            layer_mask = pytoshop.layers.ChannelImageData(image=mask, compression=pytoshop.enums.Compression.zip)
            layer_r = pytoshop.layers.ChannelImageData(image=channels[0], compression=pytoshop.enums.Compression.zip)
            layer_g = pytoshop.layers.ChannelImageData(image=channels[1], compression=pytoshop.enums.Compression.zip)
            layer_b = pytoshop.layers.ChannelImageData(image=channels[2], compression=pytoshop.enums.Compression.zip)
            layer = pytoshop.layers.LayerRecord(
                channels={ -1: layer_mask, 0: layer_r, 1: layer_g, 2: layer_b },
                top=0,
                bottom=h,
                left=0,
                right=w,
                name=i.name,
                opacity=255
            )
            psd.layer_and_mask_info.layer_info.layer_records.append(layer)

        with open(self.filepath, 'wb') as fd:
            psd.write(fd)

        return {"FINISHED"}

# without PIL
def resize_pixels(img, width, height):
    _width = int(width)
    _height = int(height)
    orig_width = int(img.size[0])
    orig_height = int(img.size[1])

    if orig_width == _width and orig_height == _height:
        return convert_img(img)

    pixels = img.pixels[:]

    channels = int(img.channels)
    # nearest neighber?
    np_resized_channel = []
    for i in range(img.channels):
        resized_channel = [0] * _width * _height
        for k in range(_width * _height):
            x = int(k % _width)
            y = int(k / _width)
            sx = int(x * orig_width / _width)
            sy = int(y * orig_height / _height)
            resized_channel[x + y * _width] = int(pixels[(sx + (orig_height - sy - 1) * orig_width) * channels] * 255)
        
        np_resized_channel.append(resized_channel)
    
    np_2d_channels = [np.reshape(np.array(c, dtype=np.uint8), (_height, _width)) for c in np_resized_channel]
    return np_2d_channels

def convert_img(img):
    width = int(img.size[0])
    height = int(img.size[1])
    pixels = img.pixels[:]
    channels = int(img.channels)
    np_2d_channels = [
        np.flipud(
            np.array(np.array(pixels[i::channels]) * 255, dtype=np.uint8)
                .reshape((height, width))
        ) for i in range(channels)
    ]
    return np_2d_channels