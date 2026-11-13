import bpy,json
from pathlib import Path
p=Path(__file__).resolve().parents[1]
protected=['Ceiling','Ceiling recess','Continuous ceiling light','Recessed linear LED channel','Diffused ceiling LED','Long soft ceiling wash','Broad linear ambient']
def collect(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));out={}
 for o in bpy.context.scene.objects:
  if any(o.name==n or o.name.startswith(n+'.') for n in protected):
   out[o.name]={'type':o.type,'position':list(o.location),'dimensions':list(o.dimensions)}
   if o.type=='LIGHT':out[o.name]['light']=[o.data.energy,list(o.data.color),o.data.size,o.data.size_y]
 return out
old=collect(p.with_name('anqa-showroom-v9')/'authoring/work/architecture.blend');new=collect(p/'authoring/work/architecture.blend')
assert old.keys()==new.keys()
for name,a in old.items():
 b=new[name];assert a['type']==b['type'];assert abs(a['position'][2]-b['position'][2])<.001
 assert abs((b['position'][1]-a['position'][1])-.8)<.001
 if name=='Ceiling':
  assert abs(b['dimensions'][0]-a['dimensions'][0]-.8)<.002
 else:
  assert abs(b['position'][0]-a['position'][0])<.001 if abs(a['position'][0])<2 else abs(abs(b['position'][0])-abs(a['position'][0])-.4)<.001
 if a['type']=='LIGHT':
  assert a['light'][:3]==b['light'][:3];assert abs(b['light'][3]-a['light'][3]-1.6)<.001
 else:assert abs(b['dimensions'][1]-a['dimensions'][1]-1.6)<.002
(p/'ceiling-verification.json').write_text(json.dumps({'same_design_and_strip_count':True,'extension_only_for_larger_room':True,'protected_count':len(new),'ceiling':new},indent=2));print('CEILING DESIGN PRESERVED',len(new))
