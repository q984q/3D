"""2D registration check, not a technical review of the proposed design."""
from pathlib import Path
import fitz, json
import numpy as np
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parent.parent
page=fitz.open(next((root/'source').glob('*.pdf')))[0]
paths={d['seqno']:d for d in page.get_drawings()};r=page.rotation_matrix
im=Image.open(root/'public/model/plan_underlay.png').convert('RGB');draw=ImageDraw.Draw(im)
def pix(p):
 q=fitz.Point(p)*r
 return (q.x*1568/page.rect.width,q.y*1109/page.rect.height)
def line(seq):
 pts=[]
 for item in paths[seq]['items']:
  if item[0]=='l':
   if not pts:pts.append(pix(item[1]))
   pts.append(pix(item[2]))
  elif item[0]=='c':
   a,b,c,d=[np.array(pix(x)) for x in item[1:]]
   if not pts:pts.append(tuple(a))
   for t in np.linspace(0,1,25)[1:]:pts.append(tuple((1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d))
 return pts
central=line(47085)+list(reversed(line(47086)))+line(47087)
draw.line(central+[central[0]],fill=(228,39,180),width=3)
audit=json.loads((root/'public/model/reconstruction_03_audit.json').read_text())
# Orange follows the inferred field boundary, except the artificial purple seam.
outline=line(14563)+list(reversed(line(14564)))+[line(47087)[0]]
seam=audit['courtyard_partial']['artificial_seam_px']
draw.line(outline+[seam[1]],fill=(255,130,0),width=4)
draw.line([tuple(seam[0]),tuple(seam[1])],fill=(204,0,204),width=5)
for x,y in audit['central_plant_symbols']['centers_in_normalized_image_pixels']:
 draw.ellipse((x-6,y-6,x+6,y+6),outline=(0,160,200),width=3)

for x,y in audit['tree_symbols']['centers_in_normalized_image_pixels']:
 draw.ellipse((x-8,y-8,x+8,y+8),outline=(255,0,180),width=3)
 draw.line((x-11,y,x+11,y),fill=(255,0,180),width=2);draw.line((x,y-11,x,y+11),fill=(255,0,180),width=2)
im.save(root/'public/model/reconstruction_03_alignment.jpg',quality=90)
