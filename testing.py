# import bpy.ops
import bpy
import math

ctx = bpy.context
ops = bpy.ops

ctx.scene.frame_start = 0
ctx.scene.frame_end = 21

ctx.scene.frame_current = 0
ops.mesh.primitive_uv_sphere_add()
ops.object.shade_smooth()
ob = ctx.active_object
ob.name = "Root0"
ops.anim.keyframe_insert_menu(type='Location')
ops.anim.keyframe_insert_menu(type='Scaling')

ctx.scene.frame_current = 20
ops.object.select_pattern(pattern="Root0")
ob.location = (0,0,2)
ob.scale = (1,1,2)
ops.anim.keyframe_insert_menu(type='Location')
ops.anim.keyframe_insert_menu(type='Scaling')

ctx.scene.frame_current = 0