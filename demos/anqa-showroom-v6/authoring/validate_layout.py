import bpy,json
from pathlib import Path
r=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(r/'authoring/work/architecture.blend'))
names=[o.name for o in bpy.context.scene.objects]
for prefix in ['Clothing walnut base','Clothing panel','Upper four metre shelf','Solid stone storefront']:
 assert not any(n.startswith(prefix) for n in names),prefix
checks={}
for prefix,num in [('Reference travertine backing',3),('Black continuous hanging rail',3),('Stone lower cabinet',2),('Travertine drawer front',4),('Black upright',6)]:
 actual=sum(n.startswith(prefix) for n in names);assert actual==num,(prefix,actual);checks[prefix]=actual
(r/'layout-verification.json').write_text(json.dumps({'reference':'ANQA_wall_design_4_references_UPDATED.pdf, page 4','objects':checks,'old_wall_removed':True,'narrow_bay':'Full-height open metal bay','wide_bays':'Two cabinets, each with two stone drawer faces'},indent=2))
print('Layout verified')
