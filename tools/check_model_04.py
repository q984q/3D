"""Selected checks only; not a construction or accessibility audit."""
from pathlib import Path
import numpy as np,trimesh
from shapely.geometry import Polygon
from shapely.ops import unary_union
R=Path(__file__).resolve().parent.parent
s=trimesh.load(R/'public/model/palladium_reconstruction_04.glb',force='scene')
s.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2,[1,0,0]))
names=list(s.graph.nodes_geometry)
def getmesh(n):
 mat,g=s.graph[n];m=s.geometry[g].copy();m.apply_transform(mat);return m
def fp(mesh):return unary_union([p for face in mesh.faces if (p:=Polygon(mesh.vertices[face,:2])).area>1e-10])
expected={'BUILDING_':6,'TREE_SYMBOL_':32,'CENTRAL_PLANT_':9,'BED_PLANT_':12,'EXTRA_PLANT_':5,'BENCH_SYMBOL_':8,'LIGHT_SYMBOL_':24,'CURB_':13,'BED_EDGE_':8,'PDF_FILL_':7,'COURTYARD_PARTIAL_':2}
for prefix,n in expected.items():assert sum(a.startswith(prefix) for a in names)==n,(prefix,n)
for name in names:
 m=getmesh(name)
 if name.startswith(('BUILDING_','CURB_','BED_EDGE_','CENTRAL_','BED_PLANT_','EXTRA_PLANT_','BENCH_SYMBOL_','LIGHT_SYMBOL_','PLAY_SYMBOL_','COURTYARD_PARTIAL_')):assert m.is_watertight,name
 if name.startswith('PDF_FILL_'):
  f=m.faces;v=m.vertices;normal=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]])[:,2];assert np.all(normal>0),name
edges=unary_union([fp(getmesh(n)) for n in names if n.startswith(('CURB_','BED_EDGE_','CENTRAL_RING_','BUILDING_'))])
for name in names:
 if name.startswith('BENCH_SYMBOL_'):
  parts=getmesh(name).split(only_watertight=False);feet=[x for x in parts if x.bounds[0,2]<.10]
  assert len(feet)==2 and all(fp(x).intersection(edges).area<1e-6 for x in feet),name
 if name.startswith('LIGHT_SYMBOL_'):
  parts=getmesh(name).split(only_watertight=False);poles=[x for x in parts if x.bounds[0,2]<.1]
  assert len(poles)==1 and fp(poles[0]).intersection(edges).area<1e-6,name
obstacles=unary_union([edges]+[fp(getmesh(n)) for n in names if n.startswith(('BENCH_SYMBOL_','LIGHT_SYMBOL_'))])
for name in names:
 if name.startswith(('BED_PLANT_','EXTRA_PLANT_')):assert fp(getmesh(name)).intersection(obstacles).area<1e-6,name
print(f'OK: {len(names)} meshes; object counts and selected solid topology checked.')
print('Eight pairs of bench feet and 24 low lamp poles clear selected edges/building footprints; 17 plant marker footprints clear selected obstacles.')
print('Not a comprehensive collision, safety, accessibility, design or engineering assessment.')
