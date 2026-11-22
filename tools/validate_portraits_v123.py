"""Strict, reproducible production-art gate for The Living Counter.

No source-sheet crops / low-res expression busts are counted as native masters.
Owner approval is separate from technical dimensions and transparency.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SPEC=json.loads((ROOT/'art/character_art_contract_v123.json').read_text(encoding='utf-8'))
STATES=tuple(SPEC['states'])
CHARACTERS=tuple(SPEC['characters'])
MIN_W,MIN_H=SPEC['native_min_resolution']

def audit() -> dict:
    signed=json.loads((ROOT/'godot/assets/character_art_status_v123.json').read_text(encoding='utf-8'))
    report={}
    for actor in CHARACTERS:
        state_report={}
        signatures=[]
        for state in STATES:
            path=ROOT/'godot/assets'/f'vn_{actor}_{state}.png'
            if not path.is_file():
                state_report[state]={'result':'MISSING'}
                continue
            try:
                with Image.open(path) as im:
                    dimensions=list(im.size)
                    alpha=im.mode=='RGBA' and im.getchannel('A').getextrema()[0]<=10
                    native=im.width>=MIN_W and im.height>=MIN_H
                    ok=alpha and native
                    state_report[state]={'result':'PASS_TECHNICAL' if ok else 'REJECT_SIZE_OR_ALPHA', 'dimensions':dimensions,'rgba':im.mode=='RGBA','transparent_edges':alpha}
                    if ok:signatures.append(hashlib.sha256(path.read_bytes()).hexdigest())
            except Exception as exc:
                state_report[state]={'result':'UNREADABLE','error':str(exc)}
        unique=len(set(signatures))==len(STATES)
        tech_pass=len(signatures)==len(STATES) and unique
        owner_approved=bool(signed.get(actor,{}).get('approved',False))
        report[actor]={'technical_ready':tech_pass,'owner_approved':owner_approved,'production_ready':tech_pass and owner_approved,'distinct_files':unique,'passed_states':len(signatures),'required':len(STATES),'states':state_report}
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--strict',action='store_true')
    parser.add_argument('--json',action='store_true')
    a=parser.parse_args()
    r=audit()
    if a.json: print(json.dumps(r,indent=2))
    else:
        for name,entry in r.items():
            print(f'{name}: {entry["passed_states"]}/{entry["required"]} technical native RGBA, approved={entry["owner_approved"]}, production_ready={entry["production_ready"]}')
    if a.strict and not all(row['production_ready'] for row in r.values()):raise SystemExit(2)
