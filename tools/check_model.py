"""Limited topology and orientation checks; not a safety or design review."""
from pathlib import Path
import numpy as np
import trimesh
path=Path(__file__).resolve().parent.parent/'public/model/palladium_reconstruction_02.glb'
s=trimesh.load(path,force='scene')
names=list(s.graph.nodes_geometry)
assert len([n for n in names if n.startswith('BUILDING_')])==6
assert len([n for n in names if n.startswith('TREE_SYMBOL_')])==32
assert len([n for n in names if n.startswith('CURB_')])==13
assert len([n for n in names if n.startswith('BED_EDGE_')])==7
assert len([n for n in names if n.startswith('PDF_FILL_')])==7
for n in names:
 mat,g=s.graph[n];m=s.geometry[g]
 if n.startswith(('BUILDING_','CURB_','BED_EDGE_','CENTRAL_','PLAY_SYMBOL_')):assert m.is_watertight,n
 if n.startswith('PDF_FILL_'):
  v=trimesh.transform_points(m.vertices,mat);f=m.faces
  # glTF Y-up: graphic planes should be visible from above.
  normals=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]])[:,1]
  assert np.all(normals>0),n
print(f'OK: {len(names)} meshes, 6 building volumes, 20 edge groups, 32 tree symbols and 7 fill groups. Selected solids watertight; fill normals face up.')
print('No full collision, drainage, clearance, accessibility or safety checks were performed.')
