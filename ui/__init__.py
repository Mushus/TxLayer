# ui
import bpy

if "bpy" in locals():
	import importlib
	reloadable_modules = [
	"layer_list",
	"layer_panel",
	"layer_menu",
	"ui_act_item",

	]
	for module in reloadable_modules:
		if module in locals():
			importlib.reload(locals()[module])


from .layer_list import *
from .layer_panel import *
from .layer_menu import *
from .ui_act_item import *

classes = (
LAYER_MT_node_change_texture_coord,
LAYER_MT_layer_option,
LAYER_MT_new_adjustment_layer,
LAYER_MT_new_procedural_layer,
LAYER_MT_node_group_set_active,
LAYER_MT_other_option,
LAYER_MT_set_mask,
MATERIAL_UL_layerlist,
)


def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)


if __name__ == "__main__":
	register()
