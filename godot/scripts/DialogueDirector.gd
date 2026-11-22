extends RefCounted
## V0.7 Dialogue Performance Director.
## Pure local deterministic styling; never edits the spoken line or makes a model call.
## The same plan is used by gameplay and the F8 preview studio.

const RULES := [
	{"kind":"sad","priority":105,"rx":"(?i)(?:\\b(?:i am sorry|i'm sorry|it hurts|i miss|heartbroken|sad|lonely|disappointed|hopeless|lost someone|i regret|i feel terrible|my heart sank|i wish i could)\\b|难过|伤心|失望|遗憾|心碎|悲伤|我想念|唉|对不起)"},
	{"kind":"anger","priority":114,"rx":"(?i)(?:\\b(?:you insult me|how dare you|i hate you|furious|unacceptable|unbelievable|never in my life|enough is enough|absolutely ridiculous)\\b|气死我了|真是岂有此理|滚|羞辱)"},
	{"kind":"anger","priority":110,"rx":"(?i)(?:\\b(?:how dare you|you dare|absolutely not|are you kidding|what a joke|ridiculous|outrageous|insulting|unacceptable|furious|rude|never again|get out|too expensive|hate this|I refuse|shut up)\\b|太过分|岂有此理|荒唐|无礼|放肆|骗子|不可能|太贵了|太贵|高啊|滚出去|气死我|别想)"},
	{"kind":"flirt","priority":102,"rx":"(?i)(?:\\b(?:go on a date|take you on a date|dinner with me|you are cute|you're cute|you're gorgeous|you're beautiful|sweetheart|darling|my dear|kiss me|flirting|I like you|you like me|you fancy me)\\b|约会|请你吃饭|喜欢你|喜欢我|心动|好可爱|小美人|亲爱的)"},
	{"kind":"persuade","priority":98,"rx":"(?i)(?:\\b(?:a better deal|better deal|better price|lower the price|give me a discount|sweeten the deal|how about|what if|hear me out|give me a chance|make it worth|cut me a deal|meet me halfway|special price|I propose)\\b|便宜一点|便宜些|再便宜|给个面子|商量一下|能不能便宜|优惠点|再商量|打个折|一口价)"},
	{"kind":"delight","priority":92,"rx":"(?i)(?:\\b(?:wonderful|magnificent|amazing|excellent|perfect|beautiful|lovely|delighted|fantastic|brilliant|charming|gorgeous|so cute|I love it|love that|best thing ever|that's awesome|thank you so much)\\b|太棒了|太好了|真好|好漂亮|真漂亮|喜欢|谢谢|多谢|好开心|太美了|真有趣)"},
	{"kind":"doubt","priority":87,"rx":"(?i)(?:\\b(?:are you sure|you sure|really[!?]?|seriously[!?]?|perhaps|possibly|maybe|hmm+|uhh+|I doubt|I wonder|not sure|sounds suspicious|let me think|wait a moment|hold on|I'm skeptical|prove it)\\b|真的吗|真的么|不会吧|难道|也许|可能|不确定|再想想|让我想想|稍等|嗯|哎呀)"},
	{"kind":"agreement","priority":80,"rx":"(?i)(?:\\b(?:that sounds fair|sounds fair|that's fair|agreed|well played|fair enough|we have a deal|you have my word)\\b|成交|说定了|好吧|公平|不错|可以考虑)"},
	{"kind":"gold","priority":76,"rx":"(?i)(?:\\b\\d{1,5}\\s*(?:gold|coins?|g)\\b|这个价格|这价格|价钱|价格|金币|金子|金钱|黄金|值这个价|出价|报价)"},
	{"kind":"persuade","priority":47,"rx":"(?i)(?:\\b(?:bargain|discount|counteroffer|trade offer|negotiating|negotiation)\\b|讨价还价|划算|合适)"},
]

const PALETTES := {
	"gold":{"fg":"#ffedaa", "bg":"#483013", "outline":"#bd791b", "size":34, "symbol":"✦"},
	"anger":{"fg":"#ff9b9e", "bg":"#632036", "outline":"#ff324b", "size":35, "symbol":"!!"},
	"persuade":{"fg":"#9af7ff", "bg":"#153b58", "outline":"#1aaeea", "size":34, "symbol":"➶"},
	"doubt":{"fg":"#e7c9ff", "bg":"#422450", "outline":"#b47cf6", "size":32, "symbol":"?"},
	"delight":{"fg":"#ffeabb", "bg":"#603d22", "outline":"#ffc460", "size":34, "symbol":"✧"},
	"flirt":{"fg":"#ffc2dd", "bg":"#62334e", "outline":"#ed70ba", "size":33, "symbol":"♥"},
	"agreement":{"fg":"#c0f7cc", "bg":"#284b38", "outline":"#6edfa1", "size":32, "symbol":"✓"},
	"sad":{"fg":"#b8d2ee", "bg":"#26354a", "outline":"#628da8", "size":30, "symbol":"☂"},
}

static func perform(line: String, mood: String, intensity: float=1.0) -> Dictionary:
	var text: String=line.replace("[", "［").replace("]", "］")
	if text.is_empty():
		return {"bbcode":"", "cues":[], "categories":[], "plain":line}
	var raw_matches: Array=[]
	for rule in RULES:
		var rx: RegEx=RegEx.create_from_string(str(rule["rx"]))
		if rx==null:
			continue
		for found in rx.search_all(text):
			var a: int=found.get_start()
			var b: int=found.get_end()
			if b>a:
				raw_matches.append({"start":a,"end":b,"kind":rule["kind"],"priority":rule["priority"]})
	# Use the game-owned mood only as a conservative fallback for unusually emotional
	# lines with no recognized phrase. Do not paint every neutral reply.
	if raw_matches.is_empty() and mood in ["annoyed","furious","offended","angry","delighted","happy","skeptical","suspicious","sad","nervous"]:
		var category: String="anger" if mood in ["annoyed","furious","offended","angry"] else "delight" if mood in ["delighted","happy"] else "sad" if mood in ["sad","nervous"] else "doubt"
		var first: int=0
		while first<text.length() and text.substr(first,1)==" ":
			first+=1
		var last: int=mini(text.length(),first+18)
		var boundary: int=text.find(" ",first+6)
		if boundary>0 and boundary<last:
			last=boundary
		if last>first:
			raw_matches.append({"start":first,"end":last,"kind":category,"priority":42})
	raw_matches.sort_custom(func(a: Dictionary,b: Dictionary):
		if int(a["priority"])!=int(b["priority"]):
			return int(a["priority"])>int(b["priority"])
		return int(a["end"])-int(a["start"])>int(b["end"])-int(b["start"])
	)
	var cues: Array=[]
	var coverage: int=0
	var limit: int=maxi(13,roundi(float(text.length())*0.66))
	for candidate in raw_matches:
		if cues.size()>=4:
			break
		var start: int=int(candidate["start"])
		var end: int=int(candidate["end"])
		if coverage+end-start>limit:
			continue
		var overlaps: bool=false
		for existing in cues:
			if start<int(existing["end"]) and end>int(existing["start"]):
				overlaps=true
				break
		if overlaps:
			continue
		cues.append(candidate)
		coverage+=end-start
	cues.sort_custom(func(a:Dictionary,b:Dictionary):return int(a["start"])<int(b["start"]))
	var result: String=""
	var cursor: int=0
	var categories: Array=[]
	for cue in cues:
		var start: int=int(cue["start"])
		var end: int=int(cue["end"])
		var category: String=str(cue["kind"])
		result+=text.substr(cursor,start-cursor)
		result+=_span_bbcode(text.substr(start,end-start),category,intensity)
		categories.append(category)
		cursor=end
	result+=text.substr(cursor)
	return {"bbcode":result,"cues":cues,"categories":categories,"plain":line}

static func _span_bbcode(term: String, category: String, intensity: float) -> String:
	var style: Dictionary=PALETTES.get(category,PALETTES["gold"])
	var size: int=int(roundf(27.0+(float(style["size"])+2.0-27.0)*clampf(intensity,0.5,1.5)))
	var prefix: String="[emote kind=%s power=%.2f][b][bgcolor=%s][color=%s][outline_size=4][outline_color=%s][font_size=%d]" % [category,clampf(intensity,0.5,1.5),style["bg"],style["fg"],style["outline"],size]
	var suffix: String="[/font_size][/outline_color][/outline_size][/color][/bgcolor][/b][/emote]"
	if category=="persuade":
		return prefix+"[u]"+term+"[/u]"+suffix
	if category in ["sad", "doubt", "flirt"]:
		# Distinct slanted letterforms without relying on missing external fonts.
		return prefix+"[i]"+term+"[/i]"+suffix
	if category=="anger":
		return prefix+"[b]"+term+"[/b]"+suffix
	return prefix+term+suffix
