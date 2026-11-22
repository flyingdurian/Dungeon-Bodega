extends Panel
signal intensity_changed(value: float)
## F8: in-game, offline-safe performance calibration. Uses EXACT runtime director,
## glyph effects, character assets and typing SFX; never calls Exodia or Hermes.
const Director=preload("res://scripts/DialogueDirector.gd")
const Pop=preload("res://scripts/DialoguePop.gd")
const Glyph=preload("res://scripts/EmotionGlyph.gd")
const SAMPLES := [
	["Value", "That rare treasure is worth 67 GOLD, but maybe give me a better deal?", "skeptical"],
	["Anger", "HOW DARE YOU! That price is RIDICULOUS! Get out of my shop!", "annoyed"],
	["Persuasion", "Hear me out: what if you give me a better price?", "skeptical"],
	["Flirting", "Oh? You want to take me on a date? You're cute, shopkeeper!", "amused"],
	["Delight", "Wonderful! That's an amazing find. I love it!", "happy"],
	["Mandarin", "这个价格太贵了！能不能便宜一点？嗯……也许可以考虑。", "skeptical"],
]
var preview: RichTextLabel
var portrait: TextureRect
var sample_input: LineEdit
var actor: OptionButton
var mood: OptionButton
var status: Label
var intensity_control: HSlider
var speed_control: HSlider
var tick: AudioStreamPlayer
var pop: RichTextEffect
var sample_line: String=""
var running: bool=false
var progress: float=0.0
var last_visible: int=0
var last_tick_ms: int=0
var studio_intensity: float=1.0

func _ready() -> void:
	position=Vector2(290,160)
	size=Vector2(860,577)
	var box:=StyleBoxFlat.new()
	box.bg_color=Color("#190d24fb")
	box.border_color=Color("#edbd75")
	box.set_border_width_all(2)
	box.set_corner_radius_all(17)
	box.shadow_color=Color(0.0,0.0,0.0,0.65)
	box.shadow_size=14
	add_theme_stylebox_override("panel",box)
	_label("DIALOGUE PERFORMANCE STUDIO · F8",Vector2(22,14),Vector2(690,38),24,Color("#ffdf99"))
	_label("Live game renderer preview · local only · no AI/API requests",Vector2(24,51),Vector2(680,23),13,Color("#d9b8c9"))
	var close_btn:=_button("CLOSE ✕",Vector2(733,15),Vector2(104,35))
	close_btn.pressed.connect(func():visible=false)
	actor=_selector(Vector2(24,85),Vector2(170,36),["maya","liu_xue"])
	mood=_selector(Vector2(206,85),Vector2(165,36),["neutral","thinking","amused","skeptical","annoyed","happy"])
	_label("IMPACT",Vector2(391,85),Vector2(84,32),14,Color("#f4ce87"))
	intensity_control=HSlider.new()
	intensity_control.position=Vector2(469,91)
	intensity_control.size=Vector2(141,25)
	intensity_control.min_value=0.5
	intensity_control.max_value=1.5
	intensity_control.step=0.1
	intensity_control.value=1.0
	add_child(intensity_control)
	_label("SPEED",Vector2(626,85),Vector2(78,32),14,Color("#f4ce87"))
	speed_control=HSlider.new()
	speed_control.position=Vector2(701,91)
	speed_control.size=Vector2(133,25)
	speed_control.min_value=12
	speed_control.max_value=56
	speed_control.step=2
	speed_control.value=27
	add_child(speed_control)
	actor.item_selected.connect(func(_index:int):_set_portrait())
	mood.item_selected.connect(func(_index:int):_set_portrait())
	intensity_control.value_changed.connect(func(_new_value:float):_rebuild())
	portrait=TextureRect.new()
	portrait.position=Vector2(23,143)
	portrait.size=Vector2(240,276)
	portrait.expand_mode=TextureRect.EXPAND_IGNORE_SIZE
	portrait.stretch_mode=TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	portrait.mouse_filter=Control.MOUSE_FILTER_IGNORE
	add_child(portrait)
	var speech_panel:=Panel.new()
	speech_panel.position=Vector2(274,143)
	speech_panel.size=Vector2(561,275)
	var speech_style:=StyleBoxFlat.new()
	speech_style.bg_color=Color("#2d1239")
	speech_style.border_color=Color("#eab678")
	speech_style.set_border_width_all(2)
	speech_style.set_corner_radius_all(12)
	speech_panel.add_theme_stylebox_override("panel",speech_style)
	add_child(speech_panel)
	preview=RichTextLabel.new()
	preview.position=Vector2(294,175)
	preview.size=Vector2(526,195)
	preview.bbcode_enabled=true
	preview.scroll_active=false
	preview.fit_content=false
	preview.add_theme_font_size_override("normal_font_size",26)
	preview.add_theme_color_override("default_color",Color("#fff0de"))
	pop=Pop.new()
	preview.install_effect(pop)
	preview.install_effect(Glyph.new())
	add_child(preview)
	status=_label("Choose a sample and press Preview",Vector2(293,378),Vector2(529,30),13,Color("#d1a8e5"))
	sample_input=LineEdit.new()
	sample_input.position=Vector2(23,432)
	sample_input.size=Vector2(641,39)
	sample_input.max_length=420
	sample_input.text="That is a wonderful treasure, but can you give me a better deal?"
	sample_input.add_theme_font_size_override("font_size",15)
	add_child(sample_input)
	var play_btn:=_button("▶ PREVIEW",Vector2(674,432),Vector2(160,39))
	play_btn.pressed.connect(_rebuild)
	var x: float=23.0
	for i in range(SAMPLES.size()):
		var sample_button:=_button(str(SAMPLES[i][0]),Vector2(x,484),Vector2(127,40))
		sample_button.pressed.connect(_sample.bind(i))
		x+=135.0
	_label("Preview uses the same colors, animated glyphs and character assets as the main game.",Vector2(26,541),Vector2(809,23),12,Color("#bda1b9"))
	tick=AudioStreamPlayer.new()
	tick.volume_db=-28.0
	tick.stream=load("res://assets/sfx_typewriter_v061.wav")
	add_child(tick)
	_set_portrait()
	_sample(0)
	visible=false

func _process(delta: float) -> void:
	if not visible or not running:
		return
	progress+=delta*float(speed_control.value)
	var shown: int=mini(sample_line.length(),int(progress))
	preview.visible_characters=shown
	pop.set("visible_limit",shown)
	if shown>last_visible and tick.stream!=null:
		var now: int=Time.get_ticks_msec()
		if now-last_tick_ms>=135 and not tick.playing:
			tick.play()
			last_tick_ms=now
	last_visible=shown
	if shown>=sample_line.length():
		running=false

func _sample(index: int) -> void:
	sample_input.text=str(SAMPLES[index][1])
	var target_mood: String=str(SAMPLES[index][2])
	for i in range(mood.item_count):
		if mood.get_item_text(i)==target_mood:
			mood.select(i)
			break
	_rebuild()

func _rebuild() -> void:
	if preview==null:return
	sample_line=sample_input.text.strip_edges()
	if sample_line.is_empty():return
	var new_intensity: float=float(intensity_control.value)
	if not is_equal_approx(new_intensity,studio_intensity):
		studio_intensity=new_intensity
		intensity_changed.emit(studio_intensity)
	var plan: Dictionary=Director.perform(sample_line,mood.get_item_text(mood.selected),studio_intensity)
	pop.reset()
	preview.text="[revealpop]"+str(plan.get("bbcode",""))+"[/revealpop]"
	preview.visible_characters=0
	progress=0.0
	last_visible=0
	running=true
	status.text="Emphasis: %s · %d emphasized phrases · intensity %.1f" % [", ".join(PackedStringArray(plan.get("categories",[]))),plan.get("cues",[]).size(),studio_intensity]
	_set_portrait()

func set_intensity(value: float) -> void:
	studio_intensity=clampf(value,0.5,1.5)
	if intensity_control != null:
		intensity_control.set_value_no_signal(studio_intensity)

func _set_portrait() -> void:
	if portrait==null:return
	var actor_id: String=actor.get_item_text(actor.selected)
	var state: String=mood.get_item_text(mood.selected)
	if state=="happy":state="amused"
	var path: String="res://assets/vn_%s_%s.png" % [actor_id,state]
	if ResourceLoader.exists(path):portrait.texture=load(path)

func _label(value:String,at:Vector2,dimensions:Vector2,font_size:int,color:Color) -> Label:
	var control:=Label.new()
	control.text=value
	control.position=at
	control.size=dimensions
	control.add_theme_font_size_override("font_size",font_size)
	control.add_theme_color_override("font_color",color)
	add_child(control)
	return control

func _button(value:String,at:Vector2,dimensions:Vector2) -> Button:
	var control:=Button.new()
	control.text=value
	control.position=at
	control.size=dimensions
	control.focus_mode=Control.FOCUS_NONE
	var style:=StyleBoxFlat.new()
	style.bg_color=Color("#47204e")
	style.border_color=Color("#d9aa73")
	style.set_border_width_all(1)
	style.set_corner_radius_all(8)
	control.add_theme_stylebox_override("normal",style)
	var hover: StyleBoxFlat=style.duplicate() as StyleBoxFlat
	hover.bg_color=Color("#68316d")
	control.add_theme_stylebox_override("hover",hover)
	add_child(control)
	return control

func _selector(at:Vector2,dimensions:Vector2,items:Array) -> OptionButton:
	var control:=OptionButton.new()
	control.position=at
	control.size=dimensions
	for item in items:control.add_item(str(item))
	control.select(0)
	add_child(control)
	return control
