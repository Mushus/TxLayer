import bpy
from bpy.props import *


class LayerShaders(bpy.types.PropertyGroup):
    """References to all shaders that layers depends on."""

    diffuse: StringProperty(
        name="Diffuse",
        description="Diffuse Shader Node")

    transparent: StringProperty(
        name="Transparent",
        description="Transparent Shader Node")

    mix: StringProperty(
        name="mix",
        description="Mix Shader Node")

    backup_connect_socket: StringProperty(
        name="backup_connect_socket",
        description="")
