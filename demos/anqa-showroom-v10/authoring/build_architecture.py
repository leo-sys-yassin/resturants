import bpy, math, os, sys, json
from mathutils import Vector
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; A=ROOT/'assets'; WORK=Path(__file__).resolve().parent/'work'
WORK.mkdir(exist_ok=True)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
S=bpy.context.scene;S.render.engine='CYCLES';S.cycles.samples=16;S.cycles.use_denoising=False;S.cycles.max_bounces=5;S.cycles.diffuse_bounces=3;S.cycles.glossy_bounces=3
S.render.threads_mode='FIXED';S.render.threads=6
S.world.use_nodes=True;S.world.node_tree.nodes['Background'].inputs[0].default_value=(.76,.81,.88,1);S.world.node_tree.nodes['Background'].inputs[1].default_value=.27
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


plaster=mat('WarmPlaster',(.624,.462,.319),.9,'plaster',.65)
n=plaster.node_tree.nodes;l=plaster.node_tree.links;pbr=n.get('Principled BSDF');src=pbr.inputs['Base Color'].links[0].from_socket;l.remove(pbr.inputs['Base Color'].links[0]);tint=n.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1;tint.inputs[2].default_value=(.624,.462,.319,1);l.new(src,tint.inputs[1]);l.new(tint.outputs[0],pbr.inputs['Base Color'])
wood=mat('WalnutSurface',(1,1,1),.72,'walnut',.65)
stone=mat('FloorStone',(1,1,1),.72)
n=stone.node_tree.nodes;l=stone.node_tree.links;im=n.new('ShaderNodeTexImage');im.image=bpy.data.images.load(str(A/'floor-color.png'));co=n.new('ShaderNodeTexCoord');im.projection='BOX';im.projection_blend=.2;l.new(co.outputs['Generated'],im.inputs[0]);l.new(im.outputs['Color'],n.get('Principled BSDF').inputs['Base Color'])
travertine=wood
black=mat('BlackSteel',(.018,.019,.019),.91);black.node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value=.12
bronze=black
dark=mat('DarkRecess',(.015,.014,.012),.9)
fabric=mat('Upholstery',(.55,.48,.38),.95)
white=mat('GreigeCeiling',(.34,.32,.285),.95)
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
def area(name,pos,target,power,size,color=(1,.94,.86),size_y=None):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.color=color;d.shape='RECTANGLE' if size_y else 'DISK';d.size=size
 if size_y:d.size_y=size_y
 o=bpy.data.objects.new(name,d);S.collection.objects.link(o);o.location=V(pos);o.rotation_euler=(V(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
def led(name,size,pos,power=3):
 led_color=(1,.94,.83,1) if 'ceiling' in name.lower() else (1,.695,.431,1)
 m=bpy.data.materials.new(name+' glow');m.use_nodes=True;n=m.node_tree.nodes;p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=led_color;p.inputs['Emission Color'].default_value=led_color;p.inputs['Emission Strength'].default_value=power
 o=box(name,size,pos,m,.002);return o
# Floors: individual 1.2 m slabs with millimetre joints, bevelled edges.
for ix in range(-4,4):
 for iz in range(-5,7):box('Limestone floor slab',(1.196,.09,1.196),(ix*1.2+.6,-.055,iz*1.2+.6),stone,.002)
box('Left wall',(.24,3.4,9.5),(-3.52,1.7,.25));box('Right wall',(.24,3.4,9.5),(3.52,1.7,.25));box('Back wall',(7.2,3.4,.22),(0,1.7,-4.51));box('Ceiling',(7.1,.2,9.5),(0,3.5,.25),white)
# Thin skirting and recessed perimeter shadow lines.
for x in [-3.385,3.385]:box('Stone skirting',(.025,.10,9.2),(x,.055,.2),stone,.004)
# Footwear wall: three deep, softly lit walnut niches, rounded limestone shelves.
left_zone=set(S.objects)
for k in range(3):
 z=-3.25+k*2.4
 box('Walnut niche backing',(.035,2.63,1.95),(-2.985,1.60,z),plaster)
 for dz in [-1.02,1.02]:box('Walnut niche pier',(.40,3.20,.13),(-2.83,1.60,z+dz),wood)
 box('Niche upper lintel',(.44,.24,2.17),(-2.82,3.07,z),wood);box('Footwear base cabinet',(.48,.30,2.04),(-2.76,.23,z),wood,.015)
 box('Footwear recessed floor plinth',(.40,.09,1.88),(-2.80,.035,z),black,.004)
 # Drawer fronts and shadow reveal.
 box('Drawer shadow',(.01,.004,1.98),(-2.51,.22,z),dark,.001)
 for y in [.70,1.30,1.90,2.50]:
  box('Matte black steel shoe shelf',(.55,.030,2.0),(-2.72,y,z),black,.004);led('Under shelf strip',(.015,.008,1.88),(-2.47,y-.018,z),2)
  for zz in [z-.78,z+.78]:
   box('Shelf welded wall bracket',(.50,.025,.035),(-2.735,y-.0275,zz),black,.003)
   box('Shelf wall mounting plate',(.024,.13,.075),(-2.956,y-.06,zz),black,.002)
  area('Shelf wall wash',(-2.56,y-.05,z),(-2.99,y-.30,z),12,1.75,(1,.695,.431),.07)
for o in set(S.objects)-left_zone:o.location.x-=.4
# New right wall — three actual cabinets matching PDF proportions, replacing all old furniture.
right_zone=set(S.objects)
bays=[(-3.25,.25),(.50,3.20),(3.50,4.40)]
for i,(a,b) in enumerate(bays):
 z=(a+b)/2;length=b-a
 box('Reference travertine backing',(.085,3.15,length),(2.96,1.60,z),plaster,.006)
 for zz in [a,b]:

  for xx in [2.4725,2.9475]:box('Open black upright',(.045,3.18,.045),(xx,1.58,zz),black,.003)
  for yy in [.0725,3.1275]:box('Black frame cross member',(.52,.045,.045),(2.71,yy,zz),black,.003)
 for zz in [a,b]:
  box('Frame floor plate',(.11,.022,.11),(2.4725,.001,zz),black,.003)
  for yy in [.32,2.99]:box('Frame wall fixing',(.065,.05,.045),(2.9725,yy,zz),black,.002)
 box('Steel upper frame',(.52,.045,length),(2.71,3.13,z),black,.004)
 box('Display upper shelf',(.54,.07,length-.04),(2.69,2.84 if i<2 else 2.77,z),black,.006)
 rail_y=2.63 if i<2 else 2.55
 tube('Black continuous hanging rail',(2.40,rail_y,a+.025),(2.40,rail_y,b-.025),.018,black)
 for zz in [a+.025,b-.025]:tube('Rail bracket',(2.40,rail_y,zz),(2.96,rail_y,zz),.012,black)
 shelf_y=1.10 if i<2 else .09
 box('Lower black display shelf',(.54,.065,length-.04),(2.69,shelf_y,z),black,.005)
 led('Warm top niche LED',(.018,.009,length-.12),(2.84,3.065,z),3)
 area('Warm niche wash',(2.70,3.03,z),(2.95,1.6,z),45,length-.12,(1,.695,.431),.10)
 if i<2:
  box('Stone lower cabinet',(.55,.47,length),(2.70,.32,z),travertine,.008)
  box('Stone cabinet countertop',(.59,.045,length+.02),(2.68,.58,z),travertine,.006)
  box('Cabinet recessed toe',(.43,.095,length-.06),(2.77,.0375,z),dark,.003)
  for j in range(2):
   box('Travertine drawer front',(.025,.42,length/2-.012),(2.412,.32,a+length*(j+.5)/2),travertine,.003)
  led('Lower shelf LED',(.018,.008,length-.10),(2.47,1.06,z),3)
  area('Under shelf stone wash',(2.5,1.03,z),(2.94,.67,z),14,length-.12,(1,.695,.431),.08)
  led('Floating cabinet LED',(.016,.008,length-.10),(2.50,.076,z),3)
# The narrow cabinet retains its full-height open bay, as in the supplied reference.
for o in set(S.objects)-right_zone:o.location.x+=.4
# Rear sealed expansion doorway and architectural signature.
rear_zone=set(S.objects)
box('Rear door recess',(2.08,2.88,.14),(0,1.44,-2.76),dark)
for x in [-1.015,1.015]:box('Door jamb',(.055,2.83,.16),(x,1.42,-2.65),bronze,.004)
box('Rear expansion door',(1.94,2.75,.08),(0,1.40,-2.66),plaster,.01)
box('Rear door shadow gap',(.006,2.68,.012),(0,1.40,-2.61),dark,.001)
tube('Door handle',(.76,1.02,-2.57),(.76,1.39,-2.57),.012)
for y in [.65,1.23,1.81,2.39]:
 for xx in [1.54,2.54]:
  box('Accessory concealed shelf arm',(.028,.025,.38),(xx,y-.03,-2.61),black,.002)
  box('Accessory wall plate',(.065,.12,.02),(xx,y-.07,-2.79),black,.002)
 box('Accessory shelf',(1.43,.04,.45),(2.04,y,-2.57),travertine,.007);led('Accessory shelf light',(1.32,.009,.012),(2.04,y-.025,-2.36),3)
 area('Accessory wash',(2.04,y-.06,-2.4),(2.04,y-.33,-2.87),6,1.2,(1,.695,.431),.08)
area('Signature wall wash',(-1.99,2.8,-2.40),(-1.99,1.9,-2.9),28,1.3,(1,.695,.431),.10)
for o in set(S.objects)-rear_zone:
 o.location.y+=1.6
 if o.name.startswith('Accessory'):o.location.x+=.2
 if o.name.startswith('Signature'):o.location.x-=.23
# Enlarged central display: structural walnut top, recessed frame and continuous warm underside LEDs.
box('Island plinth',(1.38,.15,.98),(0,.065,.75),dark,.025)
box('Island walnut body',(1.52,.55,1.08),(0,.405,.75),wood,.025)
for x in [-.68+i*.068 for i in range(21)]:box('Fluted walnut face',(.035,.51,.028),(x,.41,1.30),wood,.010)
box('Walnut island top',(1.80,.12,1.28),(0,.74,.75),wood,.025)
for x in [-.80,.80]:
 box('Island LED aluminum channel',(.020,.008,1.10),(x,.676,.75),black,.002)
 led('Island under top LED',(.012,.006,1.08),(x,.670,.75),2.0)
 area('Island soft downward wash',(x,.662,.75),(x*.88,.18,.75),6,.025,(1,.695,.431),1.04)
for z in [.19,1.31]:
 box('Island LED end channel',(1.60,.008,.020),(0,.676,z),black,.002)
 led('Island underside end LED',(1.58,.006,.012),(0,.670,z),2.0)
 area('Island end soft wash',(0,.662,z),(0,.17,.75+(z-.75)*.9),5,1.5,(1,.695,.431),.025)
# Bench: soft cushion, upholstered seam, slim bronze base.
bench_zone=set(S.objects)
box('Bench seat',(1.30,.23,.62),(-1.75,.48,-1.60),fabric,.09)
box('Bench seat piping',(1.29,.012,.61),(-1.75,.51,-1.60),white,.006)
for x in [-2.27,-1.23]:
 for z in [-1.82,-1.38]:tube('Bench leg',(x,-.01,z),(x,.37,z),.016)
for o in set(S.objects)-bench_zone:o.location.x-=.4;o.location.y+=1.4
# Ceiling cove built with a real recess and soft indirect bounce.
for x in [-2.96,2.96]:
 box('Ceiling recess',(.20,.025,9.15),(x,3.382,.2),dark,.003)
 led('Continuous ceiling light',(.045,.012,9.02),(x,3.36,.2),3)
 area('Long soft ceiling wash',(x,3.32,.2),(x*.8,1.5,.2),190,.15,(1,.94,.86),8.9)
# Two continuous diffused LED lines; no spotlights or track heads.
for x in [-.95,.95]:
 box('Recessed linear LED channel',(.17,.025,8.5),(x,3.375,.2),black,.004)
 led('Diffused ceiling LED',(.12,.009,8.4),(x,3.355,.2),2.5)
 area('Broad linear ambient',(x,3.33,.2),(x,.1,.2),95,.17,(1,.94,.86),8.3)
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
area('Daylight',(0,5.5,9),(0,1.4,2),420,6,(.91,.95,1),5)
area('Entrance fill',(-5,3.8,6),(0,1.7,3),150,4,(1,.94,.85),3)
# Shadow-only wardrobe geometry: not exported, so live garments remain interactive.
for name,z in zip(['coal','wine','oat','forest','sky'],[-2.85,-1.75,-.65,1.0,2.1]):
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(A/(name+'-product.glb')))
 imported=[o for o in bpy.data.objects if o not in before]
 shift=V((2.8,2.63-.464,z))
 for o in imported:
  if o.parent is None:o.location+=shift
# Quality preview camera.
bpy.ops.object.camera_add(location=V((0,1.75,12.5)));cam=bpy.context.object;cam.rotation_euler=(V((0,1.7,4.7))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=30;S.camera=cam;S.render.resolution_x=1200;S.render.resolution_y=800;S.render.resolution_percentage=100
(ROOT/'layout.json').write_text(json.dumps({'objects':[o.name for o in static],'light_types':[o.data.type for o in S.objects if o.type=='LIGHT'],'shelf_material':'BlackSteel','interior_size_m':[6.8,9.5,3.4],'rear_corner_clearance_m':.64,'wall_material':'WarmPlaster','furniture_material':'WalnutSurface'}))
# The exterior and interior share one packed UV atlas; render first for lighting review.
bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'architecture.blend'))
if '--geometry-only' in sys.argv:sys.exit()
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
