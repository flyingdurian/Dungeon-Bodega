"""Extract four V1.2 expression sheets into independently loadable transparent VN sprites.

Run from the project root with Python + Pillow. Source sheets stay under
art/source_sheets_v121. The sheet's small faces are deliberately NOT upscaled
and are used as reaction busts, while a separate large master anchors the actor.
"""
from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
import json, shutil
import numpy as np
import cv2

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'godot'/'assets'
SOURCE=ROOT/'art'/'source_sheets_v121'
STATES=['neutral','amused','delighted','skeptical','surprised','annoyed','thinking','sad']
# Cell order reads from upper-left to lower-right. Last source tile is a broad
# happy/relieved expression; 'sad' is the most subdued of the available tiles.
# Artistic accuracy of the sadness state is tracked as a remaining art note.
SPEC={
 'mara_copperwell':{'sheet':'mara_copperwell_expression_sheet.png', 'master':(0,0,475,1383),
    'cells':[(480,0,790,347),(790,0,1122,347),(480,350,790,688),(790,350,1122,688),(480,692,790,1016),(790,692,1122,1016),(480,1020,790,1383),(790,1020,1122,1383)],
    'states':['sad','amused','delighted','skeptical','surprised','annoyed','thinking','elated']},
 'tarek_ashwood':{'sheet':'tarek_ashwood_expression_sheet.png','master':(0,0,497,881),
    'cells':[(506,0,800,449),(800,0,1122,449),(506,451,800,884),(800,451,1122,884),(0,892,280,1382),(280,892,504,1382),(504,892,817,1382),(817,892,1122,1382)],
    'states':['sad','amused','delighted','skeptical','surprised','annoyed','thinking','elated']},
 'yuna_seo':{'sheet':'forensic_gemologist_expression_sheet.png','master':(0,0,463,883),
    'cells':[(468,0,790,444),(790,0,1122,444),(468,447,790,883),(790,447,1122,883),(0,892,276,1383),(276,892,552,1383),(552,892,829,1383),(829,892,1122,1383)],
    'states':['sad','amused','delighted','skeptical','surprised','annoyed','thinking','elated']},
 'felix_rowe':{'sheet':'felix_rowe_expression_sheet.png','master':(0,0,480,1383),
    'cells':[(482,0,790,347),(790,0,1122,347),(482,350,790,688),(790,350,1122,688),(482,692,790,1018),(790,692,1122,1018),(482,1020,790,1383),(790,1020,1122,1383)],
    'states':['sad','amused','delighted','skeptical','surprised','annoyed','thinking','elated']},
}

def clean_alpha(img:Image.Image, name:str) -> Image.Image:
    arr=np.array(img.convert('RGBA'),dtype=np.uint8)
    a=arr[:,:,3].astype(np.float32)
    a[a<16]=0
    if name=='tarek_ashwood':
        # The supplied Tarek sheet contains gray, low-opacity compositing haze.
        # Remove its gray matte and preserve saturated skin/clothing/ink detail.
        rgb=arr[:,:,:3].astype(np.int16)
        sat=rgb.max(2)-rgb.min(2)
        lum=rgb.mean(2)
        dusty=(sat<23)&(lum>125)
        a[dusty]=0
        a[(sat<32)&(lum>157)&(a<245)]=0
        a[a<105]=0
    # Remove stray neighboring-tile fragments and checker/matte islands.
    solid=(a>=95).astype(np.uint8)
    count, components, stats, _=cv2.connectedComponentsWithStats(solid,8)
    if count>1:
        biggest=1+int(np.argmax(stats[1:,cv2.CC_STAT_AREA]))
        primary=(components==biggest).astype(np.uint8)
        primary=cv2.dilate(primary,np.ones((3,3),np.uint8),iterations=1)
        a=np.where(primary>0,a,0)
    arr[:,:,3]=a.astype('uint8')
    return Image.fromarray(arr,'RGBA')

def trim(img:Image.Image,padding:int=3)->Image.Image:
    bbox=img.getchannel('A').point(lambda a:255 if a>35 else 0).getbbox()
    if not bbox:raise ValueError('Empty art tile')
    x0,y0,x1,y1=bbox
    return img.crop((max(0,x0-padding),max(0,y0-padding),min(img.width,x1+padding),min(img.height,y1+padding)))

def build():
    ASSETS.mkdir(exist_ok=True,parents=True)
    manifest={'version':'1.2.1','source':'newly generated individual-expression character-sheet paintings', 'display':'master neutral actor with separate emotion-specific cut-in', 'characters':{}}
    for id,cfg in SPEC.items():
        sheet=Image.open(SOURCE/cfg['sheet']).convert('RGBA')
        master_path=ASSETS/f'vn_{id}_neutral.png'
        if id!='mara_copperwell':
            master=trim(clean_alpha(sheet.crop(cfg['master']),id))
            master.save(master_path,optimize=True)
        else:
            # Retain the existing independent 1024x1536 master, which is finer
            # and aligns with the sheet more closely than a cropped 480px copy.
            assert master_path.exists(), 'Mara full-size master missing'
            master=Image.open(master_path).convert('RGBA')
        # Main thumbnails come from the actual actor, never from a concept UI.
        alpha_bbox=master.getchannel('A').getbbox()
        focus=master.crop((max(0,alpha_bbox[0]),max(0,alpha_bbox[1]),min(master.width,alpha_bbox[2]),min(master.height,alpha_bbox[1]+int((alpha_bbox[2]-alpha_bbox[0])*1.12))))
        thumb=Image.new('RGBA',(320,320),(0,0,0,0))
        focus.thumbnail((310,310),Image.Resampling.LANCZOS)
        thumb.alpha_composite(focus,((320-focus.width)//2,(320-focus.height)//2))
        thumb.save(ASSETS/f'vn_{id}_thumb.png',optimize=True)
        states={}
        # A calm close-up from the independent master is the neutral cut-in.
        focus_for_reaction=trim(focus.copy(),2)
        neutral_path=ASSETS/f'vn_{id}_reaction_neutral.png'
        focus_for_reaction.save(neutral_path,optimize=True)
        states['neutral']={'reaction_file':neutral_path.relative_to(ROOT).as_posix(), 'source_pixels':list(focus_for_reaction.size), 'alpha':True}
        for cell,state in zip(cfg['cells'],cfg['states']):
            crop=trim(clean_alpha(sheet.crop(cell),id),2)
            output=ASSETS/f'vn_{id}_reaction_{state}.png'
            crop.save(output,optimize=True)
            if state!='neutral':
                # Preserve standard path for other UI consumers; main scene
                # intentionally does NOT stretch the 300px reaction bust.
                crop.save(ASSETS/f'vn_{id}_{state}.png',optimize=True)
            states[state]={'reaction_file':output.relative_to(ROOT).as_posix(), 'source_pixels':list(crop.size), 'alpha': True}
        manifest['characters'][id]={'master':master_path.relative_to(ROOT).as_posix(),'master_pixels':list(master.size), 'states':states,
           'ui_runtime_complete': True,'production_art_complete': False,
           'note':'Eight required reaction states plus one extra elated state are wired; full-resolution eight-pose paintings and a stronger grief/sadness pose still require art approval.'}
    manifest_file=ROOT/'art'/'character_art_runtime_v121.json'
    manifest_file.parent.mkdir(parents=True,exist_ok=True)
    manifest_file.write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    return manifest

if __name__=='__main__':
    data=build()
    for name,c in data['characters'].items():print(name,c['master_pixels'],{k:v['source_pixels'] for k,v in c['states'].items()})
