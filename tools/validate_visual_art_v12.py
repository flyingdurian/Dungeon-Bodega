"""Audit prior and newly introduced cast under the same non-placeholder art rule.

A genuine single portrait can be previewable without declaring an eight-state rig
production complete. A contact sheet or an upscaled small crop never passes.
"""
from __future__ import annotations
from pathlib import Path
from PIL import Image
import argparse, hashlib, json
ROOT=Path(__file__).resolve().parents[1]
STATES=('neutral','thinking','amused','skeptical','delighted','annoyed','surprised','sad')
CHARACTERS=('safiya','elara_veyne','rin_kaede','master_chen','mara_copperwell','tarek_ashwood','yuna_seo','felix_rowe')

def audit():
    results={}
    for name in CHARACTERS:
        results[name]={'states':{},'complete':False}
        digests=[]
        for expression in STATES:
            file=ROOT/'godot/assets'/f'vn_{name}_{expression}.png'
            if not file.exists():
                results[name]['states'][expression]='missing';continue
            try:
                with Image.open(file) as img:
                    rgba=img.mode=='RGBA'
                    w,h=img.size
                    transparent=rgba and img.getpixel((0,0))[3]<=30
                    status='pass' if rgba and w>=1024 and h>=1536 and transparent else 'needs_art_review'
                    results[name]['states'][expression]=status
                    if status=='pass':digests.append(hashlib.sha256(file.read_bytes()).hexdigest())
            except Exception:
                results[name]['states'][expression]='unreadable'
        results[name]['complete']=(len(digests)==8 and len(set(digests))==8)
    return results

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--strict',action='store_true');parser.add_argument('--json',action='store_true')
    a=parser.parse_args();data=audit()
    if a.json:print(json.dumps(data,indent=2))
    else:
        for k,v in data.items():
            print('%s: %d/8 native RGBA states; COMPLETE=%s'%(k,sum(x=='pass' for x in v['states'].values()),v['complete']))
    if a.strict and not all(v['complete'] for v in data.values()):raise SystemExit(2)
