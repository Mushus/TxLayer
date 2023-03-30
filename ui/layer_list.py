import bpy
from bpy.props import *
from .. import layer_utils
from .. import utils


class MATERIAL_UL_layerlist(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        sc = bpy.context.scene
        props = sc.texpaint_layers
        mat = bpy.context.object.active_material
        layer = mat.layer_list[index]
        ntree = layer_utils.get_item_node_tree(item)
        prefs = layer_utils.preference()


        # if self.layout_type in {'DEFAULT', 'COMPACT'}:
        if self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label("")
            return


        # index
        # row = layout.row(align=True)
        # row.scale_x = 0.3
        # row.label(text=str(index).zfill(2),icon="NONE")
        # layout.prop(item,"layer_type",text="")

        # フォルダー
        if item.layer_type == "FOLDER":
            # col = layout.column(align=True)
            # col.separator()
            row_main = layout.row(align=True)
            rows = row_main.row(align=True)
            rows.ui_units_x = 0.4
            rows.label(text="",icon="BLANK1")
            rows.label(text="",icon="BLANK1")


            # palette_color
            rows = row_main.row(align=True)
            rows.ui_units_x = 0.3
            if list(item.palette_color) == [0,0,0]:
                rows.label(text="",icon="NONE")
            else:
                rows.prop(item, "palette_color",text="")

            # hide
            row_main.prop(item, "hide", icon = 'HIDE_ON' if item.hide else 'HIDE_OFF', text="", emboss=False)

            row_main.separator()

            row_main.prop(item,"folder_fold",text="",icon="TRIA_RIGHT" if item.folder_fold else "TRIA_DOWN", emboss=False)
            row_main.label(text="",icon="FILE_FOLDER")
            row_main.prop(item,"name",text="",icon="NONE",emboss=False)


            return



        sp = layout.split(align=True,factor=0.7)
        row = sp.row(align=True)

        # solo
        rows = row.row(align=True)
        rows.ui_units_x = 0.4
        if mat.layer_solo_index == index:
            icon_val = "DOT"
        elif mat.layer_index == index:
            icon_val = "LAYER_USED"
        else:
            icon_val = "NONE"
        op = rows.operator("layer_list.layer_toggle_solo",text="",icon=icon_val,emboss=False)
        op.index = index

        # palette_color
        rows = row.row(align=True)
        rows.ui_units_x = 0.3
        if list(item.palette_color) == [0,0,0]:
            rows.label(text="",icon="NONE")
        else:
            rows.prop(item, "palette_color",text="")


        # lock
        if not item.layer_type in {"ADJUSTMENT","PROCEDURAL"}:
            if item.lock:
                row.prop(item, "lock", icon = 'LOCKED', text="", emboss=False)
            else:
                row.label(text="",icon="BLANK1")
            # row.prop(item, "lock", icon = 'LOCKED' if item.lock else 'UNLOCKED', text="", emboss=False)
        else:
            row.label(text="",icon="BLANK1")

        # hide
        row.prop(item, "hide", icon = 'HIDE_ON' if item.hide else 'HIDE_OFF', text="", emboss=False)


        rows.separator()

        use_folder = None
        use_folder = [i for i,ly in enumerate(mat.layer_list) if ly.layer_type == "FOLDER"]
        if use_folder:
            if index > use_folder[0]:
                row.label(text="",icon="BLANK1")

        # fill
        if (layer.mix in ntree.nodes) and not ntree.nodes[layer.mix].inputs[2].links:
            row.separator()
            rows = row.row(align=True)
            rows.ui_units_x = 1
            rows.prop(ntree.nodes[layer.mix].inputs[2],"default_value",text="")
        else:
            rows = row.row(align=True)
            rows.ui_units_x = 1.3
            rows.label(text="",icon="BLANK1")


        if layer.layer_type == "ADJUSTMENT" and (layer.img_tex in ntree.nodes):
            tgt_node = ntree.nodes[layer.img_tex]
            icon_val = "IMAGE_ALPHA"
            if tgt_node.type == "CURVE_RGB":
                icon_val = "IPO_EASE_IN_OUT"
            elif tgt_node.type == "VALTORGB":
                icon_val = "SEQ_SPLITVIEW"
            elif tgt_node.type == "HUE_SAT":
                icon_val = "MOD_HUE_SATURATION"

            row_ic = row.row(align=True)
            row_ic.active=True
            row_ic.label(text="",icon=icon_val)
            rows = row.row(align=True)
            rows.active = bool(not item.hide)
            rows.prop(item,"name",text="",emboss=False)
        elif layer.layer_type == "PROCEDURAL" and (layer.img_tex in ntree.nodes):
            tgt_node = ntree.nodes[layer.img_tex]
            row_ic = row.row(align=True)
            row_ic.active=True
            row_ic.label(text="",icon="TEXTURE_DATA")
            rows = row.row(align=True)
            rows.active = bool(not item.hide)
            rows.prop(item,"name",text="",emboss=False)

        elif layer.layer_type in {"IMAGE","FILL"} and (layer.img_tex in ntree.nodes) and ntree.nodes[layer.img_tex].image:
            icon_val = layout.icon(ntree.nodes[layer.img_tex].image)
            row_ic = row.row(align=True)
            row_ic.active=True
            row_ic.label(text="",icon_value=icon_val)
            rows = row.row(align=True)
            rows.active = bool(not item.hide)
            rows.prop(item,"name",text="",emboss=False)

        else:
            rows = row.row(align=True)
            rows.active = bool(not item.hide)
            rows.prop(item,"name",text="",icon="ERROR",emboss=False)


        if prefs.ui.toggle_node_group:
            row.prop_search(item,"node_tree",bpy.data,"node_groups",text="",icon="NODETREE")



        # row.prop(item,"add",text="")
        # row.prop(item,"mix",text="")
        # row.prop(item,"multiply",text="")
        # row.prop(item,"mask",text="")
        # row.prop(item,"img_tex",text="")
        # row.prop(item,"texture",text="")


        # mask
        if (layer.mask in ntree.nodes) and ntree.nodes[layer.mask].inputs[1].links:
            rows = row.row(align=True)
            rows.ui_units_x = 0.3
            rows.prop(prefs,"clipping_mask_color")

            rows = row.row(align=True)
            rows.active = False
            mk_src_mult_name = ntree.nodes[layer.mask].inputs[1].links[0].from_node.name
            for ly in mat.layer_list:
                if ly.multiply == mk_src_mult_name:
                    rows.label(text=ly.name,icon="NONE")
                    break



        row = sp.row(align=True)
        row.active = bool(not item.hide)

        rows = row.row(align=True)
        rows.alignment="RIGHT"
        rows.active = False

        if (layer.multiply in ntree.nodes) and not ntree.nodes[layer.multiply].inputs[2].links:
            rowx = rows.row(align=True)
            rowx.alignment="LEFT"
            mult_value = ntree.nodes[layer.multiply].inputs[1].default_value
            opa_text = '{:.2f}'.format(round(mult_value,2))
            rowx.label(text=opa_text)


        if (layer.mix in ntree.nodes):
            rowx = rows.row(align=True)
            rowx.alignment="RIGHT"
            rowx.ui_units_x = 3

            cls = bpy.types.ShaderNodeMixRGB
            enum_rna = cls.bl_rna.properties['blend_type'].enum_items
            for i in enum_rna:
                try:
                    if i.identifier == ntree.nodes[layer.mix].blend_type:
                        rowx.label(text=i.name,icon="NONE")
                        break
                except AttributeError: pass


    def draw_filter(self, context, layout):
        prefs = layer_utils.preference()
        col = layout.column(align=True)

        row = col.row(align=True)
        row.prop(self, 'filter_name', text='', icon='VIEWZOOM')
        row.prop(self, 'use_filter_invert', text='', icon='ZOOM_IN')
        row.separator()
        row.prop(self, 'use_filter_sort_alpha', text='', icon='SORTALPHA')
        row.prop(self, 'use_filter_sort_reverse', text='', icon='SORT_DESC' if self.use_filter_sort_reverse else "SORT_ASC")
        row.separator()
        row.prop(prefs.ui, 'only_active_group', text='', icon='GROUP')


    def filter_items(self, context, data, propname):
        prefs = layer_utils.preference()
        filtered = []
        ordered = []
        items = getattr(data, propname)
        helper_funcs = bpy.types.UI_UL_list

        filtered = [self.bitflag_filter_item] * len(items)

        if self.filter_name:
            filtered = helper_funcs.filter_items_by_name(
            self.filter_name,
            self.bitflag_filter_item,
            items,
            "name",
            reverse=self.use_filter_sort_reverse)

        if self.use_filter_sort_alpha:
            ordered = helper_funcs.sort_items_by_name(items, "name")


        # アクティブノードツリーにないレイヤーを除去
        if prefs.ui.only_active_group:
            ntree = layer_utils.get_target_node_tree()
            for i, item in enumerate(items):
                if ntree.name == "Shader Nodetree":
                    if item.node_tree:
                        filtered[i] &= ~self.bitflag_filter_item
                else:
                    if not item.node_tree == ntree.name:
                            filtered[i] &= ~self.bitflag_filter_item


        # フォルダーの折りたたみ機能
        # フォルダーの位置インデックス < 消したいインデックス < 上にある別のフォルダーのインデックスで判定する
        use_folder = None
        use_folder = [i for i,ly in enumerate(items) if ly.layer_type == "FOLDER"]
        if use_folder:
            gl_l = [i for i,ly in enumerate(items) if ly.layer_type == "FOLDER"]
            fold_l = [i for i,ly in enumerate(items) if ly.layer_type == "FOLDER" and ly.folder_fold]
            # print("gp     ",gl_l)
            # print("fold   ",fold_l)
            for top_index in fold_l:
                bm =  gl_l[gl_l.index(top_index)]
                try:
                    top =  gl_l[gl_l.index(top_index)+1]
                except IndexError:
                    top =  len(items)
                for i,ly in enumerate(items):
                    if bm < i < top:
                        filtered[i] &= ~self.bitflag_filter_item

        return filtered,ordered
