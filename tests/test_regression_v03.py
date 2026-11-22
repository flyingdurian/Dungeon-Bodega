"""Regression for repeated off-topic fallback and false Exodia content rejection."""
import pytest
from backend.brain import offline_flavor
from backend.engine import ShopGame
from backend.exodia import ExodiaError, clean_answer


def make_scene(prompt):
    g = ShopGame(seed=88)
    encounter = g.open_encounter('silas', 'buy')
    return g.take_turn(encounter['session_id'], prompt, 1)


def test_gta6_valid_in_character_ai_answer():
    line = "GTA 6? Sounds like the sixth chapter of a thieves' guild, if you ask me."
    assert clean_answer(line, 'Silas') == line


def test_other_numbers_in_nonfinancial_ai_answer():
    line = 'The third moon of winter is an unlucky day, merchant.'
    assert clean_answer(line, 'Silas') == line


@pytest.mark.parametrize('line', [
    'I will pay 900 gold and settle it now.',
    'I accept your offer of 100 gold.',
    'Give me the sword for 10g.',
    'I can afford the asking price.',
    'My price is a secret.',
])
def test_generated_flavor_cannot_invent_trade_contract(line):
    with pytest.raises(ExodiaError):
        clean_answer(line, 'Silas')


def test_iphone_and_gta6_fallback_are_distinct():
    a, state_a = make_scene('Have you seen the new iPhone?')
    b, state_b = make_scene('What do you think of GTA 6?')
    iphone = offline_flavor(a, state_a)
    gta = offline_flavor(b, state_b)
    assert iphone != gta
    assert 'eye-phone' in iphone.lower()
    assert 'g-t-a' in gta.lower()
    assert 'eye-phone' not in gta.lower()


def test_latest_topic_selected_when_multiple_appear():
    scene, state = make_scene('I asked about the iPhone before. Now what is GTA6?')
    assert 'g-t-a' in offline_flavor(scene, state).lower()


def test_audio_player_waits_for_pcm_and_drains_generator():
    # Source contract test: Godot executable not available in test environment.
    from pathlib import Path
    script = (Path(__file__).resolve().parents[1] / 'godot/scripts/HermesStream.gd').read_text()
    assert 'player.play()' not in script.split('if phase == "requesting":', 1)[1].split('if phase == "body":', 1)[0]
    assert 'buffer_capacity_frames = playback.get_frames_available()' in script
    assert 'get_playback_position()' not in script.replace('get_playback_position():', '')
