"""Static composition reference, not an in-engine screenshot."""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
A=BASE/'godot'/'assets'
im=Image.open(A/'shop_bg_v04.png').convert('RGBA')
p=Image.open(A/'customer_silas_suspicious.png').convert('RGBA')
im.alpha_composite(p,(508,113))
p=Image.open(A/'item_mana_potion.png').convert('RGBA').resize((170,164))
im.alpha_composite(p,(750,456))
im.alpha_composite(Image.open(A/'counter_overlay.png'))
d=ImageDraw.Draw(im,'RGBA')
for box in [(22,18,1418,88),(22,107,311,753),(22,767,311,877),(1080,107,1418,593),(335,609,1418,764),(335,777,1418,877)]:
 d.rounded_rectangle(box,radius=14,fill=(17,35,38,239),outline=(169,138,89,245),width=2)
font_path='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';bold_path='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
F=lambda n,b=False:ImageFont.truetype(bold_path if b else font_path,n)
def text(t,x,y,size=17,col=(234,227,206),bold=False):d.text((x,y),t,font=F(size,bold),fill=col)
G=(239,200,133);M=(176,169,149);W=(245,238,215)
text('THE LIVING COUNTER',43,28,31,G,True)
text('CROSSROADS / PROTOTYPE 0.4 · EXODIA + HERMES',44,66,11,M)
text('DAY 1',790,43,18,W);text('450 GOLD',923,42,21,G,True)
text('OFFLINE AI  |  HERMES',1096,43,14,M)
text('SETTINGS',1300,42,14,W,True)
text('YOUR SHELVES',43,128,23,G,True)
text('ITEMS IN STOCK',43,166,12,M)
items=[('Greater Mana Potion',50,4),('Crimson Healing Draught',38,6),('Moonsteel Dagger',115,2),('Charm of Dawn',72,3),('Scroll of Emberlight',42,4),('Wyvern Scale',88,1),('Silver Road Buckle',23,6),('Bottled Storm',130,2),('Sageleaf Salve',18,7)]
for i,(name,price,stock) in enumerate(items):
 y=196+i*46; d.rounded_rectangle((37,y,296,y+40),radius=8,fill=(32,53,55,230),outline=(81,111,99,170))
 text(name[:23],50,y+6,13,W)
 text(f'{price}g   x{stock}',218,y+23,10,G)
text('SHOP LEDGER',43,782,17,G,True)
text('No transaction yet.  F3: developer stats.',43,819,12,M)
text('AT THE COUNTER',1100,130,18,G,True)
text('Silas',1100,178,30,W,True)
text('The Shady Fence',1100,214,16,M)
text('DISPOSITION',1100,259,13,G)
text('Suspicious',1100,291,21,W)
text('They are watching you carefully.',1100,335,14,M)
text('ON THE COUNTER',1100,400,14,G)
text('Greater Mana Potion',1100,433,18,W)
text('LISTED 50 GOLD',1100,483,18,G,True)
text('OFFER 20 GOLD',1100,511,18,G)
text('THEY WANT TO BUY FROM YOUR SHOP',1100,546,11,M)
text('SILAS / SUSPICIOUS  ·  HERMES QWEN STREAM',356,620,13,G)
text('I have heard prettier offers from a drunken pickpocket.',356,660,18,W)
text('I can offer 20 gold for the Greater Mana Potion.',356,693,18,W)
text('What do you say?',356,726,18,W)
d.rounded_rectangle((350,790,1077,841),radius=8,fill=(34,52,54,255),outline=(113,114,101,170))
text('Ask anything, negotiate a price...',363,805,15,M)
d.rounded_rectangle((1087,791,1215,841),radius=8,fill=(163,112,61,255),outline=(242,180,110,220))
text('SEND',1111,806,15,W,True)
d.rounded_rectangle((1225,791,1400,841),radius=8,fill=(34,65,64,255),outline=(104,130,113,220))
text('HOLD MIC',1247,806,15,W,True)
# Action row is a faithful static counterpart to the v0.4 in-game button layout.
for label,x,w in [('ACCEPT OFFER',342,165),('COUNTER + / - 10G',516,202),('ASK LIST PRICE',727,176),('END NEGOTIATION',912,177)]:
 d.rounded_rectangle((x,556,x+w,598),radius=9,fill=(48,35,55,246),outline=(204,166,108,240),width=2)
 text(label,x+12,567,12,W,True)
text('INTERRUPT at any time by typing or holding the microphone.',356,849,12,M)
preview=BASE/'preview_layout.png'
im.convert('RGB').save(preview,optimize=True)
print(preview)
