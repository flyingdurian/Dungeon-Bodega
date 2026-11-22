"""V0.9.2 renderer and API regression contract (static; native Godot is separate)."""
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]


def test_ui_has_real_trade_shelf_action_and_no_old_floating_labels():
    gd=(ROOT/'godot/scripts/Main.gd').read_text()
    assert 'func _stage_inspected_item()' in gd
    assert 'func _update_add_trade_button()' in gd
    assert '"bonus_items"' in gd
    assert 'Rect2(1039,728,375,74)' in gd
    assert 'Vector2(1062,369)' not in gd
    assert 'Vector2(205,782)' not in gd
    assert 'SOCIAL TERMS · %s gold' in gd


def test_microphone_status_explains_listening():
    gd=(ROOT/'godot/scripts/Main.gd').read_text()
    assert 'YOU  ·  RECORDING' in gd and 'YOU  ·  MIC READY' in gd
    assert 'YOU  ·  MIC OFF' in gd


def test_sad_type_animation_and_emotive_letterforms():
    director=(ROOT/'godot/scripts/DialogueDirector.gd').read_text()
    glyph=(ROOT/'godot/scripts/EmotionGlyph.gd').read_text()
    assert '"kind":"sad"' in director and '"sad":{"fg"' in director
    assert '"sad", "doubt", "flirt"' in director
    assert 'if cues.size()>=4' in director
    assert 'elif kind == "sad"' in glyph
    assert 'char_fx.relative_index' in glyph and 'absolute_index' not in glyph


def test_all_godot_scripts_use_consistent_indentation():
    for file in (ROOT/'godot/scripts').glob('*.gd'):
        lines=file.read_text().splitlines()
        indents={('tab' if x.startswith('\t') else 'space') for x in lines
                 if x.startswith(('\t',' ')) and x.strip() and not x.lstrip().startswith('#')}
        assert len(indents)<=1, str(file)


def test_important_files_preserve_exodia_api_provider_contract():
    src=(ROOT/'backend/exodia.py').read_text()
    assert "'groq', 'gemini-api'" in src
    assert "/api/command/tasks/game-dialogue" in src
    assert "'transport': 'api' if self.provider in ('groq', 'gemini-api') else 'browser'" in src
    assert (ROOT/'docs/EXODIA_API_PROVIDERS.md').exists()
