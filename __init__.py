'''
- "Cycles Texture Paint Layers"
    Add-ons before derivation.
    Copyright (C) 2018 DAVID DIGIOIA
    DAVIDOFJOY@GMAIL.com

    Created by DAVID DIGIOIA


- "Tx Layer"
    Created by Bookyakuno
    "Tx Layer" is an add-on derived from "Cycles Texture Paint Layers" ver0.0.2.
    It has been updated by Bookyakuno since ver0.0.3.

    "Tx Layer"は、"Cycles Texture Paint Layers"ver0.0.2 を元に派生したアドオンです。
    ver0.0.3からBookyakunoがアップデートしています。


- "Licence"
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

bl_info = {
    "name": "Tx Layer by Mushus",
    "description": "Layer functionality using nodes for texture paint",
    "author": "David DiGioia, Alexander Belyakov, Bookyakuno(ver0.0.3-), Mushus",
    "version": (0, 0, 53),
    "blender": (3, 2, 0),
    "location": "View3D > Texture Paint Mode > Tool > Layers",
    "warning": "",
    "wiki_url": "",
    "category": "Paint"
}


if "bpy" in locals():
    import importlib
    reloadable_modules = [
    "data",
    "layer_utils",
    "operators",
    "ui",
    "utils",

    ]
    for module in reloadable_modules:
        if module in locals():
            importlib.reload(locals()[module])


import bpy, sys, os
from bpy.props import *
from bpy.types import AddonPreferences



from .data.props import LAYER_PR_ui
from .layer_utils import *
from .utils import GetTranslationDict

from . import (
data,
operators,
ui,
)
from .ui.layer_panel import LAYER_PT_panel,LAYER_PT_panel_sub


def update_panel(self, context):
    message = ": Updating Panel locations has failed"
    try:
        cate = context.preferences.addons[__name__.partition('.')[0]].preferences.category
        if cate:
            for panel in panels:
                if "bl_rna" in panel.__dict__:
                    bpy.utils.unregister_class(panel)

            for panel in panels:
                panel.bl_category = cate
                bpy.utils.register_class(panel)
        else:
            for panel in panels:
                if "bl_rna" in panel.__dict__:
                    bpy.utils.unregister_class(panel)

    except Exception as e:
        print("\n[{}]\n{}\n\nError:\n{}".format(__name__, message, e))
        pass


class LAYER_MT_AddonPreferences(AddonPreferences):
    bl_idname = __name__

    category : StringProperty(name="Tab Category", description="Choose a name for the category of the panel", default="Addons", update=update_panel)
    tab_addon_menu : EnumProperty(name="Tab", description="", items=[('OPTION', "Option", "","DOT",0),('LINK', "Link", "","URL",1)], default='OPTION')
    debug_mode : BoolProperty(name="Debug Mode")
    ui : PointerProperty(type=LAYER_PR_ui)
    clipping_mask_color : FloatVectorProperty(name="Clipping Mask Color", default=(0.791298, 0.215861, 0.215861, 1.000000), size=4, subtype="COLOR", min=0, max=1)
    items = [
    ("ShaderNodeBsdfPrincipled","Principled BSDF",""),
    ("ShaderNodeBsdfDiffuse","Diffuse",""),
    ("ShaderNodeEmission","Emission",""),
    ]
    default_shader_type : EnumProperty(default="ShaderNodeBsdfPrincipled",name="Default Shader Type",items= items)


    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.prop(self, "tab_addon_menu",expand=True)

        if self.tab_addon_menu == "OPTION":
            layout.prop(self.ui,"display_panel_other_than_texture_paint_mode")
            if self.ui.display_panel_other_than_texture_paint_mode:
                layout.prop(self,"category")
            else:
                layout.label(text="",icon="NONE")
            layout.separator()
            # row.prop(self,"default_shader_type")
            row = layout.row(align=True)
            row.prop(self,"clipping_mask_color")
            layout.separator()
            layout.prop(self,"debug_mode")

        if self.tab_addon_menu == "LINK":
            row = layout.row()
            row.label(text="Store :")
            row.operator( "wm.url_open", text="gumroad", icon="URL").url = "https://bookyakuno.gumroad.com/l/CyclesTexturePaintLayers"
            row = layout.row()
            row.label(text="Description")
            row.operator( "wm.url_open", text="bookyakuo.com", icon="URL").url = "https://bookyakuno.com/cycles-texture-paint-layers/"

            layout.separator()
            col = layout.column(align=True)
            col.label(text="'Tx Layer' is an add-on derived from 'Cycles Texture Paint Layers' ver0.0.2.",icon="NONE")
            col.label(text="It has been updated by Bookyakuno since ver0.0.3.",icon="NONE")
            row = layout.row()
            row.label(text="Old version Blender Artists :")
            row.operator( "wm.url_open", text="Blender Artists", icon="URL").url = "https://blenderartists.org/t/cycles-texture-paint-layers/1126636?u=bookyakuno"
            row = layout.row()
            row.label(text="Old version Download :")
            row.operator( "wm.url_open", text="GitLab", icon="URL").url = "https://gitlab.com/AlexBelyakov/cycles-texture-paint-layers"


panels = (
LAYER_PT_panel_sub,
)

classes = (
LAYER_PT_panel,
LAYER_MT_AddonPreferences,
)

def register():
    operators.register()
    ui.register()
    data.register()

    for cls in classes:
        bpy.utils.register_class(cls)



    update_panel(None, bpy.context)
    # translation
    try:
        translation_dict = GetTranslationDict()
        bpy.app.translations.register(__name__, translation_dict)
    except Exception as e: print(e)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    for cls in reversed(panels):
        bpy.utils.unregister_class(cls)

    data.unregister()
    operators.unregister()
    ui.unregister()

    # translation
    try:
        bpy.app.translations.unregister(__name__)
    except: pass
