"""V1.1 regression tests for living encounters and production asset boundaries."""
from __future__ import annotations
import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from backend.app import app
from backend.engine import GameError, ShopGame
from backend import living_encounters as living
from backend.exodia import PROVIDERS

ROOT=Path(__file__).resolve().parents[1]

@pytest.mark.parametrize('visitor', ['maya','liu_xue','garrick'])
def test_featured_characters_have_three_distinct_encounters(visitor):
    scenes=[living.build(visitor,day,'Mana Potion') for day in (1,2,3)]
    assert len({s['id'] for s in scenes})==3
    assert all(s['motive'] and s['private_concern'] and s['lead'] for s in scenes)


def test_other_characters_unchanged_no_synthetic_story():
    assert living.build('safiya',4,'Potion') is None


def test_inspection_and_origin_never_change_money_stock_or_offer(tmp_path):
    g=ShopGame(seed=19,save_path=tmp_path/'save.json')
    r=g.open_encounter('maya','buy')
    sid=r['session_id'];gold=g.world['gold'];stock=dict(g.world['stock']);offer=r['offer']
    action=g.encounter_action(sid,'inspect',1)
    assert action['event']=='encounter_action'
    assert action['living_encounter']['beat']=='discovery'
    assert action['ai_mode']=='game_authoritative'
    assert 'maker' in action['line'].lower() or 'label' in action['line'].lower() or 'number' in action['line'].lower()
    g.encounter_action(sid,'ask_origin',2)
    assert g.world['gold']==gold and g.world['stock']==stock
    assert g.sessions[sid]['offer']==offer


def test_help_requires_discovery_and_is_repeat_safe(tmp_path):
    g=ShopGame(seed=5,save_path=tmp_path/'save.json')
    x=g.open_encounter('liu_xue','sell');sid=x['session_id']
    initially=g.encounter_action(sid,'offer_help',1)
    assert initially['living_encounter']['lead_awarded'] is False
    assert len(g.leads())==0
    g.encounter_action(sid,'ask_origin',2)
    helped=g.encounter_action(sid,'offer_help',3)
    assert helped['living_encounter']['beat']=='resolved'
    assert len(g.leads())==1
    assert any('\u4e00' <= c <= '\u9fff' for c in helped['line'])
    gold=g.world['gold']
    again=g.encounter_action(sid,'offer_help',4)
    assert 'already' in again['line'].lower()
    assert len(g.leads())==1 and g.world['gold']==gold


def test_leads_survive_server_reload_and_old_saves(tmp_path):
    save=tmp_path/'world.json'
    g=ShopGame(seed=7,save_path=save)
    x=g.open_encounter('garrick','buy');sid=x['session_id']
    g.encounter_action(sid,'inspect',1)
    g.encounter_action(sid,'offer_help',2)
    before=g.leads()
    assert len(before)==1
    restored=ShopGame(seed=7,save_path=save)
    assert restored.leads()==before
    save.write_text(json.dumps({'stock':{'mana_potion':2},'gold':103,'relationships':{},'day':1}))
    legacy=ShopGame(seed=1,save_path=save)
    assert legacy.leads()==[]


def test_voice_request_has_same_interaction_effect_as_click():
    g=ShopGame(seed=15)
    start=g.open_encounter('garrick','sell')
    scene,state=g.take_turn(start['session_id'],'Let me inspect that item',1)
    assert scene['event']=='encounter_action'
    assert state['living']['beat']=='discovery'
    assert state['offer']==start['offer']
    assert state['pending_trade'] is None


def test_initiative_reveals_once_without_touching_trade():
    g=ShopGame(seed=11)
    start=g.open_encounter('maya','buy')
    sid=start['session_id']
    events=[]
    for i,t in enumerate(['How are you?','What brings you here?','Any stories today?','Interesting day, huh?','Tell me more'],1):
        scene,_=g.take_turn(sid,t,i)
        events.append(scene['event'])
        g.finalize(sid,scene.get('anchor') or 'Interesting.',scene)
    assert events.count('encounter_initiative')==1
    assert not g.sessions[sid]['closed']
    assert g.world['deals']==0


def test_action_replay_does_not_repeat_trust_reward():
    g=ShopGame(seed=5)
    x=g.open_encounter('maya','sell');sid=x['session_id']
    g.encounter_action(sid,'inspect',1)
    trust=g.sessions[sid]['trust']
    g.encounter_action(sid,'inspect',2)
    assert g.sessions[sid]['trust']==trust


def test_api_action_contract_and_version():
    with TestClient(app) as c:
        health=c.get('/health')
        assert health.status_code==200 and health.json()['version']=='1.2.4.4'
        # API validation: never create action for a forged or missing session.
        resp=c.post('/encounter/action',json={'session_id':'a'*32,'turn':1,'action':'inspect'})
        assert resp.status_code==404
        assert c.get('/leads').status_code==200


def test_release_still_supports_all_five_exodia_transports():
    assert PROVIDERS==frozenset(('chatgpt','gemini','deepseek','groq','gemini-api'))
    source=(ROOT/'backend/exodia.py').read_text()
    assert '/api/command/tasks/game-dialogue' in source
    assert "'transport': 'api' if self.provider in ('groq', 'gemini-api') else 'browser'" in source


def test_native_layout_has_contextual_buttons_not_baked_screenshot():
    main=(ROOT/'godot/scripts/Main.gd').read_text()
    assert '_send_encounter_action' in main and 'game_url+"/encounter/action"' in main
    assert 'Rect2(110,519,913,189)' in main
    assert 'action_buttons[action_key]=action_button' in main
    assert 'case_title' in main and 'F12' in main
    assert 'vn_ui_ornaments_v061.png' not in main


def test_elara_illustration_states_and_manifest_are_real_rgba():
    from PIL import Image
    manifest=json.loads((ROOT/'art/character_art_manifest_v11.json').read_text())
    labels=manifest['expression_states']
    assert len(labels)==8
    assert manifest['characters']['elara_veyne']['complete']
    for emotion in labels:
        path=ROOT/f'godot/assets/vn_elara_veyne_{emotion}.png'
        with Image.open(path) as im:
            assert im.mode=='RGBA' and im.size==(768,1024)
            assert im.getpixel((0,0))[3]==0
