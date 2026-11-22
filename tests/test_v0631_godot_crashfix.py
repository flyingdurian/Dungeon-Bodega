"""Regression guards for the November 18 Godot 4 V0.6.3 runtime errors."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = (ROOT / 'godot/scripts/Main.gd').read_text(encoding='utf-8')
POP = (ROOT / 'godot/scripts/DialoguePop.gd').read_text(encoding='utf-8')
MIC = (ROOT / 'godot/scripts/MicrophoneCapture.gd').read_text(encoding='utf-8')
EXODIA = (ROOT / 'backend/exodia.py').read_text(encoding='utf-8')


def test_godot4_effect_index_uses_supported_property():
    assert 'char_fx.relative_index' in POP
    assert 'char_fx.absolute_index' not in POP
    assert 'func reset() -> void:' in POP
    assert 'pop_effect.reset()' in MAIN


def test_catalog_refresh_requests_are_coalesced():
    assert 'var catalog_request_in_flight: bool=false' in MAIN
    assert 'var catalog_refresh_pending: bool=false' in MAIN
    refresh = MAIN.split('func _refresh_catalog() -> void:', 1)[1].split('\nfunc ', 1)[0]
    assert refresh.index('if catalog_request_in_flight:') < refresh.index('catalog_http.request(')
    assert 'catalog_refresh_pending=true' in refresh
    assert 'catalog_request_in_flight=true' in refresh
    callback = MAIN.split('func _on_catalog_response(', 1)[1].split('\nfunc ', 1)[0]
    assert 'catalog_request_in_flight=false' in callback
    assert 'if catalog_refresh_pending:' in callback
    assert 'call_deferred("_refresh_catalog")' in callback


def test_mic_bus_renamed_without_breaking_microphone_routing():
    assert 'var mic_bus_name: String = "LivingCounterMic"' in MIC
    assert 'AudioServer.get_bus_index(mic_bus_name)' in MIC
    assert 'AudioServer.set_bus_name(bus_index,mic_bus_name)' in MIC
    assert 'microphone_player.bus=mic_bus_name' in MIC


def test_exodia_api_provider_compatibility_untouched():
    assert "'groq', 'gemini-api'" in EXODIA
    assert "/api/command/tasks/game-dialogue" in EXODIA
    assert "'api' if self.provider in ('groq', 'gemini-api') else 'browser'" in EXODIA
