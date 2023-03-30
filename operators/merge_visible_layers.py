import bpy, datetime, bmesh, re
from bpy.props import *

from .. import layer_utils



#
def update_bake_type(self, context):
    # shading_bake = ["COMBINED", "AO", "SHADOW", "ENVIRONMENT",]
    flat_bake = ["NORMAL", "UV", "EMIT", "DIFFUSE", "GLOSSY", "TRANSMISSION","ROUGHNESS"]

    if self.bake_type in flat_bake:
        self.use_tmp_plane = True
    else:
        self.use_tmp_plane = False


class LAYER_OT_MergeVisibleLayers(bpy.types.Operator):
    bl_idname = "merge.visible_layers"
    bl_label = "Merge visible layers (Bake)"
    bl_description = "Merge(Bake) visible layers into single image"
    bl_options = {"REGISTER"}

    items = [
    ("DIFFUSE","Diffuse","","SHADING_SOLID",0),
    ("EMIT","Emit","","LIGHT_SUN",1),
    ("COMBINED","Combined","","DOT",2),
    ("AO","AO","","SHADING_RENDERED",3),
    ("SHADOW","Shadow","","LIGHT",4),
    ("NORMAL","Normal","","NORMALS_FACE",5),
    ("UV","UV","","UV",6),
    ("ROUGHNESS","Roughness","","NODE_MATERIAL",7),
    ("ENVIRONMENT","Environment","","WORLD",8),
    ("GLOSSY","Glossy","","NODE_MATERIAL",9),
    ("TRANSMISSION","Transmission","","NODE_MATERIAL",10),
    ]
    bake_type : EnumProperty(default="DIFFUSE",name="Type",items= items)
    samples : IntProperty(name="Samples",min=1,default=1)
    use_tmp_plane : BoolProperty(name="Use Temp Plane Mesh",default=True, description="Bake all areas of the material by using a plane mesh.\n(Because it bake with a flat mesh, the baking time will be a little faster)\nYou can avoid the problem that normal baking only bakes the area of the selected object")


    def invoke(self, context, event):
        self.old_render_settings = get_current_render_settings()
        obj = bpy.context.object
        mat = obj.active_material

        if mat.layer_shaders.diffuse in mat.node_tree.nodes:
            old_node = mat.node_tree.nodes[mat.layer_shaders.diffuse]
            if old_node.type =="EMISSION":
                self.bake_type = 'EMIT'

        return context.window_manager.invoke_props_dialog(self, width=300)


    def execute(self, context):
        self.info_finish_time = ""
        self.info_start_time = datetime.datetime.now()

        # Store current scene settings
        scene = context.scene
        render_engine = scene.render.engine
        scene.render.engine = 'CYCLES'
        samples = scene.cycles.samples
        bake_type = scene.cycles.bake_type
        pass_direct = scene.render.bake.use_pass_direct
        pass_indirect = scene.render.bake.use_pass_indirect


        old_sel = bpy.context.selected_objects
        old_act = bpy.context.object
        mat = old_act.active_material
        ntree = mat.node_tree

        plane_obj = None


        if self.use_tmp_plane and not self.bake_type in {"COMBINED", "AO", "SHADOW", "ENVIRONMENT"}:
            for obj in bpy.context.selected_objects:
                obj.select_set(False)
            plane_obj = create_temp_mesh(self, mat)


        # Bake layers
        img_data = mat.layer_img_data
        img = bpy.data.images.new(name="merged_layers", alpha=True, width=img_data.width,
                                  height=img_data.height, float_buffer=img_data.bit_depth)


        current_active_node = ntree.nodes.active
        nodes = ntree.nodes
        node_texture = nodes.new(type="ShaderNodeTexImage")
        nodes.active = node_texture
        node_texture.image = img

        scene.cycles.samples = self.samples
        scene.cycles.bake_type = self.bake_type
        scene.render.bake.use_pass_direct = False
        scene.render.bake.use_pass_indirect = False
        scene.render.bake.use_pass_color = True

        # bake
        bpy.ops.object.bake(type=self.bake_type)


        # Restore
        restore_settings_after_all_process(self, old_act, old_sel, plane_obj)
        nodes.active = current_active_node
        bpy.ops.layer_list.new_layer("INVOKE_DEFAULT",img_type = "LOAD",load_image_name = node_texture.image.name)
        nodes.remove(node_texture)


        # レンダリング時間
        date_o = datetime.datetime.now() - self.info_start_time
        date_o_l = re.match("^(.+\.)(\d\d)\d\d\d\d$",str(date_o))
        date_o = date_o_l[1] + date_o_l[2]
        self.info_finish_time = date_o
        self.report({'INFO'}, "End of Rendering [%s]" % self.info_finish_time)

        return {"FINISHED"}


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        cbk = scene.render.bake
        obj = bpy.context.object
        mat = obj.active_material
        col_main = layout.column(align=True)
        col_main.prop(self, "bake_type")
        col_main.separator()
        col_main.use_property_split = True
        col_main.use_property_decorate = False
        col_main.prop(self, "use_tmp_plane")
        col_main.separator()
        row = col_main.row(align=True)
        col = row.column(align=True)
        col.prop(self, "samples")
        col.prop(cbk, "margin")
        row.label(text="",icon="BLANK1")
        col_main.separator()
        row = col_main.row(align=True)
        col = row.column(align=True)
        col.prop(mat.layer_img_data, 'width')
        col.prop(mat.layer_img_data, 'height')
        col = row.column(align=True)
        col.operator("layer_list.layer_setting_resize_2x",text="",icon="SORT_DESC",emboss=False).up=True
        col.operator("layer_list.layer_setting_resize_2x",text="",icon="SORT_ASC",emboss=False).up=False
        col_main.prop(mat.layer_img_data, "bit_depth")


#
def create_temp_mesh(self, mat):
    mesh = bpy.data.meshes.new(name="tmp_bake_plane")
    plane_obj = bpy.data.objects.new(name="tmp_bake_plane",object_data=mesh)
    plane_obj.data.materials.append(mat)
    bpy.context.collection.objects.link(plane_obj)
    bpy.context.view_layer.objects.active = plane_obj
    plane_obj.select_set(True)
    bm = bmesh.new()
    bm.from_object(plane_obj, bpy.context.view_layer.depsgraph)
    s = 1
    bm.verts.new((s,s,0))
    bm.verts.new((s,-s,0))
    bm.verts.new((-s,s,0))
    bm.verts.new((-s,-s,0))
    bmesh.ops.contextual_create(bm, geom=bm.verts)
    bm.to_mesh(mesh)
    mesh.uv_layers.new(name='UVMap')
    return plane_obj


#
# 現在のレンダリング設定を保存
def get_current_render_settings():
    sc = bpy.context.scene
    sc_bk = sc.render.bake

    old_render_settings = {
    "sc.render.image_settings.file_format":sc.render.image_settings.file_format,
    "sc.render.image_settings.compression":sc.render.image_settings.compression,
    "sc.render.image_settings.color_mode":sc.render.image_settings.color_mode,
    "sc.render.image_settings.color_depth":sc.render.image_settings.color_depth,

    "sc_bk.cage_extrusion":sc_bk.cage_extrusion,
    "sc_bk.cage_object":sc_bk.cage_object,
    "sc_bk.margin":sc_bk.margin,
    "sc_bk.max_ray_distance":sc_bk.max_ray_distance,
    "sc_bk.normal_b":sc_bk.normal_b,
    "sc_bk.normal_g":sc_bk.normal_g,
    "sc_bk.normal_r":sc_bk.normal_r,
    "sc_bk.normal_space":sc_bk.normal_space,
    "sc_bk.use_cage":sc_bk.use_cage,
    "sc_bk.use_clear":sc_bk.use_clear,
    "sc_bk.use_pass_color":sc_bk.use_pass_color,
    "sc_bk.use_pass_direct":sc_bk.use_pass_direct,
    "sc_bk.use_pass_indirect":sc_bk.use_pass_indirect,
    "sc_bk.use_selected_to_active":sc_bk.use_selected_to_active,

    "sc.cycles.samples":sc.cycles.samples,
    "sc.cycles.use_denoising":sc.cycles.use_denoising,
    "sc.render.engine":sc.render.engine,

    "sc.view_settings.exposure":sc.view_settings.exposure,
    "sc.view_settings.gamma":sc.view_settings.gamma,
    "sc.view_settings.look":sc.view_settings.look,
    "sc.view_settings.use_curve_mapping":sc.view_settings.use_curve_mapping,
    "sc.view_settings.view_transform":sc.view_settings.view_transform,
    }
    return old_render_settings


# 終了後に設定を戻す
def restore_settings_after_all_process(self, old_act, old_sel, plane_obj):
    sc = bpy.context.scene
    sc_bk = sc.render.bake

    # restore setting
    for i in self.old_render_settings.keys():
        try:
            exec(i + " = self.old_render_settings[i]")
        except Exception as e: print("restore_settings_after_all_process : ",e)


    for obj in old_sel:
        obj.select_set(True)

    # Restore object select
    if self.use_tmp_plane and not self.bake_type in {"COMBINED", "AO", "SHADOW", "ENVIRONMENT"}:
        bpy.data.objects.remove(plane_obj)
        for obj in bpy.context.selected_objects:
            obj.select_set(True)

        bpy.context.view_layer.objects.active = old_act
