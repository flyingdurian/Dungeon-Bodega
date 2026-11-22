"""V1.0 explicit roster, gallery, artwork and compatibility regression gates."""
from pathlib import Path
import json
import re
from PIL import Image
import pytest
from backend.content import NPCS, NPC_BY_ID, OFFLINE_FLAVOR
from backend.engine import ShopGame
from backend import exodia

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'godot/assets'
CAST=('safiya','elara_veyne','rin_kaede','master_chen')


def test_four_unique_archetypes_and_balance():
    assert len(NPCS)==29 and len({p['id'] for p in NPCS})==29
    assert sum(p['era']=='fantasy' for p in NPCS)==15
    assert sum(p['era']=='modern' for p in NPCS)==14
    for id in CAST:
        npc=NPC_BY_ID[id]
        assert npc['personality'] and npc['strategy'] and npc['lore']
        assert len(OFFLINE_FLAVOR[id])>=3
        assert 0<npc['patience']<=100
        assert 0<npc['trust']<=100


def test_each_new_customer_is_authentic_encounter_and_can_converse():
    for id in CAST:
        game=ShopGame(seed=17)
        scene=game.open_encounter(id,era=NPC_BY_ID[id]['era'])
        assert scene['customer']['id']==id
        followup,_=game.take_turn(scene['session_id'],"Tell me why you're interested in this antique",1)
        assert str(followup['event']) not in ('deal','walkout')
        assert game.sessions[scene['session_id']]['turn']==1


def test_all_new_art_assets_are_real_rgba_files():
    for id in CAST:
        for filename in (f'vn_{id}_neutral.png',f'vn_{id}_thumb.png'):
            p=ART/filename
            assert p.exists() and p.stat().st_size>10_000, filename
            with Image.open(p) as im:
                assert im.mode=='RGBA'
                assert im.width>=300
                assert im.height>=300
                if filename.endswith('_neutral.png'):
                    assert im.getextrema()[3][0]==0
                assert im.getextrema()[3][1]==255


def test_four_voice_preset_ids_exist_in_hermes_manifest():
    manifest=json.loads((ART/'hermes_profile_manifest.json').read_text())
    for id in CAST:
        voice=NPC_BY_ID[id]['chatterbox']
        assert voice in manifest,(id,voice)
        assert manifest[voice]['qwen'] and manifest[voice]['instruct']


def test_native_ui_gallery_and_new_environment_references():
    main=(ROOT/'godot/scripts/Main.gd').read_text()
    gallery=(ROOT/'godot/scripts/VisitorGallery.gd').read_text()
    assert 'const VisitorGallery = preload("res://scripts/VisitorGallery.gd")' in main
    assert 'func _on_gallery_choose(' in main
    assert 'visitor_gallery.connect("selected",Callable(self,"_on_gallery_choose"))' in main
    assert 'KEY_F11' in main
    assert all(id in main and id in gallery for id in CAST)
    assert 'shop_bg_v100_jade_atelier.jpg' in main
    assert 'shop_bg_v061_dynasty.png' in main
    assert 'shop_theme="jade"' in main
    assert 'dialogue.substr(first,last-first)' in main
    assert (ART/'shop_bg_v100_jade_atelier.jpg').stat().st_size>250000
    assert 'window/size/viewport_width=1440' in (ROOT/'godot/project.godot').read_text()


def test_no_screen_paste_or_old_portrait_crossfade():
    main=(ROOT/'godot/scripts/Main.gd').read_text()
    assert 'v061_hud_overlay' not in main
    assert 'fading.texture=portrait.texture' not in main
    assert 'func _show_portrait' in main
    assert 'res://assets/vn_%s_neutral.png' in main
    assert 'voice_lock_session=sid' in main


def test_five_provider_exodia_contract_preserved():
    src=(ROOT/'backend/exodia.py').read_text()
    assert set(exodia.PROVIDERS)=={'chatgpt','gemini','deepseek','groq','gemini-api'}
    assert "'transport': 'api' if self.provider in ('groq', 'gemini-api') else 'browser'" in src
    assert "/api/command/tasks/game-dialogue" in src
    assert 'GROQ_API_KEY' not in (ROOT/'.env.example').read_text()


def test_release_docs_and_versions():
    from backend.app import app
    assert app.version in ('1.0.0','1.1.0','1.2.0','1.2.1','1.2.2','1.2.3','1.2.4.4')
    assert 'V1.2.4.4 Two-Visitor Portrait QA Candidate' in (ROOT/'godot/project.godot').read_text()
    for file in ('CHANGELOG_V100.md','docs/V100_ACCEPTANCE.md','docs/V100_ART_BIBLE.md'):
        assert (ROOT/file).exists()
