"""Experimental shopkeeper intuition, deliberately probabilistic and non-authoritative.

A reading observes behavioral pressure, not a psychic truth or a truth detector.
Neither the visual expression nor this guess can change inventory, gold, or a deal.
"""
from __future__ import annotations
import hashlib

# Never claim to have established that an NPC is lying, flirting, or hiding an item.
READINGS = {
    'guarded': ('Guarded', 'The visitor seems to be weighing how much to reveal.', 'Notice what they avoid saying; ask about their evidence.'),
    'tense': ('Tense', 'There is pressure behind their measured response.', 'A gentler question may help, or they may need space.'),
    'hesitant': ('Hesitant', 'Something about the item or its history may trouble them.', 'Inspect the object or ask about its origin.'),
    'testing': ('Testing the price', 'Their reaction to the number looks carefully controlled.', 'Ask what supports the quoted amount.'),
    'open': ('Open', 'They appear comparatively comfortable with you.', 'There may be room for a sincere conversation.'),
}


def read(session: dict, reputation: int) -> dict:
    """Return a bounded, repeatable impression for a single encounter turn.

    Low-skill readings can be mistaken, and even high-skill readings are hints.
    Avoid revealing the authored secret, reservation, exact motive, or true state.
    """
    living = session.get('living') if isinstance(session.get('living'), dict) else {}
    observed = len(living.get('actions_taken', [])) + len(session.get('trade_desk', {}).get('actions_taken', [])) if isinstance(session.get('trade_desk'), dict) else len(living.get('actions_taken', []))
    skill = max(0, min(3, (int(reputation) - 25) // 25 + min(1, observed)))
    confidence = min(0.84, 0.50 + 0.09 * skill + 0.03 * min(2, observed))
    patience = int(session.get('patience', 55))
    trust = int(session.get('trust', 50))
    if patience < 35:
        actual = 'tense'
    elif trust < 40:
        actual = 'guarded'
    elif living and not living.get('actions_taken'):
        actual = 'hesitant'
    elif int(session.get('offer', 0)) > 0 and session.get('turn', 0) >= 2:
        actual = 'testing'
    else:
        actual = 'open'
    token = f"{session['id']}:{session.get('turn', 0)}:{observed}"
    chance = int.from_bytes(hashlib.sha256(token.encode('ascii')).digest()[:4], 'big') / 0xFFFFFFFF
    # Alternative impressions represent reasonable misreads, not random facts.
    alternative = {'tense': 'guarded', 'guarded': 'hesitant', 'hesitant': 'guarded', 'testing': 'hesitant', 'open': 'testing'}[actual]
    perceived = actual if chance <= confidence else alternative
    title, note, suggestion = READINGS[perceived]
    return {
        'title': title,
        'impression': note,
        'suggestion': suggestion,
        'confidence': 'high' if confidence >= 0.78 else 'medium' if confidence >= 0.62 else 'low',
        'scope': 'tentative_read',
        'uncertain': True,
        'turn': int(session.get('turn', 0)),
        'skill': skill,
        'disclaimer': 'Your impression, not the visitor’s confirmed inner thoughts.'
    }
