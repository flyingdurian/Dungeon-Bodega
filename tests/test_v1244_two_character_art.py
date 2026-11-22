"""V1.2.4.4 two-actor illustrated portraits: asset fidelity + truth in runtime preview.

This intentionally DOES NOT assert production approval or native Godot playback.
"""
from pathlib import Path
import hashlib, json
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
ASSET=ROOT/'godot/assets'
STATES=('neutral','thinking','amused','skeptical','annoyed')
PAIRS=('master_chen','tarek_ashwood')


def test_each_character_has_five_distinct_real_native_rgba_master_files():
    for actor in PAIRS:
        unique=set()
        for state in STATES:
            file=ASSET/f'vn_{actor}_{state}.png'
            assert file.is_file() and file.stat().st_size>500_000, file
            unique.add(hashlib.sha256(file.read_bytes()).hexdigest())
            with Image.open(file) as img:
                assert img.size==(1024,1536), (file,img.size)
                assert img.mode=='RGBA'
                alpha=img.getchannel('A')
                assert alpha.getextrema()==(0,255), (file,alpha.getextrema())
                assert alpha.getpixel((0,0))==0
                assert alpha.getpixel((512,720))>=245
                assert sum(n for i,n in enumerate(alpha.histogram()) if i==0)>0.05*img.width*img.height
        assert len(unique)==5, f'duplicated images for {actor}'


def test_f2_uses_same_independent_images_as_normal_dialogue():
    for actor in PAIRS:
        for state in STATES:
            name=f'vn_{actor}_{state}.png'
            assert (ASSET/'art_review'/name).read_bytes()==(ASSET/name).read_bytes()


def test_engine_uses_real_portrait_variants_during_normal_encounters():
    code=(ROOT/'godot/scripts/Main.gd').read_text()
    assert 'LIVE_PORTRAIT_TRIAL_IDS := ["master_chen", "tarek_ashwood"]' in code
    assert 'if id in LIVE_PORTRAIT_TRIAL_IDS:' in code
    assert 'path="res://assets/vn_%s_%s.png" % [id,selected_trial]' in code
    assert 'fallback_reason="FIVE_STATE_TRIAL_NOT_APPROVED"' in code
    assert '"TRIAL_NEAREST_STATE_NOT_APPROVED"' in code
    assert 'selected_expression=actually_displayed' in code
    assert 'REJECTED_ART_LOCKED_TO_NEUTRAL' in code
    # No simultaneous full-face crossfade or unwanted expression thumbnail UI.
    assert 'fading.texture=portrait.texture' not in code
    assert 'if reaction_card!=null:reaction_card.visible=false' in code


def test_strict_art_approval_is_still_blocked_for_seven_characters():
    signed=json.loads((ASSET/'character_art_status_v123.json').read_text())
    manifest=json.loads((ROOT/'art/portrait_trial_v1244.json').read_text())
    assert not manifest['owner_approved']
    assert manifest['required_by_art_bible']==12
    assert set(manifest['scope_characters'])==set(PAIRS)
    assert all(not signed[actor]['approved'] for actor in signed)
    assert all(len(manifest['scope_characters'][actor]['states'])==5 for actor in PAIRS)


def test_old_rejected_five_visitors_keep_locked_neutral_path():
    code=(ROOT/'godot/scripts/Main.gd').read_text()
    for actor in ('felix_rowe','safiya','rin_kaede','yuna_seo','mara_copperwell'):
        assert actor in code.split('const REJECTED_ART_IDS :=')[1].split('\n')[0]
        assert actor not in code.split('const LIVE_PORTRAIT_TRIAL_IDS :=')[1].split('\n')[0]


def test_version_and_unchanged_exodia_provider_contract():
    code=(ROOT/'godot/scripts/Main.gd').read_text()
    project=(ROOT/'godot/project.godot').read_text()
    assert 'V1.2.4.4' in code and 'V1.2.4.4' in project
    assert hashlib.sha256((ROOT/'backend/exodia.py').read_bytes()).hexdigest()==('3682ae40ca6d80c60a1c8d759b657f26a998a0ee7be09a4358faf5bcf9da2263')
