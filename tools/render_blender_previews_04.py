"""Render seven low-sample draft views from the saved Blender file.
blender --background public/model/palladium_reconstruction_04.blend --python tools/render_blender_previews.py
These are schematic progress previews, not final photorealistic renders.
"""
from pathlib import Path
import bpy
R=Path(__file__).resolve().parent.parent
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=12;scene.cycles.use_denoising=True
scene.render.resolution_x=1600;scene.render.resolution_y=1100;scene.render.resolution_percentage=60;scene.render.image_settings.file_format='PNG'
out=R/'public/model/views_04';out.mkdir(exist_ok=True)
for i,camera,layer in [('01','CAM_01_CONTROL_TOP','CONTROL_TOP_no_decor'),('02','CAM_02_AXON','ViewLayer'),('03','CAM_03_COURTYARD','ViewLayer'),('04','CAM_04_PLAYGROUND','ViewLayer'),('05','CAM_05_CENTRE','ViewLayer'),('06','CAM_06_SHEVCHENKO','ViewLayer'),('07','CAM_07_SHARIPOVA','ViewLayer')]:
 scene.camera=bpy.data.objects[camera];scene.render.filepath=str(out/f'{i}.png')
 bpy.ops.render.render(write_still=True,layer=layer)
 print('RENDERED',scene.render.filepath,flush=True)
