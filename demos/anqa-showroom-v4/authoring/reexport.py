import bpy
from pathlib import Path
A=Path(__file__).resolve().parents[1]/'assets'
bpy.ops.wm.open_mainfile(filepath=str(Path(__file__).resolve().parent/'work/architecture-baked.blend'))
for image in bpy.data.images:
 if 'ANQA architectural' in image.name:image.filepath=str(A/'architecture-light.jpg');image.reload()
bpy.ops.object.select_all(action='DESELECT');o=bpy.data.objects['ANQA_baked_architecture'];o.select_set(True);bpy.context.view_layer.objects.active=o
bpy.ops.export_scene.gltf(filepath=str(A/'architecture.glb'),export_format='GLB',use_selection=True,export_apply=True,export_image_format='JPEG',export_jpeg_quality=94,export_yup=True)
