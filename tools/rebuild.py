"""Partial reconstruction from the user's PDF. Provisional, not recovered v5."""
from pathlib import Path
import fitz
import numpy as np
from PIL import Image
from shapely.geometry import box, Polygon
from shapely.ops import unary_union
import trimesh
from trimesh.visual.texture import TextureVisuals
R=Path(__file__).resolve().parent.parent
p=fitz.open(str(next((R/'source').glob('*.pdf'))))[0]
W,H=1568,1109
# Rasterized orientation is the orientation shown on the original page.
pix=p.get_pixmap(matrix=fitz.Matrix(W/p.rect.width,H/p.rect.height),alpha=False)
img=Image.frombytes('RGB',(pix.width,pix.height),pix.samples).resize((W,H))
img.save(R/'public/model/plan_underlay.png',optimize=True)
paths={d['seqno']:d for d in p.get_drawings()}; rot=p.rotation_matrix
# image coordinate -> local metric XY; 12.44 px/m is the earlier multi-dimension calibration.
def norm(point):
 q=fitz.Point(point)*rot
 return (q.x*W/p.rect.width,q.y*H/p.rect.height)
def world(point):
 x,y=norm(point);return (x/12.44,(H-y)/12.44)
def rect(seq):
 r=paths[seq]['rect']; pts=[world((r.x0,r.y0)),world((r.x0,r.y1)),world((r.x1,r.y0)),world((r.x1,r.y1))]
 return box(min(x for x,y in pts),min(y for x,y in pts),max(x for x,y in pts),max(y for x,y in pts))
def polylines(seq):
 pts=[]
 for item in paths[seq]['items']:
  op=item[0]
  if op=='l':
   a,b=item[1:];
   if not pts:pts.append(world(a))
   pts.append(world(b))
  elif op=='c':
   a,b,c,d=[np.array(world(x)) for x in item[1:]]
   if not pts:pts.append(tuple(a))
   for t in np.linspace(0,1,25)[1:]:pts.append(tuple((1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d))
 return pts
s=trimesh.Scene()
def add(name,mesh,color=None):
 if color is not None:mesh.visual.face_colors=color
 s.add_geometry(mesh,geom_name=name,node_name=name)
# embed raster as a texture on a horizontal XY quad.
w,h=W/12.44,H/12.44
v=np.array([[0,0,0],[w,0,0],[w,h,0],[0,h,0]],float)
f=np.array([[0,1,2],[0,2,3]])
# UV origin is bottom-left; image origin is top-left.
uv=np.array([[0,0],[1,0],[1,1],[0,1]],float)
plane=trimesh.Trimesh(vertices=v,faces=f,visual=TextureVisuals(uv=uv,image=img),process=False)
add('REFERENCE_PDF_NOT_GEOMETRY',plane)
# Rectangles are envelope proxies only, not measured architecture.
groups=[[9051],[9054,9068],[9151],[9588,9600],[9691],[9661,9680]]
for i,ids in enumerate(groups,1):
 geom=unary_union([rect(x) for x in ids])
 # Bounding rectangle for the pair 9588/9600, whose intermediates are not reconstructed.
 if i==4:geom=box(*geom.bounds)
 polys=list(geom.geoms) if hasattr(geom,'geoms') else [geom]
 for j,poly in enumerate(polys,1):
  mesh=trimesh.creation.extrude_polygon(poly,8.0);mesh.apply_translation((0,0,.02));add(f'BUILDING_{i:02d}_{j:02d}_ENVELOPE_HEIGHT_8M_CONDITIONAL',mesh,[155,160,159,255])
outer=Polygon(polylines(39129)); inner=Polygon(polylines(39186))
ring=outer.difference(inner)
if not ring.is_valid:ring=ring.buffer(0)
ring_mesh=trimesh.creation.extrude_polygon(ring,.10);ring_mesh.apply_translation((0,0,.02));add('CENTRAL_RING_CONDITIONAL_10CM',ring_mesh,[141,145,138,255])
# Two simple MAF placeholders from visible outlined squares.
for i,seq in enumerate((25669,25722),1):
 mesh=trimesh.creation.extrude_polygon(rect(seq),.12);mesh.apply_translation((0,0,.02));add(f'PLAY_SYMBOL_{i:02d}_CONDITIONAL',mesh,[206,180,109,255])
# Blender's Z-up to glTF Y-up conversion.
s.apply_transform(trimesh.transformations.rotation_matrix(-np.pi/2,[1,0,0]))
out=R/'public/model/palladium_reconstruction_01.glb';s.export(out)
print('Saved',out,'nodes',len(s.graph.nodes_geometry),'bounds',s.bounds.tolist())
