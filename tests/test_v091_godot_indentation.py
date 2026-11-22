"""Prevent mixed tab/space indentation regressions like the V0.9 Hermes startup bug."""
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "godot" / "scripts"


def test_all_gd_scripts_are_consistently_tab_indented():
    checked = 0
    for script in SCRIPTS.rglob("*.gd"):
        checked += 1
        for number, line in enumerate(script.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            prefix = line[: len(line) - len(line.lstrip(" \t"))]
            assert not prefix or set(prefix) == {"\t"}, (
                f"{script.name}:{number} has spaces in leading indentation: {prefix!r}"
            )
    assert checked >= 7


def test_hermes_global_class_and_api_are_present():
    source = (SCRIPTS / "HermesStream.gd").read_text(encoding="utf-8")
    assert "class_name HermesStream" in source
    assert "func total_audio_seconds() -> float:\n\treturn" in source
    assert "func stream_is_complete() -> bool:\n\treturn" in source
    assert "func speak(" in source
    assert "func heard_seconds() -> float:" in source
