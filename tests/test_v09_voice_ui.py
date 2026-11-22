"""V0.9 source/asset regression gates. Native Godot and real Hermes remain separate smoke tests."""
from pathlib import Path
import json
import struct
import pytest
from backend import exodia, stt_local
from backend.content import NPCS

ROOT=Path(__file__).resolve().parents[1]
MAIN=(ROOT/'godot/scripts/Main.gd').read_text(encoding='utf-8')
HERMES=(ROOT/'godot/scripts/HermesStream.gd').read_text(encoding='utf-8')


def test_api_provider_transport_contract_is_unchanged():
    assert set(exodia.PROVIDERS)=={'groq','gemini-api','gemini','deepseek','chatgpt'}
    assert exodia.EXODIA_GAME_ROUTE=='/api/command/tasks/game-dialogue'
    assert "'transport': 'api' if self.provider in ('groq', 'gemini-api') else 'browser'" in (ROOT/'backend/exodia.py').read_text()
    assert (ROOT/'docs/EXODIA_API_PROVIDERS.md').exists()


def test_painted_shop_not_a_concept_screenshot():
    assert 'res://assets/shop_bg_v061_dynasty.png' in MAIN
    assert 'res://assets/atmospheric_lantern_glow_v09.png' in MAIN
    assert 'LIU_XUE_ART_BIBLE' not in MAIN
    assert 'Layout_Design_Preview' not in MAIN
    assert 'mouse_filter=Control.MOUSE_FILTER_IGNORE' in MAIN


def test_lighting_asset_is_transparent_and_correct_size():
    path=ROOT/'godot/assets/atmospheric_lantern_glow_v09.png'
    content=path.read_bytes()
    assert content[:8]==b'\x89PNG\r\n\x1a\n'
    assert struct.unpack('>II',content[16:24])==(1440,900)
    assert content[25]==6  # truecolor + alpha
    assert 15000<len(content)<5_000_000


def test_real_dual_waveforms_replaced_the_old_decorative_wave():
    widget=ROOT/'godot/scripts/AudioWaveformMeter.gd'
    assert widget.exists()
    assert 'var rms: float = sqrt(power/' in (ROOT/'godot/scripts/MicrophoneCapture.gd').read_text()
    assert 'mic_wave_meter.push_level(microphone.live_rms,mic_live)' in MAIN
    assert 'visitor_wave_meter.push_level(hermes.audible_output_level(),visitor_live)' in MAIN
    assert 'res://assets/voice_waveform_v09.png' not in MAIN
    assert 'voice_note.text=' in MAIN
    assert 'F5 Voice' in MAIN


def test_hermes_pcm_timing_and_jitter_diagnostics():
    for token in ('total_audio_seconds()', 'stream_is_complete()', 'audio_telemetry()',
                  'last_played_seconds', 'audio_underruns', 'get_frames_available()',
                  'voice_level', 'last_server'):
        assert token in HERMES
    assert 'hermes.heard_seconds()' in MAIN
    assert '_caption_timing_factor()' in MAIN
    assert '_learn_voice_pacing()' in MAIN
    assert 'cfg.set_value("voice","caption_calibration",voice_timing_factors)' in MAIN


def test_stable_hermes_voice_does_not_pitch_shift():
    assert 'voice_lock_session=sid' in MAIN
    assert '"pitch_shift":0.0' in HERMES
    assert 'var pace: float=1.0' in MAIN
    assert 'if engine=="qwen":voice_id="Vivian"' in MAIN
    manifest=json.loads((ROOT/'godot/assets/hermes_profile_manifest.json').read_text())
    assert len(manifest)>=20
    assert len(NPCS)==29


def test_character_acting_uses_illustrations_not_drawn_faceless_sprites():
    for token in ('portrait.pivot_offset=', 'portrait.texture=next_texture',
                  'Never overlay independently drawn full-size portraits', 'actor_arrived_at',
                  'atmosphere_overlay.modulate.a'):
        assert token in MAIN
    for name in ('maya','liu_xue'):
        for expression in ('neutral','thinking','amused','skeptical','annoyed'):
            assert (ROOT/f'godot/assets/vn_{name}_{expression}.png').exists()


def test_voice_studio_is_hidden_and_nonblocking():
    assert 'voice_panel.visible=false' in MAIN
    assert 'KEY_F5' in MAIN
    assert 'func _check_voice_health()' in MAIN
    assert 'func _on_voice_health(' in MAIN
    assert 'voice_health_http.request(hermes_url.trim_suffix("/")+"/health")' in MAIN
    assert 'voice_panel.visible=not voice_panel.visible' in MAIN
    assert 'voice_lock.get("profile"' in MAIN


def test_optional_multilingual_stt_safely_requires_multilingual_model(monkeypatch):
    monkeypatch.setenv('STT_MODEL_SIZE','tiny.en')
    monkeypatch.setenv('STT_LANGUAGE','auto')
    class Dummy:
        def transcribe(self,*args,**kwargs):
            raise AssertionError('Should stop before transcription')
    monkeypatch.setattr(stt_local,'get_model', lambda: Dummy())
    with pytest.raises(stt_local.STTUnavailable,match='multilingual'):
        stt_local.transcribe(b'RIFF'+b'\0'*4+b'WAVE'+b'\0'*40)
