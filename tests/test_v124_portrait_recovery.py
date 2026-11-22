"""V1.2.4 recovery gate: usable preview with production artwork protected."""
from pathlib import Path
import hashlib
import json
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
REJECTED=('master_chen','tarek_ashwood','felix_rowe','safiya','rin_kaede','yuna_seo','mara_copperwell')
STATES=('neutral','thinking','curious','skeptical','suspicious','amused','delighted','annoyed','angry','surprised','sad','flustered')


def test_master_chen_five_native_originals_in_trial():
    stage=ROOT/'godot/assets/art_review'
    paths=[stage/f'vn_master_chen_{state}.png' for state in ('neutral','amused','thinking','skeptical','annoyed')]
    assert all(p.is_file() for p in paths)
    assert len({hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})==5
    for p in paths:
        with Image.open(p) as im:
            assert im.size==(1024,1536)
            assert im.mode=='RGBA'
            assert im.getpixel((0,0))[3]<=10
            assert im.getpixel((im.width//2,im.height//2))[3]>=200


def test_art_preview_does_not_approve_unfinished_characters():
    signed=json.loads((ROOT/'godot/assets/character_art_status_v123.json').read_text())
    contract=json.loads((ROOT/'art/character_art_contract_v123.json').read_text())
    assert tuple(contract['characters'])==REJECTED
    assert tuple(contract['states'])==STATES
    assert all(not signed[id]['approved'] for id in REJECTED)
    notes=json.loads((ROOT/'art/portrait_recovery_v124.json').read_text())
    assert notes['candidate_status']=='INCOMPLETE_4_OF_12'
    assert not notes['owner_approved']


def test_f2_preview_is_bound_and_no_missing_state_fallback():
    gd=(ROOT/'godot/scripts/Main.gd').read_text()
    assert 'const REJECTED_ART_IDS :=' in gd
    assert 'KEY_F2' in gd and '_preview_v124_portrait()' in gd
    assert 'ART_REVIEW_ROOT' in gd and 'if ResourceLoader.exists(preview_path)' in gd
    assert 'if review_override and id in REJECTED_ART_IDS:' in gd
    assert 'elif id in REJECTED_ART_IDS:' in gd
    assert 'var options: Array[String]=[]' in gd
    assert 'var candidate_states: Array=LIVE_PORTRAIT_TRIAL_STATES if visitor_id in LIVE_PORTRAIT_TRIAL_IDS else PORTRAIT_REVIEW_STATES' in gd
    assert 'if ResourceLoader.exists(asset):' in gd
    assert '_show_portrait(visitor_id,chosen,true)' in gd
    assert 'UNAPPROVED' in gd
    assert 'path="res://assets/vn_%s_neutral.png" % id' in gd
    assert 'reaction_card=_ornate_panel' not in gd
    assert 'left_rail=_ornate_panel' not in gd


def test_review_only_version_contract():
    from backend.app import app
    assert app.version=='1.2.4.4'
    assert 'V1.2.4.4 Two-Visitor Portrait QA Candidate' in (ROOT/'godot/project.godot').read_text()
    for name in ('Shelves','Ledger','Relationships','Leads'):
        assert name.upper() in (ROOT/'godot/scripts/Main.gd').read_text().upper()
    assert (ROOT/'docs/V124_PORTRAIT_RECOVERY.md').exists()


def test_exodia_provider_file_unchanged_from_v123():
    expected='3682ae40ca6d80c60a1c8d759b657f26a998a0ee7be09a4358faf5bcf9da2263'
    assert hashlib.sha256((ROOT/'backend/exodia.py').read_bytes()).hexdigest()==expected
