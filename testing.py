import bpy
from mathutils import Vector
from mathutils import Quaternion

ctx = bpy.context
sc = ctx.scene
ops = bpy.ops

sc.render.fps = 25
delta_t = 1.0 / sc.render.fps
sc.frame_start = 0
sc.frame_end = 100

# CCode to get polar decomposition
# from numpy import array
# from scipy.linalg import polar
# a = array([[1,-1], [2,4]])
# u,p = polar(a)
# u

# plant = { "parent":{}, "children":[], "name":"Root0", "x":ob.location, "q":Vector(0.0, 0.0, 1.0), "v":Vector(0.0, 0.0, 0.0), "w":Vector(0.0, 0.0, 0.0), "abc":ob.scale }
accel_g = Vector((0.0,0.0,-10))
plant = { 'name':'root_0' }

sc.frame_current = 0
ops.mesh.primitive_uv_sphere_add()
ops.object.shade_smooth()
# ops.transform.translate(value=(0,0,1))
ops.transform.resize(value=(1,1,2))
ops.anim.keyframe_insert_menu(type='Location')
ops.anim.keyframe_insert_menu(type='Rotation')
# ops.anim.keyframe_insert_menu(type='Scaling')
# bpy.ops.anim.keyframe_delete(type='Rotation')

ob = ctx.active_object
ob.name = plant['name']
plant['abc'] = ob.scale
plant['x'] = ob.location
plant['v'] = Vector((0.0, 0.0, 10.0))
# plant['q'] = Vector((0.0, 0.0, 1.0))
plant['q'] = Quaternion((0.0, 0.0, 0.0, 1.0))
plant['w'] = Vector((1.0, 0.0, 0.0))
plant['accel_e'] = Vector((0.0, 0.0, 0.0))

frame_step = 1; loop_num = 1
sc.frame_current = loop_num*frame_step
while sc.frame_current <= sc.frame_end:
	# plant["x"] = plant["x"] + 
	delta_x = (plant["v"]*delta_t) + ((accel_g + plant['accel_e'])*delta_t*delta_t/2)
	plant['x'] += delta_x
	plant['v'] = delta_x / delta_t
	wq = Quaternion(plant['w'][:], plant['w'].length)
	wqI = wq.copy()
	wqI.invert()
	q_w = wq * plant['q'] * wqI

	ops.object.select_pattern(pattern=plant['name'])
	# ops.transform.translate(value=(0,0,growth_rate))
	# ops.transform.translate(delta_x)
	ob = ctx.active_object
	ob.location = ob.location + delta_x
	ops.transform.rotate(value=plant['w'].length*delta_t, axis=plant['w'][:])
	# ops.transform.resize(value=(1,1,((loop_num+1)/loop_num)))
	# ob.location = (0,0,2)
	# ob.scale = (1,1,2)
	ops.anim.keyframe_insert_menu(type='Location')
	ops.anim.keyframe_insert_menu(type='Rotation')
	# ops.anim.keyframe_insert_menu(type='Scaling')

	qin = plant['q'].copy()
	qin.invert()
	wnew = q_w * qin
	plant['w'] = wnew.axis * wnew.angle / 2
	plant['q'] = q_w

	loop_num += 1
	sc.frame_current = loop_num*frame_step

sc.frame_current = 0