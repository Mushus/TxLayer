import bpy
from .. import layer_utils
from .. import utils
from .ui_act_item import *


class LAYER_PT_panel_sub(bpy.types.Panel):
    bl_label = "Layers"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Addons'

    @classmethod
    def poll(cls, context):
        prefs = utils.preference()
        if bpy.context.object:
            if prefs.ui.display_panel_other_than_texture_paint_mode:
                if not (prefs.category == "Tool" and bpy.context.mode == "PAINT_TEXTURE"):
                    if bpy.context.object.type == "MESH":
                        return True

    def draw(self, context):
        layout = self.layout
        main_panel_menu(self, layout)


class LAYER_PT_panel(bpy.types.Panel):
    bl_label = "Layers"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'
    bl_context = 'imagepaint'

    @classmethod
    def poll(cls, context):
        return bpy.context.mode == "PAINT_TEXTURE"


    def draw(self, context):
        layout = self.layout
        main_panel_menu(self, layout)


# メインメニュー
def main_panel_menu(self, layout):
    # layout.operator("layer_list.layer_read_psd",icon="NONE")
    # layout.operator("layer_list.node_group_create_select_root_nodes",icon="NONE")
    is_no_layerlist = draw_setup_setting(self, layout)
    # is_no_layerlist = draw_layer_option(self, layout, True)
    if is_no_layerlist:
        return

    draw_layer_list(self, layout)

    draw_active_item_option(self, layout)

    draw_layer_option(self, layout)


# レイヤーのヘッダー
def draw_layer_header(self,layout):
    sc = bpy.context.scene
    props = sc.texpaint_layers
    obj = bpy.context.object
    mat = obj.active_material

    if not mat:
        return

    # Node Group
    row = layout.row()
    row.operator("layer_list.node_group_create",text="",icon="COLLECTION_NEW")
    row.menu("LAYER_MT_node_group_set_active",text="",icon="COLLAPSEMENU")
    rows = row.row(align=True)
    check_ng_in_nodes_bool = (mat.layer_active_node_group_name in ([""] + [i.node_tree.name for i in mat.node_tree.nodes if i.type == "GROUP"]))
    rows.alert = (not check_ng_in_nodes_bool)
    rows.alignment="LEFT"
    rows.operator("layer_list.node_group_rename_active_ng",text=mat.layer_active_node_group_name,icon="NONE",emboss=False,translate=False)

    row_sd = row.row(align=True)
    row_sd.alignment="RIGHT"
    op = row_sd.operator("layer_list.node_viewer",text="",icon="SHADING_SOLID")
    op.shader_type = "ShaderNodeBsdfDiffuse"
    op = row_sd.operator("layer_list.node_viewer",text="",icon="LIGHT_SUN")
    op.shader_type = "ShaderNodeEmission"
    # row_sd.separator()
    # op = row_sd.operator("layer_list.change_shadernode",text="",icon="SHADING_SOLID")
    # op.shader_type = "ShaderNodeBsdfDiffuse"
    # op = row_sd.operator("layer_list.change_shadernode",text="",icon="LIGHT_SUN")
    # op.shader_type = "ShaderNodeEmission"
    # op = row_sd.operator("layer_list.change_shadernode",text="",icon="SHADING_RENDERED")
    # op.shader_type = "ShaderNodeBsdfPrincipled"
    row_sd.separator()
    row_sd.menu("LAYER_MT_other_option",text="",icon="DOWNARROW_HLT")


    if not mat.layer_list:
        layout.label(text="",icon="NONE")
        return


    index = mat.layer_index
    if not (index >= 0 and index < len(mat.layer_list) and mat.layer_list):
        layout.label(text="",icon="NONE")
        return
    layer = mat.layer_list[index]

    row = layout.row()
    # row.prop(layer,"layer_type",text="")
    if layer.layer_type == "FOLDER":
        row.label(text="",icon="NONE")
    else:
        ntree = layer_utils.get_item_node_tree(layer)
        op = row.operator("layer_list.layer_toggle_solo",text="",icon="VIS_SEL_01" if mat.layer_solo_backup_hide_dic else "VIS_SEL_10",emboss=False)
        op.index = index

        if not layer.layer_type in {"ADJUSTMENT","PROCEDURAL"}:
            row.prop(layer, "lock", icon = 'LOCKED' if layer.lock else 'UNLOCKED', text="", emboss=False)

        if layer.mix in ntree.nodes:
            row.prop(ntree.nodes[layer.mix], 'blend_type', text="")
        else:
            row.label(text="",icon="NONE")

        row.prop(props,"multiply_slider",slider=True)
        row.menu("LAYER_MT_set_mask",text="",icon="MOD_OPACITY")

        row.label(text="",icon="BLANK1")


# レイヤーリスト
def draw_layer_list(self, layout):
    sc = bpy.context.scene
    props = sc.texpaint_layers
    obj = bpy.context.object
    if not obj:
        return
    mat = obj.active_material
    if not mat:
        return
    # if not mat.layer_list:
    #     return


    draw_layer_header(self,layout)


    # layer list
    row = layout.row()
    row.template_list('MATERIAL_UL_layerlist', "", mat, 'layer_list', mat, 'layer_index')

    col = row.column(align=True)
    op = col.operator('layer_list.new_layer', icon='ADD', text="")
    op.img_type = "NEW"
    op = col.operator('layer_list.new_layer', icon='IMAGE', text="")
    op.img_type = "FILL"
    # op = col.operator('layer_list.new_layer', icon='TEXTURE_DATA', text="")
    # op.img_type = "PROCEDURAL"
    # op = col.operator('layer_list.search_load_image', icon='IMAGE_DATA', text="")
    # col.separator()
    # op = col.operator('layer_list.new_layer', icon='IPO_EASE_IN_OUT', text="")
    # op.img_type = "ADJUSTMENT"
    col.menu("LAYER_MT_new_procedural_layer",text="",icon="TEXTURE_DATA")
    col.menu("LAYER_MT_new_adjustment_layer",text="",icon="IPO_EASE_IN_OUT")

    # op = col.operator('layer_list.new_layer', icon='DUPLICATE', text="")
    # op.img_type = "DUPLICATE"

    col.operator('layer_list.layer_add_folder', icon='FILE_FOLDER', text="")
    col.separator()
    col.operator('layer_list.delete_layer', icon='REMOVE', text="")
    col.separator()

    col.operator('layer_list.move_layer', icon='TRIA_UP', text="").direction = 'UP'
    col.operator('layer_list.move_layer', icon='TRIA_DOWN', text="").direction = 'DOWN'
    col.separator()

    # col.operator('merge.visible_layers', icon='NODE_COMPOSITING', text="")
    col.menu('LAYER_MT_layer_option', icon='DOWNARROW_HLT', text="")


# オプション
def draw_layer_option(self, layout):
    obj = bpy.context.object
    mat = obj.active_material

    prefs = layer_utils.preference()
    row = layout.row(align=True)
    row.alignment="LEFT"
    row.prop(prefs.ui,"toggle_layer_option",icon="TRIA_DOWN" if prefs.ui.toggle_layer_option else "TRIA_RIGHT", emboss=False)


    if not prefs.ui.toggle_layer_option:
        return


    draw_layer_setting(self, layout, mat)

    draw_mat_setting(self, layout, mat, False)


# セットアップ設定
def draw_setup_setting(self, layout):
    obj = bpy.context.object
    if not obj:
        return True
    mat = obj.active_material

    if not mat:
        row = layout.row()
        row.label(text="Add material to use layers", icon='INFO')
        row = layout.row()
        row.template_ID(obj, "active_material")
        row.operator("layer_list.mat_new",icon="ADD")
        return True

    if not mat.layer_list and not mat.layer_active_node_group_name:
        layout.label(text="Apply and create layer:")
        col = layout.column(align=True)
        col.scale_y = 1.5
        col.operator("layer_list.node_group_create",text="Create Node Groups and Layers",icon="COLLECTION_NEW")
        row = layout.row()
        op = row.operator('layer_list.new_layer', text="New Layer",icon="FILE_NEW")
        op.img_type = "NEW"
        # op = row.operator('layer_list.new_layer', text="",icon="IMAGE_DATA")
        # op.img_type == "LOAD"
        op = row.operator('layer_list.new_layer', text="",icon="IMAGE")
        op.img_type = "FILL"

        box = layout.box()
        col_main = box.column(align=True)
        col_main.label(text="Settings",icon="NONE")
        draw_layer_setting(self, col_main, mat)

        draw_mat_setting(self, col_main, mat, True)
        return True


# レイヤー設定
def draw_layer_setting(self, layout, mat):
    box = layout.box()
    col_main = box.column(align=True)
    col_main.label(text="New Layer Settings",icon="FILE")
    col_main.use_property_split = True
    col_main.use_property_decorate = False
    row = col_main.row(align=True)
    col = row.column(align=True)
    col.prop(mat.layer_img_data, 'width')
    col.prop(mat.layer_img_data, 'height')
    col = row.column(align=True)
    col.operator("layer_list.layer_setting_resize_2x",text="",icon="SORT_DESC",emboss=False).up=True
    col.operator("layer_list.layer_setting_resize_2x",text="",icon="SORT_ASC",emboss=False).up=False
    col_main.separator()
    # col_main.prop(mat.layer_img_data, 'color')
    col_main.separator()
    col_main.prop(mat.layer_img_data, 'bit_depth')
    col_main.prop(mat.layer_img_data, 'interpolation')


# マテリアル設定
def draw_mat_setting(self, layout, mat, is_add_new_mat):
    prefs = layer_utils.preference()
    # material
    if is_add_new_mat:
        box = layout.box()
        col_main = box.column(align=True)
        col_main.use_property_split = True
        col_main.use_property_decorate = False
        col_main.label(text="Material",icon="NONE")
        col_main.prop(mat.layer_img_data, 'base_color')
        col_main.prop(mat.layer_img_data, 'metallic')
        col_main.prop(mat.layer_img_data, 'roughness')
        layout.separator()


    else:
        nodes = mat.node_tree.nodes
        if mat.layer_shaders.diffuse in nodes:
            tgt_shader = nodes[mat.layer_shaders.diffuse]
            if tgt_shader.type == "BSDF_PRINCIPLED":
                box = layout.box()
                col_main = box.column(align=True)
                col_main.use_property_split = True
                col_main.use_property_decorate = False
                col_main.label(text="Material",icon="MATERIAL")

                col = col_main.column(align=True)
                col.alignment="RIGHT"
                tgt_skt = tgt_shader.inputs["Base Color"]
                if tgt_skt.links:
                    row = col.row(align=True)
                    row.active = False
                    row.label(text="Base Color")
                    row.label(text="Linked")
                else:
                    col.prop(tgt_skt, 'default_value',text="Base Color")

                tgt_skt = tgt_shader.inputs["Metallic"]
                if tgt_skt.links:
                    row = col.row(align=True)
                    row.active = False
                    row.label(text="Metallic")
                    row.label(text="Linked")

                else:
                    col.prop(tgt_skt, 'default_value',text="Metallic")

                tgt_skt = tgt_shader.inputs["Roughness"]
                if tgt_skt.links:
                    row = col.row(align=True)
                    row.active = False
                    row.label(text="Metallic")
                    row.label(text="Linked")
                else:
                    col.prop(tgt_skt, 'default_value',text="Roughness")


        if prefs.debug_mode:
            col_main.separator()
            box = layout.box()
            col_main = box.column(align=True)
            col_main.label(text="Shader Node Settings",icon="NONE")
            col = col_main.column(align=True)
            col.prop(mat.layer_shaders,"diffuse")
            col.prop(mat.layer_shaders,"mix")
            col.prop(mat.layer_shaders,"transparent")
