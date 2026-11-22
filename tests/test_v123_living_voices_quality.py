"""V1.2.3 owner quality-lock regression tests.
The strict production-art gate intentionally fails until real portraits are ready.
"""
from pathlib import Path
import hashlib, json
import importlib.util

ROOT=Path(__file__).resolve().parents[1]
MAIN=(ROOT/'godot/scripts/Main.gd').read_text()
MIC=(ROOT/'godot/scripts/MicrophoneCapture.gd').read_text()
HERMES=(ROOT/'godot/scripts/HermesStream.gd').read_text()
WAVE=(ROOT/'godot/scripts/AudioWaveformMeter.gd').read_text()


def test_shop_shortcuts_are_visible_without_reintroducing_rejected_rail():
    assert 'utility_dock:=_ornate_panel(self' in MAIN
    for title in ('Shelves','Ledger','Relations','Leads'):
        assert f'"{title}"' in MAIN or title in MAIN
    assert '_open_shelves_from_menu' in MAIN
    assert '_open_ledger_from_menu' in MAIN
    assert '_open_relationship_from_menu' in MAIN
    assert '_open_leads_from_menu' in MAIN
    assert 'left_rail=_ornate_panel' not in MAIN
    assert 'reaction_card=_ornate_panel' not in MAIN
    assert 'VisitorGallery.new()' in MAIN


def test_signal_driven_waves_have_separate_sources_and_silence_behaviour():
    assert 'res://assets/voice_waveform_v09.png' not in MAIN
    assert 'mic_wave_meter.push_level(microphone.live_rms,mic_live)' in MAIN
    assert 'visitor_wave_meter.push_level(hermes.audible_output_level(),visitor_live)' in MAIN
    assert 'live_rms=rms' in MIC
    assert 'AudioEffectCapture.new()' in MIC
    assert 'AudioServer.get_bus_peak_volume_left_db' in HERMES
    assert 'AudioServer.get_bus_peak_volume_right_db' in HERMES
    assert 'player.bus=VISITOR_AUDIO_BUS' in HERMES
    assert 'return 0.0' in HERMES
    assert 'var level: float=clampf(actual_level,0.0,1.0) if is_active else 0.0' in WAVE
    assert 'no fabricated motion' in WAVE.lower()
    assert 'Hermes audible peak %.2f' in MAIN


def test_chat_accents_are_native_and_mouse_transparent():
    assert 'var left_flower:=_text' in MAIN
    assert 'var right_flower:=_text' in MAIN
    assert '_rule(_speech_card,Vector2' in MAIN
    assert 'left_flower.mouse_filter=Control.MOUSE_FILTER_IGNORE' in MAIN
    assert 'right_flower.mouse_filter=Control.MOUSE_FILTER_IGNORE' in MAIN
    assert 'dialogue_label=RichTextLabel.new()' in MAIN


def test_portrait_state_quality_lock_is_explicit_and_rejects_old_crops():
    spec=json.loads((ROOT/'art/character_art_contract_v123.json').read_text())
    state=json.loads((ROOT/'godot/assets/character_art_status_v123.json').read_text())
    assert len(spec['states'])==12
    assert len(spec['characters'])==7
    assert spec['native_min_resolution']==[1024,1536]
    assert 'flustered' in spec['states'] and 'suspicious' in spec['states']
    assert all(not state[name]['approved'] for name in spec['characters'])
    assert 'if not bool(approval.get("approved",false))' in MAIN
    assert 'func _read_art_approval(visitor_id: String)' in MAIN
    assert 'quality lock' in (ROOT/'docs/QUALITY_LOCK_V123.md').read_text().lower()
    assert 'QUALITY_LOCK_V123' in (ROOT/'AGENTS.md').read_text()
    assert 'QUALITY_LOCK_V123' in (ROOT/'.agents/skills/living-counter-visual-bible/SKILL.md').read_text()


def test_strict_art_audit_reports_not_ready_without_mislabeling():
    spec=importlib.util.spec_from_file_location('portrait_validate',ROOT/'tools/validate_portraits_v123.py')
    module=importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    review=module.audit()
    assert len(review)==7
    assert all(not review[name]['production_ready'] for name in review)
    assert all(row['required']==12 for row in review.values())
    assert all(not row['owner_approved'] for row in review.values())


def test_exodia_contract_was_not_replaced():
    expected='3682ae40ca6d80c60a1c8d759b657f26a998a0ee7be09a4358faf5bcf9da2263'
    assert hashlib.sha256((ROOT/'backend/exodia.py').read_bytes()).hexdigest()==expected
    assert "'groq'" in (ROOT/'backend/exodia.py').read_text()
