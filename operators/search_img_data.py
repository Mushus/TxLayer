import bpy
from bpy.types import Operator
from bpy.props import *

class LAYER_create_enum_SearchOperator:
    use_cache = False

    def fill_enum_items(self, items):
        pass

    def get_enum_items(self, context):
        cls = getattr(bpy.types, self.__class__.__name__)
        if not hasattr(cls, "enum_items"):
            return tuple()

        if cls.enum_items is None:
            cls.enum_items = []
            cls.fill_enum_items(self, cls.enum_items)

        return cls.enum_items


    value: EnumProperty( name="Value", items=get_enum_items)

    def invoke(self, context, event):
        # cls = getattr(bpy.types, self.__class__.__name__)
        cls = bpy.types.LAYER_LIST_OT_search_load_image
        if not hasattr(cls, "enum_items"):
            cls.enum_items = None
        elif not self.use_cache and cls.enum_items:
            cls.enum_items.clear()
            cls.enum_items = None

        context.window_manager.invoke_search_popup(self)
        return {'FINISHED'}


class LAYER_LIST_OT_search_load_image(LAYER_create_enum_SearchOperator, Operator):
    bl_idname = "layer_list.search_load_image"
    bl_label = "Import Existing Image"
    bl_description = "Import an existing image in your project as a layer"
    # bl_options = {'INTERNAL', 'UNDO'}
    bl_property = "value"

    item : IntProperty(name="Item")

    idx: IntProperty(options={'SKIP_SAVE'})
    mouse_over: BoolProperty(options={'SKIP_SAVE'})
    pie: BoolProperty(options={'SKIP_SAVE'})


    def fill_enum_items(self, items):
        for i,img in enumerate(bpy.data.images):
            if img.preview:
                items += [(img.name, img.name, "",img.preview.icon_id,i)]
            else:
                items += [(img.name, img.name, "","NONE",i)]


    def execute(self, context):
        bpy.ops.layer_list.new_layer("INVOKE_DEFAULT",img_type="LOAD",load_image_name=self.value)
        return{'FINISHED'}
