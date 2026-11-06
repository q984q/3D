"""Conditional Blender-only preview colors, not a materials specification."""
import bpy

def material(name,color):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=.85
 return m

materials={
 'green':material('PREVIEW_GREEN_not_species_or_material',(.14,.30,.12)),
 'paving':material('PREVIEW_PAVING_material_unknown',(.43,.37,.29)),
 'field':material('PREVIEW_COURTYARD_material_unknown',(.31,.32,.30)),
 'edge':material('PREVIEW_EDGE_material_unknown',(.40,.40,.37)),
}
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 n=o.name
 if n.startswith('PDF_FILL_GREEN_FILL_'):key='green'
 elif n.startswith('CENTRAL_PAVING_'):key='paving'
 elif n.startswith('COURTYARD_PARTIAL_'):key='field'
 elif n.startswith(('CURB_','BED_EDGE_','CENTRAL_RING_')):key='edge'
 else:continue
 o.data.materials.clear();o.data.materials.append(materials[key])
 for poly in o.data.polygons:poly.material_index=0
