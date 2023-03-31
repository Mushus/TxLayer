import os, bpy
from .. import layer_utils
from .._vendor import pytoshop
from PIL import Image
import numpy as np

def get_layer_list(context):
    obj = bpy.context.object
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
            self.report({'ERROR'}, "'%s' is not PSD file." % self.filepath)
            return {"FINISHED"}
            # return {'CANCELLED'}

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

        with open(self.filepath, 'wb') as fd2:
            psd.write(fd2)

        return {"FINISHED"}

# without PIL
def resize_pixels(img, width, height):
    orig_width, orig_height = img.size
    xrange = lambda x: np.linspace(0, 1, x)

    nppixels = np.array(img.pixels[:]) * 255
    nppixels = nppixels.astype(np.uint8)
    
    np_flat_channels = [nppixels[c::img.channels] for c in range(img.channels)]
    np_2d_channels = [np.reshape(c, (orig_height, orig_width)) for c in np_flat_channels]
    
    # nearest neighber?
    np_2d_resuzed_channels = [
        np.array([
            [
                channel2d[int(x * orig_width / width)][int(y * orig_height / height)] for x in range(width)
            ] for y in range(height)
        ], dtype=np.uint8) for channel2d in np_2d_channels
    ]

    return np_2d_resuzed_channels