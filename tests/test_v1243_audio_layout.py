"""V1.2.4.3 layout and real-audio wiring contracts (native Godot playtest remains separate)."""
from pathlib import Path
import hashlib,re,json
ROOT=Path(__file__).resolve().parents[1]
MAIN=(ROOT/'godot/scripts/Main.gd').read_text()
WAVE=(ROOT/'godot/scripts/AudioWaveformMeter.gd').read_text()
EMOTION=(ROOT/'godot/scripts/EmotionGlyph.gd').read_text()


def test_opaque_dedicated_audio_cards_and_no_old_floating_meters():
    assert 'Rect2(218,768,393,55),Color("#081b29fa")' in MAIN
    assert 'Rect2(620,768,403,55),Color("#260e28fa")' in MAIN
    assert 'mic_wave_card.add_child(mic_wave_meter)' in MAIN
    assert 'visitor_wave_card.add_child(visitor_wave_meter)' in MAIN
    assert 'Vector2(24,726)' not in MAIN
    assert 'Vector2(680,548)' not in MAIN
    assert 'VISITOR AUDIO' not in MAIN
    assert 'voice_note=_text(mic_wave_card' in MAIN


def test_viewport_layout_has_distinct_nonoverlapping_audio_action_compose_rows():
    assert 'Rect2(110,519,913,189)' in MAIN
    assert 'Rect2(211,712,812,49)' in MAIN
    assert 'Rect2(218,830,806,65)' in MAIN
    assert 519+189<712
    assert 712+49<768
    assert 768+55<830
    assert 830+65<=900


def test_audio_waveforms_are_real_not_fake_and_both_stay_within_viewport():
    assert 'mic_wave_meter.push_level(microphone.live_rms,mic_live)' in MAIN
    assert 'visitor_wave_meter.push_level(hermes.audible_output_level(),visitor_live)' in MAIN
    assert 'var visitor_live: bool=voice_active and hermes.is_busy()' in MAIN
    assert 'var level: float=clampf(actual_level,0.0,1.0) if is_active else 0.0' in WAVE
    assert 'No random oscillation' in WAVE
    assert 'smoothed_level=' in WAVE


def test_four_utility_controls_stay_accessible_without_visitor_rail():
    assert 'Rect2(20,134,207,224)' in MAIN
    for button in ('Shelves','Shop Ledger','Relationships','World Leads'):
        assert button in MAIN
    assert 'left_rail=_ornate_panel' not in MAIN
    assert 'reaction_card=_ornate_panel' not in MAIN


def test_f4_does_not_open_f8_studio_or_trigger_other_side_effects():
    f4=MAIN.split('event.keycode == KEY_F4:',1)[1].split('event.keycode == KEY_F8:',1)[0]
    assert 'diagnostics_panel.visible' in f4
    assert '_toggle_performance_studio()' not in f4
    f8=MAIN.split('event.keycode == KEY_F8:',1)[1].split('event.keycode == KEY_F9:',1)[0]
    assert '_toggle_performance_studio()' in f8


def test_typography_uses_actual_speaker_level_not_assumed_word_timestamps():
    assert 'emotion_effect.set("voice_energy",hermes.audible_output_level() if visitor_live else 0.0)' in MAIN
    assert 'var voice_energy: float=0.0' in EMOTION
    assert 'voice_active' in EMOTION
    assert 'char_fx.relative_index' in EMOTION


def test_portrait_approval_blocker_is_preserved_and_exodia_unchanged():
    assert 'REJECTED_ART_LOCKED_TO_NEUTRAL' in MAIN
    assert 'selected_expression=actually_displayed' in MAIN
    assert 'if not bool(approval.get("approved",false))' in MAIN
    assert hashlib.sha256((ROOT/'backend/exodia.py').read_bytes()).hexdigest()==('3682ae40ca6d80c60a1c8d759b657f26a998a0ee7be09a4358faf5bcf9da2263')
    state=json.loads((ROOT/'godot/assets/character_art_status_v123.json').read_text())
    assert all(not state[id]['approved'] for id in ('master_chen','tarek_ashwood','felix_rowe','safiya','rin_kaede','yuna_seo','mara_copperwell'))


def test_release_versions_match_and_docs_are_explicit_about_art_gate():
    project=(ROOT/'godot/project.godot').read_text()
    assert 'V1.2.4.4' in MAIN and 'V1.2.4.4' in project
    assert 'The portrait gate remains locked' in (ROOT/'docs/V1243_AUDIO_LAYOUT.md').read_text()
