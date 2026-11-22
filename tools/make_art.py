"""Generate original lightweight 2.5D shop and 10 transparent character illustrations. No external asset licenses."""
from PIL import Image, ImageDraw, ImageFilter
from pathlib import Path
import math, random

ROOT=Path(__file__).resolve().parents[1]/'godot'/'assets'; ROOT.mkdir(parents=True,exist_ok=True)
R=random.Random(91)
W,H=1440,900

def rgb(h):return tuple(int(h[i:i+2],16) for i in (1,3,5))
def mix(a,b,t):return tuple(round(a[i]*(1-t)+b[i]*t) for i in range(3))
def grad(img,top,bottom):
 p=img.load();a,b=rgb(top),rgb(bottom)
 for y in range(img.height):
  c=mix(a,b,y/(img.height-1))
  for x in range(img.width):p[x,y]=c+(255,)
def ellipse_glow(img,x,y,r,rgba):
 layer=Image.new('RGBA',img.size); dr=ImageDraw.Draw(layer); dr.ellipse((x-r,y-r,x+r,y+r),fill=rgba);layer=layer.filter(ImageFilter.GaussianBlur(r//2));img.alpha_composite(layer)

def bottle(draw,x,y,w=14,h=30,color=(45,131,130)):
 draw.rectangle((x+w*.37,y,x+w*.65,y+6),fill=(155,129,81,255));draw.rounded_rectangle((x,y+5,x+w,y+h),radius=4,fill=color+(245,),outline=(211,176,111,200),width=1)
 draw.line((x+3,y+8,x+3,y+h-5),fill=(244,231,181,90),width=2)

def make_bg():
 im=Image.new('RGBA',(W,H));grad(im,'#172f32','#4a2c23');d=ImageDraw.Draw(im,'RGBA')
 # wall paneling and shadow arch
 d.rectangle((0,82,W,590),fill=(45,45,40,68))
 for x in (40,300,593,890,1160,1370):
  d.rounded_rectangle((x-13,70,x+12,615),8,fill=(75,43,29,255),outline=(171,107,55,240),width=4)
  d.line((x-8,85,x-8,603),fill=(229,174,94,65),width=3)
 for y in (70,145,555):
  d.rectangle((0,y,W,y+18),fill=(65,35,25,255));d.line((0,y,W,y),fill=(204,141,79,190),width=3)
 # stained-glass window left
 d.rounded_rectangle((65,170,288,482),radius=92,fill=(14,29,35,255),outline=(154,95,54,255),width=15)
 d.rounded_rectangle((81,185,272,464),radius=82,fill=(44,94,96,255),outline=(224,177,100,190),width=4)
 for c,xx in enumerate((82,130,177,225)):
  d.polygon([(xx,196),(xx+39,196),(xx+32,453),(xx+5,453)],fill=((62+22*c),110+(c*12),121,140))
 d.line((178,181,178,467),fill=(228,185,106,200),width=8);d.line((84,325,270,325),fill=(228,185,106,200),width=8)
 ellipse_glow(im,175,280,250,(244,176,96,55))
 # doorway on right
 d=ImageDraw.Draw(im,'RGBA')
 d.rounded_rectangle((1173,174,1370,600),radius=87,fill=(35,22,26,255),outline=(132,78,48,255),width=17)
 d.rounded_rectangle((1192,194,1350,596),radius=70,fill=(26,31,31,255),outline=(202,131,74,140),width=5)
 d.polygon([(1210,245),(1332,245),(1332,595),(1210,595)],fill=(41,47,47,240))
 d.line((1269,250,1269,580),fill=(204,148,84,95),width=3)
 d.ellipse((1321,408,1330,417),fill=(231,190,108,255))
 # shelves with bottles and goods
 for shelf_x,shelf_y,length in ((354,260,235),(355,366,220),(910,260,210),(913,377,210)):
  d.rounded_rectangle((shelf_x-6,shelf_y+27,shelf_x+length+8,shelf_y+40),4,fill=(79,43,29,255),outline=(197,131,68,255),width=2)
  for k in range(7):
   bx=shelf_x+11+k*29+R.randint(-3,3);by=shelf_y+R.randint(-5,7)
   if k%4==1:
    d.polygon([(bx+2,by+32),(bx+12,by-11),(bx+22,by+32)],fill=(131,95,125,230),outline=(205,171,104,160))
   else:
    bottle(d,bx,by,14+R.randint(0,4),32,R.choice([(80,145,124),(116,59,106),(174,89,69),(86,94,157),(191,147,65)]))
 # hanging lanterns
 for x in (350,1030):
  d.line((x,0,x,130),fill=(190,132,67,255),width=5)
  d.polygon([(x-22,130),(x+22,130),(x+28,170),(x-28,170)],fill=(63,45,36,255),outline=(218,161,93,255))
  d.ellipse((x-12,139,x+12,162),fill=(255,199,106,235))
  ellipse_glow(im,x,150,125,(255,176,66,75))
 # floor and tonal shadow
 d=ImageDraw.Draw(im,'RGBA');d.rectangle((0,590,W,H),fill=(32,24,24,255))
 for y in (609,657,716,780,848):d.line((0,y,W,y+18),fill=(171,110,67,70),width=2)
 for x in range(0,W,190):d.line((x+R.randint(-20,40),595,x+R.randint(-70,60),900),fill=(115,73,43,75),width=2)
 # faint ambience particles
 for _ in range(180):
  x=R.randint(40,1400);y=R.randint(90,630);radius=R.choice((1,1,1,2))
  d.ellipse((x-radius,y-radius,x+radius,y+radius),fill=(232,186,110,R.randint(20,85)))
 im.convert('RGB').save(ROOT/'shop_bg.png',optimize=True)

def counter():
 im=Image.new('RGBA',(W,H));d=ImageDraw.Draw(im,'RGBA')
 # counter front: strong perspective, visible over customer's waist
 d.polygon([(0,585),(1440,585),(1440,900),(0,900)],fill=(59,33,25,254))
 d.polygon([(0,581),(1440,581),(1440,625),(0,625)],fill=(96,51,32,255))
 d.line((0,584,1440,584),fill=(228,178,105,255),width=5)
 d.line((0,619,1440,619),fill=(27,17,19,235),width=8)
 d.rectangle((0,638,1440,652),fill=(120,66,42,235));d.line((0,651,1440,651),fill=(205,138,77,180),width=3)
 for x in range(20,1440,230):
  d.rounded_rectangle((x,670,x+195,870),radius=7,fill=(87,48,31,170),outline=(176,114,62,160),width=3)
  d.line((x+16,689,x+16,845),fill=(223,149,82,40),width=2)
 d.rectangle((0,876,1440,897),fill=(34,22,20,245));d.line((0,876,1440,876),fill=(201,129,67,180),width=3)
 for x in range(0,1440,14):
  y=R.randrange(634,879);d.line((x,y,x+R.randint(9,35),y+R.choice([-1,0,1])),fill=(214,149,89,R.randint(8,24)),width=1)
 im.save(ROOT/'counter_overlay.png',optimize=True)

SKINS=[('#e8bc9c','#ad725c'),('#f4c9af','#c98a71'),('#a77f61','#6a4937'),('#e9b9a2','#ba7a63'),('#c9aa98','#805d5d'),('#d49b80','#95634e'),('#e7c1a4','#ba887b'),('#d4a383','#9a6252'),('#ecd2c5','#b58e83'),('#c99b77','#946b50')]
HAIRS=['#bd8658','#34223e','#55504b','#efc678','#272d39','#a65d38','#72544a','#563330','#e7d8bd','#8b5635']
CLOTHES=['#60798b','#683d59','#6d4a34','#466965','#3c4451','#8a5d39','#495c84','#884437','#345970','#86703d']

def portrait(index,id,mood="neutral"):
 target=ROOT/f'customer_{id}_{mood}.png'
 if target.exists() and target.stat().st_size>1000:return
 w,h=520,660;im=Image.new('RGBA',(w,h),(0,0,0,0));d=ImageDraw.Draw(im,'RGBA')
 skin1,skin2=map(rgb,SKINS[index]);hair=rgb(HAIRS[index]);cloth=rgb(CLOTHES[index]);
 # subtle background shadow halo independent from scenic background
 halo=Image.new('RGBA',(w,h),(0,0,0,0));hd=ImageDraw.Draw(halo);hd.ellipse((95,45,445,555),fill=(251,207,129,24));halo=halo.filter(ImageFilter.GaussianBlur(26));im.alpha_composite(halo)
 d=ImageDraw.Draw(im,'RGBA')
 # arms cloak silhouette
 d.ellipse((55,355,470,814),fill=tuple(max(0,c-30) for c in cloth)+(255,))
 d.polygon([(105,425),(180,345),(351,345),(433,425),(464,660),(52,660)],fill=cloth+(255,))
 d.polygon([(162,362),(259,407),(357,362),(321,553),(207,553)],fill=tuple(min(255,c+30) for c in cloth)+(255,))
 d.line((168,367,206,625),fill=(205,154,91,170),width=8);d.line((354,364,321,622),fill=(205,154,91,150),width=8)
 # neck and ears
 d.rounded_rectangle((223,342,301,436),radius=25,fill=skin2+(255,))
 d.ellipse((155,235,220,323),fill=skin2+(255,));d.ellipse((298,235,362,323),fill=skin2+(255,))
 # hair back head and pointed elf ears
 d.ellipse((165,121,365,403),fill=hair+(255,))
 if index==8:
  d.polygon([(172,253),(107,218),(162,316)],fill=skin1+(255,),outline=skin2+(255,))
  d.polygon([(347,253),(403,218),(353,316)],fill=skin1+(255,),outline=skin2+(255,))
 # face shape highlights
 d.ellipse((169,144,357,390),fill=skin2+(255,))
 d.ellipse((178,137,347,380),fill=skin1+(255,))
 # Avoid low-alpha face shading over the opaque skin: would punch a dark hole when composited.
 # hair framing forehead
 if index in (1,3,5,8):
  d.pieslice((165,123,355,274),181,356,fill=hair+(255,))
  d.ellipse((150,178,210,328),fill=hair+(255,));d.ellipse((323,165,365,330),fill=hair+(255,))
 else:
  d.polygon([(171,246),(182,142),(253,118),(342,143),(353,237),(327,202),(288,185),(255,211),(211,182)],fill=hair+(255,))
 # emotional facial variants: expressive brows, eye shapes, mouth corners
 if mood in ("furious","annoyed"):
  d.line((189,211,247,231),fill=(65,40,37,255),width=7)
  d.line((274,231,330,211),fill=(65,40,37,255),width=7)
 elif mood=="suspicious":
  d.line((187,205,244,219),fill=(60,44,38,255),width=5)
  d.arc((274,192,333,229),184,339,fill=(60,44,38,255),width=6)
 elif mood=="sad":
  d.line((190,231,243,212),fill=(77,54,52,255),width=5)
  d.line((277,212,332,231),fill=(77,54,52,255),width=5)
 else:
  d.arc((188,198,251,238),200,340,fill=(56,45,45,255),width=5)
  d.arc((272,198,332,238),200,340,fill=(56,45,45,255),width=5)
 eye_height=29 if mood=="surprised" else 14 if mood=="furious" else 22
 for x in (213,301):
  d.ellipse((x-10,248-eye_height/2,x+10,248+eye_height/2),fill=(246,240,230,255))
  d.ellipse((x-5,247-eye_height/2,x+5,251+eye_height/2),fill=(40,61,64,255))
  d.ellipse((x-2,239,x+1,242),fill=(255,255,255,235))
 d.line((258,246,247,298,260,305),fill=(164,104,87,175),width=3)
 if mood in ("happy","amused"):
  d.arc((222,296,295,355),6,170,fill=(111,53,61,255),width=5)
  d.arc((223,297,293,350),20,140,fill=(255,227,217,235),width=2)
 elif mood=="delighted":
  d.ellipse((238,308,284,350),fill=(104,46,56,255))
  d.arc((239,303,283,330),8,174,fill=(244,236,220,250),width=4)
 elif mood=="surprised":
  d.ellipse((247,309,272,346),fill=(105,53,59,255))
 elif mood=="furious":
  d.line((233,331,286,327),fill=(110,48,58,255),width=6)
  d.line((236,333,284,333),fill=(241,211,185,200),width=2)
 elif mood=="annoyed":
  d.line((236,327,285,324),fill=(112,52,60,255),width=4)
 elif mood=="suspicious":
  d.arc((238,313,287,340),195,356,fill=(105,55,59,255),width=4)
 elif mood=="sad":
  d.arc((234,319,290,366),200,340,fill=(109,58,58,255),width=4)
 else:
  d.arc((238,308,283,342),8,155,fill=(110,58,65,235),width=3)
 # character-specific costumes and silhouette accents
 if index==0: # knight pauldrons
  for x in (94,352):d.rounded_rectangle((x,392,x+82,471),radius=22,fill=(143,158,165,255),outline=(222,199,131,235),width=5)
  d.polygon([(203,427),(265,440),(318,424),(288,505),(229,505)],fill=(145,163,168,245),outline=(210,170,101,255))
 if index==1: # tiara, earrings, necklace
  d.arc((204,142,318,190),165,355,fill=(242,208,126,255),width=10)
  d.polygon([(258,147),(270,124),(280,147)],fill=(196,98,161,255))
  d.ellipse((167,310,185,334),fill=(227,181,95,255));d.ellipse((336,310,354,334),fill=(227,181,95,255))
  d.line((220,440,258,474,298,440),fill=(247,201,131,255),width=8)
 if index==2: # scars beard
  d.arc((198,279,329,393),0,178,fill=(62,47,38,255),width=32)
  d.line((312,217,291,272),fill=(148,82,68,255),width=5)
  for y in (429,461,493):d.line((217,y,310,y),fill=(143,103,68,200),width=6)
 if index==3: # glasses and potion crest
  for x in (215,301):d.ellipse((x-32,220,x+32,279),outline=(216,161,90,255),width=6)
  d.line((247,235,269,236),fill=(216,161,90,255),width=5)
  d.polygon([(254,478),(231,521),(280,521)],fill=(85,188,164,245),outline=(233,196,111,255))
 if index==4: # hood silhouette
  d.polygon([(131,278),(135,145),(214,85),(308,98),(378,166),(390,322),(355,215),(304,157),(229,157),(171,221)],fill=(46,52,65,247),outline=(103,91,106,245))
  d.polygon([(146,245),(182,156),(220,137),(170,324)],fill=(35,42,51,195))
 if index==5: # braided hair and merchant medallion
  for y in range(255,430,22):d.ellipse((161,y,189,y+29),fill=(158,91,51,255),outline=(209,147,85,190))
  d.ellipse((246,460,277,493),fill=(239,199,110,255));d.ellipse((256,469,266,482),fill=(113,82,58,255))
 if index==6: # broad pointed wizard cap
  d.polygon([(139,194),(245,25),(347,207)],fill=(62,81,139,255),outline=(189,158,95,255))
  d.polygon([(111,203),(380,203),(366,224),(126,224)],fill=(45,66,116,255))
  d.ellipse((259,142,277,158),fill=(240,202,103,255))
 if index==7: # red scarf and ornate pauldrons
  d.polygon([(209,397),(337,392),(310,464),(194,489)],fill=(186,66,63,255))
  d.ellipse((84,408,164,486),fill=(190,129,90,255),outline=(230,190,113,235),width=4)
  d.ellipse((355,408,433,486),fill=(190,129,90,255),outline=(230,190,113,235),width=4)
 if index==8: # moon circlet
  d.arc((196,120,323,204),175,355,fill=(213,198,161,255),width=8)
  d.ellipse((256,127,271,144),fill=(134,208,222,255))
 if index==9: # feather hat
  d.ellipse((138,137,374,227),fill=(93,62,43,255))
  d.polygon([(158,174),(189,77),(319,83),(358,178)],fill=(111,75,47,255),outline=(226,176,94,255))
  d.polygon([(335,158),(381,50),(354,61),(319,160)],fill=(112,166,141,255))
 # warm painterly highlight
 d.arc((173,151,348,356),207,289,fill=(255,224,183,72),width=4)
 im.save(target,compress_level=2)

if __name__=='__main__':
 from sys import path
 path.insert(0,str(Path(__file__).resolve().parents[1]))
 from backend.content import NPCS
 make_bg();counter()
 for i,n in enumerate(NPCS):
  for mood in ("neutral","happy","delighted","suspicious","annoyed","furious","sad","amused","surprised","skeptical"):
   portrait(i,n['id'],mood)
 print('Generated',len(list(ROOT.glob('*.png'))),'original PNG assets')
