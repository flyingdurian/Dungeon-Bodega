"""Regression checks for the shipped V1.2.1 illustrated portrait integration."""
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
IDS=('mara_copperwell','tarek_ashwood','yuna_seo','felix_rowe')
STATES=('neutral','thinking','amused','skeptical','delighted','annoyed','surprised','sad','elated')

def test_character_assets_are_distinct_rgba_and_runtime_mapped():
    data=json.loads((ROOT/'art/character_art_runtime_v121.json').read_text())
    assert len(data['characters'])==4
    for actor in IDS:
        specs=data['characters'][actor]
        assert specs['ui_runtime_complete']
        assert not specs['production_art_complete']
        assert set(specs['states'])==set(STATES)
        unique=set()
        for state in STATES:
            f=ROOT/'godot/assets'/f'vn_{actor}_reaction_{state}.png'
            assert f.exists(),f
            with Image.open(f) as im:
                assert im.mode=='RGBA'
                assert im.width>=200 and im.height>=270
                assert im.getchannel('A').getextrema()[0]==0 and im.getchannel('A').getextrema()[1]>=240
            unique.add(hashlib.sha256(f.read_bytes()).hexdigest())
        assert len(unique)==len(STATES),actor
        assert (ROOT/'godot/assets'/f'vn_{actor}_thumb.png').exists()
        assert (ROOT/'godot/assets'/f'vn_{actor}_neutral.png').exists()

def test_character_master_is_stable_when_expression_changes():
    gd=(ROOT/'godot/scripts/Main.gd').read_text()
    assert 'func _update_v121_reaction(_id: String, _expression: String)' in gd
    assert 'reaction_card=_ornate_panel' not in gd
    assert 'path="res://assets/vn_%s_neutral.png" % id' in gd
    assert 'func _preview_v121_reaction()' in gd # dev preview helper kept, not bound in main screen
    assert 'KEY_F2' in gd  # V1.2.4: review-only shortcut, never gameplay art approval
    assert 'if reaction_card!=null:reaction_card.visible=false' in gd
    assert gd.count('func _show_portrait')==1


def test_gallery_shows_all_four_new_customers():
    gallery=(ROOT/'godot/scripts/VisitorGallery.gd').read_text()
    gd=(ROOT/'godot/scripts/Main.gd').read_text()
    for actor in IDS:
        assert actor in gallery
        assert actor in gd
    assert 'VisitorGallery.new()' in gd
    assert 'func _open_gallery_from_menu' in gd
    # Rejected compact rail is gone; the gallery retains all new visitors.
    assert 'left_rail=_ornate_panel' not in gd

def test_exodia_contract_is_identical_to_v12_source():
    expected='3682ae40ca6d80c60a1c8d759b657f26a998a0ee7be09a4358faf5bcf9da2263'
    assert hashlib.sha256((ROOT/'backend/exodia.py').read_bytes()).hexdigest()==expected
    assert (ROOT/'backend/app.py').read_text().count("'1.2.4'")>=1
