import bpy
from bpy.props import *


class LayerImgData(bpy.types.PropertyGroup):
    """Data to be used each time layer is created."""

    width: IntProperty(
        name="Width",
        description="Horizontal dimension",
        default=1024,
        subtype = "PIXEL",
        )

    height: IntProperty(
        name="Height",
        description="Vertical dimension",
        default=1024,
        subtype = "PIXEL",
        )

    base_color: FloatVectorProperty(
        name="BG Color",
        description='Color picker',
        subtype='COLOR',
        size=4,
        default=(1, 1, 1, 1),
        min=0.0,
        max=1.0)
    metallic: FloatProperty(name="Metallic",min=0,max=1)
    roughness: FloatProperty(name="Roughness",min=0,max=1,default=0.5)

    bit_depth: BoolProperty(
        name="32 bit",
        description="Create image with 32 bit floating point bit depth",
        default=False)


    items = [
    ("Linear", "Linear", "Linear interpolation"),
    ("Closest", "Closest", "No interpolation (sample closest texel)"),
    ("Cubic", "Cubic", "Cubic interpolation"),
    ("Smart", "Smart", "Bicubic when magnifying, else bilinear (OSL only)"),
    ]
    interpolation : EnumProperty(default="Linear",name="Interpolation",items= items, description="Texture interpolation.\nFor bump map textures, it will always be [Cubic] automatically")
