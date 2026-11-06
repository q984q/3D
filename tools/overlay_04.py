"""Registration overlay for new approximate markers and original PDF seat quads."""
from pathlib import Path
import json,fitz
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent.parent
page=fitz.open(next((R/'source').glob('*.pdf')))[0];paths={d['seqno']:d for d in page.get_drawings()};rot=page.rotation_matrix
im=Image.open(R/'public/model/plan_underlay.png').convert('RGB');draw=ImageDraw.Draw(im)
def pix(pt):
 p=fitz.Point(pt)*rot
 return (p.x*1568/page.rect.width,p.y*1109/page.rect.height)
audit=json.loads((R/'public/model/reconstruction_04_audit.json').read_text())
for item in audit['bench_symbols']:
 q=paths[item['source_seqno']]['items'][0][1];pts=[pix(x) for x in (q.ul,q.ur,q.lr,q.ll,q.ul)];draw.line(pts,fill=(0,220,255),width=3)
for item in audit['light_symbols']:
 x,y=item['center_m'];x=x*12.44;y=1109-y*12.44
 draw.ellipse((x-6,y-6,x+6,y+6),outline=(245,60,40),width=3)
for label in ('bed_plant_symbols','extra_plant_symbols'):
 for x,y in audit[label]['centers_in_normalized_image_pixels']:
  draw.line((x-6,y,x+6,y),fill=(220,0,220),width=2);draw.line((x,y-6,x,y+6),fill=(220,0,220),width=2)
im.save(R/'public/model/reconstruction_04_alignment.jpg',quality=91)
