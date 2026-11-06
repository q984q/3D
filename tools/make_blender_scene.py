"""Create editable Blender reconstruction. Use Blender 5 in background.
blender --background --python tools/make_blender_scene.py
Images, lights, cameras and all provisional geometry are intentionally editable.
"""
from pathlib import Path
import bpy
from mathutils import Vector
R=Path(__file__).resolve().parent.parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(R/'public/model/palladium_reconstruction_03.glb'))
bpy.context.view_layer.update()
scene=bpy.context.scene
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;scene.unit_settings.length_unit='METERS'
meshes=[o for o in scene.objects if o.type=='MESH']
for ob in meshes:
 matrix=ob.matrix_world.copy();ob.parent=None;ob.matrix_world=matrix
for obj in list(scene.objects):
 if obj.type=='EMPTY':bpy.data.objects.remove(obj,do_unlink=True)
groups={
 '01_Reference_PDF':lambda n:n.startswith('REFERENCE_PDF'),
 '02_Buildings_CONDITIONAL':lambda n:n.startswith('BUILDING_'),
 '03_Vector_fill_GRAPHIC_COLORS':lambda n:n.startswith('PDF_FILL_'),
 '04_Courtyard_partial_INFERRED':lambda n:n.startswith('COURTYARD_PARTIAL_'),
 '05_Central_paving_CONDITIONAL':lambda n:n.startswith('CENTRAL_PAVING_'),
 '06_Edges_CONDITIONAL':lambda n:n.startswith(('CURB_','BED_EDGE_','CENTRAL_RING_')),
 '07_Plants_CONDITIONAL':lambda n:n.startswith(('TREE_SYMBOL_','CENTRAL_PLANT_')),
 '08_Play_markers_CONDITIONAL':lambda n:n.startswith('PLAY_SYMBOL_'),
}
coll={name:bpy.data.collections.new(name) for name in groups}
for c in coll.values():scene.collection.children.link(c)
other=bpy.data.collections.new('09_Other');scene.collection.children.link(other)
for obj in meshes:
 dest=next((coll[k] for k,rule in groups.items() if rule(obj.name)),other)
 for old in list(obj.users_collection):old.objects.unlink(obj)
 dest.objects.link(obj)
rig=bpy.data.collections.new('10_Cameras_and_daylight');scene.collection.children.link(rig)
for c in list(scene.collection.children):
 if c not in list(coll.values()) and c not in (other,rig) and len(c.all_objects)==0:scene.collection.children.unlink(c)
# Blender-only preview colors; not specifications.
exec(compile((R/'tools/apply_preview_materials.py').read_text(),str(R/'tools/apply_preview_materials.py'),'exec'))
# Make raster independent of illumination for comparison; it is not terrain.
ref=next((o for o in meshes if o.name.startswith('REFERENCE_PDF')),None)
if ref and ref.data.materials:
 m=ref.data.materials[0];m.use_nodes=True
 nodes=m.node_tree.nodes;links=m.node_tree.links
 image=next((n for n in nodes if n.type=='TEX_IMAGE'),None);output=next((n for n in nodes if n.type=='OUTPUT_MATERIAL'),None)
 if image and output:
  for l in list(output.inputs['Surface'].links):links.remove(l)
  em=nodes.new('ShaderNodeEmission');em.inputs['Strength'].default_value=.8;links.new(image.outputs['Color'],em.inputs['Color']);links.new(em.outputs['Emission'],output.inputs['Surface'])
light=bpy.data.lights.new('DAYLIGHT_CONDITIONAL','SUN');light.energy=1.4;light.angle=.12
sun=bpy.data.objects.new('DAYLIGHT_CONDITIONAL',light);rig.objects.link(sun);sun.rotation_euler=(.42,-.52,-.45)
scene.world.use_nodes=True
bg=scene.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.72,.78,.85,1);bg.inputs['Strength'].default_value=.55

def camera(name,eye,target,lens,ortho=False):
 data=bpy.data.cameras.new(name);obj=bpy.data.objects.new(name,data);rig.objects.link(obj)
 obj.location=eye;obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
 if ortho:data.type='ORTHO';data.ortho_scale=132
 else:data.lens=lens;data.sensor_width=36
 data.clip_end=1000
 return obj
cams={}
cams['01']=camera('CAM_01_CONTROL_TOP',(63,44.6,230),(63,44.6,0),50,True)
cams['02']=camera('CAM_02_AXON',(150,-70,115),(62,45,0),31.5)
cams['03']=camera('CAM_03_COURTYARD',(62,125,55),(62,68,0),25.9)
cams['04']=camera('CAM_04_PLAYGROUND',(20,100,37),(34,68,0),23.6)
cams['05']=camera('CAM_05_CENTRE',(79,103,35),(53.5,62,0),23.6)
cams['06']=camera('CAM_06_SHEVCHENKO',(62,-38,35),(62,19,0),23.6)
cams['07']=camera('CAM_07_SHARIPOVA',(154,42,32),(105,42,0),23.6)
scene.camera=cams['02'];scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=24;scene.cycles.use_denoising=True
scene.render.resolution_x=1600;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
control=scene.view_layers.new('CONTROL_TOP_no_decor')
for name in ('07_Plants_CONDITIONAL','08_Play_markers_CONDITIONAL'):
 control.layer_collection.children[name].exclude=True
bpy.ops.file.pack_all();bpy.context.preferences.filepaths.save_version=0
out=R/'public/model/palladium_reconstruction_03.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(out))
print('SAVED BLEND',len(meshes),'meshes',len(cams),'cameras','packed images',sum(bool(i.packed_file) for i in bpy.data.images))
