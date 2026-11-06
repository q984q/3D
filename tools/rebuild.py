"""Partial reconstruction from the user's PDF. Provisional, not recovered v5."""
from pathlib import Path
import fitz
import numpy as np
from PIL import Image
from shapely.geometry import box, Polygon
from shapely import set_precision, from_wkb, to_wkb
import json
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
# PDF graphic fills are triangulated in groups of three line segments.
# Only exact source colours/layers are selected, without guessing a construction.
color_groups=[('GREEN_FILL','Штриховка_зелень',(218,243,211)),
 ('PLAY_GREEN','ПОКР.ТИП-1',(99,159,20)),('PLAY_YELLOW','ПОКР.ТИП-1',(229,238,124)),
 ('PLAY_PURPLE','ПОКР.ТИП-1',(90,22,148)),('PLAY_LILAC','ПОКР.ТИП-1',(207,166,242)),
 ('PLAY_ORANGE','ПОКР.ТИП-1',(255,132,46)),('RIGHT_GREY','Штриховка_зелень',(147,149,152))]
fills={};audit={}
for name,layer,color in color_groups:
 triangles=[];seqs=[]
 for d in paths.values():
  if d['layer']!=layer or d['fill'] is None or tuple(round(255*c) for c in d['fill'])!=color:continue
  items=d['items']
  if len(items)%3 or any(t[0]!='l' for t in items):continue
  for i in range(0,len(items),3):
   t=Polygon([world(item[1]) for item in items[i:i+3]])
   if t.is_valid and t.area>1e-8:triangles.append(t)
  seqs.append(d['seqno'])
 if not triangles:raise ValueError(name)
 # Preserve original vector triangle boundaries: small discrepancies between
 # neighbouring PDF fragments do not justify inventing missing material.
 verts=[];faces=[]
 for poly in triangles:
  coords=list(poly.exterior.coords)[:3];start=len(verts)
  if not poly.exterior.is_ccw:coords.reverse()
  verts.extend([(x,y,.025) for x,y in coords]);faces.append((start,start+1,start+2))
 mesh=trimesh.Trimesh(vertices=verts,faces=faces,process=False)
 add('PDF_FILL_'+name+'_MATERIAL_UNCONFIRMED',mesh,[*color,255])
 fills[name]=unary_union([set_precision(t,.0001) for t in triangles])
 audit[name]={'pdf_layer':layer,'rgb':color,'source_seqnos':seqs,'triangle_count':len(triangles),'union_area_m2':fills[name].area}
# Curbs / planter edging: paired PDF contours; provisional 0.10 m height.
curb_pairs=[(99757,99758),(99759,99760),(99761,99762),(99763,99764),(99765,99766),(99767,99768),(99769,99772),(99770,99771),(99888,99889),(99890,99891),(99892,99893),(99894,99895),(99896,99897)]
bed_pairs=[(1125,1198),(1199,1200),(1201,1202),(1204,1206),(14597,14598),(14575,14576),(39218,39225)]
def path_points(seq):
 d=paths[seq]
 if len(d['items'])==1 and d['items'][0][0]=='qu':
  q=d['items'][0][1];return [world(q.ul),world(q.ur),world(q.lr),world(q.ll),world(q.ul)]
 return polylines(seq)
def paired_polygon(a,b):
 A=path_points(a);B=path_points(b)
 if np.linalg.norm(np.array(A[0])-A[-1])<.001 and np.linalg.norm(np.array(B[0])-B[-1])<.001:
  p,q=Polygon(A),Polygon(B)
  if p.area<q.area:p,q=q,p
  return p.difference(q)
 # Match the closer pair of endpoints before connecting; small ends are assumed.
 if np.linalg.norm(np.array(A[-1])-B[0])+np.linalg.norm(np.array(A[0])-B[-1]) > np.linalg.norm(np.array(A[-1])-B[-1])+np.linalg.norm(np.array(A[0])-B[0]):B=B[::-1]
 return Polygon(A+B)
edge_geoms=[];edge_audit=[]
for prefix,pairs in [('CURB',curb_pairs),('BED_EDGE',bed_pairs)]:
 for i,(a,b) in enumerate(pairs,1):
  poly=paired_polygon(a,b)
  repaired=not poly.is_valid
  if repaired:poly=poly.buffer(0)
  poly=set_precision(poly,.001)
  if edge_geoms:poly=poly.difference(unary_union(edge_geoms))
  chunks=list(poly.geoms) if poly.geom_type=='MultiPolygon' else [poly]
  saved=[]
  for j,g in enumerate(chunks,1):
   if not isinstance(g,Polygon) or g.area<.0001:continue
   mesh=trimesh.creation.extrude_polygon(g,.10)
   if not mesh.is_watertight:
    # Skip questionable components rather than silently assert a valid solid.
    continue
   mesh.apply_translation((0,0,.02));add(f'{prefix}_{i:02d}_{j:02d}_HEIGHT_CONDITIONAL',mesh,[150,148,140,255]);saved.append(g);edge_geoms.append(g)
  edge_audit.append({'kind':prefix,'seqnos':[a,b],'repaired':repaired,'components_saved':len(saved),'area_m2':sum(x.area for x in saved)})
audit['edge_pairs']=edge_audit

# Central area formed from the three source boundary fragments. Two ends have
# small drawing gaps; joins are straight and explicitly recorded in the report.
central=Polygon(polylines(47085)+list(reversed(polylines(47086)))+polylines(47087))
assert central.is_valid, 'Central polygon requires manual review'
mask=unary_union([ring]+edge_geoms+list(fills.values()))
central=central.difference(mask)
for i,poly in enumerate((central.geoms if central.geom_type=='MultiPolygon' else [central]),1):
 if poly.area<.01:continue
 # The base is an assumed thin preview surface; cannot be used as construction.
 m=trimesh.creation.extrude_polygon(poly,.015)
 if not m.is_watertight:
  # Drop fixed precision before a 0.1 mm inset at point-touching boundaries.
  clean=from_wkb(to_wkb(poly)).buffer(-.0001)
  pieces=[clean] if clean.geom_type=='Polygon' else [g for g in clean.geoms if g.geom_type=='Polygon' and g.area>1e-6]
  if not pieces:raise ValueError('Inset erased a central paving part')
  m=trimesh.util.concatenate([trimesh.creation.extrude_polygon(piece,.015) for piece in pieces])
  if not m.is_watertight:raise ValueError('Non-watertight central paving after inset')
  audit.setdefault('central_topology_insets_0_1mm',[]).append(i)
 m.apply_translation((0,0,.005));add(f'CENTRAL_PAVING_PART_{i:02d}_CONDITIONAL',m,[194,178,152,255])
audit['central']={'boundary_seqnos':[47085,47086,47087], 'joins':'47086 reversed, small gaps bridged', 'area_after_fill_exclusions_m2':central.area,'thickness_m_conditional':.015}
# Approximate centers from repeated, visible tree symbols on the two streets.
# The morphology and height are solely neutral placeholders, not a species choice.
tree_pixels=[(34,996),(99,996),(163,996),(230,996),(301,996),(365,996),(428,996),(490,996),(552,996),(615,996),(676,996),(801,996),(863,996),(926,996),(988,996),(1054,996),(1148,996),(1210,996),(1273,996),(1335,996),(1397,996),(1459,996)]+[(1474,y) for y in (328,392,452,514,578,639,700,765,827,889)]
for i,(px,py) in enumerate(tree_pixels,1):
 x,y=px/12.44,(H-py)/12.44
 trunk=trimesh.creation.cylinder(radius=.10,height=1.4,sections=10);trunk.apply_translation((x,y,.72));trunk.visual.face_colors=[103,83,61,255]
 crown=trimesh.creation.icosphere(subdivisions=2,radius=1);crown.apply_scale([1.1,1.1,1.0]);crown.apply_translation((x,y,2.05));crown.visual.face_colors=[87,137,74,255]
 tree=trimesh.util.concatenate([trunk,crown]);add(f'TREE_SYMBOL_{i:02d}_LOCATION_APPROX_HEIGHT_AND_TYPE_CONDITIONAL',tree)
audit['tree_symbols']={'count':len(tree_pixels),'centers_in_normalized_image_pixels':tree_pixels,'crown_radius_m_conditional':1.1,'approx_height_m_conditional':3.05}
(R/'public/model/reconstruction_02_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2))
# Blender's Z-up to glTF Y-up conversion.
s.apply_transform(trimesh.transformations.rotation_matrix(-np.pi/2,[1,0,0]))
out=R/'public/model/palladium_reconstruction_02.glb';s.export(out)
print('Saved',out,'nodes',len(s.graph.nodes_geometry),'bounds',s.bounds.tolist())
