"""Create a separate Blender visual test; keep the reference model untouched.
blender --background --python tools/create_lookdev.py
See public/assets/CREDITS.md for source licenses and substitutions.
"""
from pathlib import Path
import bpy
from mathutils import Vector, Matrix
R=Path(__file__).resolve().parent.parent
bpy.ops.wm.open_mainfile(filepath=str(R/'public/model/palladium_reconstruction_03.blend'))
scene=bpy.context.scene
bpy.context.view_layer.update()
markers=[o for o in scene.objects if o.type=='MESH' and o.name.startswith('CENTRAL_PLANT_')]
assert len(markers)==9
# One source component, shared mesh/material across nine optional visual stand-ins.
before=set(scene.objects)
bpy.ops.import_scene.gltf(filepath=str(R/'public/assets/polyhaven/shrub_02.glb'))
bpy.context.view_layer.update()
new=[o for o in scene.objects if o not in before]
source=next(o for o in new if o.type=='MESH' and o.name=='shrub_02_a')
def bounds(obj):
 return [obj.matrix_world @ Vector(v) for v in obj.bound_box]
box=bounds(source);mins=[min(v[i] for v in box) for i in range(3)];maxs=[max(v[i] for v in box) for i in range(3)]
width=max(maxs[0]-mins[0],maxs[1]-mins[1]);assert width>0
scale=.68/width;center=((mins[0]+maxs[0])/2,(mins[1]+maxs[1])/2)
collection=bpy.data.collections.new('11_PREVIEW_ONLY_PolyHaven_plants');scene.collection.children.link(collection)
for i,marker in enumerate(sorted(markers,key=lambda x:x.name),1):
 points=bounds(marker);x=(max(v.x for v in points)+min(v.x for v in points))/2;y=(max(v.y for v in points)+min(v.y for v in points))/2
 obj=source.copy();obj.name=f'PREVIEW_ONLY_SHRUB_{i:02d}_NOT_CONFIRMED';collection.objects.link(obj)
 obj.matrix_world=Matrix.Translation((x,y,.02)) @ Matrix.Scale(scale,4) @ Matrix.Translation((-center[0],-center[1],-mins[2])) @ source.matrix_world
 marker.hide_render=True;marker.hide_set(True)
for obj in new:bpy.data.objects.remove(obj,do_unlink=True)
# Optically plausible CC0 PBR pavement: material and 2m texture repeat are visual assumptions.
mat=bpy.data.materials.new('PREVIEW_ONLY_ambientCG_PavingStones002_NOT_SPECIFIED');mat.use_nodes=True
nodes=mat.node_tree.nodes;links=mat.node_tree.links;bsdf=nodes.get('Principled BSDF');bsdf.inputs['Metallic'].default_value=0
images={}
for kind in ('Color','Normal','Roughness'):
 image=bpy.data.images.load(str(R/f'public/assets/ambientcg/PavingStones002_{kind}_1k.jpg'),check_existing=True)
 if kind!='Color':image.colorspace_settings.name='Non-Color'
 node=nodes.new('ShaderNodeTexImage');node.image=image;node.label='CC0 ambientCG '+kind;images[kind]=node
links.new(images['Color'].outputs['Color'],bsdf.inputs['Base Color'])
links.new(images['Roughness'].outputs['Color'],bsdf.inputs['Roughness'])
normal=nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.35
links.new(images['Normal'].outputs['Color'],normal.inputs['Color']);links.new(normal.outputs['Normal'],bsdf.inputs['Normal'])
for obj in [o for o in scene.objects if o.type=='MESH' and o.name.startswith('CENTRAL_PAVING_')]:
 # Reconstruct UVs from world metric positions; each tile visually repeats every 2 m.
 layer=obj.data.uv_layers.new(name='PREVIEW_WORLD_METERS_2M')
 for polygon in obj.data.polygons:
  for li in polygon.loop_indices:
   vertex=obj.data.vertices[obj.data.loops[li].vertex_index];co=obj.matrix_world @ vertex.co
   layer.data[li].uv=(co.x/2,co.y/2)
 obj.data.uv_layers.active=layer;obj.data.materials.clear();obj.data.materials.append(mat)
 for p in obj.data.polygons:p.material_index=0
# Keep plan control without preview plants.
scene.view_layers['CONTROL_TOP_no_decor'].layer_collection.children[collection.name].exclude=True
rig=bpy.data.collections['10_Cameras_and_daylight']
camera_data=bpy.data.cameras.new('CAM_08_CLOSEUP_PREVIEW_NOT_FINAL');camera=bpy.data.objects.new(camera_data.name,camera_data);rig.objects.link(camera)
camera.location=(65,80,13);target=Vector((53.5,62,0));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera_data.lens=32;camera_data.clip_end=1000
scene.camera=camera
bpy.ops.file.pack_all();bpy.context.preferences.filepaths.save_version=0
out=R/'public/model/palladium_lookdev_test.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out))
print('SAVED',out,'plant scale',scale,'9 instances; 8 cameras; CC0 textures packed')
