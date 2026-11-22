"""Asset and source gates for the active V0.6.2 native Godot rebuild.

These are static validations. Native rendering, Exodia and Hermes require the user's Windows/Mac test.
"""
from pathlib import Path
import re
import wave
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'godot' / 'assets'
MAIN = (ROOT / 'godot' / 'scripts' / 'Main.gd').read_text()
DIRECTOR = (ROOT / 'godot' / 'scripts' / 'DialogueDirector.gd').read_text()


def test_character_expression_assets_are_transparent_and_high_resolution():
    for state in ('neutral', 'thinking', 'amused', 'skeptical', 'annoyed'):
        art = Image.open(ASSETS / f'vn_liu_xue_{state}.png').convert('RGBA')
        assert art.width >= 1000 and art.height >= 1200
        assert art.getextrema()[3][0] == 0
        assert art.getextrema()[3][1] == 255


def test_ui_is_constructed_from_native_controls_not_screenshot_overlay():
    assert 'shop_bg_v061_dynasty.png' in MAIN  # environment only
    assert 'vn_ui_ornaments_v061.png' not in MAIN
    assert 'expression_thumbs' not in MAIN
    assert 'func _preview_expression' not in MAIN
    assert 'THE DYNASTIC COUNTER' not in MAIN
    assert 'func _ornate_panel' in MAIN
    assert 'func _emotion_bbcode' in MAIN
    assert 'func _replay_voice' in MAIN
    assert 'func _on_enter_submit' in MAIN
    assert 'func _toggle_open_mic' in MAIN
    assert 'Rect2(110,519,913,189)' in MAIN
    assert 'Rect2(1036,81,378,284)' in MAIN
    assert 'dialogue_nameplate.text=' in MAIN
    assert 'offer_label.text=' in MAIN
    assert 'diagnostics_panel.visible=false' in MAIN
    assert '/api/command/tasks/game-dialogue' in (ROOT / 'backend' / 'exodia.py').read_text()


def test_five_primary_ctas_are_present_and_functional():
    for label, action in [
        ('Ask Price', '_quick_list_price'),
        ('Counter Offer', '_quick_counter'),
        ('Accept Deal', '_quick_accept'),
        ('End Chat', '_quick_end'),
        ('Next Visitor', '_begin_encounter'),
    ]:
        assert label in MAIN
        assert re.search(rf'\.pressed\.connect\({action}\)', MAIN)
    assert 'COUNTER OFFER DRAFT' in MAIN


def test_emotion_and_speech_reveal_are_on_screen():
    # V0.7 moves semantic categories out of Main.gd into a shared runtime
    # director, so the F8 studio and gameplay cannot drift apart.
    for term in ('better deal', '这个价格', '太贵', 'wonderful', 'bgcolor=', 'outline_color=', 'persuade'):
        assert term in DIRECTOR
    assert 'DialogueDirector.perform(line,mood,performance_intensity)' in MAIN
    assert 'speech_sync and hermes.is_busy()' in MAIN
    assert '_on_text_advanced' in MAIN
    assert 'typing_fx.volume_db=-25.0' in MAIN


def test_new_shop_audio_is_pcm_and_wired_to_events():
    for name in ('sfx_shop_bell_v062.wav', 'sfx_counter_settle_v062.wav', 'sfx_typewriter_v061.wav'):
        with wave.open(str(ASSETS / name), 'rb') as sound:
            assert sound.getnchannels() == 1
            assert sound.getframerate() == 24000
            assert sound.getnframes() > 900
    assert '_play_scene_sfx("sfx_shop_bell_v062.wav"' in MAIN
    assert '_play_scene_sfx("sfx_counter_settle_v062.wav"' in MAIN
