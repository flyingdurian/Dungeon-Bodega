"""Transparent portrait and expression-set audit for The Living Counter.

Default: produce an honest report. --strict: return failure if *any* new character
has fewer than eight high-resolution original transparent assets.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
MANDATORY=('neutral','thinking','amused','skeptical','delighted','annoyed','surprised','sad')
CHARACTERS=('safiya','elara_veyne','rin_kaede','master_chen')

def check():
    report={}
    for cid in CHARACTERS:
        checks=[]
        for state in MANDATORY:
            f=ROOT/'godot'/'assets'/f'vn_{cid}_{state}.png'
            if not f.exists():
                checks.append({'expression':state,'status':'missing'})
                continue
            with Image.open(f) as img:
                w,h=img.size
                corners=(img.getpixel((0,0))[3] if img.mode=='RGBA' else 255)
                status='pass' if img.mode=='RGBA' and w>=1024 and h>=1536 and corners<30 else 'needs_rework'
                checks.append({'expression':state,'status':status,'size':[w,h],'RGBA':img.mode=='RGBA','transparent_corner':corners<30})
        report[cid]={'complete':all(c['status']=='pass' for c in checks),'assets':checks}
    return report

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--strict',action='store_true');ap.add_argument('--json',action='store_true')
    args=ap.parse_args();report=check()
    if args.json:print(json.dumps(report,indent=2))
    else:
        for cid,data in report.items():
            passed=sum(x['status']=='pass' for x in data['assets'])
            present=sum(x['status']!='missing' for x in data['assets'])
            print(f'{cid}: {passed}/8 production PASS; {present}/8 expression files present')
    if args.strict and not all(x['complete'] for x in report.values()):sys.exit(2)
