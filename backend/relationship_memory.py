"""Small, verifiable per-customer memories; no second LLM or raw chat archive.

Only explicitly identified player statements are recorded. Neither a model reply
nor a player's imagined side payment becomes an accepted shop transaction.
Persistence is capped, version tolerant and intentionally conservative.
"""
from __future__ import annotations

import re
from typing import Any

MAX_MOMENTS = 3
MAX_SUMMARY_CHARS = 105
MAX_PROMPT_CHARS = 280

# The topic vocabulary is fixed. We never persist arbitrary player-supplied
# instructions in a prompt-shaped memory (and never remember secrets).
TOPICS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ('Nintendo Switch', re.compile(r'\b(?:nintendo\s+switch|switch\s+(?:console|2))\b', re.I)),
    ('iPhone', re.compile(r'\biphone\b', re.I)),
    ('games', re.compile(r'\b(?:video\s+games?|gaming|playstation|xbox|gta\s*6)\b', re.I)),
    ('a movie', re.compile(r'\b(?:movies?|cinema|film|popcorn)\b', re.I)),
    ('a date', re.compile(r'\b(?:date\s+night|go\s+on\s+a\s+date|take\s+you\s+out)\b', re.I)),
    ('dinner', re.compile(r'\b(?:dinner|lunch|restaurant)\b', re.I)),
    ('tea', re.compile(r'\btea\b|茶')), 
    ('jade', re.compile(r'\bjade\b|玉')), 
    ('rare collectibles', re.compile(r'\b(?:collect(?:or|ibles?)|rare\s+(?:item|artifact|card)|antiques?)\b', re.I)),
)
FUTURE_INTENT = re.compile(r"(?i)\b(?:i\s+promise\s+(?:to|you)|i(?:'ll|\s+will)\s+bring\s+you|i\s+swear\s+i(?:'ll|\s+will))\b")
HYPOTHETICAL = re.compile(r"(?i)\b(?:if\s+(?:you|we|i)|what\s+if|imagine|would\s+you|could\s+you|in\s+exchange|throw\s+in|plus)\b")
SOCIAL = re.compile(r"(?i)\b(?:take\s+you\s+(?:to|out)|go\s+(?:to\s+the\s+movies|on\s+a\s+date)|go\s+out\s+with|dinner\s+with\s+you|movie\s+with\s+you)\b")
INTEREST = re.compile(r"(?i)\b(?:i\s+(?:love|like|collect|enjoy)|my\s+(?:favorite|hobby)|i(?:'m|\s+am)\s+into)\b")


def _topic(text: str) -> str | None:
    return next((name for name, pattern in TOPICS if pattern.search(text)), None)


def extract_player_moment(text: str, *, side_deal: bool = False) -> dict | None:
    """Classify conservatively; only fixed descriptive facts, never raw dialogue.

    An explicit future intention is still only what the *player stated*, not a
    contract or an NPC promise. Side offers remain hypothetical regardless of
    whether the player used the word 'deal'.
    """
    utterance = str(text or '')[:500]
    topic = _topic(utterance)
    if not topic:
        return None
    if side_deal or (HYPOTHETICAL.search(utterance) and topic in ('Nintendo Switch','iPhone','games')):
        kind = 'hypothetical'
        summary = f'Player floated {topic} as an idea, not an accepted trade'
    elif FUTURE_INTENT.search(utterance) and not HYPOTHETICAL.search(utterance):
        kind = 'stated_intent'
        summary = f'Player said they intended to bring or arrange {topic}; not verified'
    elif SOCIAL.search(utterance):
        kind = 'social_invitation'
        summary = f'Player mentioned an invitation involving {topic}; no agreement recorded'
    elif HYPOTHETICAL.search(utterance):
        kind = 'hypothetical'
        summary = f'Player floated {topic} as an idea, not an accepted trade'
    elif INTEREST.search(utterance):
        kind = 'interest_mentioned'
        summary = f'Player said they enjoy or collect {topic}'
    else:
        return None
    return {'kind': kind, 'topic': topic, 'summary': summary[:MAX_SUMMARY_CHARS]}


def sanitize_moments(value: Any) -> list[dict]:
    """Never trust old save JSON as instructions, even when it looks structured."""
    if not isinstance(value, list):
        return []
    acceptable = {'hypothetical', 'stated_intent', 'social_invitation', 'interest_mentioned'}
    safe_topics = {name for name, _ in TOPICS}
    safe: list[dict] = []
    for record in value[-20:]:
        if not isinstance(record, dict):
            continue
        kind, topic = record.get('kind'), record.get('topic')
        if kind not in acceptable or topic not in safe_topics:
            continue
        # Reconstruct description from the known fixed vocabulary. Treat
        # any stored 'summary' or 'source' strings as untrusted.
        description = {
            'hypothetical': f'Player floated {topic} as an idea, not an accepted trade',
            'stated_intent': f'Player said they intended to bring or arrange {topic}; not verified',
            'social_invitation': f'Player mentioned an invitation involving {topic}; no agreement recorded',
            'interest_mentioned': f'Player said they enjoy or collect {topic}',
        }[kind]
        entry = {'kind': kind, 'topic': topic, 'summary': description[:MAX_SUMMARY_CHARS]}
        if entry not in safe:
            safe.append(entry)
    return safe[-MAX_MOMENTS:]


def remember(existing: Any, incoming: dict | None) -> list[dict]:
    notes = sanitize_moments(existing)
    if not incoming:
        return notes
    incoming = sanitize_moments([incoming])
    if not incoming:
        return notes
    new = incoming[0]
    notes = [x for x in notes if (x['kind'], x['topic']) != (new['kind'], new['topic'])]
    return (notes + [new])[-MAX_MOMENTS:]


def relationship_context(seen: Any) -> str:
    if not isinstance(seen, dict) or not seen:
        return ''
    visits = max(0, min(999, int(seen.get('visits', 0) or 0)))
    if not visits and not seen.get('moments'):
        return ''
    last = str(seen.get('last_outcome', ''))
    last = last if last in ('deal','walkout') else 'none'
    parts = [f'Prior visits={visits}; last finished encounter={last}.']
    for event in sanitize_moments(seen.get('moments')):
        parts.append(event['summary'] + '.')
    roleplay = seen.get('last_social_roleplay')
    if isinstance(roleplay,dict) and roleplay.get('status')=='roleplay_agreed' and roleplay.get('topic') in ('date','dinner','movie','music'):
        parts.append('Later they roleplayed a mutual invitation involving '+roleplay['topic']+'; social fiction only, no real-world obligation.')
    result = ' '.join(parts)
    return result[:MAX_PROMPT_CHARS]


def public_relationship(seen: Any) -> dict:
    """Public UI gets only safe, non-secret relationship indicators."""
    if not isinstance(seen, dict):
        seen = {}
    visits = max(0, min(999, int(seen.get('visits', 0) or 0)))
    return {
        'visits': visits,
        'deals': max(0, min(999, int(seen.get('deals', 0) or 0))),
        'status': 'Returning visitor' if visits else 'First meeting',
        'last_outcome': seen.get('last_outcome') if seen.get('last_outcome') in ('deal','walkout') else None,
        'memory_count': len(sanitize_moments(seen.get('moments'))),
        'notes': [note['summary'] for note in sanitize_moments(seen.get('moments'))],
        'social_roleplay': (str(seen['last_social_roleplay']['topic'])
                            if isinstance(seen.get('last_social_roleplay'),dict)
                            and seen['last_social_roleplay'].get('status')=='roleplay_agreed'
                            and seen['last_social_roleplay'].get('topic') in ('date','dinner','movie','music')
                            else None),
    }
