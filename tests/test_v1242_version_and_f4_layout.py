from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
MAIN=(ROOT/'godot/scripts/Main.gd').read_text(encoding='utf-8')
PROJECT=(ROOT/'godot/project.godot').read_text(encoding='utf-8')


def test_version_banner_matches_godot_window_title():
    label=re.search(r'const RELEASE_LABEL := "(V\d+\.\d+\.\d+)',MAIN)
    window=re.search(r'config/name="[^"\n]*?(V\d+\.\d+\.\d+)',PROJECT)
    assert label and window
    assert label.group(1)==window.group(1)
    assert 'V1.2.3 · LIVING VOICES' not in MAIN


def test_f4_telemetry_is_scrolling_and_clipped():
    assert 'ScrollContainer.new()' in MAIN
    assert 'diagnostics_scroll.vertical_scroll_mode=ScrollContainer.SCROLL_MODE_AUTO' in MAIN
    assert 'diagnostics_scroll.horizontal_scroll_mode=ScrollContainer.SCROLL_MODE_DISABLED' in MAIN
    assert '_text(diagnostics_scroll,' in MAIN
    assert 'PORTRAIT · %s' in MAIN
    assert 'Requested: %s   Displayed: %s' in MAIN


def test_art_gate_remains_truthful():
    assert 'fallback_reason="REJECTED_ART_LOCKED_TO_NEUTRAL"' in MAIN
    assert 'selected_expression=actually_displayed' in MAIN
    assert 'REJECTED_ART_IDS' in MAIN
