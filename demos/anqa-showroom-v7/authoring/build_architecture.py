import bpy, math, os, sys, json
from mathutils import Vector
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; A=ROOT/'assets'; WORK=Path(__file__).resolve().parent/'work'
WORK.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
S=bpy.context.scene;S.render.engine='CYCLES';S.cycles.samples=16;S.cycles.use_denoising=False;S.cycles.max_bounces=5;S.cycles.diffuse_bounces=3;S.cycles.glossy_bounces=3
S.render.threads_mode='FIXED';S.render.threads=6
S.world.use_nodes=True;S.world.node_tree.nodes['Background'].inputs[0].default_value=(.76,.81,.88,1);S.world.node_tree.nodes['Background'].inputs[1].default_value=.35
S.view_settings.view_transform='AgX'
static=[];emissions=[]
def V(p):return Vector((p[0],-p[2],p[1]))
def mat(name,color,rough=.7,tex=None,scale=1):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough
 if tex:
  co=n.new('ShaderNodeTexCoord');mapping=n.new('ShaderNodeVectorMath');mapping.operation='SCALE';mapping.inputs[3].default_value=scale;l.new(co.outputs['Object'],mapping.inputs[0]);co.object=origin
  for suffix,socket,colorspace in [('color','Base Color','sRGB'),('rough','Roughness','Non-Color')]:
   path=A/f'{tex}-{suffix}.jpg'
   if not path.exists():continue
   im=n.new('ShaderNodeTexImage');im.image=bpy.data.images.load(str(path),check_existing=True);im.image.colorspace_settings.name=colorspace;im.projection='BOX';im.projection_blend=.2;l.new(mapping.outputs[0],im.inputs[0]);l.new(im.outputs['Color'],p.inputs[socket])
 return m
origin=bpy.data.objects.new('World texture scale',None);S.collection.objects.link(origin)

plaster=mat('OakWall',(.25,.12,.055),.54,'oak',.65)
wood=mat('OakBody',(.25,.12,.055),.54,'oak',.65)
stone=mat('FloorStone',(1,1,1),.65)
n=stone.node_tree.nodes;l=stone.node_tree.links;im=n.new('ShaderNodeTexImage');im.image=bpy.data.images.load(str(A/'floor-color.png'));co=n.new('ShaderNodeTexCoord');im.projection='BOX';im.projection_blend=.2;l.new(co.outputs['Generated'],im.inputs[0]);l.new(im.outputs['Color'],n.get('Principled BSDF').inputs['Base Color'])
travertine=mat('CabinetStone',(1.5,1.4,1.2),.60,'cabinet',.65)
bronze=mat('Bronze',(.055,.043,.032),.32);bronze.node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value=.82
dark=mat('DarkRecess',(.015,.012,.009),.78)
fabric=mat('Upholstery',(.55,.48,.38),.95)
white=mat('WhiteCeiling',(.54,.49,.41),.85)
black=mat('BlackSteel',(.015,.016,.014),.38);black.node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value=.65
# Tint the measured oak to the requested dark brown finish while retaining its grain.
for m in [plaster,wood,travertine]:
 n=m.node_tree.nodes;l=m.node_tree.links;pbr=n.get('Principled BSDF');src=pbr.inputs['Base Color'].links[0].from_socket;l.remove(pbr.inputs['Base Color'].links[0]);mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=(*((.25,.12,.055) if m!=travertine else (1.5,1.4,1.2)),1);l.new(src,mix.inputs[1]);l.new(mix.outputs[0],pbr.inputs['Base Color'])
def finish(o,name,m,bevel=0,bake=True):
 o.name=name;o.data.materials.append(m)
 if bevel:
  mod=o.modifiers.new('Small real edge radius','BEVEL');mod.width=bevel;mod.segments=3
  bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
  mod=o.modifiers.new('Weighted surface normals','WEIGHTED_NORMAL');mod.keep_sharp=True;bpy.ops.object.modifier_apply(modifier=mod.name)
 if bake:static.append(o)
 return o
def box(name,size,pos,m=plaster,bevel=.008):
 bpy.ops.mesh.primitive_cube_add(size=1,location=V(pos));o=bpy.context.object;o.scale=(size[0],size[2],size[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,name,m,bevel)
def tube(name,a,b,r=.014,m=bronze):
 av,bv=V(a),V(b);bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=r,depth=(bv-av).length,location=(av+bv)/2);o=bpy.context.object;o.rotation_euler=(bv-av).to_track_quat('Z','Y').to_euler();return finish(o,name,m,.002)
def area(name,pos,target,power,size,color=(1,.82,.60),size_y=None):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.color=color;d.shape='RECTANGLE' if size_y else 'DISK';d.size=size
 if size_y:d.size_y=size_y
 o=bpy.data.objects.new(name,d);S.collection.objects.link(o);o.location=V(pos);o.rotation_euler=(V(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
def led(name,size,pos,power=3):
 m=bpy.data.materials.new(name+' glow');m.use_nodes=True;n=m.node_tree.nodes;p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=(1,.83,.57,1);p.inputs['Emission Color'].default_value=(1,.77,.43,1);p.inputs['Emission Strength'].default_value=power
 o=box(name,size,pos,m,.002);return o
# Floors: individual 1.2 m slabs with millimetre joints, bevelled edges.
for ix in range(-4,4):
 for iz in range(-3,7):box('Limestone floor slab',(1.196,.09,1.196),(ix*1.2+.6,-.055,iz*1.2+.6),stone,.002)
box('Left wall',(.24,3.4,7.9),(-3.12,1.7,1.05));box('Right wall',(.24,3.4,7.9),(3.12,1.7,1.05));box('Back wall',(6.4,3.4,.22),(0,1.7,-2.91));box('Ceiling',(6.3,.2,7.9),(0,3.5,1.05),white)
# Thin skirting and recessed perimeter shadow lines.
for x in [-2.985,2.985]:box('Stone skirting',(.025,.10,7.6),(x,.055,1),stone,.004)
# Footwear wall: three deep, softly lit walnut niches, rounded limestone shelves.
for k in range(3):
 z=-1.85+k*1.85
 box('Walnut niche backing',(.035,2.63,1.60),(-2.985,1.60,z),wood)
 for dz in [-.845,.845]:box('Plaster niche pier',(.40,3.20,.13),(-2.83,1.60,z+dz))
 box('Niche upper lintel',(.44,.24,1.78),(-2.82,3.07,z));box('Floating cabinet',(.48,.30,1.66),(-2.76,.23,z),wood,.015)
 # Drawer fronts and shadow reveal.
 box('Drawer shadow',(.01,.004,1.60),(-2.51,.22,z),dark,.001)
 for y in [.70,1.30,1.90,2.50]:
  box('Smooth stone shoe shelf',(.55,.045,1.62),(-2.72,y,z),travertine,.007);led('Under shelf strip',(.015,.008,1.50),(-2.47,y-.027,z),2)
  area('Shelf wall wash',(-2.56,y-.05,z),(-2.99,y-.30,z),8,1.4,(1,.80,.58),.07)
# New right wall — three actual cabinets matching PDF proportions, replacing all old furniture.
bays=[(-2.55,.25),(.50,3.20),(3.25,4.20)]
for i,(a,b) in enumerate(bays):
 z=(a+b)/2;length=b-a
 box('Reference travertine backing',(.085,3.15,length),(2.96,1.60,z),plaster,.006)
 for zz in [a,b]:

  for xx in [2.4725,2.9475]:box('Open black upright',(.045,3.10,.045),(xx,1.60,zz),black,.003)
  for yy in [.0725,3.1275]:box('Black frame cross member',(.52,.045,.045),(2.71,yy,zz),black,.003)
 box('Steel upper frame',(.52,.045,length),(2.71,3.13,z),black,.004)
 box('Display upper shelf',(.54,.07,length-.04),(2.69,2.84 if i<2 else 2.77,z),black,.006)
 rail_y=2.63 if i<2 else 2.55
 tube('Black continuous hanging rail',(2.40,rail_y,a+.06),(2.40,rail_y,b-.06),.018,black)
 for zz in [a+.07,b-.07]:tube('Rail bracket',(2.40,rail_y,zz),(2.90,rail_y,zz),.012,black)
 shelf_y=1.10 if i<2 else .09
 box('Lower black display shelf',(.54,.065,length-.04),(2.69,shelf_y,z),black,.005)
 led('Warm top niche LED',(.018,.009,length-.12),(2.84,3.065,z),3)
 area('Warm niche wash',(2.70,3.03,z),(2.95,1.6,z),32,length-.12,(1,.82,.59),.10)
 if i<2:
  box('Stone lower cabinet',(.55,.47,length),(2.70,.32,z),travertine,.008)
  box('Stone cabinet countertop',(.59,.045,length+.02),(2.68,.58,z),travertine,.006)
  box('Cabinet recessed toe',(.43,.06,length-.06),(2.77,.045,z),dark,.003)
  for j in range(2):
   box('Travertine drawer front',(.025,.42,length/2-.012),(2.412,.32,a+length*(j+.5)/2),travertine,.003)
  led('Lower shelf LED',(.018,.008,length-.10),(2.47,1.06,z),3)
  area('Under shelf stone wash',(2.5,1.03,z),(2.94,.67,z),14,length-.12,(1,.82,.60),.08)
  led('Floating cabinet LED',(.016,.008,length-.10),(2.50,.076,z),3)
# The narrow cabinet retains its full-height open bay, as in the supplied reference.
# Rear sealed expansion doorway and architectural signature.
box('Rear door recess',(2.08,2.88,.14),(0,1.44,-2.76),dark)
for x in [-1.015,1.015]:box('Door jamb',(.055,2.83,.16),(x,1.42,-2.65),bronze,.004)
box('Rear expansion door',(1.94,2.75,.08),(0,1.40,-2.66),wood,.01)
box('Rear door shadow gap',(.006,2.68,.012),(0,1.40,-2.61),dark,.001)
tube('Door handle',(.76,1.02,-2.57),(.76,1.39,-2.57),.012)
for y in [.65,1.23,1.81,2.39]:
 box('Accessory shelf',(1.43,.04,.45),(2.04,y,-2.57),travertine,.007);led('Accessory shelf light',(1.32,.009,.012),(2.04,y-.025,-2.36),3)
 area('Accessory wash',(2.04,y-.06,-2.4),(2.04,y-.33,-2.87),6,1.2,(1,.8,.58),.08)
area('Signature wall wash',(-1.99,2.8,-2.40),(-1.99,1.9,-2.9),28,1.3,(1,.83,.64),.10)
# Forward island: thick honed stone on a recessed fluted walnut plinth.
box('Island plinth',(1.20,.11,.85),(0,.06,.75),dark,.025)
box('Island walnut body',(1.33,.55,.93),(0,.365,.75),wood,.025)
for x in [-.60+i*.06 for i in range(21)]:box('Fluted oak face',(.033,.51,.028),(x,.37,1.225),wood,.010)
box('Monolithic stone island',(1.55,.16,1.12),(0,.72,.75),travertine,.035)
box('Island top inset',(1.43,.015,1.0),(0,.805,.75),travertine,.008)
# Bench: soft cushion, upholstered seam, slim bronze base.
box('Bench seat',(1.30,.23,.62),(-1.75,.48,-1.60),fabric,.09)
box('Bench seat piping',(1.29,.012,.61),(-1.75,.51,-1.60),white,.006)
for x in [-2.27,-1.23]:
 for z in [-1.82,-1.38]:tube('Bench leg',(x,.04,z),(x,.37,z),.016)
# Ceiling cove built with a real recess and soft indirect bounce.
for x in [-2.56,2.56]:
 box('Ceiling recess',(.20,.025,7.55),(x,3.382,1),dark,.003)
 led('Continuous ceiling light',(.045,.012,7.42),(x,3.36,1),5)
 area('Long soft ceiling wash',(x,3.32,1),(x*.8,1.5,1),170,.15,(1,.86,.70),7.3)
box('Black ceiling track',(.055,.045,6.4),(0,3.365,1),dark,.004)
for z in [-1.85,-.45,1.05,2.55,3.85]:
 tube('Track spotlight',(0,3.33,z),(0,3.18,z),.042,dark)
 led('Spot lens',(.055,.007,.055),(0,3.10,z),5)
 area('Downlight',(0,3.13,z),(0,0,z),24,.10,(1,.87,.72))
# Facade carved out of one solid stone mass, including rounded opening.
def arch_shape(w,h,r):
 pts=[(-w,-.3),(w,-.3),(w,h-r)]
 for i in range(1,17):
  a=(i/16)*math.pi/2;pts.append((w-r+r*math.cos(a),h-r+r*math.sin(a)))
 pts.append((-w+r,h))
 for i in range(1,17):
  a=math.pi/2+(i/16)*math.pi/2;pts.append((-w+r+r*math.cos(a),h-r+r*math.sin(a)))
 return pts
def prism(name,pts,z0,z1,m):
 n=len(pts);vs=[V((x,y,z)) for z in [z0,z1] for x,y in pts];faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];me=bpy.data.meshes.new(name);me.from_pydata(vs,[],faces);me.update();o=bpy.data.objects.new(name,me);S.collection.objects.link(o);o.data.materials.append(m);return o
# Exterior facade is an actual extruded opening built at runtime, with photo-projected stone only.
box('Upper entrance step',(5.6,.11,.65),(0,-.02,5.42),stone,.012);box('Lower entrance step',(5.9,.09,.68),(0,-.10,6.02),stone,.012)
# Frontside reflection panels are outside the walking path and add plausible daylight gradients.
area('Daylight',(0,5.5,9),(0,1.4,2),700,6,(.91,.95,1),5)
area('Entrance fill',(-5,3.8,6),(0,1.7,3),220,4,(1,.94,.85),3)
# Quality preview camera.
bpy.ops.object.camera_add(location=V((0,1.75,12.5)));cam=bpy.context.object;cam.rotation_euler=(V((0,1.7,4.7))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=30;S.camera=cam;S.render.resolution_x=1200;S.render.resolution_y=800;S.render.resolution_percentage=100
# The exterior and interior share one packed UV atlas; render first for lighting review.
bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'architecture.blend'))
if '--preview' in sys.argv:
 S.render.filepath=str(WORK/'architecture-preview.png');bpy.ops.render.render(write_still=True);sys.exit()
# Preserve object/world-based photographed surface mapping while creating a dedicated bake UV.
bpy.ops.object.select_all(action='DESELECT')
for o in static:o.select_set(True)
bpy.context.view_layer.objects.active=static[0];bpy.ops.object.join();mesh=bpy.context.object;mesh.name='ANQA_baked_architecture'
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.004,area_weight=.5);bpy.ops.object.mode_set(mode='OBJECT')
image=bpy.data.images.new('ANQA architectural light and surface',width=4096,height=4096);image.colorspace_settings.name='sRGB'
for m in mesh.data.materials:
 node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=image;m.node_tree.nodes.active=node
S.cycles.samples=16;S.render.bake.use_pass_direct=True;S.render.bake.use_pass_indirect=True;S.render.bake.use_pass_color=False;S.render.bake.margin=12;S.render.bake.use_clear=True
print('BAKE START',flush=True);bpy.ops.object.bake(type='DIFFUSE');image.filepath_raw=str(A/'architecture-irradiance.jpg');image.file_format='JPEG';S.render.image_settings.quality=95;image.save();print('BAKE DONE',flush=True)

# Preserve irradiance UVs on channel 1, independent of high-resolution surface UVs on channel 0.
base=mesh.data.uv_layers.active;light=mesh.data.uv_layers.new(name='IrradianceUV')
for i,d in enumerate(base.data):light.data[i].uv=d.uv.copy()
for face in mesh.data.polygons:
 normal=mesh.matrix_world.to_3x3()@face.normal
 mat_name=mesh.data.materials[face.material_index].name
 for li in face.loop_indices:
  pos=mesh.matrix_world@mesh.data.vertices[mesh.data.loops[li].vertex_index].co
  x,y,z=pos.x,pos.z,-pos.y
  if abs(normal.z)>.7:uv=(x/1.2,z/1.2)
  elif abs(normal.x)>.7:uv=(z/1.2,y/2.4)
  else:uv=(x/1.2,y/2.4)
  base.data[li].uv=uv
mesh.data.uv_layers.active_index=0;base.active_render=True
# Keep semantic materials as simple export markers. Runtime installs measured PBR maps and the irradiance atlas.
for m in mesh.data.materials:
 m.node_tree.nodes.clear();out=m.node_tree.nodes.new('ShaderNodeOutputMaterial');pbr=m.node_tree.nodes.new('ShaderNodeBsdfPrincipled');pbr.inputs['Base Color'].default_value=(.7,.7,.7,1);m.node_tree.links.new(pbr.outputs[0],out.inputs[0])
bpy.ops.export_scene.gltf(filepath=str(A/'architecture.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_texcoords=True)
bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'architecture-baked.blend'))
print('EXPORT DONE',flush=True)
