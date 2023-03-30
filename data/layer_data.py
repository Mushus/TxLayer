import bpy
from .. import layer_utils
from bpy.props import *
from ..operators import add_dummy_image_node


def update_img_name(self,context):
    obj = bpy.context.object
    if not obj:
        return
    mat = obj.active_material
    if not mat:
        return
    if not mat:
        return
    layer_list = mat.layer_list
    if not layer_list:
        return

    tgt_layer = layer_list[mat.layer_index]
    ntree = layer_utils.get_item_node_tree(tgt_layer)

    if tgt_layer.img_tex in ntree.nodes and not tgt_layer.layer_type in {"ADJUSTMENT","PROCEDURAL"}:
    # if tgt_layer.img_tex in ntree.nodes and not tgt_layer.layer_type in {"ADJUSTMENT"}:
        img = ntree.nodes[tgt_layer.img_tex].image
        tgt_name = tgt_layer.name

        if tgt_name in bpy.data.images:
            if tgt_layer.node_tree:
                tgt_name = tgt_name + "_" + tgt_layer.node_tree
            else:
                tgt_name = tgt_name + "_" + mat.name

            if tgt_name in bpy.data.images:
                count = [i for i in bpy.data.node_groups if not i.name.find(tgt_name + ".00") == -1]
                if len(count):
                    tgt_name = tgt_name + ".00" + len(count)
                else:
                    tgt_name = tgt_name + ".001"


        img.name = tgt_name
        tgt_layer.texture = tgt_name

        # 同名の入力ソケット名を変更 (なぜか最大深度のエラーが出る
        if tgt_layer.node_tree:
            if not tgt_layer.name_private in {"Color","Alpha"}:
                gp_out_node = [i for i in ntree.nodes if i.type == "GROUP_OUTPUT"][0]
                if tgt_layer.name_private in [inp.name for inp in gp_out_node.inputs]:
                    gp_out_node = ntree.nodes["Group Output"]
                    gp_out_node.inputs[tgt_layer.name_private].name = tgt_layer.name


        tgt_layer.name_private = tgt_layer.name



#

def update_lock(self,context):
    obj = bpy.context.object
    mat = obj.active_material
    layer = self
    ntree = layer_utils.get_item_node_tree(layer)

    # ロック用のダミー画像を作成
    if layer.lock or layer.layer_type == "PROCEDURAL":
        if not "LAYER_DUMMY" in mat.node_tree.nodes:
            add_dummy_image_node(mat)

    slots = mat.texture_paint_images
    slot_index = None
    for i, slot in enumerate(slots):
        # レイヤーがロックまたはプロシージャルの場合は、ダミー画像をアクティブする
        if layer.lock or layer.layer_type == "PROCEDURAL":
            if slot.name == "LAYER_DUMMY":
                slot_index = i
                mat.paint_active_slot = slot_index
                break
        else:
            if slot.name == ntree.nodes[layer.img_tex].image.name:
                slot_index = i
                mat.paint_active_slot = slot_index
                break


class Layer(bpy.types.PropertyGroup):
    """Group of properties representing a layer in the list."""

    # Getters / Setters
    def hide_get(self):
        ntree = layer_utils.get_item_node_tree(self)
        if self.mix in ntree.nodes:
            return ntree.nodes[self.mix].mute
        elif self.layer_type == "FOLDER":
            return self.folder_hide
        else:
            return True

    def hide_set(self, value):
        ntree = layer_utils.get_item_node_tree(self)
        if self.mix in ntree.nodes:
            ntree.nodes[self.mix].mute = value

        if self.layer_type == "FOLDER":
            obj = bpy.context.object
            mat = obj.active_material

            for i,item in enumerate(mat.layer_list):
                if item == self:
                    index = i
                    break

            bottom_gp_index = len(mat.layer_list)-1
            gp_l = [(i,ly) for i,ly in enumerate(mat.layer_list) if ly.layer_type == "FOLDER" if index < i]
            # gp_l = []
            # for i,ly in enumerate(mat.layer_list):
            #     if ly.layer_type == "FOLDER":
            #         if index < i:
            #             gp_l += [(i,ly)]

            if len(gp_l) >= 1:
                bottom_gp_index = gp_l[0][0] # 対象グループの下

            # hide_item_l = [ly for i,ly in enumerate(mat.layer_list) if  index <= i < bottom_gp_index]
            hide_item_l = []
            for i,ly in enumerate(mat.layer_list):
                if index <= i < bottom_gp_index:
                    # print(ly.name)
                    if not ly.layer_type == "FOLDER":
                        ly.hide = not (self.hide)

            self.folder_hide = not self.hide

    # Properties
    name: StringProperty(
        name="Name",
        description="Layer name",
        default="New Layer",
        update=update_img_name,
        )
    name_private: StringProperty(
        name="Name",
        description="Layer name",
        default="",
        )

    hide: BoolProperty(
        name="Hide",
        description="Toggle layer visibility",
        default=False,
        get=hide_get,
        set=hide_set)

    lock: BoolProperty(name="lock", description="Lock", update=update_lock)

    folder_hide : BoolProperty(name="Hide")
    folder_fold : BoolProperty(name="Fold")

    node_tree: StringProperty(
        name="Node ntree Name",
        description="") # ルート(シェーダーノード)の場合はなし

    mix: StringProperty(
        name="Mix Node Name",
        description="Node handles mixing between adjacent layers based on opacity")

    multiply: StringProperty(
        name="Multiply Node Name",
        description="Multiplies alpha, serves as opacity")

    mask: StringProperty(
        name="Mask Texture Node Name",
        description="Mask")

    img_tex: StringProperty(
        name="Image Texture Node Name",
        description="Image texture node being stored in the layer")

    texture: StringProperty(
        name="Image Texture Name",
        description="Image texture being stored in the layer")

    add: StringProperty(
        name="Add Node Name",
        description="Adds alpha to produce final alpha map")

    adjustment: StringProperty(
        name="Adjustment Node Name",
        description="Adjustment Node Name")

    items = [
    ("IMAGE","Image",""),
    ("FILL","Fill",""),
    ("ADJUSTMENT","Adjustment",""),
    ("PROCEDURAL","Procedural",""),
    ("FOLDER","Folder",""),
    ]
    layer_type : EnumProperty(default="IMAGE",name="Type",items= items)

    palette_color: FloatVectorProperty(
        name="Palette Color",
        description='Palette Color',
        subtype='COLOR',
        size=3,
        default=(0,0,0),
        min=0.0,
        max=1.0)


    mapping : StringProperty()
    texcoord : StringProperty()
