import bpy
from pathlib import Path
r=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(r/'authoring/work/architecture-baked.blend'))
o=bpy.data.objects['ANQA_baked_architecture']
# Close sub-centimetre foundation clearances while keeping all furniture tops and placement.
# Components retain independent topology after joining. Only recessed plinth/plate components are touched.
black_indices={i for i,m in enumerate(o.data.materials) if m.name in {'BlackSteel','DarkRecess'}}
adj={}
for face in o.data.polygons:
 if face.material_index not in black_indices:continue
 for v in face.vertices:adj.setdefault(v,set()).update(face.vertices)
seen=set();grounded=0
for first in adj:
 if first in seen:continue
 stack=[first];component=[];seen.add(first)
 while stack:
  v=stack.pop();component.append(v)
  for n in adj[v]:
   if n not in seen:seen.add(n);stack.append(n)
 lo=min((o.matrix_world@o.data.vertices[i].co).z for i in component);hi=max((o.matrix_world@o.data.vertices[i].co).z for i in component)
 if -.009<lo<.001 and hi<.10 and hi>lo+.005:
  for i in component:
   v=o.data.vertices[i];world=o.matrix_world@v.co;world.z=hi+(world.z-hi)*(hi+.010)/(hi-lo);v.co=o.matrix_world.inverted()@world
  grounded+=1
print('Floor-contact corrections:',grounded)
for ceiling in [False,True]:
 glow=[i for i,m in enumerate(o.data.materials) if 'glow' in m.name and ('ceiling' in m.name.lower())==ceiling]
 if glow:
  first=glow[0];o.data.materials[first].name='LED_Diffuser_glow' if ceiling else 'WarmLED_Diffuser_glow'
  for f in o.data.polygons:
   if f.material_index in glow:f.material_index=first
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
bpy.ops.export_scene.gltf(filepath=str(r/'assets/architecture.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_texcoords=True)
print('Merged LED diffusers by ceiling/furniture color temperature')
