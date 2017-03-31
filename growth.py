import bpy
import random
from mathutils import Vector, Euler, Quaternion
from math import pi

ctx = bpy.context
sc = ctx.scene
ops = bpy.ops
dat = bpy.data

sc.cursor_location = Vector((0,0,0))
sc.render.fps = 25
delta_t = 1.0 / sc.render.fps
sc.frame_start = 0
sc.frame_end = 150

growth_z = 0.3
growth_xy = 0.1
smallest_radius_factor = 0.1
largest_xy_radius = 0.1
largest_z_radius = 0.2
default_r = Vector((smallest_radius_factor*largest_xy_radius, smallest_radius_factor*largest_xy_radius, smallest_radius_factor*largest_xy_radius))
delta_z_r = Vector((0, 0, growth_z*largest_z_radius))
delta_xy_r = Vector((growth_xy*largest_xy_radius, growth_xy*largest_xy_radius, 0))

srf_adt_str = 8 # Surface adaptation strength (for apical particles to become parallel to anchor surface)
ptr_res_str = 2 # Phototropism response strength
light_E = 25

b_prob = 0.0 # branching probablity
b_dir_var = pi/3 # branching directional variance in radians

mat = bpy.data.materials.get("Green")
if mat is None:
	# create material
	mat = bpy.data.materials.new(name="Green")
	mat.diffuse_color = Color((0,1,0))

def closest_anchor(v):
	a,b,c,d = bpy.data.objects['Suzanne'].closest_point_on_mesh(bpy.data.objects['Suzanne'].matrix_world.inverted() * v)
	p = bpy.data.objects['Suzanne'].matrix_world * b
	return p

def get_dir(eul):
	# unit = Vector((0,0,1))
	# unit.rotate(eul)
	return eul.to_quaternion() * Vector((0,0,1))

def apply_rot(eul, a1, t1):
	quat = eul.to_quaternion() * Quaternion(a1[:], t1)
	return quat.to_euler()

def apply_rot_2(eul, a1, t1, a2, t2):
	quat = eul.to_quaternion() * Quaternion(a1[:], t1) * Quaternion(a2[:], t2)
	return quat.to_euler()

def get_new_b(p, child_num, branch=False):
	new_plant = { 'depth':p['depth']+1, 'num':child_num, 'children':[], 'parent':p['name'] }
	new_plant['name'] = "root_"+str(new_plant['depth'])+"_"+str(new_plant['num'])
	new_plant['c'] = default_r.z
	new_plant['ab'] = default_r.x
	p['rot'] = bpy.data.objects[p['name']].rotation_euler # just to be safe
	p['loc'] = bpy.data.objects[p['name']].location # just to be safe
	new_plant['loc'] = p['loc'] + (2*p['c']*get_dir(p['rot']))
	if branch==False:
		new_plant['rot'] = p['rot']
	else:# branch==True: # use the divergence and child number to decide direction of child
		omg = (new_plant['loc']-p['loc']).cross(p['loc']-bpy.data.objects[p['parent']].location)
		omg.normalize()
		alp = random.uniform(b_dir_var/2,b_dir_var)
		new_plant['rot'] = apply_rot(p['rot'], omg, alp)
	new_plant['anchor'] = closest_anchor(new_plant['loc'])
	sc.cursor_location = new_plant['loc']
	# ops.object.select_all(action='DESELECT')
	ops.mesh.primitive_uv_sphere_add()

	# ops.object.select_pattern(pattern=new_plant['name'])
	# ob = ctx.active_object

	# print("Hello")

	# ob.scale = default_r
	ops.transform.resize(value=default_r[:])

	ops.object.mode_set(mode='EDIT')
	ops.transform.translate(value=(0,0,default_r.z))
	ops.object.mode_set(mode='OBJECT')
	
	ob = ctx.active_object
	ob.name = new_plant['name']
	ob.rotation_euler = new_plant['rot']
	ob.hide = True
	ob.keyframe_insert(data_path='hide', index=-1, frame=sc.frame_start)
	ob.hide = False
	ob.keyframe_insert(data_path='hide', index=-1, frame=sc.frame_current)
	if bpy.data.objects[new_plant['name']].data.materials:
		bpy.data.objects[new_plant['name']].data.materials[0] = mat
	else:
		bpy.data.objects[new_plant['name']].data.materials.append(mat)
	ops.object.shade_smooth()
	ops.anim.keyframe_insert_menu(type='Location')
	ops.anim.keyframe_insert_menu(type='Rotation')
	ops.anim.keyframe_insert_menu(type='Scaling')
	p['children'].append(new_plant)
	sc.cursor_location = Vector((0,0,0))
	# print(bpy.data.objects[new_plant['parent']].scale, new_plant['depth'], "new")

def grow(p):
	# Change with the change of logic of growth of plant
	ops.object.select_all(action='DESELECT')
	p['rot'] = bpy.data.objects[p['name']].rotation_euler # just to be safe
	p['loc'] = bpy.data.objects[p['name']].location # just to be safe
	
	if p['c'] < largest_z_radius or p['ab'] < largest_xy_radius:
		# ops.object.select_all(action='DESELECT')
		ops.object.select_pattern(pattern=p['name'])
		obj = ctx.active_object
		delta = bpy.data.objects[p['name']].scale.copy()
		rot = bpy.data.objects[p['name']].rotation_euler.copy()
		bpy.data.objects[p['name']].rotation_euler = Euler((0,0,0), 'XYZ')
		# print(delta, p['depth'])
		delta_p = delta.copy()
		if p['c'] < largest_z_radius:
			delta += delta_z_r
			p['c'] += delta_z_r.z
		if p['ab'] < largest_xy_radius:
			delta += delta_xy_r
			# print(obj.scale, p['depth'])
			p['ab'] += delta_xy_r.x
		# print(delta, delta_p, p['depth'], bpy.data.objects[p['name']].location)
		bpy.data.objects[p['name']].scale = delta
		# ops.transform.resize(value=(delta.x/delta_p.x, delta.y/delta_p.y, delta.z/delta_p.z))

		bpy.data.objects[p['name']].rotation_euler = rot
		ops.anim.keyframe_insert_menu(type='Scaling')

	if p['name'] != 'root_0_0':
		parent_s = bpy.data.objects[p['parent']].scale.copy()
		parent_r = bpy.data.objects[p['parent']].rotation_euler.copy()
		parent_l = bpy.data.objects[p['parent']].location.copy()
		parent_h = parent_l + (2*parent_s.z*get_dir(parent_r))

		# 0 < phi < 1 and phi is dependent on mass = volume
		phi = (p['ab']*p['ab']*p['c'])/(largest_xy_radius*largest_xy_radius*largest_z_radius*2)
		d_anchored = phi * (p['anchor'] - p['loc'])
		if d_anchored.length > 0.1:
			# bpy.data.objects[p['name']].location += d_anchored
			# p['loc'] += d_anchored
			parent_dir = 2*parent_s.z*get_dir(parent_r)
			req_anchor = parent_dir + d_anchored
			parent_dir.normalize(); req_anchor.normalize();
			a_n = parent_dir.cross(req_anchor)
			alpha_n = (parent_dir * req_anchor) * phi * 0.05
			new_rot = apply_rot(parent_r, a_n, alpha_n)
			bpy.data.objects[p['parent']].rotation_euler = new_rot
			ops.object.select_pattern(pattern=p['parent'])
			ops.anim.keyframe_insert_menu(type='Rotation')
			ops.object.select_all(action='DESELECT')
			# req_anchor = parent_h + d_anchored
			parent_h = parent_l + (2*parent_s.z*get_dir(new_rot))
			p['anchor'] = closest_anchor(parent_h)

		# if (closest_anchor(parent_h)-p['anchor']).length > 1:
		bpy.data.objects[p['name']].location = parent_h
		p['loc'] = parent_h
		
		ops.object.select_pattern(pattern=p['name'])
		ops.anim.keyframe_insert_menu(type='Location')
		# else:
		# 	parent_h = parent_l + (2*parent_s.z*get_dir(parent_s))
	
	if len(p['children']) == 0: # plant orientation growth
		# surface adaptation
		v_s = p['anchor'] - p['loc']
		v_f = get_dir(p['rot'])
		v_s.normalize(); v_f.normalize();
		a_a = v_s.cross(v_f)
		alpha_a = (v_s * v_f) * srf_adt_str * delta_t
		# phototropism
		v_l = bpy.data.objects['Point'].location.copy()
		d_l = v_l - p['loc']
		radial = d_l.length
		oclusion = light_E/(radial*radial) # not the correct way
		v_l.normalize()
		# a_p = v_l.cross(v_f)
		# alpha_p = (1 - oclusion) * ptr_res_str * delta_t
		a_p = v_f.cross(v_l)
		alpha_p = (v_f * v_l) * ptr_res_str * delta_t
		new_rot = apply_rot_2(p['rot'], a_a, alpha_a, a_p, alpha_p)
		# new_rot = apply_rot(p['rot'], a_a, alpha_a)
		bpy.data.objects[p['name']].rotation_euler = new_rot
		p['rot'] = new_rot
		ops.object.select_pattern(pattern=p['name'])
		ops.anim.keyframe_insert_menu(type='Rotation')

	ops.object.select_all(action='DESELECT')

	if len(p['children']) == 0 and p['c'] >= largest_z_radius:
		# Consider the branching part in this segment
		ops.object.select_pattern(pattern="root_"+str(p['depth']+1)+"_*")
		all_h = len(bpy.context.selected_objects)
		ops.object.select_all(action='DESELECT')
		rand = random.random()
		rand = 1 - rand
		# print(rand)
		if rand < b_prob and p['depth'] > 1:
			for x in range(2):
				get_new_b(p, x+all_h, True)
		else:
			get_new_b(p, 0+all_h)
	elif len(p['children']) > 0 and p['c'] >= largest_z_radius:
		for child in p['children']:
			grow(child)

# ops.mesh.primitive_monkey_add(radius=2)
# bpy.data.objects['Suzanne'].location = Vector((0,2,0))
# ops.object.lamp_add()
# bpy.context.object.data.energy = light_E
# bpy.data.objects['Point'].location = Vector((0,0,5))

plant = { 'depth':0, 'num':0, 'loc':Vector((0,0,0)), 'children':[] }
plant['name'] = "root_"+str(plant['depth'])+"_"+str(plant['num'])
plant['c'] = default_r.z
plant['ab'] = default_r.x
plant['rot'] = Euler((0, 0, 0), 'XYZ')
plant['anchor'] = closest_anchor(plant['loc'])

sc.frame_current = 0

ops.mesh.primitive_uv_sphere_add()
ob = ctx.active_object
ob.name = plant['name']
# ob.scale = default_r
ops.transform.resize(value=default_r[:])
ops.object.mode_set(mode='EDIT')
ops.transform.translate(value=(0,0,default_r.z))
ops.object.mode_set(mode='OBJECT')
ob.rotation_euler = plant['rot']
# ops.transform.rotate(value=pi/3, axis=Vector((1,0,0)))
# bpy.data.objects[plant['name']].data.materials[0] = mat
if bpy.data.objects[plant['name']].data.materials:
	bpy.data.objects[plant['name']].data.materials[0] = mat
else:
	bpy.data.objects[plant['name']].data.materials.append(mat)
ops.object.shade_smooth()
ops.anim.keyframe_insert_menu(type='Location')
ops.anim.keyframe_insert_menu(type='Rotation')
ops.anim.keyframe_insert_menu(type='Scaling')

frame_step = 1; loop_num = 1
sc.frame_current = loop_num*frame_step
while sc.frame_current <= sc.frame_end:
	grow(plant)
	# print(plant, loop_num)
	loop_num += 1
	sc.frame_current = loop_num*frame_step

sc.frame_current = 0
