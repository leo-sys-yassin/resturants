import bpy,bmesh
from pathlib import Path
r=Path(__file__).resolve().parents[1];w=r/'authoring/work'
bpy.ops.wm.open_mainfile(filepath=str(w/'architecture.blend'))
keys=set()
for o in bpy.context.scene.objects:
 if o.name.startswith('Black upright'):
  for v in o.data.vertices:keys.add(tuple(round(c,5) for c in o.matrix_world@v.co))
bpy.ops.wm.open_mainfile(filepath=str(w/'architecture-baked.blend'))
o=bpy.data.objects['ANQA_baked_architecture'];bm=bmesh.new();bm.from_mesh(o.data)
remove=[]
for f in bm.faces:
 if all(tuple(round(c,5) for c in o.matrix_world@v.co) in keys for v in f.verts):remove.append(f)
assert len(remove)>0
bmesh.ops.delete(bm,geom=remove,context='FACES');bm.to_mesh(o.data);bm.free()
bpy.ops.wm.save_as_mainfile(filepath=str(w/'architecture-baked.blend'))
print('Removed slab uprights:',len(remove),'faces; replaced by runtime open metal frames.')
