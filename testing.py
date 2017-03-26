import bpy
import math

ctx = bpy.context
sc = ctx.scene
ops = bpy.ops

sc.frame_start = 0
sc.frame_end = 60

sc.frame_current = 0
ops.mesh.primitive_uv_sphere_add()
ops.object.shade_smooth()
ob = ctx.active_object
ob.name = "Root0"
ops.transform.translate(value=(0,0,1))
ops.anim.keyframe_insert_menu(type='Location')
ops.anim.keyframe_insert_menu(type='Scaling')

frame_step = 20; growth_rate = 1; loop_num = 1
sc.frame_current = loop_num*frame_step
while sc.frame_current <= sc.frame_end:
	ops.object.select_pattern(pattern="Root0")
	ops.transform.translate(value=(0,0,growth_rate))
	ops.transform.resize(value=(1,1,((loop_num+1)/loop_num)))
	# ob.location = (0,0,2)
	# ob.scale = (1,1,2)
	ops.anim.keyframe_insert_menu(type='Location')
	ops.anim.keyframe_insert_menu(type='Scaling')
	loop_num += 1
	sc.frame_current = loop_num*frame_step

sc.frame_current = 0