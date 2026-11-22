"""Simple original item-sprite paintings for the proof-of-concept counter."""
from PIL import Image,ImageDraw,ImageFilter
from pathlib import Path
import math
from sys import path
path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.content import ITEMS
ROOT=Path(__file__).resolve().parents[1]/'godot'/'assets'

def art(i,it):
 im=Image.new('RGBA',(260,260));d=ImageDraw.Draw(im,'RGBA')
 g=Image.new('RGBA',im.size);gd=ImageDraw.Draw(g,'RGBA');gd.ellipse((29,21,230,236),fill=(255,185,78,68));g=g.filter(ImageFilter.GaussianBlur(38));im.alpha_composite(g);d=ImageDraw.Draw(im,'RGBA')
 d.ellipse((48,210,220,246),fill=(0,0,0,105))
 if 'potion' in it['id'] or it['id'] in ('storm_vial','healing_draught'):
  glass=(49,137,175,245) if 'mana' in it['id'] or 'storm' in it['id'] else (166,48,79,245)
  d.rounded_rectangle((99,48,161,83),radius=7,fill=(110,68,48,255),outline=(225,170,94,230),width=4)
  d.rounded_rectangle((82,74,179,207),radius=28,fill=(101,172,176,110),outline=(222,204,151,245),width=6)
  d.rounded_rectangle((93,114,169,201),radius=22,fill=glass)
  d.ellipse((111,136,140,174),fill=(229,244,242,78))
  d.line((98,96,98,178),fill=(255,255,255,145),width=6)
  d.rectangle((102,41,158,65),fill=(183,132,75,255),outline=(237,199,132,255),width=3)
 elif it['id']=='moonblade':
  d.polygon([(79,210),(166,44),(195,28),(192,62),(109,220)],fill=(161,202,216,255),outline=(243,227,181,255))
  d.line((89,217,174,56),fill=(236,251,255,225),width=7)
  d.line((80,179,133,204),fill=(185,140,86,255),width=16)
  d.line((81,207,68,235),fill=(106,70,54,255),width=17)
 elif 'scroll' in it['id']:
  d.polygon([(53,103),(203,80),(192,207),(57,223)],fill=(218,183,117,255),outline=(109,73,53,235))
  for j in range(4):d.arc((93,124+j*15,174,173+j*15),182,340,fill=(120,93,73,240),width=4)
  d.ellipse((43,99,76,226),fill=(182,137,81,255))
 elif it['id'] in ('wyvern_scale','rune_stone','sun_charm'):
  points=[(130,36),(206,106),(178,206),(132,239),(65,201),(45,109)]
  col=(101,167,175,245) if it['id']=='rune_stone' else (205,140,70,255)
  d.polygon(points,fill=col,outline=(243,220,151,255))
  d.line((131,47,131,220),fill=(245,229,182,150),width=4)
  d.line((58,120,189,116),fill=(245,229,182,120),width=4)
  if it['id']=='sun_charm':d.ellipse((112,112,148,149),fill=(255,221,106,255))
 else:
  d.rounded_rectangle((58,82,202,193),radius=28,fill=(155,171,108,255),outline=(223,198,136,255),width=7)
  d.polygon([(95,160),(135,91),(174,159),(135,135)],fill=(228,215,162,240))
 im.save(ROOT/f'item_{it["id"]}.png',compress_level=2)

if __name__=='__main__':
 for i,it in enumerate(ITEMS):art(i,it)
 print('Generated',len(ITEMS),'counter items')
