"""V0.7 source-directed tests. These exercise the SAME regex specifications used
by DialogueDirector.gd rather than mirroring a second set of match patterns.
Godot visual/runtime acceptance remains separate (see docs/V07_ACCEPTANCE.md).
"""
import json
import re
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
GODOT = ROOT / "godot"
DIRECTOR = (GODOT / "scripts/DialogueDirector.gd").read_text()
STUDIO = (GODOT / "scripts/DialogueTestStudio.gd").read_text()
MAIN = (GODOT / "scripts/Main.gd").read_text()
GLYPH = (GODOT / "scripts/EmotionGlyph.gd").read_text()
EXODIA = (ROOT / "backend/exodia.py").read_text()


def rules():
    """Decode exact Godot JSON-compatible rule literals."""
    out = []
    for line in DIRECTOR.splitlines():
        if line.lstrip().startswith('{"kind":') and '"rx"' in line:
            raw = line.strip().removesuffix(',')
            out.append(json.loads(raw))
    return out


def matched_categories(line):
    return {item['kind'] for item in rules() if re.search(item['rx'], line)}


def test_all_effect_categories_have_live_pattern_and_glyph_animation():
    expected = {'gold', 'anger', 'persuade', 'doubt', 'delight', 'flirt', 'agreement'}
    assert expected <= {item['kind'] for item in rules()}
    assert expected <= set(re.findall(r'"(gold|anger|persuade|doubt|delight|flirt|agreement)":\{', DIRECTOR))
    assert '[emote kind=%s power=%.2f]' in DIRECTOR
    assert 'char_fx.env.get("power",1.0)' in GLYPH
    for cat in expected:
        assert f'kind == "{cat}"' in GLYPH or f'"{cat}"' in GLYPH


def test_actual_rules_match_target_bilingual_dialogue():
    cases = [
        ('That item is worth 67 gold.', 'gold'),
        ('How dare you! This is ridiculous!', 'anger'),
        ('Perhaps a better deal?', 'persuade'),
        ('Really? Are you sure?', 'doubt'),
        ('Wonderful! An amazing find!', 'delight'),
        ('Would you go on a date with me?', 'flirt'),
        ('That sounds fair.', 'agreement'),
        ('这个价格太贵了！', 'anger'),
        ('能不能便宜一点？', 'persuade'),
        ('真的吗？', 'doubt'),
        ('喜欢你', 'flirt'),
    ]
    for phrase, category in cases:
        assert category in matched_categories(phrase), (phrase, category)


def test_local_studio_uses_same_director_and_no_server_calls():
    assert 'Director.perform(sample_line' in STUDIO
    assert 'DialogueDirector.perform(line,mood,performance_intensity)' in MAIN
    assert 'KEY_F8' in MAIN
    assert 'performance_studio.visible=false' in MAIN
    assert 'func _fire_performance_cues' in MAIN
    assert '_act_out_cue(' in MAIN
    assert 'intensity_changed' in STUDIO
    assert 'emphasis_intensity' in MAIN
    assert 'http://' not in STUDIO
    assert 'HTTPRequest' not in STUDIO
    assert 'HermesStream' not in STUDIO
    assert 'speak(' not in STUDIO


def test_glyph_reveal_and_audio_timing_remain_enabled():
    assert 'hermes.heard_seconds()' in MAIN
    assert 'dialogue_label.visible_characters=reveal_count' in MAIN
    assert '_fire_performance_cues(visible_now)' in MAIN
    assert '_fire_performance_cues(maxi(0,dialogue_label.visible_characters))' in MAIN
    assert '[revealpop]' in MAIN
    assert 'typing_fx.volume_db=-25.0' in MAIN
    assert 'script' not in (GODOT / 'scenes/Main.tscn').read_text() or (GODOT / 'scripts/DialoguePop.gd').exists()


def test_legacy_exodia_api_profile_contract_preserved():
    for provider in ('chatgpt', 'gemini', 'deepseek', 'groq', 'gemini-api'):
        assert f"'{provider}'" in EXODIA
    assert "('groq', 'gemini-api')" in EXODIA
    assert "else 'browser'" in EXODIA
    assert "'/api/command/tasks/game-dialogue'" in EXODIA
    assert (ROOT / 'docs/EXODIA_API_PROVIDERS.md').exists()


def test_portraits_are_real_rgba_assets_for_f8_studio():
    for identity in ('maya', 'liu_xue'):
        for emotion in ('neutral', 'thinking', 'amused', 'skeptical', 'annoyed'):
            path = GODOT / 'assets' / f'vn_{identity}_{emotion}.png'
            assert path.is_file(), path
            with Image.open(path) as im:
                assert im.mode == 'RGBA'
                alpha = im.getchannel('A').getextrema()
                assert alpha[0] == 0 and alpha[1] == 255
