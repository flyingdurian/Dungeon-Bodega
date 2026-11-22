"""Validate and install one *complete* original 12-state VN character rig.

Input: one independently illustrated native-size transparent image per emotion,
not contact-sheet slices. All validation occurs before any project file changes.
Installation leaves owner approval false until separate native Godot review.
"""
from __future__ import annotations
import argparse, hashlib, json, shutil
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
CONTRACT=json.loads((ROOT/'art/character_art_contract_v123.json').read_text())


def validate_source(character: str, directory: Path) -> tuple[bool,list[str]]:
    errors=[]
    signatures=[]
    if character not in CONTRACT['characters']:
        return False,[f'Unknown or non-rejected character: {character}']
    for emotion in CONTRACT['states']:
        p=directory/f'{emotion}.png'
        if not p.is_file():
            errors.append(f'{emotion}: missing independent PNG master')
            continue
        try:
            with Image.open(p) as im:
                if im.mode!='RGBA':errors.append(f'{emotion}: not RGBA')
                if im.width<1024 or im.height<1536:
                    errors.append(f'{emotion}: native size {im.width}×{im.height} below 1024×1536')
                if im.mode=='RGBA' and im.getchannel('A').getextrema()[0]>10:
                    errors.append(f'{emotion}: no genuinely transparent exterior')
                signatures.append(hashlib.sha256(p.read_bytes()).hexdigest())
        except Exception as exc:
            errors.append(f'{emotion}: unreadable ({exc})')
    if len(signatures)==len(CONTRACT['states']) and len(set(signatures))!=len(signatures):
        errors.append('Identical PNG content used for multiple emotions')
    return not errors,errors


def review_atlas(character: str, directory:Path, output:Path)->None:
    """Contact sheet for human inspection ONLY; never used as an in-game image."""
    states=CONTRACT['states']
    width,height=4*250,3*390
    canvas=Image.new('RGB',(width,height),(35,20,37))
    draw=ImageDraw.Draw(canvas)
    for i,emotion in enumerate(states):
        img=Image.open(directory/f'{emotion}.png').convert('RGBA')
        preview=ImageOps.contain(img,(228,340))
        x=(i%4)*250+(250-preview.width)//2
        y=(i//4)*390+8+(340-preview.height)//2
        canvas.paste(preview,(x,y),preview)
        draw.text(((i%4)*250+15,(i//4)*390+355),f'{character} · {emotion}',fill=(240,215,181))
    output.parent.mkdir(parents=True,exist_ok=True)
    canvas.save(output,quality=90)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--character',required=True)
    parser.add_argument('--source',type=Path,required=True,help='Folder with 12 independently illustrated <state>.png files')
    parser.add_argument('--install',action='store_true',help='Copy validated originals into Godot; does not approve artwork')
    a=parser.parse_args()
    okay,errors=validate_source(a.character,a.source)
    if not okay:
        print('ART REJECTED:')
        for err in errors:print(' -',err)
        raise SystemExit(2)
    review=ROOT/'art/reviews'/f'{a.character}_v123_review.jpg'
    review_atlas(a.character,a.source,review)
    print('12/12 technically valid distinct PNG masters, review atlas:',review)
    if a.install:
        dest=ROOT/'godot/assets'
        for state in CONTRACT['states']:
            shutil.copy2(a.source/f'{state}.png',dest/f'vn_{a.character}_{state}.png')
        # Never auto-approve: identity, emotion, and native layout still need review.
        status_file=dest/'character_art_status_v123.json'
        status=json.loads(status_file.read_text())
        status[a.character]['approved']=False
        status[a.character]['production_art_status']='IMPORTED_AWAITING_VISUAL_AND_RUNTIME_REVIEW'
        status_file.write_text(json.dumps(status,indent=2)+'\n')
        print('Installed original images. STATUS: awaiting owner approval; game keeps safe neutral art until signoff.')

if __name__=='__main__':main()
