import bpy
from .. import layer_utils
from .. import utils


def draw_active_item_option(self, layout):
    obj = bpy.context.object
    if not obj:
        return
    mat = obj.active_material
    if not mat:
        return

    colle = mat.layer_list
    if not colle:
        return
    item = colle[mat.layer_index]

    ntree = layer_utils.get_item_node_tree(item)

    if not item.img_tex in ntree.nodes:
        return


    prefs = layer_utils.preference()
    sp = layout.split(align=True,factor=0.9)
    row = sp.row(align=True)
    row.alignment="LEFT"
    row.prop(prefs.ui,"toggle_node_setting",text=item.name,icon="TRIA_DOWN" if prefs.ui.toggle_node_setting else "TRIA_RIGHT", emboss=False,translate=False)
    if item.layer_type == "PROCEDURAL":
        row = sp.row(align=True)
        row.alignment="RIGHT"
        row.menu("LAYER_MT_node_change_texture_coord",text="",icon="MOD_UVPROJECT")

    if not prefs.ui.toggle_node_setting:
        return


    tgt_node = ntree.nodes[item.img_tex]
    if not item.layer_type in {"ADJUSTMENT","PROCEDURAL"}:
        box = layout.box()
        col_main = box.column()
        # col_main.label(text=str(tgt_node.image),icon="NONE")
        col_main.template_ID(tgt_node, "image", new="image.new",open="image.open")
        col_main.prop(tgt_node,"interpolation")


    if not item.layer_type in {"ADJUSTMENT","PROCEDURAL"}:
        return


    if item.layer_type == "PROCEDURAL":
        # row = layout.row(align=True)
        # row.label(text=item.name,icon="NONE")
        # row.menu("LAYER_MT_node_change_texture_coord",text="",icon="DOWNARROW_HLT")

        box = layout.box()
        col_main = box.column()

        if tgt_node.type == "TEX_NOISE":
            col_main.prop(tgt_node,"noise_dimensions",text="")
            col_main.separator()
            if tgt_node.noise_dimensions in {"1D"}:
                col_main.prop(tgt_node.inputs[1],"default_value",text=tgt_node.inputs[1].name)
                col_main.prop(tgt_node.inputs[2],"default_value",text=tgt_node.inputs[2].name)
                col_main.prop(tgt_node.inputs[3],"default_value",text=tgt_node.inputs[3].name)
                col_main.prop(tgt_node.inputs[4],"default_value",text=tgt_node.inputs[4].name)
                col_main.prop(tgt_node.inputs[5],"default_value",text=tgt_node.inputs[5].name)
            elif tgt_node.noise_dimensions in {"2D","3D"}:
                col_main.prop(tgt_node.inputs[2],"default_value",text=tgt_node.inputs[2].name)
                col_main.prop(tgt_node.inputs[3],"default_value",text=tgt_node.inputs[3].name)
                col_main.prop(tgt_node.inputs[4],"default_value",text=tgt_node.inputs[4].name)
                col_main.prop(tgt_node.inputs[5],"default_value",text=tgt_node.inputs[5].name)
            elif tgt_node.noise_dimensions in {"4D"}:
                col_main.prop(tgt_node.inputs[1],"default_value",text=tgt_node.inputs[1].name)
                col_main.prop(tgt_node.inputs[2],"default_value",text=tgt_node.inputs[2].name)
                col_main.prop(tgt_node.inputs[3],"default_value",text=tgt_node.inputs[3].name)
                col_main.prop(tgt_node.inputs[4],"default_value",text=tgt_node.inputs[4].name)
                col_main.prop(tgt_node.inputs[5],"default_value",text=tgt_node.inputs[5].name)


        elif tgt_node.type == "TEX_VORONOI":
            col_main.prop(tgt_node,"voronoi_dimensions",text="")
            col_main.prop(tgt_node,"feature",text="")
            col_main.prop(tgt_node,"distance",text="")
            if tgt_node.voronoi_dimensions in {"1D","4D"}:
                col_main.prop(tgt_node.inputs[1],"default_value",text=tgt_node.inputs[1].name)

            col_main.prop(tgt_node.inputs[2],"default_value",text=tgt_node.inputs[2].name)
            if tgt_node.feature == "SMOOTH_F1":
                col_main.prop(tgt_node.inputs[3],"default_value",text=tgt_node.inputs[3].name)
            if tgt_node.voronoi_dimensions in {"2D","3D","4D"}:
                if tgt_node.distance == "MINKOWSKI":
                    col_main.prop(tgt_node.inputs[4],"default_value",text=tgt_node.inputs[4].name)

            col_main.prop(tgt_node.inputs[5],"default_value",text=tgt_node.inputs[5].name)


        elif tgt_node.type == "TEX_WAVE":
            col_main.prop(tgt_node,"wave_type",text="")
            col_main.prop(tgt_node,"rings_direction",text="")
            col_main.prop(tgt_node,"wave_profile",text="")
            col_main.prop(tgt_node.inputs[1],"default_value",text=tgt_node.inputs[1].name)
            col_main.prop(tgt_node.inputs[2],"default_value",text=tgt_node.inputs[2].name)
            col_main.prop(tgt_node.inputs[3],"default_value",text=tgt_node.inputs[3].name)
            col_main.prop(tgt_node.inputs[4],"default_value",text=tgt_node.inputs[4].name)
            col_main.prop(tgt_node.inputs[5],"default_value",text=tgt_node.inputs[5].name)
            col_main.prop(tgt_node.inputs[6],"default_value",text=tgt_node.inputs[6].name)


        elif tgt_node.type == "TEX_MAGIC":
            col_main.prop(tgt_node,"turbulence_depth",text="Depth")
            col_main.separator()
            col_main.prop(tgt_node.inputs[1],"default_value",text=tgt_node.inputs[1].name)
            col_main.prop(tgt_node.inputs[2],"default_value",text=tgt_node.inputs[2].name)


        elif tgt_node.type == "TEX_MUSGRAVE":
            col_main.prop(tgt_node,"musgrave_dimensions",text="")
            col_main.prop(tgt_node,"musgrave_type",text="")
            col_main.separator()
            if tgt_node.musgrave_dimensions in {"1D","4D"}:
                col_main.prop(tgt_node.inputs[1],"default_value",text=tgt_node.inputs[1].name)
            col_main.prop(tgt_node.inputs[2],"default_value",text=tgt_node.inputs[2].name)
            col_main.prop(tgt_node.inputs[3],"default_value",text=tgt_node.inputs[3].name)
            col_main.prop(tgt_node.inputs[4],"default_value",text=tgt_node.inputs[4].name)
            col_main.prop(tgt_node.inputs[5],"default_value",text=tgt_node.inputs[5].name)
            if tgt_node.musgrave_type in {'HETERO_TERRAIN', 'HYBRID_MULTIFRACTAL', 'RIDGED_MULTIFRACTAL'}:
                col_main.prop(tgt_node.inputs[6],"default_value",text=tgt_node.inputs[6].name)
            if tgt_node.musgrave_type in {'RIDGED_MULTIFRACTAL','HYBRID_MULTIFRACTAL'}:
                col_main.prop(tgt_node.inputs[7],"default_value",text=tgt_node.inputs[7].name)


        elif tgt_node.type == "TEX_BRICK":
            col_main.prop(tgt_node,"offset")
            col_main.prop(tgt_node,"offset_frequency")
            col_main.prop(tgt_node,"squash")
            col_main.prop(tgt_node,"squash_frequency")
            col_main.separator()
            row = col_main.row(align=True)
            row.prop(tgt_node.inputs[1],"default_value",text=tgt_node.inputs[1].name)
            row = col_main.row(align=True)
            row.prop(tgt_node.inputs[2],"default_value",text=tgt_node.inputs[2].name)
            row = col_main.row(align=True)
            row.prop(tgt_node.inputs[3],"default_value",text=tgt_node.inputs[3].name)
            col_main.prop(tgt_node.inputs[4],"default_value",text=tgt_node.inputs[4].name)
            col_main.prop(tgt_node.inputs[5],"default_value",text=tgt_node.inputs[5].name)
            col_main.prop(tgt_node.inputs[6],"default_value",text=tgt_node.inputs[6].name)
            col_main.prop(tgt_node.inputs[7],"default_value",text=tgt_node.inputs[7].name)
            col_main.prop(tgt_node.inputs[8],"default_value",text=tgt_node.inputs[8].name)
            col_main.prop(tgt_node.inputs[9],"default_value",text=tgt_node.inputs[9].name)


        elif tgt_node.type == "TEX_GRADIENT":
            col_main.prop(tgt_node,"gradient_type")


        elif tgt_node.type == "TEX_CHECKER":
            row = col_main.row(align=True)
            row.prop(tgt_node.inputs[1],"default_value",text=tgt_node.inputs[1].name)
            row = col_main.row(align=True)
            row.prop(tgt_node.inputs[2],"default_value",text=tgt_node.inputs[2].name)
            col_main.prop(tgt_node.inputs[3],"default_value",text=tgt_node.inputs[3].name)


        if item.mapping in ntree.nodes:
            col_main.separator()
            box = col_main.box()
            col = box.column(align=True)
            tgt_node = ntree.nodes[item.mapping]
            # col_main.prop(tgt_node,"vecter_type")
            row = col.row(align=True)
            col = row.column(align=True)
            col.prop(tgt_node.inputs[1],"default_value",text="Location")
            col = row.column(align=True)
            col.prop(tgt_node.inputs[2],"default_value",text="Rotation")
            col = row.column(align=True)
            col.prop(tgt_node.inputs[3],"default_value",text="Scale")




    elif item.layer_type == "ADJUSTMENT":
        if not tgt_node.type in ["CURVE_RGB", "VALTORGB", "HUE_SAT", "BRIGHTCONTRAST", "GAMMA"]:
            return

        # layout.label(text=tgt_node.type,icon="NONE")


        box = layout.box()
        col_main = box.column()
        if tgt_node.type == "CURVE_RGB":
            col_main.template_curve_mapping(tgt_node,"mapping",type="COLOR")

        elif tgt_node.type == "VALTORGB":
            col_main.template_color_ramp(tgt_node,"color_ramp")

        elif tgt_node.type == "HUE_SAT":
            col_main.prop(tgt_node.inputs[0],"default_value",text="Hue")
            col_main.prop(tgt_node.inputs[1],"default_value",text="Saturation")
            col_main.prop(tgt_node.inputs[2],"default_value",text="Value")
            col_main.prop(tgt_node.inputs[3],"default_value",text="Fac")

        elif tgt_node.type == "BRIGHTCONTRAST":
            col_main.prop(tgt_node.inputs[1],"default_value",text="Bright")
            col_main.prop(tgt_node.inputs[2],"default_value",text="Contrast")

        elif tgt_node.type == "GAMMA":
            col_main.prop(tgt_node.inputs[1],"default_value",text="Gamma")
            col_main.template_color_ramp(tgt_node,"color_ramp")

        # elif tgt_node.type == "RGBTOBW":
        #     col_main.prop(tgt_node.inputs[0],"default_value",text="Gamma")
        #     col_main.template_color_ramp(tgt_node,"color_ramp")
        # elif tgt_node.type == "INVERT":
        #     col_main.template_color_ramp(tgt_node,"color_ramp")
