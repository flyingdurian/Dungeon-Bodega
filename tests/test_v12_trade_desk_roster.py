"""V1.2 item-evidence, provider, role and interaction regressions."""
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from backend.app import app
from backend.engine import GameError, ShopGame
from backend.content import NPCS, NPC_BY_ID, OFFLINE_FLAVOR
from backend.living_encounters import build
from backend.exodia import PROVIDERS

ROOT=Path(__file__).resolve().parents[1]
NEW=('mara_copperwell','tarek_ashwood','yuna_seo','felix_rowe')


def test_four_new_distinct_npcs_and_valid_voice_profiles():
    assert len(NPCS)==29 and len({x['id'] for x in NPCS})==29
    assert sum(x.get('era')=='fantasy' for x in NPCS)==15
    assert sum(x.get('era')=='modern' for x in NPCS)==14
    import json
    voices=json.loads((ROOT/'godot/assets/hermes_profile_manifest.json').read_text())
    for npc_id in NEW:
        npc=NPC_BY_ID[npc_id]
        assert npc['chatterbox'] in voices
        assert npc['personality'] and npc['strategy'] and npc['lore']
        assert len(OFFLINE_FLAVOR[npc_id])>=3
        assert len({build(npc_id,day,'Moonsteel Dagger')['id'] for day in (1,2,3)})==3


@pytest.mark.parametrize('npc_id',NEW)
def test_new_customer_has_bounded_trade_desk(npc_id,tmp_path):
    g=ShopGame(seed=22,save_path=tmp_path/'game.json')
    start=g.open_encounter(npc_id,era=NPC_BY_ID[npc_id]['era'])
    sid=start['session_id']
    assert start['trade_desk']['condition']=='Unexamined'
    assert start['trade_desk']['estimated_range'] is None
    assert start['trade_desk']['provenance']=='Unverified'
    before_gold=g.world['gold'];before_stock=dict(g.world['stock']);before_offer=start['offer']
    examined=g.trade_desk_action(sid,'examine',1)
    assert examined['event']=='trade_inspection' and examined['ai_mode']=='game_authoritative'
    assert examined['trade_desk']['condition'] in ('excellent','worn','restored')
    assert examined['trade_desk']['estimated_range'] is None
    history=g.trade_desk_action(sid,'check_origin',2)
    assert history['trade_desk']['provenance'] in ('plausible','incomplete','documented')
    estimate=g.trade_desk_action(sid,'appraise',3)
    low,high=estimate['trade_desk']['estimated_range']
    assert 0<low<=high
    assert g.world['gold']==before_gold and g.world['stock']==before_stock
    assert g.sessions[sid]['offer']==before_offer and g.sessions[sid]['reservation']>0
    trust=g.sessions[sid]['trust']
    repeat=g.trade_desk_action(sid,'appraise',4)
    assert 'already' in repeat['line'].lower()
    assert g.sessions[sid]['trust']==trust
    assert repeat['trade_desk']['estimated_range']==[low,high]


def test_require_examination_and_never_commit_economic_change():
    g=ShopGame(seed=32)
    r=g.open_encounter('maya','buy')
    sid=r['session_id'];price=r['offer']
    refused=g.trade_desk_action(sid,'appraise',1)
    assert refused['trade_desk']['estimated_range'] is None
    assert 'examine' in refused['line'].lower()
    g.trade_desk_action(sid,'examine',2)
    assert g.sessions[sid]['offer']==price and not g.sessions[sid]['closed']
    with pytest.raises(GameError) as err: g.trade_desk_action(sid,'check_origin',1)
    assert err.value.status==409
    with pytest.raises(GameError) as err: g.trade_desk_action(sid,'invent_object',3)
    assert err.value.status==422


def test_fastapi_trade_desk_route_and_schema():
    with TestClient(app) as client:
        assert client.get('/health').json()['version']=='1.2.4'
        r=client.post('/encounter',json={'npc_id':'yuna_seo','era':'modern'}).json()
        sid=r['session_id']
        response=client.post('/trade-desk/action',json={'session_id':sid,'turn':1,'action':'examine'})
        assert response.status_code==200
        assert response.json()['trade_desk']['condition'] in ('excellent','worn','restored')
        dup=client.post('/trade-desk/action',json={'session_id':sid,'turn':1,'action':'appraise'})
        assert dup.status_code==409
        bad=client.post('/trade-desk/action',json={'session_id':sid,'turn':2,'action':'free_gems'})
        assert bad.status_code==422


def test_godot_has_native_trade_desk_controls_and_no_baked_mockup():
    main=(ROOT/'godot/scripts/Main.gd').read_text()
    panel=(ROOT/'godot/scripts/TradeDeskPanel.gd').read_text()
    gallery=(ROOT/'godot/scripts/VisitorGallery.gd').read_text()
    assert 'TradeDeskPanel.new()' in main
    assert 'game_url+"/trade-desk/action"' in main
    assert '⚒ TRADE DESK' in main
    assert 'item_%s.png' in panel
    assert 'ROTATE' in panel and 'ZOOM' in panel
    assert 'Examine the object' in panel and 'Nonbinding' in panel
    assert '29 CHARACTERS' in gallery
    assert all(f'"id":"{x}"' in gallery for x in NEW)
    assert 'vn_ui_ornaments_v061.png' not in main


def test_exodia_transport_contract_untouched():
    assert PROVIDERS==frozenset(('chatgpt','gemini','deepseek','groq','gemini-api'))
    source=(ROOT/'backend/exodia.py').read_text()
    assert "'transport': 'api' if self.provider in ('groq', 'gemini-api') else 'browser'" in source
    assert "/api/command/tasks/game-dialogue" in source


def test_spoken_inspection_actions_use_game_logic_and_do_not_call_exodia(monkeypatch):
    from backend.app import app
    with TestClient(app) as c:
        start=c.post('/encounter',json={'npc_id':'mara_copperwell','era':'fantasy'}).json()
        response=c.post('/talk',json={'session_id':start['session_id'],'turn':1,'text':'Examine the condition'})
        assert response.status_code==200
        result=response.json()
        assert result['event']=='trade_inspection'
        assert result['ai_mode']=='game_authoritative'
        assert result['trade_desk']['condition']!='Unexamined'
        second=c.post('/talk',json={'session_id':start['session_id'],'turn':2,'text':'Appraise'})
        assert second.status_code==200
        assert second.json()['trade_desk']['estimated_range'] is not None


def test_art_manifest_honestly_flags_incomplete_character_assets():
    import json
    from PIL import Image
    manifest=json.loads((ROOT/'art/character_art_manifest_v12.json').read_text())
    assert len(manifest['new_cast'])==4
    assert not any(x['complete'] for x in manifest['new_cast'].values())
    # The single new full-size neutral candidate is a real independent RGBA image,
    # not a transparent 384x512 cell stretched to fit 1024x1536.
    p=ROOT/'godot/assets/vn_mara_copperwell_neutral.png'
    with Image.open(p) as img:
        assert img.mode=='RGBA' and img.size==(1024,1536) and img.getpixel((0,0))[3]==0
    # V1.2.1 now supplies transparent main portraits for all four newcomers.
    # These are native-resolution art previews, not the finished 8-pose HD gate.
    for actor in ('tarek_ashwood','yuna_seo','felix_rowe'):
        with Image.open(ROOT/'godot/assets'/f'vn_{actor}_neutral.png') as portrait:
            assert portrait.mode=='RGBA'
            assert portrait.getpixel((0,0))[3]<=30
            assert portrait.width>=450 and portrait.height>=850
