"""Deterministic narrative safety fallback for The Living Counter.

Exodia Tower, not this module, supplies live AI dialogue. Nothing in the
fallback module calls a hosted model, reads credentials or mutates the economy.
"""
from __future__ import annotations
import hashlib
import re
from .content import OFFLINE_FLAVOR

OFFTOPIC = re.compile(r'\b(?:iphone|smartphone|gta\s*6|internet|youtube|bitcoin|wifi|computer|playstation)\b', re.I)
ATTACK = re.compile(r'\b(?:ignore (?:all|previous)|system prompt|instructions|maximum price|secret price|hidden value|roleplay as|developer mode|print your)\b', re.I)


def offline_flavor(scene, state):
    text = scene['user_text']
    npc = state['npc_id']
    if scene.get('event') == 'deal':
        return "Hm. You bargain better than most merchants I've met."
    if scene.get('event') == 'walkout':
        return 'I believe this discussion has reached its end.'
    if scene.get('event') == 'rejected':
        return 'That offer does not sit right with me.'
    if ATTACK.search(text):
        return 'Nice try, shopkeeper. I keep my own counsel.'
    if state.get('npc_id') and __import__('backend.content',fromlist=['NPC_BY_ID']).NPC_BY_ID[npc].get('era') != 'modern' and OFFTOPIC.search(text):
        # Keep the fallback topical when Exodia is unreachable/rejects a reply.
        # Do not falsely make the user think a fresh model response was generated.
        newest = list(OFFTOPIC.finditer(text))
        topic = newest[-1].group(0).lower() if newest else ''
        if 'iphone' in topic or 'smartphone' in topic:
            return 'An eye-phone? Is that some new kind of scrying charm?'
        if topic.startswith('gta'):
            return 'G-T-A six? Is that a new guild or some foreign knightly order?'
        if topic in ('wifi', 'internet'):
            return 'A web without spiders? I have never heard of such magic.'
        if topic == 'youtube':
            return 'You-tube? Sounds like an alchemist\'s glasswork to me.'
        if topic == 'bitcoin':
            return 'Bit-coin? I take proper minted gold, not imaginary coins.'
        if topic == 'playstation':
            return 'A station for playing? Surely the tavern already serves that purpose.'
        if topic == 'computer':
            return 'A com-pu-ter? That word tells me nothing, friend.'
        return 'Strange words, merchant. I have never heard of such a thing.'
    if scene.get('interrupted'):
        return 'Hmph! I was not quite finished speaking.'
    if 'dragon' in text.lower():
        return 'Dragons? Aye, I know better than to underestimate them.'
    if 'mana' in text.lower() and npc == 'pippa':
        return "Mana is the very lifeblood of an alchemist's craft!"
    choices = OFFLINE_FLAVOR[npc]
    i = int(hashlib.sha256(f'{state["id"]}:{state["turn"]}:{text}'.encode()).hexdigest()[:8], 16) % len(choices)
    return choices[i]


def narrative(scene, state):
    """Legacy safe local fallback. Real AI is scheduled by dialogue_jobs.py."""
    return offline_flavor(scene, state), False
