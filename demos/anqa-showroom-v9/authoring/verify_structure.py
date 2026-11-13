import bpy,json,bmesh
from pathlib import Path
from mathutils import Vector
p=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(p/'authoring/work/architecture.blend'))
shelves=[o for o in bpy.data.objects if o.name.startswith('Matte black steel shoe shelf')]
assert len(shelves)==12
assert all(abs(o.dimensions.x-.55)<.002 for o in shelves)
assert all(any(a.name.startswith('Shelf welded wall bracket') and abs(a.location.z-(s.location.z-.0275))<.003 and abs(a.location.y-s.location.y)<.8 for a in bpy.data.objects) for s in shelves)
posts=[o for o in bpy.data.objects if o.name.startswith('Open black upright')]
for o in posts:
 lo=min((o.matrix_world@Vector(c)).z for c in o.bound_box);assert abs(lo+.01)<.001,(o.name,lo)
legs=[o for o in bpy.data.objects if o.name.startswith('Bench leg')]
for o in legs:assert min((o.matrix_world@v.co).z for v in o.data.vertices)<=-.009
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(p/'assets/architecture.glb'))
contact=0
for o in list(bpy.context.scene.objects):
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00005);bm.to_mesh(o.data);bm.free()
 for slot in o.material_slots:
  if slot.material and slot.material.name.split('.')[0] in ['BlackSteel','DarkRecess']:
   adj={}
   for f in o.data.polygons:
    if o.material_slots[f.material_index].material!=slot.material:continue
    for i in f.vertices:adj.setdefault(i,set()).update(f.vertices)
   seen=set()
   for first in adj:
    if first in seen:continue
    stack=[first];seen.add(first);points=[]
    while stack:
     v=stack.pop();points.append(o.matrix_world@o.data.vertices[v].co)
     for n in adj[v]:
      if n not in seen:seen.add(n);stack.append(n)
    lo=min(v.z for v in points);hi=max(v.z for v in points)
    if hi<.10 and lo<.001 and hi>lo+.005:
     assert abs(lo+.010)<.001,(lo,hi);contact+=1
assert contact>=5,contact
(p/'structure-verification.json').write_text(json.dumps({'shoe_shelves_aligned_and_bracketed':len(shelves),'floor_resting_frame_posts':len(posts),'bench_legs_reach_floor':len(legs),'exported_foundation_components_contact_floor':contact},indent=2));print('STRUCTURE PASS',contact)
