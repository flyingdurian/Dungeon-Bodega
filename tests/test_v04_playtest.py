"""V0.4 regression gates from first live Windows/Exodia/Hermes playtest."""
import os
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from backend.engine import ShopGame, GameError, evaluate_abuse
from backend.content import NPCS, NPC_BY_ID
from backend.exodia import build_instructions, build_prompt, clean_answer, DEPARTURE_CLAIM
from backend import app as service


def test_parallel_rosters_have_ten_distinct_characters_each():
    assert len({n['id'] for n in NPCS}) == 29
    assert len([p for p in NPCS if p['era']=='fantasy']) == 15
    assert len([p for p in NPCS if p['era']=='modern']) == 14
    assert NPC_BY_ID['kai']['era'] == 'modern'
    assert NPC_BY_ID['silas']['era'] == 'fantasy'


def test_modern_customer_understands_iphone_and_gta6():
    game=ShopGame(seed=42)
    first=game.open_encounter('maya','buy',era='modern')
    scene,state=game.take_turn(first['session_id'],'Have you seen the new iPhone and GTA 6?',1)
    instructions=build_instructions(scene,state)
    assert 'Modern visitor: knows phones' in instructions
    assert 'GTA 6' in build_prompt(scene,state)
    assert 'Maya' in build_prompt(scene,state)
    assert 'GTA 6' in clean_answer('I cannot believe how long GTA 6 took!', 'Maya "Byte" Torres')


def test_fantasy_still_has_its_distinct_knowledge():
    game=ShopGame(seed=42)
    first=game.open_encounter('aldric','buy',era='fantasy')
    scene,state=game.take_turn(first['session_id'],'Have you heard of an iPhone?',1)
    assert 'modern terms unknown' in build_instructions(scene,state)


def test_roster_selection_and_contract():
    g=ShopGame(seed=7)
    for _ in range(20):
        result=g.open_encounter(era='modern')
        assert result['customer']['era']=='modern'
    with pytest.raises(GameError):g.open_encounter('silas',era='modern')
    assert g.open_encounter('silas',era='mixed')['customer']['era']=='fantasy'


def test_severe_personal_abuse_forces_terminal_walkout():
    g=ShopGame(seed=7)
    start=g.open_encounter('vesper','buy')
    scene,state=g.take_turn(start['session_id'],'Fuck you. Get lost, you awful idiot.',1)
    assert scene['event']=='walkout'
    assert state['closed'] is True and state['outcome']=='walkout'
    assert scene['transaction'] is None
    assert 'offer' not in scene['anchor'].lower()
    assert g.world['deals']==0
    with pytest.raises(GameError):g.take_turn(start['session_id'],'35 gold',2)


def test_firm_bargaining_and_slang_are_not_severe_insults():
    assert evaluate_abuse('The price is fucking ridiculous, try again.') == 0
    assert evaluate_abuse('That offer is bullshit, mate.') == 0
    assert evaluate_abuse('You are a moron.') >= 20
    assert evaluate_abuse('Fuck you.') >= 50


def test_chat_avoids_repeating_counteroffer_every_turn():
    g=ShopGame(seed=7)
    start=g.open_encounter('silas','buy')
    scene1,_=g.take_turn(start['session_id'],'Tell me about your travels.',1)
    scene2,_=g.take_turn(start['session_id'],'And the strangest traveler you saw?',2)
    scene3,_=g.take_turn(start['session_id'],'Where did you go after that?',3)
    assert scene1['event']==scene2['event']==scene3['event']=='banter'
    assert scene1['anchor']=='' and scene2['anchor']==''
    # V0.6.4: no forced sales pitch every third freeform chat turn.
    assert scene3['anchor']==''


def test_live_npc_departure_becomes_authoritative_and_persists(tmp_path):
    g=ShopGame(save_path=tmp_path/'world.json',seed=7)
    start=g.open_encounter('kai','buy')
    scene,state=g.take_turn(start['session_id'],'You are making this difficult.',1)
    assert DEPARTURE_CLAIM.search("Nope, I'll take my business elsewhere.")
    assert g.apply_npc_departure(start['session_id'],state['turn'],scene)
    assert scene['event']=='walkout' and scene['anchor']=='I have heard enough. Goodbye.'
    result=g.finalize(start['session_id'],"Nope, I'll take my business elsewhere.",scene,True)
    assert result['closed'] and result['outcome']=='walkout'
    assert result['event']=='walkout' and result['transaction'] is None
    assert g.world['relationships']['kai']['visits']==1
    assert g.world['deals']==0
    with pytest.raises(GameError):g.take_turn(start['session_id'],'60 gold',2)


def test_stale_ai_departure_does_not_close_newer_turn():
    g=ShopGame(seed=8)
    start=g.open_encounter('kai','buy')
    scene,state=g.take_turn(start['session_id'],'You are making this difficult.',1)
    g.take_turn(start['session_id'],'Let me try again.',2)
    assert not g.apply_npc_departure(start['session_id'],1,scene)
    assert not g.debug(start['session_id'])['closed']


def test_live_benign_price_vocabulary_and_brand_names_allowed():
    for x in ('That price is pretty steep.', 'I cannot afford that today.',
              "I've never used ChatGPT.", 'I saw GTA 6 on the news.'):
        assert clean_answer(x,'Kai Navarro')==x


def test_live_binding_contract_still_rejected():
    from backend.exodia import ExodiaError
    for x in ('I will pay 900 gold.', 'My price is 50 coins.',
              'I accept your offer of 100 gold.', 'Pay 999 gold now.'):
        with pytest.raises(ExodiaError):clean_answer(x,'Kai Navarro')


def test_http_modern_encounter_returns_era(monkeypatch,tmp_path):
    monkeypatch.setenv('LIVING_COUNTER_OFFLINE','1')
    service.game=ShopGame(tmp_path/'world.json',seed=17)
    client=TestClient(service.app)
    response=client.post('/encounter',json={'era':'modern'})
    assert response.status_code==200
    assert response.json()['customer']['era']=='modern'
    assert client.post('/encounter',json={'era':'otherworld'}).status_code==422


def test_diag_is_opt_in_local_and_does_not_expose_dialogue(monkeypatch,tmp_path):
    monkeypatch.setenv('LIVING_COUNTER_DEBUG','0')
    service.game=ShopGame(tmp_path/'world.json',seed=10)
    c=TestClient(service.app)
    assert c.get('/diagnostics/dialogue').status_code==403
    monkeypatch.setenv('LIVING_COUNTER_DEBUG','1')
    response=c.get('/diagnostics/dialogue')
    assert response.status_code==200
    assert 'jobs' in response.json()
    assert 'prompt' not in response.text and 'answer' not in response.text
