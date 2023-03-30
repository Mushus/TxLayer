# op
import bpy

if "bpy" in locals():
	import importlib
	reloadable_modules = [
	"delete_layer",
	"merge_visible_layers",
	"move_layer",
	"new_layer_fanc",
	"new_layer_node",
	"node_group",
	"op_other",
	"search_img_data",
	"set_mask",
	"op_brush",
	"op_image",
	#
	"new_layer_core",

	]
	for module in reloadable_modules:
		if module in locals():
			importlib.reload(locals()[module])


from .delete_layer import *
from .merge_visible_layers import *
from .move_layer import *
from .new_layer_fanc import *
from .new_layer_node import *
from .node_group import *
from .op_other import *
from .search_img_data import *
from .set_mask import *
from .op_brush import *
from .op_image import *
#
from .new_layer_core import *

classes = (
LAYER_OT_node_viewer,
LAYER_Decolorization,
LAYER_img_invert_color,
LAYER_LIST_OT_search_load_image,
LAYER_OT_brush_set_eraser,
LAYER_OT_brush_set_gradient,
LAYER_OT_change_shadernode,
LAYER_OT_dellayer,
LAYER_OT_img_icon_update,
LAYER_OT_layer_add_folder,
LAYER_OT_layer_setting_resize_2x,
LAYER_OT_layer_toggle_solo,
LAYER_OT_mat_new,
LAYER_OT_MergeVisibleLayers,
LAYER_OT_movelayer,
LAYER_OT_newlayer,
LAYER_OT_node_change_texture_coord,
LAYER_OT_node_group_create,
LAYER_OT_node_group_create_layer_input_socket,
LAYER_OT_node_group_create_select_root_nodes,
LAYER_OT_node_group_remove_layer_input_socket,
LAYER_OT_node_group_rename_active_ng,
LAYER_OT_node_group_set_active,
LAYER_OT_set_mask,
LAYER_OT_layer_load_external_image,
LAYER_OT_layer_read_psd,
)


def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)


if __name__ == "__main__":
	register()
