"""V0.9.2: explicit conditional proposals and atomic, catalog-backed bundles."""
from __future__ import annotations
import pytest
from backend.engine import ShopGame, GameError
from backend.proposals import interpret_offer
from backend.trade_dialogue import assemble_trade_dialogue
from backend.exodia import build_prompt, PROVIDERS


def new_game(kind='buy'):
    g=ShopGame(seed=17)
    arrival=g.open_encounter('maya',kind)
    s=g.sessions[arrival['session_id']]
    return g, arrival, s

@pytest.mark.parametrize('text',[
    "I'll give you 100 gold if you go on a date with me",
    "I'll pay 100 gold provided that you give me your iPhone",
    "100 gold only if you trade me your GTA 6 game",
    "I'll pay you 100 gold in exchange for a Nintendo Switch",
    "I could do 100 gold if we meet for dinner later",
    "If you give me a kiss, I'll offer 100 gold",
])
def test_conditions_never_trigger_sale(text):
    g,a,s=new_game()
    initial=(g.world['gold'],dict(g.world['stock']),g.world['deals'],s['offer'])
    scene,state=g.take_turn(a['session_id'],text,1)
    assert scene['event'] in ('social_offer','social_refused','proposal') and scene['side_deal']
    assert scene['transaction'] is None and not s['closed']
    assert (g.world['gold'],g.world['stock'],g.world['deals'],s['offer'])==initial
    prompt=build_prompt(scene,state)
    assert 'NOT a completed trade' in prompt or 'NOT completed' in prompt
    assert text in prompt


def test_social_yes_or_confirm_does_not_close_trade():
    g,a,s=new_game()
    g.take_turn(a['session_id'],"I'll pay you 100 gold if you go to a movie with me",1)
    scene,_=g.take_turn(a['session_id'],"I accept!",2)
    assert scene['event'] in ('social_declined','banter') and not s['closed']
    scene,_=g.take_turn(a['session_id'],'confirm trade',3)
    assert scene['event']=='banter' and not s['closed']
    assert g.world['deals']==0


def test_real_bundle_staged_then_confirmed_atomically():
    g,a,s=new_game('sell')
    # Shopkeeper is buying the incoming item with 70g and an owned stock bonus.
    s['reservation']=80
    s['offer']=95
    stock_before=dict(g.world['stock'])
    gold_before=g.world['gold']
    scene,state=g.take_turn(a['session_id'], 'I offer 70 gold and this item to sweeten the deal',1,bonus_items=['mana_potion'])
    assert scene['event']=='proposal' and scene['proposal_status']=='ready'
    assert g.world['gold']==gold_before and g.world['stock']==stock_before
    assert s['pending_trade']['items']==['mana_potion']
    assert state['pending_trade']['ready']
    confirmed,_=g.take_turn(a['session_id'], 'confirm trade',2)
    assert confirmed['event']=='deal' and s['closed']
    assert confirmed['transaction']['price']==70
    assert confirmed['transaction']['bonus_item_ids']==['mana_potion']
    assert g.world['stock']['mana_potion']==stock_before['mana_potion']-1
    assert g.world['stock'][a['item']['id']]==stock_before[a['item']['id']]+1
    assert g.world['gold']==gold_before-70
    assert g.world['deals']==1


def test_unavailable_bonus_is_rejected_without_mutation():
    g,a,s=new_game('sell')
    g.world['stock']['mana_potion']=0
    before=dict(g.world['stock'])
    with pytest.raises(GameError) as ex:
        g.take_turn(a['session_id'], 'I offer 70 gold and mana potion',1,bonus_items=['mana_potion'])
    assert ex.value.status == 422
    assert s['turn'] == 0  # malformed proposal cannot consume the client's turn number
    assert g.world['stock']==before and g.world['deals']==0


def test_bonus_validation_rejects_unowned_and_negotiated_item():
    g,a,s=new_game()
    with pytest.raises(GameError):
        g.take_turn(a['session_id'],'I offer 80 gold plus an iPhone',1,bonus_items=['iphone'])
    with pytest.raises(GameError):
        g.take_turn(a['session_id'],'I offer 80 gold plus this item',1,bonus_items=[a['item']['id']])


def test_pending_trade_does_not_commit_if_stock_disappears():
    g,a,s=new_game('sell')
    s['reservation']=60
    g.take_turn(a['session_id'],'I offer 70 gold with a mana potion',1,bonus_items=['mana_potion'])
    g.world['stock']['mana_potion']=0
    before=g.world['gold']
    scene,_=g.take_turn(a['session_id'],'confirm trade',2)
    assert scene['event']=='rejected' and not s['closed']
    assert g.world['gold']==before


def test_unconditional_cash_offer_still_works_after_social_proposal():
    g,a,s=new_game()
    g.take_turn(a['session_id'],"I'll offer you 100 gold if you date me",1)
    assert s['pending_trade'] is not None
    s['wallet']=200
    s['reservation']=150
    g.rng.random=lambda:0.0
    scene,_=g.take_turn(a['session_id'],'I offer 100 gold for the item, no conditions',2)
    assert scene['event']=='deal'
    assert g.world['deals']==1 and s['pending_trade'] is None


def test_nontransaction_question_with_gadgets_is_banter():
    g,a,s=new_game()
    scene,_=g.take_turn(a['session_id'],'What is GTA 6 and an iPhone?',1)
    assert scene['event']=='banter'


def test_model_must_not_say_done_for_pending_trade():
    scene={'event':'proposal','user_text':"100 gold if you date me",'npc_id':'maya','turn':1,'anchor':''}
    line,mode=assemble_trade_dialogue('Done. We have a deal! I will take your 100 gold.',scene)
    assert 'we have a deal' not in line.lower() and 'i will take' not in line.lower()


def test_exodia_api_provider_contract_preserved():
    assert {'groq','gemini-api','deepseek','chatgpt','gemini'}<=PROVIDERS


def test_api_talk_accepts_catalog_bonus_ids(monkeypatch):
    from fastapi.testclient import TestClient
    from backend import app as game_app
    monkeypatch.setenv('LIVING_COUNTER_OFFLINE','1')
    client=TestClient(game_app.app)
    a=client.post('/encounter',json={'npc_id':'maya','intent':'sell'}).json()
    target='mana_potion'
    if a['item']['id']==target:
        target='wyvern_scale'
    request={'session_id':a['session_id'],'turn':1,
             'text':'I offer 70 gold and this bonus item', 'bonus_items':[target]}
    result=client.post('/talk',json=request)
    assert result.status_code==200, result.text
    payload=result.json()
    assert payload['event']=='proposal'
    assert payload['pending_trade']['items']==[target]
    assert not payload['closed']

@pytest.mark.parametrize('text',[
    'I offer 100 gold for your Nintendo Switch.',
    'I will give 100 gold for a date.',
    'I pay 100 gold for the iPhone.',
])
def test_different_named_goods_not_mistaken_for_target_sale(text):
    g,a,s=new_game()
    scene,_=g.take_turn(a['session_id'],text,1)
    assert scene['event'] in ('social_offer','social_refused')
    assert not s['closed'] and g.world['deals']==0


def test_spoken_bundle_name_auto_resolves_only_catalogued_owned_goods():
    g,a,s=new_game('sell')
    s['reservation']=65
    other='wyvern_scale' if a['item']['id'] != 'wyvern_scale' else 'mana_potion'
    name='wyvern scale' if other=='wyvern_scale' else 'mana potion'
    scene,_=g.take_turn(a['session_id'],f'I offer 70 gold and a {name}.',1)
    assert scene['event']=='proposal'
    assert s['pending_trade']['items']==[other]
