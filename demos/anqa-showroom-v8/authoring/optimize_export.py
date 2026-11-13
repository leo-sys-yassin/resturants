import bpy
from pathlib import Path
r=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(r/'authoring/work/architecture-baked.blend'))
o=bpy.data.objects['ANQA_baked_architecture'];glow=[i for i,m in enumerate(o.data.materials) if 'glow' in m.name]
if glow:
 first=glow[0];o.data.materials[first].name='LED_Diffuser_glow'
 for f in o.data.polygons:
  if f.material_index in glow:f.material_index=first
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
bpy.ops.export_scene.gltf(filepath=str(r/'assets/architecture.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_texcoords=True)
print('Merged repeated LED materials into one render batch')
