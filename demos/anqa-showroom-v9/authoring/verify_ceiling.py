import bpy,json,hashlib
from pathlib import Path
p=Path(__file__).resolve().parents[1]
protected=['Ceiling','Ceiling recess','Continuous ceiling light','Recessed linear LED channel','Diffused ceiling LED','Long soft ceiling wash','Broad linear ambient']
def signature(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));result={}
 for o in bpy.context.scene.objects:
  if any(o.name==n or o.name.startswith(n+'.') for n in protected):
   item={'type':o.type,'matrix':[list(r) for r in o.matrix_world],'dimensions':list(o.dimensions)}
   if o.type=='MESH':item['mesh']=hashlib.sha256(str(([list(v.co) for v in o.data.vertices],[list(f.vertices) for f in o.data.polygons])).encode()).hexdigest()
   elif o.type=='LIGHT':item['light']=[o.data.type,o.data.energy,list(o.data.color),o.data.shape,o.data.size,o.data.size_y]
   result[o.name]=item
 return result
old=signature(p.with_name('anqa-showroom-v8')/'authoring/work/architecture.blend');new=signature(p/'authoring/work/architecture.blend')
assert old==new, [k for k in old if old[k]!=new.get(k)]
(p/'ceiling-verification.json').write_text(json.dumps({'matches_v8_exactly':True,'protected_objects':old},indent=2));print('CEILING IDENTICAL',len(old),flush=True)
