import bpy
from bpy.types import Operator
from bpy.props import *

from .. import layer_utils
from .new_layer_fanc import *
from .new_layer_node import *


class LAYER_OT_newlayer(Operator):
    """Add a new layer to the material"""
    bl_idname = 'layer_list.new_layer'
    bl_label = "Add a New Layer"
    bl_options = {'REGISTER', 'UNDO'}

    layer_name : StringProperty(name="Layer Name")
    blend_type : StringProperty(name="Blend Type",default="MIX")
    items = [
    ("NEW","New",""),
    ("FILL","Fill",""),
    ("LOAD","Load",""),
    ("DUPLICATE","Duplicate",""),
    ("ADJUSTMENT","Adjustment",""),
    ("PROCEDURAL","Procedural",""),
    ]
    img_type : EnumProperty(default="NEW",name="Type",items= items)
    load_image_name : StringProperty(name="Load Image Name")
    old_mode : StringProperty(default="TEXTURE_PAINT")
    fill_color : FloatVectorProperty(name="Fill Color", default=(1,1,1,1), size=4, subtype="COLOR", min=0, max=1)
    items = [
    ("PICKER","Picker",""),
    ("CUSTOM","Custom",""),
    ]
    fill_color_mode : EnumProperty(default="PICKER",name="Fill Color Mode",items= items)

    is_first_add : BoolProperty()

    items = [
    ("ShaderNodeRGBCurve","RGB Curves",""),
    ("ShaderNodeValToRGB","Color Ramp",""),
    ("ShaderNodeHueSaturation","Hue/Saturation",""),
    ("ShaderNodeBrightContrast","Bright Contrast",""),
    ("ShaderNodeGamma","Gamma",""),
    ("ShaderNodeRGBToBW","RGB To BW",""),
    ("ShaderNodeInvert","Invert",""),
    ]
    adjustment_type : EnumProperty(default="ShaderNodeRGBCurve",name="Adjustment Type",items= items)


    items = [
    ("ShaderNodeTexNoise","Noise",""),
    ("ShaderNodeTexVoronoi","Voronoi",""),
    ("ShaderNodeTexWave","Wave",""),
    ("ShaderNodeTexMagic","Magic",""),
    ("ShaderNodeTexMusgrave","Musgrave",""),
    ("ShaderNodeTexBrick","Brick",""),
    ("ShaderNodeTexGradient","Gradient",""),
    ("ShaderNodeTexChecker","Checker",""),
    ]
    procedural_type : EnumProperty(default="ShaderNodeTexNoise",name="Procedural Texture Type",items= items)

    @classmethod
    def poll(cls, context):
        obj = bpy.context.active_object
        if obj:
            mat = obj.active_material
            return mat

    def invoke(self, context,event):
        self.old_item_name = ""
        obj = bpy.context.object
        mat = obj.active_material
        ntree = layer_utils.get_target_node_tree()
        layer_list = mat.layer_list
        layer_index = mat.layer_index


        if event.ctrl and self.img_type == "LOAD":
            ntree.nodes[layer_list[layer_index].img_tex].image = bpy.data.images[self.load_image_name]
            layer_list[layer_index].texture = self.load_image_name

            self.report({'INFO'}, "Change Active Layer Image to [%s]" % self.load_image_name)
            return{'FINISHED'}

        self.is_first_add = False
        if ntree.name == "Shader Nodetree":
            nt_name = ""
        else:
            nt_name = ntree.name
        tgt_layer_l = [i for i in layer_list if i.node_tree == nt_name]
        if len(tgt_layer_l) == 0:
            self.is_first_add = True

        if self.img_type == "DUPLICATE":
            self.old_item = layer_list[layer_index]

        elif self.img_type == "FILL":
            # ブラシの色を取得して、sRGB補正する
            if self.fill_color_mode == "PICKER":
                new_col_l = get_fill_color(self)
                self.fill_color =  new_col_l + [1]

            # dpi_value = bpy.context.preferences.system.dpi
            # return context.window_manager.invoke_props_dialog(self, width=dpi_value*3)

        return self.execute(context)


    def draw(self, context):
        layout = self.layout
        if self.img_type == "LOAD":
            layout.prop(self,"load_image_name")
        if self.img_type == "FILL":
            layout.prop(self,"fill_color")


    def execute(self, context):
        set_view_shading(self)
        bpy.context.scene.tool_settings.image_paint.mode = 'MATERIAL'

        obj = bpy.context.object
        mat = obj.active_material
        ntree = layer_utils.get_target_node_tree()
        nodes = ntree.nodes
        layer_list = mat.layer_list
        layer_index = mat.layer_index
        img_data = mat.layer_img_data

        if not mat.use_nodes:
            mat.use_nodes = True


        # ベースカラーにノードグループが接続されていると、ルートで新規レイヤー作成で起こる問題の回避
        # 一時的にルートのMixノードとベースカラーを接続する
        old_link_socket = layer_utils.temp_link_root_top_layer(self)



        # get new image
        img = get_target_image(self)


        # add new item
        new_layer = layer_list.add()
        if not ntree.name == "Shader Nodetree":
            new_layer.node_tree = ntree.name

        # make node
        make_nodes(self, context, new_layer, img)


        if self.img_type == "LOAD":
            new_layer.name = img.name
        elif self.img_type == "DUPLICATE":
            new_layer.name = self.old_item.name
        elif self.img_type in {"FILL","NEW"}:
            new_layer.name = "Layer " + str(len(layer_list) - 1)
            img.name = new_layer.name
        elif self.img_type in {"ADJUSTMENT"}:
            ly_name = get_adjustment_name(self)
            ly_l = [i for i in layer_list if not i.name.find(ly_name + " ") == -1]
            ly_name += " " + str(len(ly_l))
            new_layer.name  = ly_name
        elif self.img_type in {"PROCEDURAL"}:
            ly_name = get_procedural_name(self)
            ly_l = [i for i in layer_list if not i.name.find(ly_name + " ") == -1]
            ly_name += " " + str(len(ly_l))
            new_layer.name =  ly_name

        if self.layer_name:
            new_layer.name =  self.layer_name


        new_layer.texture = new_layer.name


        # get index
        layer_index = mat.layer_index
        mat.layer_index = len(layer_list) - 1

        # sort list
        move_up_count = len(layer_list) - max(layer_index, 0) - 1
        for i in range(move_up_count):
            bpy.ops.layer_list.move_layer(direction='UP')


        if old_link_socket:
            ntree.links.new(nodes[mat.layer_shaders.diffuse].inputs[0],old_link_socket)

        return {'FINISHED'}
