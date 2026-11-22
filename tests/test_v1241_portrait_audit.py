from pathlib import Path
from tools.audit_runtime_portraits import scan, REJECTED
ROOT=Path(__file__).resolve().parents[1]

def test_all_rejected_really_are_neutral_locked():
    data=scan(ROOT)
    assert not data['master_chen']['forced_neutral_in_game']
    assert not data['tarek_ashwood']['forced_neutral_in_game']
    assert all(data[id]['forced_neutral_in_game'] for id in REJECTED if id not in ('master_chen','tarek_ashwood'))
    assert all(data[id]['approved'] is False for id in REJECTED)

def test_new_debug_display_is_truthful():
    gd=(ROOT/'godot/scripts/Main.gd').read_text(encoding='utf-8')
    assert 'var portrait_requested_expression:' in gd
    assert 'var actually_displayed: String=expressive' in gd
    assert 'actually_displayed="neutral"' in gd
    assert 'selected_expression=actually_displayed' in gd
    assert 'Gate: %s' in gd and 'File: %s' in gd and 'Requested: %s   Displayed: %s' in gd

def test_audit_rejects_existing_small_crops():
    data=scan(ROOT)
    for actor in ('felix_rowe','yuna_seo','mara_copperwell'):
        assert data[actor]['production_files']>=8
        assert data[actor]['native_rgba_files']<=1
    assert data['tarek_ashwood']['native_rgba_files']==5
    assert data['master_chen']['native_rgba_files']==5
    assert data['rin_kaede']['production_files']==1
    assert data['master_chen']['review_candidates']==5
