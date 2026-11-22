"""Owner-confirmed Dungeon Bodega v1.2.4.4 identity and boundary regression checks."""
from pathlib import Path
from fastapi.testclient import TestClient
from backend.app import app

ROOT=Path(__file__).resolve().parents[1]

def test_api_identity_is_v1244_dungeon_bodega():
    assert app.title.startswith('Dungeon Bodega')
    assert app.version=='1.2.4.4'
    with TestClient(app) as client:
        r=client.get('/health')
        assert r.status_code==200
        assert r.json()['game']=='Dungeon Bodega'
        assert r.json()['version']=='1.2.4.4'

def test_client_launcher_and_boundaries_keep_baseline():
    project=(ROOT/'godot/project.godot').read_text(encoding='utf-8')
    launcher=(ROOT/'start_windows.ps1').read_text(encoding='utf-8')
    main=(ROOT/'godot/scripts/Main.gd').read_text(encoding='utf-8')
    assert 'config/name="Dungeon Bodega — V1.2.4.4' in project
    assert 'Dungeon Bodega v1.2.4.4' in launcher
    assert 'V1.2.4.4' in main
    assert (ROOT/'docs/PROJECT_BOUNDARIES.md').is_file()
    assert (ROOT/'docs/HERMES_TTS_CONSUMER_CONTRACT.md').is_file()
    exodia=(ROOT/'backend/exodia.py').read_text(encoding='utf-8')
    assert "'gemini-api'" in exodia and "'groq'" in exodia
