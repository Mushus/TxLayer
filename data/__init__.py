# data
import bpy
from bpy.app.handlers import persistent

if "bpy" in locals():
	import importlib
	reloadable_modules = [
	"layer_data",
	"layer_img_data",
	"layer_shader_data",
	"props",

	]
	for module in reloadable_modules:
		if module in locals():
			importlib.reload(locals()[module])


from .layer_data import *
from .layer_img_data import *
from .layer_shader_data import *
from .props import *
from .. import layer_utils
from ..operators import add_dummy_image_node


classes = (
Layer,
LayerImgData,
LayerShaders,
LAYER_PR_texpaint_layers,
LAYER_PR_ui,
)


@persistent
def undo_fix_active_slot_in_node_group(scene):
	if not bpy.context.mode == "PAINT_TEXTURE":
		return

	obj = bpy.context.object
	if not obj:
		return
	mat = obj.active_material
	if not mat:
		return
	if not mat:
		return
	# if not mat.layer_active_node_group_name:
	# 	return
	layer_list = mat.layer_list
	if not layer_list:
		return
	layer = layer_list[mat.layer_index]
	img_name = layer.texture
	if not layer.node_tree:
		return

	if layer.node_tree in bpy.data.node_groups:
		nodes = bpy.data.node_groups[layer.node_tree].nodes
		nodes.active = nodes[layer.img_tex]


	# Need to update scene in order for slots to update in time
	vl = bpy.context.view_layer
	vl.update()


	slots = mat.texture_paint_images
	slot_index = None
	for i, slot in enumerate(slots):
		if slot.name == img_name:
			slot_index = i
			mat.paint_active_slot = slot_index
			break


def register():
	for cls in classes:
		bpy.utils.register_class(cls)


	def get_index(self):
		return self.layer_private_index


	def set_index(self, index):
		mat = bpy.context.object.active_material
		layer_list = mat.layer_list

		if index < 0 or index >= len(layer_list):
			self.layer_private_index = index
			return

		layer = layer_list[index]
		img_name = layer.texture
		ntree = layer_utils.get_item_node_tree(layer)

		self.layer_private_index = index

		if layer.layer_type == "FOLDER":
			return

		if layer.multiply in ntree.nodes:
			sc = bpy.context.scene
			props = sc.texpaint_layers
			props.multiply_slider = ntree.nodes[layer.multiply].inputs[1].default_value * 100



		if layer.node_tree:
			# ノードグループ内のレイヤーを選択
			if layer.node_tree in bpy.data.node_groups:
				nodes = bpy.data.node_groups[layer.node_tree].nodes
				if layer.img_tex in ntree.nodes:
					nodes.active = nodes[layer.img_tex]


		# Need to update scene in order for slots to update in time
		vl = bpy.context.view_layer
		vl.update()


		# ロック用のダミー画像を作成
		if not "LAYER_DUMMY" in mat.node_tree.nodes:
			add_dummy_image_node(mat)
		# レイヤーがロックまたはプロシージャルの場合は、ダミー画像をアクティブする
		if layer.lock or layer.hide or layer.layer_type == "PROCEDURAL":
			img_name = "LAYER_DUMMY"

		slots = mat.texture_paint_images
		slot_index = None
		for i, slot in enumerate(slots):
			if slot.name == img_name:
				slot_index = i
				mat.paint_active_slot = slot_index
				break
		# try:
		# except TypeError as e:
		# 	print("No slot names match layer name. There are probably missing slots")
		# 	print("Error: " + str(e))


		# マテリアル内のノードグループを選択
		if layer.node_tree:
			for nd in mat.node_tree.nodes:
				if nd.type == "GROUP":
					if nd.node_tree:
						if layer.node_tree == nd.node_tree.name:
							nd.select = True
							mat.node_tree.nodes.active = nd
							break


		self.layer_private_index = index



	bpy.types.Material.layer_list = bpy.props.CollectionProperty(type=Layer)
	bpy.types.Material.layer_index = bpy.props.IntProperty(name="Index for layer list", default=0, get=get_index, set=set_index)
	bpy.types.Material.layer_private_index = bpy.props.IntProperty(name="PRIVATE layer index", default=0)
	bpy.types.Material.layer_shaders = bpy.props.PointerProperty(type=LayerShaders)
	bpy.types.Material.layer_img_data = bpy.props.PointerProperty(type=LayerImgData)
	bpy.types.Material.layer_solo_backup_hide_dic = bpy.props.StringProperty()
	bpy.types.Material.layer_solo_index = bpy.props.IntProperty()
	bpy.types.Material.layer_active_node_group_name = bpy.props.StringProperty(default="")
	bpy.types.NodeTree.layer_is_bump = bpy.props.BoolProperty()
	bpy.types.Scene.texpaint_layers = bpy.props.PointerProperty(type=LAYER_PR_texpaint_layers)

	# bpy.app.handlers.undo_post.append(undo_fix_active_slot_in_node_group)
	# bpy.app.handlers.redo_post.append(undo_fix_active_slot_in_node_group)


def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)


	del bpy.types.Material.layer_list
	del bpy.types.Material.layer_index
	del bpy.types.Material.layer_private_index
	del bpy.types.Material.layer_shaders
	del bpy.types.Material.layer_img_data
	del bpy.types.NodeTree.layer_is_bump
	del bpy.types.Scene.texpaint_layers

	# bpy.app.handlers.undo_post.remove(undo_fix_active_slot_in_node_group)
	# bpy.app.handlers.redo_post.remove(undo_fix_active_slot_in_node_group)


if __name__ == "__main__":
	register()
