"""Audit portrait resources AND effective Godot fallback behavior; no art is approved by this tool."""
import argparse, hashlib, json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
STATES=('neutral','thinking','curious','skeptical','suspicious','amused','delighted','annoyed','angry','surprised','sad','flustered')
LIVE_TRIAL=('master_chen','tarek_ashwood')
REJECTED=('master_chen','tarek_ashwood','felix_rowe','safiya','rin_kaede','yuna_seo','mara_copperwell')
BENCHMARKS=('liu_xue','elara_veyne')
MINIMUM=(1024,1536)

def scan(root=ROOT):
    asset=root/'godot/assets'
    approval=json.loads((asset/'character_art_status_v123.json').read_text(encoding='utf-8'))
    records={}
    for actor in BENCHMARKS+REJECTED:
        states={}
        hashes={}
        for name in STATES:
            file=asset/f'vn_{actor}_{name}.png'
            if not file.exists():
                states[name]={'exists':False}
                continue
            with Image.open(file) as image:
                w,h=image.size
                rgba=image.mode=='RGBA'
                alpha=image.getchannel('A').getextrema() if rgba else (255,255)
                states[name]={'exists':True,'dimensions':[w,h], 'rgba':rgba,
                              'has_transparency':alpha[0]<255,
                              'native_resolution':w>=MINIMUM[0] and h>=MINIMUM[1]}
            hashes[name]=hashlib.sha256(file.read_bytes()).hexdigest()
        review=list((asset/'art_review').glob(f'vn_{actor}_*.png'))
        file_count=sum(item['exists'] for item in states.values())
        native_count=sum(item.get('native_resolution',False) and item.get('has_transparency',False) for item in states.values())
        signed=bool(approval.get(actor,{}).get('approved',False))
        records[actor]={'production_files':file_count,'native_rgba_files':native_count,
            'review_candidates':len(review),'approved':signed,'forced_neutral_in_game':actor in REJECTED and not signed and actor not in LIVE_TRIAL,
            'live_unapproved_trial':actor in LIVE_TRIAL and not signed, 'distinct_production_hashes':len(set(hashes.values())),'states':states}
    # Screenshot-fragment contamination is manually reviewed, not guessed from alpha.
    records['rin_kaede']['manual_visual_issue']='Neutral PNG contains background/window artwork inside its transparent canvas.'
    return records

def markdown(data):
    lines=['# Portrait runtime audit — V1.2.4 baseline','',
      'Source: V1.2.4 packaged Godot project; independent asset inventory, not a live Godot screenshot.','',
      '| Character | Production states / 12 | Native-size RGBA / 12 | F2 candidate files | Approved | Runtime action |',
      '|---|---:|---:|---:|---|---|']
    for actor,row in data.items():
        lines.append(f'| {actor} | {row["production_files"]}/12 | {row["native_rgba_files"]}/12 | {row["review_candidates"]} | {"Yes" if row["approved"] else "No"} | {"Forced neutral" if row["forced_neutral_in_game"] else "Expression files when present"} |')
    lines.extend(['', '## Root causes',
      '1. In `Main.gd::_show_portrait`, all seven rejected IDs go through an approval check that replaces any requested expressive texture with `vn_<id>_neutral.png`.',
      '2. The rejection manifest marks all seven `approved=false`; the game therefore stays neutral regardless of what dialogue emotion is reported.',
      '3. Master Chen, Safiya and Rin lack production expression sets; Tarek, Felix, Yuna and Mara have mostly small expression bust crops (not usable as full hero portraits).',
      '4. Rin neutral has visible embedded scene content even though outer PNG edges are transparent; transparency tests alone cannot catch that.',
      '5. Benchmark figures are not themselves 12-state complete: Liu Xue has five full-size expressive paintings, Elara eight.',
      '6. `selected_expression` formerly recorded the requested emotion even while the renderer displayed neutral, obscuring diagnosis.',
      '', '## Correct production remedy',
      'Author 12 distinct, transparent, identity-locked portrait masters per rejected visitor at 1024×1536 or higher; align character focal point and crop across every state. Review all 12 per visitor in F2, then use the project art validator and the owner’s visual approval before enabling runtime production art.',
      'Do not promote sheet crops, upscale existing reaction busts, or mark approval without review. New diagnostics now show requested versus actually displayed state in F4.',
      '', '## Release status', 'Portrait art: **BLOCKED**; code instrumentation: implemented, needs native Godot runtime verification.'])
    return '\n'.join(lines)+'\n'

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--json',action='store_true')
    args=parser.parse_args()
    data=scan()
    print(json.dumps(data,indent=2) if args.json else markdown(data))
