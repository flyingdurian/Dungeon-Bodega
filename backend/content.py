"""Canonical fictional item/NPC definitions. Never let the language model change these."""
from dataclasses import dataclass

ITEMS = [
    {'id':'mana_potion','name':'Greater Mana Potion','price':50,'stock':4,'icon':'✦','description':'Restores mana after a punishing spell.'},
    {'id':'healing_draught','name':'Crimson Healing Draught','price':38,'stock':6,'icon':'♥','description':'A restorative tonic with the taste of wild cherries.'},
    {'id':'moonblade','name':'Moonsteel Dagger','price':115,'stock':2,'icon':'⚔','description':'A light blade smithed beneath the silver moon.'},
    {'id':'sun_charm','name':'Charm of Dawn','price':72,'stock':3,'icon':'☀','description':'A talisman favored by travelers in dark forests.'},
    {'id':'ember_scroll','name':'Scroll of Emberlight','price':42,'stock':4,'icon':'✧','description':'A common but reliable illumination charm.'},
    {'id':'wyvern_scale','name':'Wyvern Scale','price':88,'stock':1,'icon':'◆','description':'Harder than iron and prized by armorers.'},
    {'id':'silver_buckle','name':'Silver Road Buckle','price':23,'stock':6,'icon':'◇','description':'A well-crafted buckle worn by traveling caravans.'},
    {'id':'storm_vial','name':'Bottled Storm','price':130,'stock':2,'icon':'ϟ','description':'A crackle of enchanted thunder in blue glass.'},
    {'id':'sage_salve','name':'Sageleaf Salve','price':18,'stock':7,'icon':'❀','description':'A gentle remedy for scrapes and bruises.'},
    {'id':'rune_stone','name':'Whispering Runestone','price':104,'stock':2,'icon':'✶','description':'An old stone that hums when moonlight falls.'},
]

NPCS = [
 {'id':'aldric','name':'Sir Aldric','title':'The Broke Knight','archetype':'Honorable, anxious, aspiring knight','personality':'Proud of his honor, embarrassed about money, genuinely kind when treated well. A bad liar.','strategy':'Appeal to duty and need. Resents public mockery.','lore':'Knighthood, squires, battlefields, goblin raids, armor, healing draughts','voice':'Dylan','kokoro':'bm_george','chatterbox':'m01_kenji_shonen','reaction':'male_young','color':'#7699ad','style':0,'patience':72,'trust':54,'knowledge':3},
 {'id':'vesper','name':'Lady Vesper','title':'The Arrogant Noble','archetype':'Wealthy, proud, impatient noblewoman','personality':'Imperious and sophisticated, impatient with bargaining, will overpay to save face.','strategy':'Uses status and wealthy acquaintances as leverage. Humiliation ends negotiations.','lore':'Courts, estates, royal ceremonies, noble fashions, jewels and enchanted heirlooms','voice':'Serena','kokoro':'bf_emma','chatterbox':'f08_elena_noble','reaction':'female_mature','color':'#bd81aa','style':1,'patience':42,'trust':35,'knowledge':4},
 {'id':'garrick','name':'Garrick','title':'The Grizzled Mercenary','archetype':'Practical, grim, scarred professional fighter','personality':'Gruff, no-nonsense, grudging respect for honest trades and quality workmanship.','strategy':'Challenges product quality, not easily swayed by flattery.','lore':'Swords, battle formations, mercenary contracts, monsters, weapon repairs','voice':'Uncle_Fu','kokoro':'bm_fable','chatterbox':'m03_garrick_dwarf','reaction':'male_deep','color':'#b98967','style':2,'patience':59,'trust':42,'knowledge':5},
 {'id':'pippa','name':'Pippa','title':'The Excitable Alchemist','archetype':'Bright, distractible apprentice alchemist','personality':'Talkative, curious and delighted by unusual ingredients. Sometimes accidentally reveals her need.','strategy':'Rambles about experiments and occasionally tips her hand.','lore':'Mana potions, alchemy, reagents, herbs, spell theory and guild examinations','voice':'Ono_Anna','kokoro':'af_sky','chatterbox':'f01_sakura_genki','reaction':'female_anime_bright','color':'#93b6a3','style':3,'patience':86,'trust':66,'knowledge':5},
 {'id':'silas','name':'Silas','title':'The Shady Fence','archetype':'Clever and unreliable black-market trader','personality':'Dry, mischievous, theatrical, opportunistic. Likes to bluff about other buyers.','strategy':'Invents other buyers, creates urgency and probes for weak spots.','lore':'Thieves guilds, contraband, lockpicks, smugglers and street markets','voice':'Eric','kokoro':'am_michael','chatterbox':'m04_silas_rogue','reaction':'male_young','color':'#9b98ab','style':4,'patience':68,'trust':30,'knowledge':4},
 {'id':'brunna','name':'Brunna','title':'The Veteran Trader','archetype':'Experienced dwarven merchant','personality':'Steady, precise, skeptical, pleasantly competitive when impressed.','strategy':'Knows prices and makes calculated offers with little emotional leakage.','lore':'Trade routes, tariffs, ore, forging, tariffs, caravans, ledgers and guild law','voice':'Vivian','kokoro':'af_sarah','chatterbox':'f09_tessa_blacksmith','reaction':'female_mature','color':'#b88758','style':5,'patience':76,'trust':47,'knowledge':5},
 {'id':'elio','name':'Elio','title':'The Nervous Apprentice','archetype':'Timid young scholar of magic','personality':'Eager to please, apologetic, flustered by confrontation, earnest about studying.','strategy':'Fears losing the errand and sometimes overpays out of anxiety.','lore':'Academy lessons, beginner spells, mana, familiars and strict tutors','voice':'Ryan','kokoro':'am_adam','chatterbox':'m01_kenji_shonen','reaction':'male_young','color':'#91a5cf','style':6,'patience':53,'trust':58,'knowledge':3},
 {'id':'roderic','name':'Roderic','title':'The Boastful Dragon Hunter','archetype':'Loud self-proclaimed dragon slayer','personality':'Boisterous, exaggerated and easily swayed by flattery about his feats.','strategy':'Demands heroic discounts and tells fantastical stories, many exaggerated.','lore':'Dragon lairs, scales, mountain passes, wyrms, axes and ballads','voice':'Aiden','kokoro':'am_onyx','chatterbox':'m05_roderic_hunter','reaction':'male_deep','color':'#bc6558','style':7,'patience':64,'trust':44,'knowledge':3},
 {'id':'seraphine','name':'Seraphine','title':'The Calculating Mage','archetype':'Composed elven arcane researcher','personality':'Thoughtful, precise and dryly witty, values information and rational arguments.','strategy':'Tests claims and leverages specialized knowledge; may offer favors.','lore':'Runes, enchantments, mana, ancient histories, wizard colleges and planar magic','voice':'Sohee','kokoro':'af_nicole','chatterbox':'f03_yuki_kuudere','reaction':'female_mature','color':'#84a9b9','style':8,'patience':75,'trust':50,'knowledge':5},
 {'id':'fenwick','name':'Fenwick','title':'The Traveling Opportunist','archetype':'Fast-talking charismatic caravan dealer','personality':'Cheerful, slippery, always chasing the next opportunity; loves bundles and clever swaps.','strategy':'Changes the pitch mid-bargain, exaggerates scarcity.','lore':'Caravans, distant kingdoms, markets, smuggling routes, wares and stories','voice':'Dylan','kokoro':'bm_lewis','chatterbox':'m06_fenwick_merchant','reaction':'male_young','color':'#b6a15f','style':9,'patience':81,'trust':47,'knowledge':4}
]

# V0.4: Parallel modern customers at the fantasy crossroads shop.
# Contemporary speech/lore is intentional; these visitors know modern culture.
NPCS.append({'id': 'maya', 'name': 'Maya "Byte" Torres', 'title': 'The Gen Z Trend Seeker', 'archetype': 'Fast-talking digital native with playful confidence', 'personality': 'Energetic, meme-literate, expressive, funny, fiercely price-conscious.', 'strategy': 'Uses playful sarcasm, social proof and bundle requests; dislikes condescension.', 'lore': 'Streaming, smartphones, iPhones, GTA 6, music, thrifting, cosplay and magical curios', 'voice': 'Ono_Anna', 'kokoro': 'af_sky', 'chatterbox': 'f01_sakura_genki', 'reaction': 'female_anime_bright', 'color': '#b985db', 'style': 0, 'patience': 78, 'trust': 57, 'knowledge': 4, 'era': 'modern'})
NPCS.append({'id': 'noah', 'name': 'Noah Chen', 'title': 'The Millennial Side Hustler', 'archetype': 'Pragmatic side-business seller', 'personality': 'Friendly but analytical, always chasing a useful margin.', 'strategy': 'Compares prices, cites resale markets and proposes practical trades.', 'lore': 'Online marketplaces, freelancing, startups, work, commuting, gadgets', 'voice': 'Dylan', 'kokoro': 'am_adam', 'chatterbox': 'm06_fenwick_merchant', 'reaction': 'male_young', 'color': '#8cacbd', 'style': 1, 'patience': 67, 'trust': 52, 'knowledge': 4, 'era': 'modern'})
NPCS.append({'id': 'denise', 'name': 'Denise Walker', 'title': 'The Budget-Conscious Parent', 'archetype': 'No-nonsense working parent', 'personality': 'Protective, warm when respected, tired of inflated prices.', 'strategy': 'Requests value and durability; walks away from pressure tactics.', 'lore': 'Family finances, groceries, smartphones, neighborhood and everyday needs', 'voice': 'Serena', 'kokoro': 'af_sarah', 'chatterbox': 'f09_tessa_blacksmith', 'reaction': 'female_mature', 'color': '#d2a38a', 'style': 2, 'patience': 65, 'trust': 64, 'knowledge': 4, 'era': 'modern'})
NPCS.append({'id': 'kai', 'name': 'Kai Navarro', 'title': 'The Gen Z Bargain Hunter', 'archetype': 'Confident gaming enthusiast', 'personality': 'Playful, social, impulsive, extremely competitive about deals.', 'strategy': 'Uses comparison shopping and friendly joking; likes surprising discounts.', 'lore': 'Games, GTA 6, phones, streamers, gaming gear and fantasy loot', 'voice': 'Ryan', 'kokoro': 'am_michael', 'chatterbox': 'm01_kenji_shonen', 'reaction': 'male_young', 'color': '#8b9ee2', 'style': 3, 'patience': 71, 'trust': 49, 'knowledge': 4, 'era': 'modern'})
NPCS.append({'id': 'imani', 'name': 'Imani Brooks', 'title': 'The Collector', 'archetype': 'Passionate limited-edition collector', 'personality': 'Curious, meticulous, thrilled by rarity and provenance.', 'strategy': 'Pays extra for verified authenticity; rejects vague claims.', 'lore': 'Rare sneakers, trading cards, memorabilia, antiques and enchanted curios', 'voice': 'Vivian', 'kokoro': 'af_nova', 'chatterbox': 'f08_elena_noble', 'reaction': 'female_mature', 'color': '#c58eaa', 'style': 4, 'patience': 79, 'trust': 58, 'knowledge': 4, 'era': 'modern'})
NPCS.append({'id': 'rafael', 'name': 'Rafael Ortiz', 'title': 'The Repair Technician', 'archetype': 'Practical hands-on expert', 'personality': 'Reserved, exacting, confident in knowing how things work.', 'strategy': 'Points out defects, rejects cosmetic hype and asks fair prices.', 'lore': 'Mechanics, phones, repairs, batteries, materials and durable goods', 'voice': 'Eric', 'kokoro': 'am_onyx', 'chatterbox': 'm03_garrick_dwarf', 'reaction': 'male_deep', 'color': '#a99b87', 'style': 5, 'patience': 70, 'trust': 54, 'knowledge': 4, 'era': 'modern'})
NPCS.append({'id': 'zoe', 'name': 'Zoe Park', 'title': 'The Social Influencer', 'archetype': 'Image-conscious but clever creator', 'personality': 'Expressive and occasionally performative; hates being patronized.', 'strategy': 'Mentions exposure or reviews but cannot force special discounts.', 'lore': 'Social media, creators, fashion, iPhones, trends and gaming culture', 'voice': 'Sohee', 'kokoro': 'af_heart', 'chatterbox': 'f05_akari_idol', 'reaction': 'female_anime_bright', 'color': '#d49aba', 'style': 6, 'patience': 66, 'trust': 44, 'knowledge': 4, 'era': 'modern'})
NPCS.append({'id': 'arthur', 'name': 'Arthur Bell', 'title': 'The Old-School Traditionalist', 'archetype': 'Retired craftsman and hard bargainer', 'personality': 'Dry wit, proud experience, skeptical of flashy trends.', 'strategy': 'Respects craftsmanship, courtesy and straight numbers.', 'lore': 'Older technology, trade history, decades of experience and current life', 'voice': 'Uncle_Fu', 'kokoro': 'bm_george', 'chatterbox': 'm03_garrick_dwarf', 'reaction': 'male_deep', 'color': '#b1a18d', 'style': 7, 'patience': 54, 'trust': 49, 'knowledge': 4, 'era': 'modern'})
NPCS.append({'id': 'priya', 'name': 'Priya Shah', 'title': 'The Data-Driven Optimizer', 'archetype': 'Methodical millennial analyst', 'personality': 'Thoughtful, composed, enjoys calculating good-value deals.', 'strategy': 'Compares total value and requests evidence rather than bluffing.', 'lore': 'Budgeting, technology, spreadsheets, consumer trends and data', 'voice': 'Vivian', 'kokoro': 'af_bella', 'chatterbox': 'f03_yuki_kuudere', 'reaction': 'female_mature', 'color': '#9bafd0', 'style': 8, 'patience': 85, 'trust': 60, 'knowledge': 4, 'era': 'modern'})
NPCS.append({'id': 'mason', 'name': 'Mason Reed', 'title': 'The Burned-Out Office Worker', 'archetype': 'Tired office commuter', 'personality': 'Wry, impatient, dryly funny but generous to friendly people.', 'strategy': 'Values speed and convenience; will pay more to end a negotiation.', 'lore': 'Work meetings, transit, coffee, apps, gaming and ordinary modern life', 'voice': 'Aiden', 'kokoro': 'bm_lewis', 'chatterbox': 'm05_roderic_hunter', 'reaction': 'male_young', 'color': '#9d9a9b', 'style': 9, 'patience': 45, 'trust': 47, 'knowledge': 4, 'era': 'modern'})

for _npc in NPCS:
    _npc.setdefault('era', 'fantasy')


# V0.5.3: Chinese-speaking dynasty-era trader, deliberately bilingual comprehension.
NPCS.append({'id':'liu_xue','name':'柳雪 · Liu Xue','title':'The Silk-Road Curio Dealer',
 'archetype':'Witty dynasty-era Chinese traveling merchant, fluent in Mandarin and understands English',
 'personality':'Playful, shrewd, elegant and easily amused by foreign expressions. Primarily speaks natural Mandarin; her limited English is charming and inconsistent.',
 'strategy':'Bargains gracefully, enjoys playful banter, values handmade work and genuine politeness.',
 'lore':'Silk roads, tea, porcelain, jade, inkstones, caravans, medicinal herbs, classical Chinese customs',
 'voice':'Vivian','kokoro':'zf_xiaoxiao','chatterbox':'f08_elena_noble','reaction':'female_mature','color':'#d6b27a','style':10,
 'patience':75,'trust':56,'knowledge':4,'era':'fantasy','language':'zh-CN'})

# V1.0 character expansion: two historical fantasy traders and two contemporary visitors.
# Each entry has an independent personality, interests, economics and Hermes preset.
NPCS.extend([
 {'id':'safiya','name':'Safiya al-Nur','title':'The Star-Road Astronomer',
  'archetype':'Desert caravan navigator, astronomer and trader of rare instruments',
  'personality':'Observant, poised, intellectually playful, patient with questions yet intolerant of fabricated expertise.',
  'strategy':'Values precision and provenance; negotiates by comparing the real craft behind an item with its price.',
  'lore':'Constellations, astrolabes, desert caravans, navigation, night skies and antique instruments',
  'voice':'Serena','kokoro':'af_nicole','chatterbox':'f13_sylvia_librarian','reaction':'female_mature',
  'color':'#ab95e8','style':11,'patience':73,'trust':50,'knowledge':5,'era':'fantasy'},
 {'id':'elara_veyne','name':'Elara Veyne','title':'The Midnight Manuscript Scholar',
  'archetype':'Mysterious archivist and collector of enchanted books',
  'personality':'Dryly witty, erudite and a little intimidating; secretly delighted by rare literature.',
  'strategy':'Inspects authenticity and asks sharp questions; rewards scholarly honesty and resists bluffing.',
  'lore':'Forbidden libraries, palimpsests, arcane scripts, rare inks and provenance of old books',
  'voice':'Sohee','kokoro':'af_nicole','chatterbox':'f13_sylvia_librarian','reaction':'female_mature',
  'color':'#9d79c9','style':12,'patience':65,'trust':47,'knowledge':5,'era':'fantasy'},
 {'id':'rin_kaede','name':'Rin Kaede','title':'The Cosplay Café Performer',
  'archetype':'Cheerful cosplay artist, performer and pop-culture collector',
  'personality':'Bubbly, theatrical, quick to tease and genuinely kind; can get serious when misunderstood.',
  'strategy':'Playfully negotiates bundles, likes gifts and surprises, dislikes dismissive comments about her craft.',
  'lore':'Cosplay, live performances, game conventions, anime, handcrafted outfits and fan art',
  'voice':'Ono_Anna','kokoro':'af_sky','chatterbox':'f05_akari_idol','reaction':'female_anime_bright',
  'color':'#ed96c6','style':13,'patience':82,'trust':61,'knowledge':5,'era':'modern'},
 {'id':'master_chen','name':'Master Chen Wei','title':'The Veteran Antique Appraiser',
  'archetype':'Retired master conservator, specialist in historic antiques',
  'personality':'Quietly humorous, courteous and stubborn about factual accuracy. A patient storyteller.',
  'strategy':'Uses material knowledge, wear patterns and restoration costs to challenge questionable valuations.',
  'lore':'Antique porcelain, calligraphy, restoration, watchmaking, conservation and auction houses',
  'voice':'Uncle_Fu','kokoro':'bm_george','chatterbox':'m03_garrick_dwarf','reaction':'male_deep',
  'color':'#b6a179','style':14,'patience':77,'trust':59,'knowledge':5,'era':'modern'},
])

# V1.2 — Four new visitors with distinct economies, personalities and existing
# locked Hermes preset IDs. Portrait readiness is separately audited by art manifest.
NPCS.extend([
 {'id':'mara_copperwell','name':'Mara Copperwell','title':'The Clockwork Restorer',
  'archetype':'Ingenious fantasy clockmaker and practical repair artisan',
  'personality':'Wry, patient when inspecting mechanisms, excited by broken curios, distrustful of beautiful but empty ornament.',
  'strategy':'Tests fittings and repairs before negotiating; prefers fixable flaws over mystery claims.',
  'lore':'Clockwork instruments, damaged heirlooms, maker stamps, springs, metalworking and restoration',
  'voice':'Vivian','kokoro':'af_sarah','chatterbox':'f09_tessa_blacksmith','reaction':'female_mature',
  'color':'#d4a275','style':15,'patience':77,'trust':54,'knowledge':5,'era':'fantasy'},
 {'id':'tarek_ashwood','name':'Tarek Ashwood','title':'The Frontier Mapmaker',
  'archetype':'Reserved frontier surveyor and keeper of old routes',
  'personality':'Watchful, principled, dry humor, values practical travel gear and honest origin stories.',
  'strategy':'Questions provenance and durability; trades information only when trust is earned.',
  'lore':'Lost roads, map ink, caravan passes, weathered tools, ancient trade routes and land claims',
  'voice':'Dylan','kokoro':'bm_lewis','chatterbox':'m06_finn_rogue','reaction':'male_young',
  'color':'#a4a87e','style':16,'patience':64,'trust':46,'knowledge':5,'era':'fantasy'},
 {'id':'yuna_seo','name':'Yuna Seo','title':'The Forensic Gemologist',
  'archetype':'Modern material-science specialist and serious jewelry collector',
  'personality':'Precise, quietly warm, direct about defects, enjoys explaining the difference between shine and value.',
  'strategy':'Insists on inspection notes and credible provenance, rejects unsupported authenticity claims.',
  'lore':'Gemstone grading, repair labs, vintage jewelry, antique markets, metallurgy and auction records',
  'voice':'Sohee','kokoro':'af_nicole','chatterbox':'f15_camille_jeweler','reaction':'female_mature',
  'color':'#8cbed4','style':17,'patience':78,'trust':59,'knowledge':5,'era':'modern'},
 {'id':'felix_rowe','name':'Felix Rowe','title':'The Auction Floor Showman',
  'archetype':'Modern auction host, charming fast talker and avid market observer',
  'personality':'Quick-witted, theatrically charming, genuinely appreciates unusual stories, hates being caught bluffing.',
  'strategy':'Mentions rival bidders and excitement, but yields to documented evidence.',
  'lore':'Auctions, collectors, provenance, social media, vintage tech, luxury memorabilia and appraisal reports',
  'voice':'Ryan','kokoro':'am_michael','chatterbox':'m04_marcus_merchant','reaction':'male_young',
  'color':'#bf98ae','style':18,'patience':67,'trust':43,'knowledge':4,'era':'modern'},
])

NPC_BY_ID = {n['id']: n for n in NPCS}
ITEM_BY_ID = {i['id']: i for i in ITEMS}

# Offline flavor sentences: enough variety to play test the mechanics without AI credentials.
OFFLINE_FLAVOR = {
 'aldric':['My honor is intact, though my purse is decidedly less so.','You have my word, and for a knight that means something.','It is no easy thing to admit one needs help.'],
 'vesper':['Must we haggle over every copper? How positively exhausting.','I have no intention of making a spectacle of myself.','My household has better things to do than stand here all afternoon.'],
 'garrick':['I know what good steel costs. Do not mistake me for a fool.','The road has taught me to count my coin twice.','Hm. At least you are talking plainly.'],
 'pippa':['Oh! My mentor says bargaining is a precise science, but I keep losing count!','Imagine what a dash of starlight could do to that!','I really, really need this for my experiment.'],
 'silas':['I have heard prettier offers from a drunken pickpocket.','Funny thing about coin: it never stays where you left it.','I would never cheat you. Well, not today.'],
 'brunna':['There is a fair price, and then there is a foolish price.','I have worked this road longer than you have tended this counter.','A good bargain leaves both parties able to sleep.'],
 'elio':['Oh dear. My tutor will ask for the receipt.','I promise I am trying to do this properly.','May we perhaps speak a little more quietly?'],
 'roderic':['HA! You should have seen me face the wyrm of Black Peak!','A dragon hunter deserves a dragon hunter’s price!','There are songs about my courage. Several, in fact.'],
 'seraphine':['I find curiosity cheaper than gold, though rarely as useful.','Magic is precise. So should a transaction be.','An intriguing proposition, if somewhat optimistic.'],
 'fenwick':['Ah, now there is the beginning of a beautiful deal!','I have crossed three kingdoms for less than that.','Give me an inch and I shall find a way to sell you a mile.'],
}

# Modern offline dialogue is explicitly a fallback, not generative dialogue.
OFFLINE_FLAVOR['maya'] = ["Okay, that's kind of wild. Let's talk actual value.", "I'm not saying you're wrong, but I'm checking the vibes on this deal.", 'I came to bargain, not get roasted, okay?']
OFFLINE_FLAVOR['noah'] = ['Let me run the numbers for a second.', "I'd like us both to walk away feeling that was fair.", 'We can work out a better margin than this.']
OFFLINE_FLAVOR['denise'] = ["I'm watching every coin, so please be reasonable.", 'I buy things to last, not to impress anyone.', "Be straight with me and we'll get somewhere."]
OFFLINE_FLAVOR['kai'] = ['Bro, the price is kinda wild, not gonna lie.', "Okay, that's actually a solid point.", 'Wait, let me try a different angle.']
OFFLINE_FLAVOR['imani'] = ["Can you tell me the item's history?", "I'm interested in authenticity, not just shiny packaging.", 'This might be special enough for my collection.']
OFFLINE_FLAVOR['rafael'] = ["I've fixed too many of these to pay for polish alone.", 'Can I inspect the construction first?', 'That part is worth something. The rest, maybe not.']
OFFLINE_FLAVOR['zoe'] = ['I love the aesthetic, but I still have a budget.', "Okay, you've got my attention.", 'That would make a great story, actually.']
OFFLINE_FLAVOR['arthur'] = ['Back in my day, people stood behind their craftsmanship.', "Let's keep the fancy talk out of it.", "Now that's a sensible way to bargain."]
OFFLINE_FLAVOR['priya'] = ["I'd like to see the value behind that number.", "The comparison isn't quite apples to apples.", "I'd rather have evidence than urgency."]
OFFLINE_FLAVOR['mason'] = ["It's been a long day, so make this easy for me.", "I'm willing to pay for less hassle.", "I don't have the energy for another endless discussion."]

OFFLINE_FLAVOR['liu_xue'] = ['这个价钱嘛……我们可以再商量商量。', '你说得有意思！可是，便宜一点，好不好？', '我听得懂英文，只是说得不太好。Very little English, hehe.']

OFFLINE_FLAVOR['safiya'] = ['A precise instrument is worth more than ornament. Shall we examine the craftsmanship?', 'The stars are steady. Prices, less so.', 'Tell me where you found this. Its history may change what I offer.']
OFFLINE_FLAVOR['elara_veyne'] = ['The ink is older than the binding. Curious.', 'A clever price, but I have read better arguments.', 'I value the record as much as the relic.']
OFFLINE_FLAVOR['rin_kaede'] = ['Oh, that would look amazing at my next convention!', 'Okay, adorable, but how much does it actually cost?', 'I know good craftsmanship when I see it, even under all that glitter.']
OFFLINE_FLAVOR['master_chen'] = ['The glaze reveals more than a seller ever will.', 'We can disagree about price without disagreeing about respect.', 'This workmanship reminds me of a piece I repaired years ago.']

OFFLINE_FLAVOR['mara_copperwell']=['That repair is worth more than polish.', 'The spring is honest; the seller may not be.', 'Bring it closer. I want to see the maker marks.']
OFFLINE_FLAVOR['tarek_ashwood']=['I have followed this mark across three border roads.', 'A map is only as true as its last honest witness.', 'Show me where the wear begins.']
OFFLINE_FLAVOR['yuna_seo']=['I can see an inconsistency in that setting.', 'A plausible history is not the same thing as a certificate.', 'Let me inspect it before we discuss numbers.']
OFFLINE_FLAVOR['felix_rowe']=['Now that is an interesting story for the auction floor.', 'You can sell excitement, but you cannot sell imaginary evidence.', 'If the provenance holds up, the bidding might surprise us.']
