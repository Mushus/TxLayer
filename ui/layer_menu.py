import bpy
from bpy.props import *
from bpy.types import Menu
from .. import layer_utils


class LAYER_MT_layer_option(Menu):
    bl_label = "Layer Option"

    def draw(self, context):
        layout = self.layout
        layout.operator('merge.visible_layers', icon='NODE_COMPOSITING')

        layout.separator()

        layout.operator('layer_list.layer_load_external_image', icon='IMAGE_DATA')
        layout.operator('layer_list.search_load_image', icon='IMAGE_DATA', text="Import Existing Image")
        op = layout.operator('layer_list.new_layer',text="Duplicate Layer", icon='DUPLICATE')
        op.img_type = "DUPLICATE"
        # layout.operator('layer_list.layer_add_folder', icon='FILE_FOLDER')

        layout.separator()
        layout.operator('layer_list.export_psd', icon='IMAGE_DATA', text="Export PSD")

class LAYER_MT_node_change_texture_coord(Menu):
    bl_label = "Change Texture Coord"

    def draw(self, context):
        layout = self.layout
        layout.operator("layer_list.node_change_texture_coord",text="Generated",icon="MOD_UVPROJECT").index = 0
        layout.operator("layer_list.node_change_texture_coord",text="Normal",icon="MOD_UVPROJECT").index = 1
        layout.operator("layer_list.node_change_texture_coord",text="UV",icon="MOD_UVPROJECT").index = 2
        layout.operator("layer_list.node_change_texture_coord",text="Object",icon="MOD_UVPROJECT").index = 3
        layout.operator("layer_list.node_change_texture_coord",text="Camera",icon="MOD_UVPROJECT").index = 4
        layout.operator("layer_list.node_change_texture_coord",text="Window",icon="MOD_UVPROJECT").index = 5
        layout.operator("layer_list.node_change_texture_coord",text="Refrection",icon="MOD_UVPROJECT").index = 6


class LAYER_MT_other_option(Menu):
    bl_label = "Other"

    def draw(self, context):
        layout = self.layout
        prefs = layer_utils.preference()
        sc = bpy.context.scene

        layout.prop(prefs.ui,"only_active_group",icon="GROUP")
        layout.prop(prefs.ui,"toggle_node_group",icon="NODETREE")
        layout.separator()
        vl_set = sc.view_settings
        layout.prop(vl_set, "view_transform",text="")
        # layout.prop(sc.render,"use_simplify")
        layout.separator()
        # layout.operator("layer_list.layer_toggle_solo",icon="HIDE_OFF")
        layout.operator("layer_list.node_group_create_layer_socket",text="Create layer output socket",icon="NODE")
        # layout.operator("layer_list.node_group_remove_layer_socket",icon="X")
        layout.separator()
        layout.operator("layer_list.img_icon_update",icon="FILE_REFRESH")
        layout.operator("layer_list.img_invert_color",icon="IMAGE_ALPHA")


class LAYER_MT_new_procedural_layer(Menu):
    bl_label = "New Procedural Layer"

    def draw(self, context):
        layout = self.layout
        prefs = layer_utils.preference()
        sc = bpy.context.scene

        layout.operator_context  = "INVOKE_DEFAULT"

        op = layout.operator("layer_list.new_layer",text="Noise",icon="TEXTURE_DATA")
        op.procedural_type = "ShaderNodeTexNoise"
        op.img_type = "PROCEDURAL"
        op = layout.operator("layer_list.new_layer",text="Voronoi",icon="TEXTURE_DATA")
        op.procedural_type = "ShaderNodeTexVoronoi"
        op.img_type = "PROCEDURAL"
        op = layout.operator("layer_list.new_layer",text="Wave",icon="TEXTURE_DATA")
        op.procedural_type = "ShaderNodeTexWave"
        op.img_type = "PROCEDURAL"
        op = layout.operator("layer_list.new_layer",text="Magic",icon="TEXTURE_DATA")
        op.procedural_type = "ShaderNodeTexMagic"
        op.img_type = "PROCEDURAL"
        op = layout.operator("layer_list.new_layer",text="Musgrave",icon="TEXTURE_DATA")
        op.procedural_type = "ShaderNodeTexMusgrave"
        op.img_type = "PROCEDURAL"
        op = layout.operator("layer_list.new_layer",text="Brick",icon="TEXTURE_DATA")
        op.procedural_type = "ShaderNodeTexBrick"
        op.img_type = "PROCEDURAL"
        op = layout.operator("layer_list.new_layer",text="Gradient",icon="TEXTURE_DATA")
        op.procedural_type = "ShaderNodeTexGradient"
        op.img_type = "PROCEDURAL"
        op = layout.operator("layer_list.new_layer",text="Checker",icon="TEXTURE_DATA")
        op.procedural_type = "ShaderNodeTexChecker"
        op.img_type = "PROCEDURAL"


class LAYER_MT_new_adjustment_layer(Menu):
    bl_label = "New Adjustment Layer"

    def draw(self, context):
        layout = self.layout
        prefs = layer_utils.preference()
        sc = bpy.context.scene

        layout.operator_context  = "INVOKE_DEFAULT"

        op = layout.operator("layer_list.new_layer",text="RGB Curves",icon="IPO_EASE_IN_OUT")
        op.adjustment_type = "ShaderNodeRGBCurve"
        op.img_type = "ADJUSTMENT"
        op = layout.operator("layer_list.new_layer",text="Color Ramp",icon="SEQ_SPLITVIEW")
        op.adjustment_type = "ShaderNodeValToRGB"
        op.img_type = "ADJUSTMENT"
        op = layout.operator("layer_list.new_layer",text="Hue/Saturation",icon="MOD_HUE_SATURATION")
        op.adjustment_type = "ShaderNodeHueSaturation"
        op.img_type = "ADJUSTMENT"
        op = layout.operator("layer_list.new_layer",text="Bright Contrast",icon="IMAGE_ALPHA")
        op.adjustment_type = "ShaderNodeBrightContrast"
        op.img_type = "ADJUSTMENT"
        op = layout.operator("layer_list.new_layer",text="Gamma",icon="IMAGE_ALPHA")
        op.adjustment_type = "ShaderNodeGamma"
        op.img_type = "ADJUSTMENT"
        op = layout.operator("layer_list.new_layer",text="RGB To BW",icon="IMAGE_ALPHA")
        op.adjustment_type = "ShaderNodeRGBToBW"
        op.img_type = "ADJUSTMENT"
        op = layout.operator("layer_list.new_layer",text="Invert",icon="IMAGE_ALPHA")
        op.adjustment_type = "ShaderNodeInvert"
        op.img_type = "ADJUSTMENT"


class LAYER_MT_node_group_set_active(Menu):
    bl_label = "Set Active Node Group"

    def draw(self, context):
        layout = self.layout

        obj = bpy.context.object
        mat = obj.active_material
        if not mat:
            return
        layer_list = mat.layer_list

        gp_nd_l = [nd for nd in mat.node_tree.nodes if nd.type == "GROUP" if nd.node_tree]
        gp_nd_l = sorted(set(gp_nd_l), key=lambda x:x.node_tree.name)
        for nd in gp_nd_l:
            op = layout.operator("layer_list.node_group_set_active",text=nd.node_tree.name,icon="NONE",translate=False)
            op.target_node_gp = nd.node_tree.name

        layout.separator()
        op = layout.operator("layer_list.node_group_set_active",text="Root",icon="NONE",translate=False)
        op.target_node_gp = ""


class LAYER_MT_set_mask(Menu):
    bl_label = "Set Clipping Mask"

    def draw(self, context):
        layout = self.layout

        obj = bpy.context.object
        mat = obj.active_material

        if not mat:
            return
        layer_list = mat.layer_list
        if not layer_list:
            return

        tgt_layer = layer_list[mat.layer_index]
        ntree = layer_utils.get_item_node_tree(tgt_layer)


        layout.label(text="Mask [%s]" % layer_list[mat.layer_index].name,icon="NONE")
        layout.separator()

        if ntree.name == "Shader Nodetree":
            nt_name = ""
        else:
            nt_name = ntree.name

        tgt_layer_l = [i for i in layer_list if i.node_tree == nt_name]

        for ly in tgt_layer_l:
            if layer_list[mat.layer_index] == ly:
                continue
            op = layout.operator("layer_list.set_mask",text=ly.name,icon="NONE",translate=False)
            op.source_layer_name = ly.name
            op.is_unlink = False

        layout.separator()
        op = layout.operator("layer_list.set_mask",text="Unlink",icon="X")
        op.source_layer_name = ""
        op.is_unlink = True
