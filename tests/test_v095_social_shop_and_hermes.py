"""V0.9.5 source gates: no endless conditions, atomic shop supply, stable voice."""
from __future__ import annotations
import json
from pathlib import Path
import pytest
from backend.engine import ShopGame, GameError
from backend.social_contracts import is_confirmation, physical_goods
from backend.shop_progression import shop_ledger, supply_cost, MAX_STOCK
from backend.trade_dialogue import assemble_trade_dialogue
from backend import exodia

ROOT=Path(__file__).resolve().parents[1]


def maya_buy(seed=8):
    game=ShopGame(seed=seed)
    a=game.open_encounter('maya','buy')
    state=game.sessions[a['session_id']]
    state.update(trust=75,patience=85, wallet=200, reservation=100, offer=50)
    return game,a,state


def test_social_terms_locked_until_user_accepts():
    g,a,s=maya_buy()
    original_stock=dict(g.world['stock'])
    original_gold=g.world['gold']
    proposal,_=g.take_turn(a['session_id'], 'I will take your 50 gold if you go on a date with me.',1)
    assert proposal['event']=='social_offer' and proposal['proposal']['ready']
    assert g.world['stock']==original_stock and g.world['gold']==original_gold
    assert s['pending_trade']['cash']==50 and s['pending_trade']['topic']=='date'
    line, mode=assemble_trade_dialogue('I also demand a hoodie, an iPhone and a car!', proposal)
    assert line==proposal['anchor'] and 'hoodie' not in line.lower() and mode=='game_locked'
    finalized,_=g.take_turn(a['session_id'],'Yes, 50 gold and a date. Sounds good!',2)
    assert finalized['event']=='deal' and finalized['transaction']['price']==50
    assert g.world['gold']==original_gold+50 and s['closed']
    assert g.world['stock'][s['item_id']]==original_stock[s['item_id']]-1
    assert g.world['relationships']['maya']['last_social_roleplay']['topic']=='date'


def test_social_terms_changed_cannot_mutate_money_or_spiral():
    g,a,s=maya_buy()
    g.take_turn(a['session_id'],'50 gold if you date me',1)
    starting_gold=g.world['gold']
    one,_=g.take_turn(a['session_id'],'Yes I accept but throw in your hoodie',2)
    assert one['event']=='social_terms_changed'
    assert s['pending_trade']['revision_count']==1
    two,_=g.take_turn(a['session_id'],'Okay I accept but give me your headphones too',3)
    assert two['event']=='social_terms_changed' and s['pending_trade'] is None
    assert g.world['gold']==starting_gold and not s['closed']
    assert g.world['deals']==0


def test_personal_headphones_are_not_salable_even_at_200_gold():
    g,a,s=maya_buy()
    start=g.world['gold']
    for turn,cash in enumerate((50,200),1):
        scene,_=g.take_turn(a['session_id'],f'I will give you {cash} gold if you hand over your headphones',turn)
        assert scene['event']=='social_refused'
        assert 'personal' in scene['anchor'].lower()
        assert g.world['gold']==start and not s['closed']
    assert 'headphones' in s['refused_goods']


def test_unaffordable_social_offer_is_declined_and_yes_not_sold():
    g,a,s=maya_buy()
    s['wallet']=55
    scene,_=g.take_turn(a['session_id'],'I would give you 150 gold if we meet for dinner',1)
    assert scene['event']=='social_offer' and scene['proposal']['ready'] is False
    second,_=g.take_turn(a['session_id'],'Yes, I accept',2)
    assert second['event']=='social_declined' and not s['closed'] and g.world['deals']==0


def test_social_confirmation_rejects_unstated_goods_and_new_prices():
    fixed={'kind':'social','ready':True,'cash':50,'topic':'date'}
    assert is_confirmation('Sure, fifty gold, date and you pick the music', fixed)  # text-only restatement
    assert not is_confirmation('Okay, 50 gold and a hoodie',fixed)
    assert not is_confirmation('Deal, now 200 gold',fixed)
    assert not is_confirmation('I accept, but only if you also give me headphones',fixed)
    assert physical_goods('A hoodie, iPhone, and your headphones')


def test_restock_spends_gold_atomically_and_persists(tmp_path):
    path=tmp_path/'world.json'
    g=ShopGame(save_path=path,seed=2)
    item='mana_potion'
    initial_gold=g.world['gold']
    initial_count=g.world['stock'][item]
    cost=supply_cost(item,g.world['day'])
    result=g.restock(item,2)
    assert result['gold_spent']==cost*2
    assert result['stock']==initial_count+2
    assert g.world['gold']==initial_gold-cost*2
    assert g.ledger()['supplies_gold']==cost*2
    again=ShopGame(save_path=path,seed=2)
    assert again.world['gold']==g.world['gold'] and again.world['stock'][item]==initial_count+2
    assert again.ledger()['supplies_gold']==cost*2


def test_restock_does_not_overdraft_or_overfill():
    g=ShopGame(seed=3)
    item='rune_stone'
    g.world['gold']=0
    original_stock=dict(g.world['stock'])
    with pytest.raises(GameError,match='Insufficient'):
        g.restock(item,1)
    assert g.world['stock']==original_stock and g.world['gold']==0
    g.world['gold']=5000
    g.world['stock'][item]=MAX_STOCK
    with pytest.raises(GameError,match='capacity'):
        g.restock(item,1)
    with pytest.raises(GameError):
        g.restock('iphone',1)
    with pytest.raises(GameError):
        g.restock(item,True)


def test_shop_ledger_and_spotlight_change_by_day():
    g=ShopGame(seed=4)
    day1=g.ledger()
    assert day1['reputation']==50 and day1['shop_rank']=='New Shopkeeper'
    assert day1['market']['item_id']=='mana_potion'
    first=supply_cost('mana_potion',1)
    second=supply_cost('mana_potion',2)
    assert first>second
    g.world['day']=2
    assert g.ledger()['market']['item_id']=='healing_draught'
    assert g.catalog()['items'][0]['restock_cost']==second


def test_public_api_restocks_and_exposes_ledger(monkeypatch):
    from fastapi.testclient import TestClient
    from backend import app
    local=ShopGame(seed=6)
    monkeypatch.setattr(app,'game',local)
    cli=TestClient(app.app)
    reply=cli.post('/restock',json={'item_id':'mana_potion','quantity':1})
    assert reply.status_code==200,reply.text
    assert reply.json()['gold_spent']>0
    ledger=cli.get('/ledger')
    assert ledger.status_code==200 and ledger.json()['supplies_gold']==reply.json()['gold_spent']
    catalog=cli.get('/catalog').json()
    assert catalog['ledger']['supplies_gold'] == ledger.json()['supplies_gold']


def test_contract_and_godot_wiring_stays_intact():
    src=(ROOT/'backend/exodia.py').read_text()
    main=(ROOT/'godot/scripts/Main.gd').read_text()
    pcm=(ROOT/'godot/scripts/HermesStream.gd').read_text()
    assert set(exodia.PROVIDERS)=={'chatgpt','gemini','deepseek','groq','gemini-api'}
    assert "'transport': 'api' if self.provider in ('groq', 'gemini-api') else 'browser'" in src
    assert '/api/command/tasks/game-dialogue' in src
    assert 'func _restock_inspected()' in main and 'func _refresh_shop_ledger()' in main
    assert 'KEY_F10' in main and 'shop_ledger_panel.visible=false' in main
    assert 'fading.texture=portrait.texture' not in main
    assert 'if str(current.get("customer",{}).get("id",""))!="liu_xue"' in main
    assert '"sample_rate": sample_rate' in pcm and 'playback_drift_s' in pcm
    assert 'float(sample_rate)*0.28' in pcm and 'gen.buffer_length = 1.20' in pcm
    assert (ROOT/'tools/hermes_pcm_compare_v095.py').exists()
