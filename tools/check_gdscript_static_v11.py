"""Quick offline GDScript source sanity checks. NOT a substitute for native Godot parsing."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
issues=[]
for path in (ROOT/'godot/scripts').glob('*.gd'):
    for n,line in enumerate(path.read_text().splitlines(),1):
        if not line.strip():continue
        # Catch the exact V0.9 Hermes mixed-indentation regression.
        indentation=line[:len(line)-len(line.lstrip())]
        if '\t' in indentation and ' ' in indentation:
            issues.append(f'{path.name}:{n}: mixed tabs and spaces')
        # Visible unescaped double quotes should pair on a normal GDScript line.
        # This catches accidental Python patch escaping that created raw newlines
        # within Godot string literals in early development.
        count=0
        prev=''
        for ch in line:
            if ch=='"' and prev!='\\': count+=1
            prev=ch
        if count%2:
            issues.append(f'{path.name}:{n}: unbalanced string quotes')
print(f'Offline GDScript lint: {len(issues)} issues across {len(list((ROOT/"godot/scripts").glob("*.gd")))} scripts')
for issue in issues[:30]:print('  '+issue)
if issues:sys.exit(2)
