extends Panel
## V1.0 visitor gallery. Every card is a native interactive button, not a painted UI image.
## Portrait images are individual assets; no generated screenshot is used as the interface.
signal selected(npc_id: String, era: String)

const CAST := [
	{"id":"mara_copperwell", "name":"Mara Copperwell", "title":"Clockwork Restorer", "era":"fantasy", "accent":"#d4a275"},
	{"id":"tarek_ashwood", "name":"Tarek Ashwood", "title":"Frontier Mapmaker", "era":"fantasy", "accent":"#a4a87e"},
	{"id":"yuna_seo", "name":"Yuna Seo", "title":"Forensic Gemologist", "era":"modern", "accent":"#8cbed4"},
	{"id":"felix_rowe", "name":"Felix Rowe", "title":"Auction Showman", "era":"modern", "accent":"#bf98ae"},
	{"id":"safiya", "name":"Safiya al-Nur", "title":"Star-Road Astronomer", "era":"fantasy", "accent":"#b9a0eb"},
	{"id":"elara_veyne", "name":"Elara Veyne", "title":"Midnight Manuscript Scholar", "era":"fantasy", "accent":"#c19ee5"},
	{"id":"rin_kaede", "name":"Rin Kaede", "title":"Cosplay Café Performer", "era":"modern", "accent":"#ffafd4"},
	{"id":"master_chen", "name":"Master Chen Wei", "title":"Veteran Antique Appraiser", "era":"modern", "accent":"#dfc188"},
	{"id":"maya", "name":"Maya 'Byte' Torres", "title":"Gen Z Trend Seeker", "era":"modern", "accent":"#cbb1f4"},
	{"id":"liu_xue", "name":"柳雪 · Liu Xue", "title":"Silk-Road Curio Dealer", "era":"fantasy", "accent":"#efb9b4"},
	{"id":"garrick", "name":"Garrick", "title":"Grizzled Mercenary", "era":"fantasy", "accent":"#c8b19c"},
	{"id":"zoe", "name":"Zoe Park", "title":"Social Influencer", "era":"modern", "accent":"#ffc7d8"},
]

var list_grid: GridContainer
var hint_label: Label

func _ready() -> void:
	custom_minimum_size=Vector2(650,665)
	position=Vector2(240,107)
	size=Vector2(650,665)
	mouse_filter=Control.MOUSE_FILTER_STOP
	var sb:=StyleBoxFlat.new()
	sb.bg_color=Color("#170c22f9")
	sb.border_color=Color("#f3ca7f")
	sb.set_border_width_all(3)
	sb.set_corner_radius_all(20)
	sb.shadow_color=Color(0.03,0.0,0.025,0.85)
	sb.shadow_size=22
	add_theme_stylebox_override("panel",sb)
	var heading:=_label("VISITOR GALLERY  ·  29 CHARACTERS",Vector2(25,13),Vector2(540,42),24,Color("#f6d390"))
	add_child(heading)
	var close_button:=Button.new()
	close_button.text="✕"
	close_button.position=Vector2(591,15)
	close_button.size=Vector2(38,38)
	close_button.pressed.connect(func():visible=false)
	add_child(close_button)
	hint_label=_label("Choose a portrait to invite that customer to your counter. V1.2 visitors appear first.",Vector2(25,52),Vector2(605,34),13,Color("#e5c7b7"))
	add_child(hint_label)
	var scroll:=ScrollContainer.new()
	scroll.position=Vector2(23,94)
	scroll.size=Vector2(607,549)
	scroll.horizontal_scroll_mode=ScrollContainer.SCROLL_MODE_DISABLED
	add_child(scroll)
	list_grid=GridContainer.new()
	list_grid.columns=2
	list_grid.add_theme_constant_override("h_separation",13)
	list_grid.add_theme_constant_override("v_separation",15)
	scroll.add_child(list_grid)
	for person in CAST:
		_add_card(person)

func _label(value: String, pos: Vector2, dimensions: Vector2, font_size: int, color: Color) -> Label:
	var label:=Label.new()
	label.text=value
	label.position=pos
	label.size=dimensions
	label.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
	label.add_theme_font_size_override("font_size",font_size)
	label.add_theme_color_override("font_color",color)
	label.mouse_filter=Control.MOUSE_FILTER_IGNORE
	return label

func _add_card(person: Dictionary) -> void:
	var id: String=str(person.get("id",""))
	var card:=Button.new()
	card.text=""
	card.custom_minimum_size=Vector2(292,238)
	card.focus_mode=Control.FOCUS_NONE
	var flat:=StyleBoxFlat.new()
	flat.bg_color=Color("#2c1633")
	flat.border_color=Color(str(person.get("accent","#ba8bba")))
	flat.set_border_width_all(2)
	flat.set_corner_radius_all(12)
	flat.shadow_color=Color("#0b0416")
	flat.shadow_size=7
	card.add_theme_stylebox_override("normal",flat)
	var hover:=flat.duplicate() as StyleBoxFlat
	hover.bg_color=Color("#4b2455")
	hover.border_color=Color("#ffdc97")
	card.add_theme_stylebox_override("hover",hover)
	card.add_theme_stylebox_override("pressed",hover)
	var thumb: String="res://assets/vn_%s_thumb.png" % id
	if not ResourceLoader.exists(thumb):
		thumb="res://assets/vn_%s_neutral_thumb.png" % id
	if not ResourceLoader.exists(thumb):
		thumb="res://assets/customer_%s_neutral.png" % id
	if ResourceLoader.exists(thumb):
		var photo:=TextureRect.new()
		photo.texture=load(thumb)
		photo.position=Vector2(8,8)
		photo.size=Vector2(276,150)
		photo.expand_mode=TextureRect.EXPAND_IGNORE_SIZE
		photo.stretch_mode=TextureRect.STRETCH_KEEP_ASPECT_COVERED
		photo.mouse_filter=Control.MOUSE_FILTER_IGNORE
		card.add_child(photo)
	card.add_child(_label(str(person.get("name","")),Vector2(13,157),Vector2(267,28),18,Color("#fff0d9")))
	card.add_child(_label(str(person.get("title","")),Vector2(13,186),Vector2(266,21),13,Color("#dec2ba")))
	card.add_child(_label("◆ %s" % str(person.get("era","fantasy")).to_upper(),Vector2(13,211),Vector2(260,18),11,Color(str(person.get("accent","#d8af87")))))
	var era: String=str(person.get("era","fantasy"))
	card.pressed.connect(func():selected.emit(id,era))
	list_grid.add_child(card)
