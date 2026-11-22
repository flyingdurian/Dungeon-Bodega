"""V0.6.4 regressions: social conversation, visible emotion, fixed Hermes voice."""
from pathlib import Path
import json

from backend.engine import ShopGame
from backend.trade_dialogue import assemble_trade_dialogue
from backend.exodia import build_instructions, build_prompt

ROOT=Path(__file__).resolve().parents[1]
MAIN=(ROOT/'godot/scripts/Main.gd').read_text(encoding='utf8')
EMOTION=(ROOT/'godot/scripts/EmotionGlyph.gd').read_text(encoding='utf8')
POP=(ROOT/'godot/scripts/DialoguePop.gd').read_text(encoding='utf8')
STREAM=(ROOT/'godot/scripts/HermesStream.gd').read_text(encoding='utf8')
EXODIA=(ROOT/'backend/exodia.py').read_text(encoding='utf8')


def _scene(user='Want to see a movie sometime?', turn=3):
    return {'event':'banter','anchor':'','npc_id':'maya','turn':turn,'user_text':user}


def test_date_banter_never_turns_into_canned_policy():
    phrase="Sure, I'd love to see that movie with you! That's sweet."
    assert assemble_trade_dialogue(phrase,_scene())==(phrase,'model')


def test_ordinary_yes_and_enthusiasm_not_filtered():
    phrase='Yes! You are charming and that sounds fun.'
    assert assemble_trade_dialogue(phrase,_scene())[0]==phrase


def test_only_fabricated_cash_commitment_is_silenced():
    line,source=assemble_trade_dialogue('You make me laugh. I accept 67 gold for this potion.',_scene())
    assert line=='You make me laugh.' and source=='model_repaired'


def test_clear_side_payment_commitment_repaired_without_policy_lecture():
    line,source=assemble_trade_dialogue('I accept a Nintendo Switch in exchange.',_scene())
    assert source=='model_repaired'
    assert 'Nintendo Switch' not in line and 'price is agreed' not in line


def test_repair_fallback_has_multiple_personality_variants():
    lines={assemble_trade_dialogue('I accept 67 gold for it.',_scene(turn=t))[0] for t in range(1,6)}
    assert len(lines)==3
    assert all('price is agreed' not in text for text in lines)


def test_cash_counter_remains_game_authoritative():
    line,src=assemble_trade_dialogue('Fine, 67 gold it is.',{'event':'counter','anchor':'My offer is 61 gold.'})
    assert line=='My offer is 61 gold.' and src=='game_locked'


def test_harmless_flavor_can_precede_game_ruling():
    line,src=assemble_trade_dialogue('You really are imaginative.',{'event':'rejected','anchor':'Are you offering 67 gold alone?'})
    assert line.startswith('You really are imaginative.')
    assert line.endswith('Are you offering 67 gold alone?')
    assert src=='game_locked'


def test_three_offtopic_turns_do_not_force_offer_repeat():
    game=ShopGame(seed=7)
    init=game.open_encounter('maya','buy')
    for n,utterance in enumerate(('How was your day?','Do you like movies?','Would you travel with me?'),1):
        scene,_=game.take_turn(init['session_id'],utterance,n)
        assert scene['event']=='banter'
        assert scene['anchor']==''


def test_prompt_is_compact_and_allows_playful_topics():
    game=ShopGame(seed=6)
    intro=game.open_encounter('maya','buy')
    scene,state=game.take_turn(intro['session_id'],'Would you like to get coffee?',1)
    assert len(build_instructions(scene,state))<800
    assert len(build_prompt(scene,state))<500
    assert 'flirting' in build_instructions(scene,state)
    assert 'do not invent a deal' in build_prompt(scene,state)


def test_godot_expression_has_five_distinct_animated_effects():
    for token in ('"anger"','"gold"','"persuade"','"doubt"','"happy"'):
        assert token in EMOTION
    assert 'install_effect(emotion_effect)' in MAIN
    director=(ROOT/'godot/scripts/DialogueDirector.gd').read_text()
    assert '[emote kind=%s' in director
    for phrase in ('高啊','这个价格','better deal','ridiculous','wonderful','真的吗'):
        assert phrase in director
    assert 'char_fx.relative_index' in EMOTION
    assert 'absolute_index' not in EMOTION


def test_reveal_is_armed_when_glyph_becomes_visible():
    assert 'visible_limit' in POP
    assert 'index >= visible_limit' in POP
    assert 'pop_effect.set("visible_limit",visible_now)' in MAIN


def test_hermes_uses_real_fixed_presets_without_pitch_shifting():
    presets=json.loads((ROOT/'godot/assets/hermes_profile_manifest.json').read_text())
    assert len(presets)>=20
    assert 'var pace: float=1.0' in MAIN
    assert 'voice_lock_session' in MAIN
    assert '"pitch_shift":0.0' in STREAM
    assert 'last_request' in STREAM and 'last_server' in STREAM
    assert 'Hermes preset:' in MAIN and 'Voice instructions:' in MAIN


def test_api_provider_route_and_transports_survive_repackaging():
    assert "PROVIDERS = frozenset(('chatgpt', 'gemini', 'deepseek', 'groq', 'gemini-api'))" in EXODIA
    assert "'transport': 'api' if self.provider in ('groq', 'gemini-api') else 'browser'" in EXODIA
    assert "EXODIA_GAME_ROUTE = '/api/command/tasks/game-dialogue'" in EXODIA
    assert (ROOT/'docs/EXODIA_API_PROVIDERS.md').exists()
