"""Static composite of REAL in-project V0.5 assets; NOT a running Godot screenshot."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
BASE=Path(__file__).resolve().parents[1]
A=BASE/'godot'/'assets'
im=Image.open(A/'shop_bg_v04.png').convert('RGBA')
character=Image.open(A/'vn_maya_thinking.png').convert('RGBA')
# Godot portrait TextureRect 520x660 with aspect fit centered inside the rectangle.
character.thumbnail((520,660),Image.Resampling.LANCZOS)
im.alpha_composite(character,(508+(520-character.width)//2,113))
item=Image.open(A/'item_mana_potion.png').convert('RGBA').resize((170,164),Image.Resampling.LANCZOS)
im.alpha_composite(item,(750,456))
im.alpha_composite(Image.open(A/'counter_overlay.png').convert('RGBA'))
d=ImageDraw.Draw(im,'RGBA')
boxes=[(22,18,1418,88),(22,107,311,753),(22,767,311,877),(1080,107,1418,593),(335,609,1418,764),(335,777,1418,877)]
for box in boxes:
    d.rounded_rectangle(box,radius=13,fill=(17,29,37,239),outline=(183,143,94,230),width=2)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
F=lambda n,heavy=False:ImageFont.truetype(bold if heavy else font,n)
def txt(s,x,y,n=17,col=(241,229,210),heavy=False):d.text((x,y),s,font=F(n,heavy),fill=col)
G=(239,202,139);M=(188,180,166);W=(244,234,219)
txt('THE LIVING COUNTER',43,29,30,G,True)
txt('V0.5  PRESENCE & RESPONSE',44,63,12,M)
txt('WAIT 2.4s   /   PROMPT 940',466,44,14,G,True)
txt('DAY 2',796,42,16,W);txt('520 GOLD',926,42,19,G,True)
txt('EXODIA / HERMES',1110,42,13,M)
txt('YOUR SHELVES',43,128,21,G,True)
for i,(name,price) in enumerate([('Greater Mana Potion',50),('Crimson Healing Draught',38),('Moonsteel Dagger',115),('Charm of Dawn',72),('Scroll of Emberlight',42),('Wyvern Scale',88),('Silver Road Buckle',23),('Sageleaf Salve',18)]):
    y=196+i*51
    d.rounded_rectangle((37,y,296,y+43),radius=8,fill=(35,46,52,224),outline=(89,94,88,165))
    txt(name,48,y+6,12,W)
    txt(f'{price} gold',220,y+26,10,G)
txt('SHOP LEDGER',43,779,15,G,True);txt('F3: economy / F4: response stats',44,818,11,M)
txt('AT THE COUNTER',1100,128,17,G,True)
txt('Maya "Byte" Torres',1101,178,18,W,True)
txt('Gen Z Trend Seeker',1101,215,14,M)
txt('CURRENT MOOD',1101,257,12,G)
txt('Thinking...',1101,288,21,W)
txt('She is considering what you said.',1101,334,11,M)
txt('CURRENT ITEM',1101,404,13,G)
txt('Greater Mana Potion',1101,437,15,W)
txt('LISTED 50 G  /  OFFER 27 G',1101,491,14,G)
txt('BUYING FROM YOUR SHOP',1101,540,11,M)
for label,x,w in [('ACCEPT OFFER',342,165),('COUNTER +/- 10',516,202),('ASK LIST PRICE',727,176),('END NEGOTIATION',912,177)]:
    d.rounded_rectangle((x,556,x+w,598),radius=9,fill=(56,37,51,245),outline=(200,163,104,225),width=2)
    txt(label,x+10,569,11,W,True)
txt('MAYA IS THINKING...  2.4s  /  GEMINI',357,617,12,G,True)
txt('... ',356,666,34,W)
txt('soft counter tap / portrait expression while waiting',440,718,13,M)
d.rounded_rectangle((350,790,946,841),radius=8,fill=(35,37,48,255),outline=(126,109,99,155))
txt('Type a reply, or use the microphone...',363,806,14,M)
for label,x,w,color in [('SEND',956,110,(142,92,45,255)),('HOLD TO TALK',1072,167,(46,45,64,255)),('OPEN MIC',1245,154,(60,51,73,255))]:
    d.rounded_rectangle((x,790,x+w,841),radius=9,fill=color,outline=(189,143,111,215),width=2)
    txt(label,x+9,808,13,W,True)
txt('RELEASE TO SEND  /  OPEN MIC SENDS AFTER 1.2s SILENCE  /  F4 TOGGLES PERFORMANCE',354,848,10,M)
im.convert('RGB').save(BASE/'preview_layout_v05.png',quality=94,optimize=True)
print('preview_layout_v05.png')
