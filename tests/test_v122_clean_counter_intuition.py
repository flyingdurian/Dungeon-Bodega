"""V1.2.2 regression gates for rejection of the old rail/cut-ins and safe intuition."""
from __future__ import annotations
import hashlib
from pathlib import Path
from fastapi.testclient import TestClient
from backend.engine import ShopGame
from backend.app import app
import importlib

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=(ROOT/'godot/scripts/Main.gd').read_text(encoding='utf-8')

def test_rejected_rail_and_cut_ins_are_not_built():
    assert 'left_rail=_ornate_panel' not in SCRIPT
    assert 'reaction_card=_ornate_panel' not in SCRIPT
    assert 'thumb.position=Vector2(17,row_y+5)' not in SCRIPT
    assert 'VisitorGallery.new()' in SCRIPT and 'KEY_F11' in SCRIPT
    assert 'func _toggle_shop_menu' in SCRIPT
    assert 'func _request_intuition' in SCRIPT
    assert 'Rect2(110,519,913,189)' in SCRIPT


def test_intuition_is_uncertain_and_repeatable_without_spending_gold_or_stock():
    game=ShopGame(seed=3)
    scene=game.open_encounter(npc_id='maya', intent='buy')
    sid=scene['session_id']
    state=game.sessions[sid]
    world_gold=game.world['gold']
    before_stock=game.world['stock'].copy()
    before_trust=state['trust']
    before_turn=state['turn']
    a=game.intuition_read(sid)
    b=game.intuition_read(sid)
    assert a==b and a['uncertain'] is True
    assert a['scope']=='tentative_read'
    assert a['confidence'] in ('low','medium','high')
    assert 'impression' in a and 'suggestion' in a
    assert 'reservation' not in str(a).lower() and 'private_concern' not in str(a)
    assert game.world['gold']==world_gold
    assert game.world['stock']==before_stock
    assert state['trust']==before_trust and state['turn']==before_turn


def test_intuition_api_is_session_bound(monkeypatch):
    app_module=importlib.import_module('backend.app')
    clean_game=ShopGame(seed=4)
    monkeypatch.setattr(app_module, 'game', clean_game)
    scene=clean_game.open_encounter(npc_id='garrick')
    with TestClient(app) as client:
        r=client.get('/intuition/'+scene['session_id'])
        assert r.status_code==200
        assert r.json()['uncertain'] is True
        assert client.get('/intuition/bad-id').status_code==404
        assert client.get('/intuition/'+'0'*32).status_code==404


def test_exodia_transport_protected():
    assert hashlib.sha256((ROOT/'backend/exodia.py').read_bytes()).hexdigest()=='3682ae40ca6d80c60a1c8d759b657f26a998a0ee7be09a4358faf5bcf9da2263'
    code=(ROOT/'backend/exodia.py').read_text()
    assert "'groq'" in code and "'gemini-api'" in code
    assert '/api/command/tasks/game-dialogue' in code
