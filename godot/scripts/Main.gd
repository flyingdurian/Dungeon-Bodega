extends Control

const DialoguePop = preload("res://scripts/DialoguePop.gd")
const EmotionGlyph = preload("res://scripts/EmotionGlyph.gd")
const DialogueDirector = preload("res://scripts/DialogueDirector.gd")
const DialogueTestStudio = preload("res://scripts/DialogueTestStudio.gd")
const VisitorGallery = preload("res://scripts/VisitorGallery.gd")
const TradeDeskPanel = preload("res://scripts/TradeDeskPanel.gd")
const AudioWaveformMeter = preload("res://scripts/AudioWaveformMeter.gd")
## Standalone visual client for The Living Counter game service (8010) and Hermes (8000).
## Godot 4.4+ recommended for WAV reaction buffer loader. No dependency on Last Emporium.

const GOLD := Color("#f7ce7c")
const CREAM := Color("#fef0df")
const MUTED := Color("#d3b4a4")
const BG := Color(0.075,0.115,0.122,0.94)
const INK := Color(0.105,0.16,0.17,0.97)
const BORDER := Color("#766348")
const GREEN := Color("#9fcb9e")
const RED := Color("#e9a09a")
const FANTASY_IDS := ["aldric","vesper","garrick","pippa","silas","brunna","elio","roderic","seraphine","fenwick","liu_xue","safiya","elara_veyne","mara_copperwell","tarek_ashwood"]
const MODERN_IDS := ["maya","noah","denise","kai","imani","rafael","zoe","arthur","priya","mason","rin_kaede","master_chen","yuna_seo","felix_rowe"]
const NPC_IDS := FANTASY_IDS + MODERN_IDS
const V121_ART_IDS := ["mara_copperwell", "tarek_ashwood", "yuna_seo", "felix_rowe"]
const REJECTED_ART_IDS := ["master_chen", "tarek_ashwood", "felix_rowe", "safiya", "rin_kaede", "yuna_seo", "mara_copperwell"]
const PORTRAIT_REVIEW_STATES := ["neutral", "thinking", "curious", "skeptical", "suspicious", "amused", "delighted", "annoyed", "angry", "surprised", "sad", "flustered"]
const ART_REVIEW_ROOT := "res://assets/art_review/"
# Owner-review-only live portrait rollout: the rest of rejected art stays neutral.
# The strict 12-state/owner-approval contract remains in force for publication.
const LIVE_PORTRAIT_TRIAL_IDS := ["master_chen", "tarek_ashwood"]
const LIVE_PORTRAIT_TRIAL_STATES := ["neutral", "thinking", "amused", "skeptical", "annoyed"]
const RELEASE_LABEL := "V1.2.4.4 · TWO VISITORS / 5 STATES"

@onready var game_http: HTTPRequest = $GameHTTP
@onready var health_http: HTTPRequest = $HealthHTTP
@onready var poll_http: HTTPRequest = $PollHTTP
@onready var catalog_http: HTTPRequest = $CatalogHTTP
@onready var stt_http: HTTPRequest = $SttHTTP
@onready var interrupt_http: HTTPRequest = $InterruptHTTP
@onready var reaction_http: HTTPRequest = $ReactionHTTP
@onready var reaction_player: AudioStreamPlayer = $ReactionPlayer
@onready var thinking_player: AudioStreamPlayer = $ThinkingPlayer
@onready var hermes: HermesStream = $HermesStream
@onready var microphone: MicrophoneCapture = $MicrophoneCapture

var game_url: String = "http://127.0.0.1:8010"
var hermes_url: String = "http://10.0.0.129:8000"
var sound_on: bool = true
var engine: String = "qwen"
var save_path: String = "user://living_counter.cfg"
var session_id: String = ""
var expected_turn: int = 1
var current: Dictionary = {}
var busy: bool = false
var voice_active: bool = false
var dialogue: String = ""
var typewriter_count: float = 0.0
var typewriter_rate: float = 22.0
var typewriter_running: bool = false
var base_portrait_pos: Vector2 = Vector2(110,29)
var elapsed: float = 0.0
var last_result: String = ""
var request_kind: String = ""
var offline_ai: bool = true
var game_online: bool = false
var voice_online: bool = false
var was_interrupted: bool = false
var microphone_active: bool = false
var awaiting_transcription: bool = false
var test_npc_index: int = 0
var dialogue_job_id: String = ""
var poll_request_job_id: String = ""
var poll_waiting: bool = false
var poll_elapsed: float = 0.0
var pending_interrupt: bool = false
var pending_heard_text: String = ""

var portrait: TextureRect
var reaction_portrait: TextureRect
var reaction_card: Panel
var reaction_state_label: Label
var reaction_character_id: String = ""
var reaction_current_state: String = ""
var reaction_test_index: int = -1
var portrait_review_active: bool = false
var item_art: TextureRect
var hero_name: Label
var hero_title: Label
var mood_label: Label
var cue_label: Label
var trade_label: Label
var item_label: Label
var price_label: Label
var gold_label: Label
var day_label: Label
var engine_status: Label
var progress_label: Label
var dialogue_label: RichTextLabel
var entry: LineEdit
var send_button: Button
var mic_button: Button
var next_button: Button
var list_container: VBoxContainer
var quick_status: Label
var detail_label: Label
var add_trade_button: Button
var inspected_item: Dictionary={}
var staged_bonus_items: Array[String]=[]
var bundle_note: Label
var debug_panel: Panel
var debug_text: Label
var settings_panel: Panel
var game_address: LineEdit
var hermes_address: LineEdit
var engine_pick: OptionButton
var voices_check: CheckButton
var npc_pick: OptionButton
var era_pick: OptionButton
var visible_npc_ids: Array[String] = []
var selected_era: String = "mixed"
var open_mic_enabled: bool = false
var open_mic_button: Button
var diagnostics_panel: Panel
var diagnostics_text: Label
var relationship_panel: Panel
var relationship_text: Label
var quick_timing: Label
var thinking_active: bool = false
var thinking_elapsed: float = 0.0
var think_sfx_time: float = 1.5
var turn_started_ms: int = 0
var voice_requested_ms: int = 0
var voice_started_ms: int = 0
var timing: Dictionary = {}
var stt_started_ms: int = 0
var inventory_panel: Panel
var selected_expression: String = "neutral" # The expression actually displayed, not just requested.
var portrait_requested_expression: String = "neutral"
var portrait_asset_status: String = "NOT_LOADED"
var portrait_asset_path: String = ""
var dialogue_nameplate: Label
var offer_label: Label
var thinking_bubble_frame: Panel
var reaction_glyph: Label
var replay_button: Button
var thought_bubble: Label
var speech_started_ms: int = 0
var reveal_glow: float = 0.0
var arrival_foley: AudioStreamPlayer
# V0.5.2: speech drives the visible dialogue, not an independent timer.
# Hermes currently provides audio samples, not phoneme/word alignment.
var speech_sync: bool = false
var speech_segment: String = ""
var speech_offset: int = 0
var early_sentence: String = ""
var early_job_id: String = ""
var early_playback: bool = false
var early_finished: bool = false
var queued_tail: String = ""
# V0.5.3: selective sound and emotional presentation. Audio timeline is authoritative.
var typing_fx: AudioStreamPlayer
var scene_fx: AudioStreamPlayer
var last_reveal: int = 0
var last_type_tick_ms: int = 0
var dialogue_origin: Vector2 = Vector2.ZERO
var impact_active: bool = false
var typewriter_caret: Label
var hermes_profiles: Dictionary={}
var voice_lock: Dictionary={}
var voice_lock_session: String=""
var last_engine_provider: String="deepseek"
var pop_effect: RichTextEffect
var emotion_effect: RichTextEffect
var last_emphasis_categories: String="none"
var dialogue_frame: Panel
var segment_time_weights: PackedFloat32Array=PackedFloat32Array()
var last_reveal_target: int=0
var expressive_sfx_on: bool=true
var text_pace_scale: float=1.0
var catalog_request_in_flight: bool=false
var catalog_refresh_pending: bool=false
# V0.7 performance cues share one renderer and the offline F8 studio.
var performance_studio
var performance_cues: Array=[]
var next_performance_cue: int=0
var performance_intensity: float=1.0
var performance_impact_played: bool=false

# V0.9: lightweight illustrated atmosphere and Hermes voice monitor.
var atmosphere_overlay: TextureRect
var mic_wave_meter
var visitor_wave_meter
var mic_meter_label: Label
var visitor_meter_label: Label
var voice_note: Label
var voice_panel: Panel
var voice_panel_text: Label
var voice_health_http: HTTPRequest
var voice_health_ok: bool=false
var voice_health_checked: bool=false
var voice_timing_factors: Dictionary={}
var voice_sentences: int=0
var character_card: Panel
var actor_arrived_at: float=-10.0
var measured_voice_glyphs_per_second: float=0.0
var measured_voice_diagnostic: String="No completed voice sample yet"
# V0.9.5 shop ledger and stock purchasing. All money remains server-authoritative.
var restock_http: HTTPRequest
var restock_button: Button
var restock_busy: bool=false
var shop_ledger_panel: Panel
var shop_ledger_text: Label
var shop_ledger_data: Dictionary={}
var last_catalog_stock: Array=[]
var visitor_gallery: Panel
var shop_wallpaper: TextureRect
var shop_theme: String="jade"
var theme_pick: OptionButton
var active_word_pop: Label
var gallery_open_button: Button
var mood_ambient: ColorRect
# V1.1 Living Encounters: native controls, no baked UI screenshot.
var case_title: Label
var case_note: Label
var action_buttons: Dictionary={}
var leads_panel: Panel
var leads_text: Label
var leads_http: HTTPRequest
var left_rail: Panel # Retired: rail intentionally not constructed in V1.2.2.
var trade_desk_panel: Panel
var shop_menu: Panel
var intuition_http: HTTPRequest
var intuition_panel: Panel
var intuition_text: Label
var intuition_title: Label
var intuition_request_session: String=""
var intuition_request_turn: int=-1






func _ready() -> void:
	var preset_file:=FileAccess.open("res://assets/hermes_profile_manifest.json",FileAccess.READ)
	if preset_file!=null:
		var parsed: Variant=JSON.parse_string(preset_file.get_as_text())
		if parsed is Dictionary:hermes_profiles=parsed
	_load_settings()
	_build_scene()
	game_http.request_completed.connect(_on_game_response)
	poll_http.request_completed.connect(_on_poll_response)
	health_http.request_completed.connect(_on_health_response)
	catalog_http.request_completed.connect(_on_catalog_response)
	stt_http.request_completed.connect(_on_transcribed)
	interrupt_http.request_completed.connect(_on_interrupt_response)
	reaction_http.request_completed.connect(_on_reaction_response)
	hermes.audio_started.connect(_on_audio_started)
	hermes.audio_finished.connect(_on_audio_finished)
	hermes.audio_failed.connect(_on_audio_failed)
	hermes.first_packet.connect(_on_first_packet)
	microphone.capture_finished.connect(_on_capture_finished)
	microphone.speech_detected.connect(_on_open_mic_detected)
	microphone.capture_failed.connect(_on_capture_failed)
	apply_settings()
	_check_voice_health()
	_check_health()
	_refresh_catalog()
	_begin_encounter()

func _process(delta: float) -> void:
	elapsed += delta
	if portrait != null and not current.is_empty():
		portrait.position.y = base_portrait_pos.y + sin(elapsed*(0.9 if thinking_active else 1.3))*(4.0 if thinking_active else 3.0)
		# Avoid fighting the entrance tween; only add tiny breathing and spoken
		# emphasis after the character has settled at the counter.
		if elapsed-actor_arrived_at>1.0:
			var actor_energy: float=clampf(hermes.voice_level*3.4,0.0,1.0) if voice_active else 0.0
			var breath: float=0.0035*sin(elapsed*1.48)+0.009*actor_energy
			portrait.scale=Vector2(1.0+breath,1.0+breath)
			portrait.rotation_degrees=0.17*sin(elapsed*0.88)
	if thought_bubble!=null:
		thinking_bubble_frame.visible=thinking_active
		thought_bubble.visible=thinking_active
		if thinking_active:
			thought_bubble.modulate.a=0.65+0.35*sin(elapsed*4.0)
	if thinking_active:
		thinking_elapsed += delta
		var dots: int = 1 + (int(thinking_elapsed*2.8) % 3)
		_set_progress("%s IS THINKING%s  ·  %.1fs  ·  EXODIA %s" % [str(current.get("customer",{}).get("name","Customer")).to_upper(),".".repeat(dots),thinking_elapsed,str(timing.get("provider","browser")).to_upper()])
		if thinking_elapsed >= think_sfx_time and not thinking_player.playing:
			thinking_player.play()
			think_sfx_time += 2.8
		_refresh_timing()
	if not dialogue_job_id.is_empty():
		poll_elapsed += delta
		if poll_elapsed >= 0.5 and not poll_waiting:
			poll_elapsed = 0.0
			_poll_dialogue()
	var previous_visible: int=maxi(0,dialogue_label.visible_characters)
	if speech_sync and hermes.is_busy():
		# PCM-played time, not generated/network time, drives the reveal.
		# Word-alignment is unavailable, so this remains perceptual pacing.
		var heard: float=hermes.heard_seconds()
		var timing_factor: float=_caption_timing_factor()
		var target: int=_speech_count_at(heard/maxf(0.01,timing_factor))
		var reveal_count: int=mini(dialogue.length(),speech_offset+target)
		if reveal_count>previous_visible:
			dialogue_label.visible_characters=reveal_count
	elif typewriter_running:
		typewriter_count+=delta*typewriter_rate
		dialogue_label.visible_characters=mini(int(typewriter_count),dialogue.length())
		if typewriter_count>=dialogue.length():typewriter_running=false
	var visible_now: int=maxi(0,dialogue_label.visible_characters)
	# Arm glyph tweens ONLY after the corresponding characters become visible.
	# Otherwise the animation can expire behind the typewriter mask.
	if pop_effect != null:
		pop_effect.set("visible_limit",visible_now)
	if visible_now>previous_visible:
		_on_text_advanced(visible_now)
		_fire_performance_cues(visible_now)
	if typewriter_caret!=null:
		typewriter_caret.visible=(speech_sync or typewriter_running) and (int(elapsed*3.0)%2==0)
	if not impact_active and dialogue_label!=null:
		dialogue_label.position=dialogue_origin
	_refresh_reaction_fx(delta)
	if atmosphere_overlay != null:
		atmosphere_overlay.modulate.a=(0.19+0.04*sin(elapsed*0.73)) if shop_theme=="jade" else (0.64+0.10*sin(elapsed*0.73))
	# Real microphone capture RMS and actual audio-render-bus peaks, not animated art.
	# Real capture/playback envelopes; never synthesize display motion in silence.
	var mic_live: bool=microphone.recording
	var visitor_live: bool=voice_active and hermes.is_busy()
	if mic_wave_meter!=null:
		mic_wave_meter.push_level(microphone.live_rms,mic_live)
	if visitor_wave_meter!=null:
		visitor_wave_meter.push_level(hermes.audible_output_level(),visitor_live)
	if voice_note != null:
		voice_note.text="YOU  ·  RECORDING" if mic_live and (not microphone.open_mode or microphone.speaking) else "YOU  ·  MIC READY" if mic_live else "YOU  ·  MIC OFF"
	if visitor_meter_label!=null:
		visitor_meter_label.text="VISITOR  ·  SPEAKING" if visitor_live else "VISITOR  ·  QUIET"
	if emotion_effect!=null:
		# The glyph movement is softly audio-reactive, not another artificial oscillator.
		emotion_effect.set("voice_energy",hermes.audible_output_level() if visitor_live else 0.0)
		emotion_effect.set("voice_active",visitor_live)
	if voice_panel != null and voice_panel.visible:
		_update_voice_inspector()

func _unhandled_key_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_F2:
		_preview_v124_portrait()
	elif event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_F3:
		debug_panel.visible = not debug_panel.visible
		if debug_panel.visible: _request_debug()
	elif event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_F4:
		diagnostics_panel.visible = not diagnostics_panel.visible
		_refresh_timing()
	elif event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_F5:
		voice_panel.visible=not voice_panel.visible
		if voice_panel.visible:_update_voice_inspector()
	elif event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_F6:
		_adjust_text_pace(0.1) # slower reveal, more seconds per glyph
	elif event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_F7:
		_adjust_text_pace(-0.1) # faster reveal
	elif event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_F8:
		_toggle_performance_studio()
	elif event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_F8:
		_toggle_performance_studio()
	elif event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_F9:
		relationship_panel.visible=not relationship_panel.visible
		_refresh_relationship_journal()
	elif event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_F10:
		shop_ledger_panel.visible=not shop_ledger_panel.visible
		_refresh_shop_ledger()
	elif event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_F11:
		_toggle_gallery()
	elif event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_F12:
		_open_leads()
	elif event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_ESCAPE:
		if leads_panel!=null and leads_panel.visible:leads_panel.visible=false
		elif visitor_gallery!=null and visitor_gallery.visible:visitor_gallery.visible=false
		elif shop_ledger_panel.visible:shop_ledger_panel.visible=false
		elif relationship_panel.visible:relationship_panel.visible=false
		elif diagnostics_panel.visible:diagnostics_panel.visible=false
		elif voice_panel.visible:voice_panel.visible=false
		elif debug_panel.visible:debug_panel.visible=false
		elif settings_panel.visible:settings_panel.visible=false
		elif performance_studio != null and performance_studio.visible:performance_studio.visible=false
		elif inventory_panel.visible:inventory_panel.visible=false

func _panel(parent: Node, box: Rect2, fill: Color = BG, edge: Color = BORDER, radius: int = 13) -> Panel:
	var p:=Panel.new()
	p.position=box.position
	p.size=box.size
	var sb:=StyleBoxFlat.new()
	sb.bg_color=fill
	sb.border_color=edge
	sb.shadow_color=Color(0.11,0.0,0.08,0.70)
	sb.shadow_size=9
	sb.set_border_width_all(2)
	sb.set_corner_radius_all(radius)
	sb.content_margin_left=10
	sb.content_margin_top=8
	p.add_theme_stylebox_override("panel",sb)
	parent.add_child(p)
	return p

func _text(parent: Node, title: String, position_: Vector2, size_: Vector2, fontsize: int=18, color: Color=CREAM) -> Label:
	var l:=Label.new()
	l.position=position_
	l.size=size_
	l.text=title
	l.add_theme_color_override("font_color",color)
	l.add_theme_font_size_override("font_size",fontsize)
	l.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
	l.vertical_alignment=VERTICAL_ALIGNMENT_CENTER
	parent.add_child(l)
	return l

func _button(parent: Node, title: String, rect: Rect2, accent: bool=false) -> Button:
	var b:=Button.new()
	b.text=title
	b.position=rect.position
	b.size=rect.size
	b.focus_mode=Control.FOCUS_NONE
	var flat:=StyleBoxFlat.new()
	flat.bg_color=Color("#9c603b") if accent else Color("#351536")
	flat.border_color=Color("#f7cf79") if accent else Color("#dbad72")
	flat.shadow_color=Color(0.05,0.0,0.03,0.85)
	flat.shadow_size=5
	flat.set_border_width_all(2)
	flat.set_corner_radius_all(9)
	var hover:=flat.duplicate() as StyleBoxFlat
	hover.bg_color=Color("#d08b56") if accent else Color("#76315e")
	b.add_theme_stylebox_override("normal",flat)
	b.add_theme_stylebox_override("hover",hover)
	b.add_theme_stylebox_override("pressed",hover)
	b.add_theme_color_override("font_color",CREAM)
	b.add_theme_color_override("font_hover_color",Color.WHITE)
	b.add_theme_font_size_override("font_size",17)
	parent.add_child(b)
	return b

func _build_scene() -> void:
	# V0.6.2: Built entirely from native Godot controls. The shop image is
	# environment art ONLY; there is no screenshot/UI artwork pasted on top.
	shop_wallpaper=TextureRect.new()
	shop_wallpaper.texture=load("res://assets/shop_bg_v100_jade_atelier.jpg") if shop_theme=="jade" else load("res://assets/shop_bg_v061_dynasty.png")
	shop_wallpaper.set_anchors_preset(Control.PRESET_FULL_RECT)
	shop_wallpaper.expand_mode=TextureRect.EXPAND_IGNORE_SIZE
	shop_wallpaper.stretch_mode=TextureRect.STRETCH_SCALE
	shop_wallpaper.mouse_filter=Control.MOUSE_FILTER_IGNORE
	add_child(shop_wallpaper)
	# The painted environment remains the illustration. This transparent
	# highlight pass gently moves the lantern light without painting UI as a screenshot.
	atmosphere_overlay=TextureRect.new()
	atmosphere_overlay.texture=load("res://assets/atmospheric_lantern_glow_v09.png")
	atmosphere_overlay.set_anchors_preset(Control.PRESET_FULL_RECT)
	atmosphere_overlay.expand_mode=TextureRect.EXPAND_IGNORE_SIZE
	atmosphere_overlay.stretch_mode=TextureRect.STRETCH_SCALE
	atmosphere_overlay.mouse_filter=Control.MOUSE_FILTER_IGNORE
	atmosphere_overlay.modulate.a=0.70
	add_child(atmosphere_overlay)

	# Center-left life-sized character. The character's changing portrait is the
	# sole expression selector; no duplicate clickable strip on the left.
	portrait=TextureRect.new()
	portrait.position=base_portrait_pos
	portrait.size=Vector2(842,740)
	portrait.expand_mode=TextureRect.EXPAND_IGNORE_SIZE
	portrait.stretch_mode=TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	portrait.mouse_filter=Control.MOUSE_FILTER_IGNORE
	portrait.modulate.a=0.0
	portrait.pivot_offset=Vector2(421,715)
	add_child(portrait)

	# V1.2.2: No floating duplicate portrait cut-ins. Facial acting belongs to
	# the main character illustration; player insight is a separate, opt-in mechanic.
	reaction_card=null
	reaction_portrait=null
	reaction_state_label=null

	# Premium native HUD. A compact custom title plate balances the upper-right
	# status ribbon without turning the whole screen into a pasted mockup.
	var brand:=_ornate_panel(self,Rect2(18,13,217,55),Color("#1d0a20f5"),Color("#edbd73"),false)
	_text(brand,"THE LIVING COUNTER",Vector2(12,4),Vector2(195,26),17,GOLD)
	_text(brand,RELEASE_LABEL,Vector2(13,31),Vector2(189,17),10,MUTED)
	_ornate_panel(self,Rect2(247,13,1159,55),Color("#220d23ed"),Color("#dfac61"),false)
	quick_timing=_text(self,"WAIT —   ·   PROMPT —",Vector2(271,25),Vector2(302,32),17,GOLD)
	day_label=_text(self,"DAY 1",Vector2(817,25),Vector2(125,32),19,CREAM)
	gold_label=_text(self,"450 GOLD",Vector2(1007,23),Vector2(241,35),23,GOLD)
	engine_status=_text(self,"CONNECTING",Vector2(1243,26),Vector2(100,30),12,MUTED)
	_button(self,"⚙",Rect2(1347,22,49,38)).pressed.connect(_toggle_settings)

	# V1.2.2: Visitors rail removed completely. Navigation is now an opt-in
	# compact menu; gallery remains available at F11 and customer picker Settings.
	var menu_toggle:=_button(self,"☰",Rect2(20,83,57,40))
	menu_toggle.tooltip_text="Shop menu · F11 opens visitor gallery"
	menu_toggle.pressed.connect(_toggle_shop_menu)
	shop_menu=_ornate_panel(self,Rect2(20,369,218,256),Color("#190b21fc"),Color("#d7a269"),true)
	shop_menu.visible=false
	# Owner-required persistent utility actions. NO Visitors roster, thumbnail rail,
	# or background portrait inside this region.
	var utility_dock:=_ornate_panel(self,Rect2(20,134,207,224),Color("#16091fe9"),Color("#d1a46b"),false)
	_button(utility_dock,"▣   Shelves",Rect2(9,9,189,45)).pressed.connect(_open_shelves_from_menu)
	_button(utility_dock,"▤   Shop Ledger",Rect2(9,62,189,45)).pressed.connect(_open_ledger_from_menu)
	_button(utility_dock,"♡   Relationships",Rect2(9,115,189,45)).pressed.connect(_open_relationship_from_menu)
	_button(utility_dock,"⌕   World Leads",Rect2(9,168,189,45)).pressed.connect(_open_leads_from_menu)
	for child in utility_dock.get_children():
		if child is Button:
			child.add_theme_font_size_override("font_size",17)
	_text(shop_menu,"SHOP MENU",Vector2(15,8),Vector2(175,28),18,GOLD)
	_button(shop_menu,"Visitors · F11",Rect2(11,45,196,34)).pressed.connect(_open_gallery_from_menu)
	_button(shop_menu,"Shelves",Rect2(11,85,196,34)).pressed.connect(_open_shelves_from_menu)
	_button(shop_menu,"Shop Ledger · F10",Rect2(11,125,196,34)).pressed.connect(_open_ledger_from_menu)
	_button(shop_menu,"Relationships · F9",Rect2(11,165,196,34)).pressed.connect(_open_relationship_from_menu)
	_button(shop_menu,"World Leads · F12",Rect2(11,205,196,34)).pressed.connect(_open_leads_from_menu)

	# The portrait alone communicates emotion. Thought FX is a transient overlay.
	var thought_frame:=_ornate_panel(self,Rect2(823,134,120,60),Color("#331739dd"),Color("#ecc789"),false)
	thought_bubble=_text(thought_frame,"···",Vector2(20,0),Vector2(80,54),36,GOLD)
	thought_frame.visible=false
	thinking_bubble_frame=thought_frame
	reaction_glyph=_text(self,"",Vector2(854,281),Vector2(78,70),47,GOLD)
	reaction_glyph.visible=false

	# Customer card: disposition, item, listed price, and actual offer are
	# separate well-aligned rows, all updated from authoritative game state.
	var card:=_ornate_panel(self,Rect2(1036,81,378,284),Color("#1b0b25f3"),Color("#f0c577"),true)
	character_card=card
	hero_name=_text(card,"Visitor",Vector2(25,11),Vector2(333,45),30,CREAM)
	hero_title=_text(card,"",Vector2(26,49),Vector2(329,22),14,MUTED)
	_rule(card,Vector2(23,80),330,Color("#c58a73aa"))
	_text(card,"DISPOSITION",Vector2(25,89),Vector2(142,30),13,MUTED)
	mood_label=_text(card,"Neutral",Vector2(172,89),Vector2(181,30),19,Color("#dfb7ef"))
	cue_label=_text(card,"",Vector2(25,115),Vector2(338,26),12,MUTED)
	_rule(card,Vector2(23,148),330,Color("#b48972aa"))
	_text(card,"ITEM",Vector2(25,159),Vector2(75,28),13,MUTED)
	item_label=_text(card,"",Vector2(105,157),Vector2(250,34),18,CREAM)
	_rule(card,Vector2(23,201),330,Color("#b48972aa"))
	_text(card,"LISTED PRICE",Vector2(25,207),Vector2(153,31),14,MUTED)
	price_label=_text(card,"— GOLD",Vector2(188,207),Vector2(164,31),20,GOLD)
	_text(card,"THEIR OFFER",Vector2(25,239),Vector2(155,32),14,MUTED)
	offer_label=_text(card,"— GOLD",Vector2(188,239),Vector2(164,32),20,Color("#e8b8f3"))
	item_art=TextureRect.new()
	item_art.position=Vector2(973,393)
	item_art.size=Vector2(78,78)
	item_art.expand_mode=TextureRect.EXPAND_IGNORE_SIZE
	item_art.stretch_mode=TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	item_art.mouse_filter=Control.MOUSE_FILTER_IGNORE
	item_art.visible=false # compact customer card shows item name; no floating item above CTA rail
	add_child(item_art)
	# This label used to float over the painted background, making it unreadable.
	# Game / bundle status now lives on its own opaque lower-right panel.

	# All five primary player actions are unified on the right. Each button
	# executes its real game action; no painted fake controls.
	_button(self,"⚖   Ask Price",Rect2(1056,392,341,54)).pressed.connect(_quick_list_price)
	_button(self,"◈   Counter Offer",Rect2(1056,458,341,54)).pressed.connect(_quick_counter)
	_button(self,"✦   Accept Deal",Rect2(1056,524,341,54),true).pressed.connect(_quick_accept)
	_button(self,"↪   End Chat",Rect2(1056,590,341,54)).pressed.connect(_quick_end)
	next_button=_button(self,"✧   Next Visitor",Rect2(1056,656,341,56),true)
	next_button.pressed.connect(_begin_encounter)

	# The main speech area is a true foreground UI surface; not part of the
	# illustration. It is large enough for 1–2 lines of English or Mandarin.
	var _speech_card:=_ornate_panel(self,Rect2(110,519,913,189),Color("#210b2af0"),Color("#ffca75"),true)
	dialogue_frame=_speech_card
	# Native decorative accents: satin tint, inset filigree hairlines, delicate
	# ornamental motifs, all mouse-transparent and outside the dialogue glyph zone.
	_rule(_speech_card,Vector2(54,12),806,Color("#e5a77e83"))
	_rule(_speech_card,Vector2(54,175),806,Color("#d982b765"))
	var left_flower:=_text(_speech_card,"❀",Vector2(14,123),Vector2(48,44),37,Color("#e0a0c0"))
	left_flower.modulate.a=0.54
	left_flower.mouse_filter=Control.MOUSE_FILTER_IGNORE
	var right_flower:=_text(_speech_card,"❀",Vector2(849,123),Vector2(49,44),37,Color("#df83ad"))
	right_flower.modulate.a=0.48
	right_flower.mouse_filter=Control.MOUSE_FILTER_IGNORE
	var corner_emblem:=_text(_speech_card,"✦",Vector2(847,12),Vector2(35,27),19,Color("#f4cc87"))
	corner_emblem.mouse_filter=Control.MOUSE_FILTER_IGNORE
	var nameplate:=_ornate_panel(self,Rect2(134,492,290,49),Color("#3d1947f7"),Color("#efbd73"),false)
	dialogue_nameplate=_text(nameplate,"Visitor",Vector2(30,7),Vector2(230,37),24,CREAM)
	progress_label=_text(self,"WAITING FOR A TRAVELER...",Vector2(438,536),Vector2(420,25),13,Color("#e4b36b"))
	dialogue_label=RichTextLabel.new()
	dialogue_label.position=Vector2(142,567)
	dialogue_label.size=Vector2(852,111)
	dialogue_label.bbcode_enabled=true
	pop_effect=DialoguePop.new()
	dialogue_label.install_effect(pop_effect)
	emotion_effect=EmotionGlyph.new()
	dialogue_label.install_effect(emotion_effect)
	dialogue_label.scroll_active=false
	dialogue_label.fit_content=false
	dialogue_label.mouse_filter=Control.MOUSE_FILTER_IGNORE
	dialogue_label.add_theme_color_override("default_color",CREAM)
	dialogue_label.add_theme_color_override("font_outline_color",Color("#190816"))
	dialogue_label.add_theme_constant_override("outline_size",2)
	dialogue_label.add_theme_font_size_override("normal_font_size",27)
	var literary_font:=SystemFont.new()
	literary_font.font_names=PackedStringArray(["Georgia","Cambria","Noto Serif CJK SC","Times New Roman"])
	dialogue_label.add_theme_font_override("normal_font",literary_font)
	add_child(dialogue_label)
	dialogue_origin=dialogue_label.position
	typewriter_caret=_text(self,"◆",Vector2(976,679),Vector2(25,28),18,Color("#f9c6ed"))
	typewriter_caret.visible=false
	replay_button=_button(self,"↻  Replay",Rect2(879,523,127,30))
	replay_button.pressed.connect(_replay_voice)
	# Dedicated legible status surface; no more gold-on-gold text behind inputs.
	var trade_status:=_ornate_panel(self,Rect2(1039,728,375,74),Color("#1d0927fa"),Color("#f3c779"),false)
	trade_label=_text(trade_status,"",Vector2(13,5),Vector2(349,29),15,CREAM)
	quick_status=_text(trade_status,"",Vector2(13,34),Vector2(349,33),13,GOLD)

	# Context controls fit below dialogue. Intuition is optional and explicitly
	# separate from the NPC's externally visible mood.
	var strip:=_ornate_panel(self,Rect2(211,712,812,49),Color("#231128f6"),Color("#d5a269"),false)
	var actions: Array=[
		["inspect","⌕ INSPECT"],["ask_origin","✧ ORIGIN"],
		["offer_help","♡ HELP"]]
	for i in range(actions.size()):
		var action_key:String=str(actions[i][0])
		var action_button:=_button(strip,str(actions[i][1]),Rect2(7+i*162,7,155,37))
		action_button.pressed.connect(_send_encounter_action.bind(action_key))
		action_buttons[action_key]=action_button
	var intuit_button:=_button(strip,"◇ INTUITION",Rect2(494,7,152,37))
	intuit_button.pressed.connect(_request_intuition)
	_button(strip,"⚒ TRADE DESK",Rect2(653,7,152,37)).pressed.connect(_open_trade_desk)

	# A contextual story label appears over the dialogue's upper edge.
	case_title=_text(self,"",Vector2(548,496),Vector2(458,27),16,Color("#ffdb93"))
	case_title.horizontal_alignment=HORIZONTAL_ALIGNMENT_RIGHT
	case_title.mouse_filter=Control.MOUSE_FILTER_IGNORE
	case_note=_text(self,"",Vector2(250,714),Vector2(746,22),12,Color("#ecd3b8"))
	case_note.visible=false  # available in title tooltip, not over action buttons

	# Compact text/voice control row. It no longer overlaps any CTA or dialogue.
	var _compose_panel:=_ornate_panel(self,Rect2(218,830,806,65),Color("#250e29f3"),Color("#d3a269"),false)
	entry=LineEdit.new()
	entry.position=Vector2(237,840)
	entry.size=Vector2(625,46)
	entry.placeholder_text="Speak or type naturally to the visitor..."
	entry.max_length=500
	entry.add_theme_font_size_override("font_size",18)
	_style_line_edit(entry)
	entry.text_submitted.connect(_on_enter_submit)
	add_child(entry)
	send_button=_button(self,"➤   Send",Rect2(871,840,141,46),true)
	send_button.pressed.connect(_send_text)
	# Conventional pressed/released mic input, separate from its open-mic toggle.
	mic_button=_button(self,"🎙   HOLD TO TALK",Rect2(21,816,180,48),true)
	mic_button.button_down.connect(_mic_down)
	mic_button.button_up.connect(_mic_up)
	open_mic_button=_button(self,"◉  OPEN MIC: OFF",Rect2(30,866,164,30))
	open_mic_button.pressed.connect(_toggle_open_mic)
	# V1.2.4.3: Audio sits in two OPAQUE, intentionally aligned cards above
	# text entry, away from dialogue and bargaining controls.
	# No wallpaper fragments or decorative-only waveform PNG are used.
	var mic_wave_card:=_ornate_panel(self,Rect2(218,768,393,55),Color("#081b29fa"),Color("#4acde9"),false)
	var visitor_wave_card:=_ornate_panel(self,Rect2(620,768,403,55),Color("#260e28fa"),Color("#f5a2cd"),false)
	voice_note=_text(mic_wave_card,"YOU  ·  MIC OFF",Vector2(16,13),Vector2(141,29),15,Color("#95f0ff"))
	visitor_meter_label=_text(visitor_wave_card,"VISITOR  ·  QUIET",Vector2(14,13),Vector2(163,29),15,Color("#ffbbdf"))
	mic_wave_meter=AudioWaveformMeter.new()
	mic_wave_meter.position=Vector2(154,9)
	mic_wave_meter.size=Vector2(225,36)
	mic_wave_meter.active_color=Color("#55e7ff")
	mic_wave_meter.idle_color=Color("#65a0b8")
	mic_wave_card.add_child(mic_wave_meter)
	visitor_wave_meter=AudioWaveformMeter.new()
	visitor_wave_meter.position=Vector2(174,9)
	visitor_wave_meter.size=Vector2(213,36)
	visitor_wave_meter.active_color=Color("#ff91d4")
	visitor_wave_meter.idle_color=Color("#b282a6")
	visitor_wave_card.add_child(visitor_wave_meter)
	# Meter labels are owned by their cards and do not overlap other controls.

	# Inventory drawer is the real source of supply purchases and trade extras.
	inventory_panel=_ornate_panel(self,Rect2(28,143,374,501),Color("#200e29fa"),Color("#d6aa72"),true)
	inventory_panel.visible=false
	_text(inventory_panel,"YOUR SHELVES",Vector2(20,13),Vector2(277,32),22,GOLD)
	_button(inventory_panel,"×",Rect2(323,11,35,34)).pressed.connect(_toggle_inventory)
	var scroll:=ScrollContainer.new()
	scroll.position=Vector2(16,54)
	scroll.size=Vector2(342,309)
	scroll.horizontal_scroll_mode=ScrollContainer.SCROLL_MODE_DISABLED
	inventory_panel.add_child(scroll)
	list_container=VBoxContainer.new()
	list_container.size_flags_horizontal=Control.SIZE_EXPAND_FILL
	list_container.add_theme_constant_override("separation",6)
	scroll.add_child(list_container)
	_refresh_inventory_placeholder()
	detail_label=_text(inventory_panel,"Select an item to inspect.",Vector2(18,362),Vector2(336,36),13,CREAM)
	add_trade_button=_button(inventory_panel,"＋ ADD ITEM TO TRADE",Rect2(17,403,339,35),true)
	add_trade_button.disabled=true
	add_trade_button.pressed.connect(_stage_inspected_item)
	restock_button=_button(inventory_panel,"RESTOCK 1 · SELECT AN ITEM",Rect2(17,449,339,35))
	restock_button.disabled=true
	restock_button.pressed.connect(_restock_inspected)
	# No trade or restocking consumes goods until the Python engine confirms it.

	# Settings are still available; developer inspector F3 and timings F4 are
	# intentionally HIDDEN by default and never consume permanent screen real estate.
	settings_panel=_ornate_panel(self,Rect2(616,105,534,454),Color("#210f2bfa"),GOLD,true)
	settings_panel.visible=false
	_text(settings_panel,"CONNECTIONS & CASTING",Vector2(23,15),Vector2(482,34),21,GOLD)
	_text(settings_panel,"Game service · authoritative economy",Vector2(24,55),Vector2(483,24),14,MUTED)
	game_address=LineEdit.new()
	game_address.position=Vector2(24,82)
	game_address.size=Vector2(483,34)
	game_address.text=game_url
	_style_line_edit(game_address)
	settings_panel.add_child(game_address)
	_text(settings_panel,"Hermes Engine · progressive speech",Vector2(24,122),Vector2(482,25),14,MUTED)
	hermes_address=LineEdit.new()
	hermes_address.position=Vector2(24,150)
	hermes_address.size=Vector2(483,34)
	hermes_address.text=hermes_url
	_style_line_edit(hermes_address)
	settings_panel.add_child(hermes_address)
	_text(settings_panel,"Voice engine",Vector2(24,193),Vector2(138,25),14,MUTED)
	engine_pick=OptionButton.new()
	engine_pick.position=Vector2(163,193)
	engine_pick.size=Vector2(161,35)
	for engine_name in ["qwen","chatterbox","kokoro"]:engine_pick.add_item(engine_name.to_upper())
	engine_pick.select(["qwen","chatterbox","kokoro"].find(engine))
	settings_panel.add_child(engine_pick)
	voices_check=CheckButton.new()
	voices_check.text="Voice on"
	voices_check.position=Vector2(336,191)
	voices_check.size=Vector2(172,39)
	voices_check.button_pressed=sound_on
	settings_panel.add_child(voices_check)
	_text(settings_panel,"Visitor roster",Vector2(24,231),Vector2(144,24),14,MUTED)
	era_pick=OptionButton.new()
	era_pick.position=Vector2(207,226)
	era_pick.size=Vector2(300,35)
	for era_name in ["Mixed: everyone (29)","Fantasy visitors (15)","Modern visitors (14)"]:era_pick.add_item(era_name)
	era_pick.select(["mixed","fantasy","modern"].find(selected_era))
	era_pick.item_selected.connect(_on_era_selected)
	settings_panel.add_child(era_pick)
	_text(settings_panel,"Choose visitor",Vector2(24,273),Vector2(157,27),14,MUTED)
	npc_pick=OptionButton.new()
	npc_pick.position=Vector2(207,269)
	npc_pick.size=Vector2(300,35)
	npc_pick.add_item("Random visitor")
	settings_panel.add_child(npc_pick)
	_refresh_npc_choices()
	_text(settings_panel,"Backdrop",Vector2(24,309),Vector2(146,25),14,MUTED)
	theme_pick=OptionButton.new()
	theme_pick.position=Vector2(207,307)
	theme_pick.size=Vector2(300,35)
	theme_pick.add_item("Jade Atelier · NEW")
	theme_pick.add_item("Dynasty Shop · Classic")
	theme_pick.select(0 if shop_theme=="jade" else 1)
	settings_panel.add_child(theme_pick)
	_text(settings_panel,"F5 Voice · F8 Text · F9 Memory · F10 Ledger · F11 Cast · F12 Leads",Vector2(24,350),Vector2(485,21),12,MUTED)
	_button(settings_panel,"APPLY & CLOSE",Rect2(24,389,483,44),true).pressed.connect(_apply_settings_from_ui)

	debug_panel=_ornate_panel(self,Rect2(410,115,556,478),Color("#170a20fa"),GOLD,true)
	debug_panel.visible=false
	_text(debug_panel,"DEVELOPER INSPECTOR · F3",Vector2(20,14),Vector2(506,28),19,GOLD)
	debug_text=_text(debug_panel,"Set LIVING_COUNTER_DEBUG=1 on the local server for hidden state.",Vector2(20,55),Vector2(515,408),14,CREAM)
	# F4 is an inspector, not a fixed-height HUD label. Long voice and portrait
	# telemetry must scroll inside the window rather than spill over trade buttons.
	diagnostics_panel=_ornate_panel(self,Rect2(910,94,504,489),Color("#170a22fb"),GOLD,true)
	diagnostics_panel.visible=false
	_text(diagnostics_panel,"TURN PERFORMANCE · F4",Vector2(19,13),Vector2(400,33),19,GOLD)
	_button(diagnostics_panel,"×",Rect2(451,11,35,34)).pressed.connect(func():diagnostics_panel.visible=false)
	var diagnostics_scroll:=ScrollContainer.new()
	diagnostics_scroll.position=Vector2(18,55)
	diagnostics_scroll.size=Vector2(472,412)
	diagnostics_scroll.horizontal_scroll_mode=ScrollContainer.SCROLL_MODE_DISABLED
	diagnostics_scroll.vertical_scroll_mode=ScrollContainer.SCROLL_MODE_AUTO
	diagnostics_panel.add_child(diagnostics_scroll)
	diagnostics_text=_text(diagnostics_scroll,"Waiting for a response...",Vector2.ZERO,Vector2(442,850),13,CREAM)
	diagnostics_text.vertical_alignment=VERTICAL_ALIGNMENT_TOP
	diagnostics_text.custom_minimum_size=Vector2(430,850)

	# Compact Voice Studio: actual Hermes profile and stream telemetry, not
	# invented per-turn voice settings. Access with F5; never obstructs play.
	voice_panel=_ornate_panel(self,Rect2(496,107,548,510),Color("#1d0d29fc"),GOLD,true)
	voice_panel.visible=false
	_text(voice_panel,"HERMES · VOICE STUDIO     F5",Vector2(18,12),Vector2(463,35),22,GOLD)
	_button(voice_panel,"×",Rect2(495,12,36,35)).pressed.connect(func():voice_panel.visible=false)
	voice_panel_text=_text(voice_panel,"Profile data will appear when a visitor arrives.",Vector2(22,55),Vector2(503,388),13,CREAM)
	_button(voice_panel,"⟳  Check Hermes",Rect2(21,454,241,45)).pressed.connect(_check_voice_health)
	_button(voice_panel,"↻  Replay Line",Rect2(277,454,247,45),true).pressed.connect(_replay_voice)
	voice_health_http=HTTPRequest.new()
	voice_health_http.timeout=3.5
	add_child(voice_health_http)
	voice_health_http.request_completed.connect(_on_voice_health)

	# V0.8: hidden relationship journal uses only the game's verified public
	# memory summaries. It is never part of the permanent HUD.
	relationship_panel=_ornate_panel(self,Rect2(531,122,483,356),Color("#190c25f9"),GOLD,true)
	relationship_panel.visible=false
	_text(relationship_panel,"VISITOR RELATIONSHIP · F9",Vector2(19,12),Vector2(432,36),19,GOLD)
	_button(relationship_panel,"×",Rect2(436,11,33,32)).pressed.connect(_hide_relationship_panel)
	relationship_text=_text(relationship_panel,"No visitor selected yet.",Vector2(21,54),Vector2(436,270),16,CREAM)

	# Shop records stay hidden during ordinary conversation; F10 reveals them.
	shop_ledger_panel=_ornate_panel(self,Rect2(524,115,508,397),Color("#190c25fa"),GOLD,true)
	shop_ledger_panel.visible=false
	_text(shop_ledger_panel,"SHOP LEDGER · F10",Vector2(18,12),Vector2(418,34),21,GOLD)
	_button(shop_ledger_panel,"×",Rect2(458,11,35,34)).pressed.connect(func():shop_ledger_panel.visible=false)
	shop_ledger_text=_text(shop_ledger_panel,"Visit the shelves to view today's market.",Vector2(22,52),Vector2(459,311),18,CREAM)
	restock_http=HTTPRequest.new()
	restock_http.timeout=7.0
	add_child(restock_http)
	restock_http.request_completed.connect(_on_restock_result)
	thinking_player.stream=load("res://assets/thinking_taps.wav")
	typing_fx=AudioStreamPlayer.new()
	typing_fx.stream=load("res://assets/sfx_typewriter_v061.wav")
	typing_fx.volume_db=-25.0
	add_child(typing_fx)
	scene_fx=AudioStreamPlayer.new()
	scene_fx.volume_db=-17.0
	add_child(scene_fx)
	arrival_foley=AudioStreamPlayer.new()
	arrival_foley.volume_db=-26.0
	add_child(arrival_foley)
	performance_studio=DialogueTestStudio.new()
	add_child(performance_studio)
	performance_studio.intensity_changed.connect(_set_performance_intensity)
	performance_studio.set_intensity(performance_intensity)
	performance_studio.visible=false
	# An unobtrusive interpretation card, visible ONLY after player action.
	intuition_http=HTTPRequest.new()
	add_child(intuition_http)
	intuition_http.request_completed.connect(_on_intuition_response)
	intuition_panel=_ornate_panel(self,Rect2(705,282,310,197),Color("#1c0c29f9"),Color("#d7b880"),true)
	intuition_panel.visible=false
	intuition_title=_text(intuition_panel,"YOUR INSTINCT",Vector2(15,9),Vector2(254,31),19,GOLD)
	_button(intuition_panel,"×",Rect2(269,6,33,30)).pressed.connect(func():intuition_panel.visible=false)
	intuition_text=_text(intuition_panel,"",Vector2(16,47),Vector2(274,141),14,CREAM)
	intuition_text.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
	visitor_gallery=VisitorGallery.new()
	add_child(visitor_gallery)
	visitor_gallery.connect("selected",Callable(self,"_on_gallery_choose"))
	visitor_gallery.visible=false
	trade_desk_panel=TradeDeskPanel.new()
	add_child(trade_desk_panel)
	trade_desk_panel.connect("action_requested",Callable(self,"_send_trade_desk_action"))
	trade_desk_panel.visible=false
	leads_http=HTTPRequest.new()
	add_child(leads_http)
	leads_http.request_completed.connect(_on_leads_response)
	leads_panel=_ornate_panel(self,Rect2(323,95,757,569),Color("#180b21fc"),GOLD,true)
	leads_panel.visible=false
	_text(leads_panel,"WORLD LEADS · F12",Vector2(30,19),Vector2(554,38),23,GOLD)
	_button(leads_panel,"×",Rect2(695,12,43,40)).pressed.connect(func(): leads_panel.visible=false)
	leads_text=_text(leads_panel,"Follow clues through living conversations...",Vector2(30,76),Vector2(690,470),17,CREAM)
	leads_text.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART

func _style_line_edit(field: LineEdit) -> void:
	var surface:=StyleBoxFlat.new()
	surface.bg_color=Color("#190d24ed")
	surface.border_color=Color("#b08a7e")
	surface.set_border_width_all(1)
	surface.set_corner_radius_all(9)
	surface.content_margin_left=12
	surface.content_margin_right=11
	field.add_theme_stylebox_override("normal",surface)
	var focused:=surface.duplicate() as StyleBoxFlat
	focused.border_color=GOLD
	focused.set_border_width_all(2)
	field.add_theme_stylebox_override("focus",focused)
	field.add_theme_color_override("font_color",CREAM)
	field.add_theme_color_override("font_placeholder_color",MUTED)
	field.add_theme_color_override("caret_color",GOLD)

func _rule(parent: Control, origin: Vector2, width_: float, color_: Color) -> void:
	var strip:=ColorRect.new()
	strip.position=origin
	strip.size=Vector2(width_,1.0)
	strip.color=color_
	strip.mouse_filter=Control.MOUSE_FILTER_IGNORE
	parent.add_child(strip)

func _ornate_panel(parent: Node, bounds: Rect2, fill: Color, edge: Color, flourishes: bool=true) -> Panel:
	var panel:=_panel(parent,bounds,fill,edge,18)
	# Fine inset line and restrained corner ornamentation are native controls.
	var inner:=Panel.new()
	inner.position=Vector2(6,6)
	inner.size=bounds.size-Vector2(12,12)
	inner.mouse_filter=Control.MOUSE_FILTER_IGNORE
	var outline:=StyleBoxFlat.new()
	outline.bg_color=Color(0,0,0,0)
	outline.border_color=Color(edge.r,edge.g,edge.b,0.36)
	outline.set_border_width_all(1)
	outline.set_corner_radius_all(13)
	inner.add_theme_stylebox_override("panel",outline)
	panel.add_child(inner)
	if flourishes:
		for pos_ in [Vector2(11,5),Vector2(bounds.size.x-31,5),Vector2(11,bounds.size.y-32),Vector2(bounds.size.x-31,bounds.size.y-32)]:
			var flourish:=_text(panel,"✦",pos_,Vector2(21,28),14,Color("#f4c47d"))
			flourish.mouse_filter=Control.MOUSE_FILTER_IGNORE
	return panel

func _toggle_inventory() -> void:
	inventory_panel.visible=not inventory_panel.visible

func _toggle_shop_menu() -> void:
	if shop_menu==null:return
	shop_menu.visible=not shop_menu.visible
	if shop_menu.visible:shop_menu.move_to_front()

func _open_gallery_from_menu() -> void:
	shop_menu.visible=false
	_toggle_gallery()

func _open_shelves_from_menu() -> void:
	shop_menu.visible=false
	_toggle_inventory()

func _open_ledger_from_menu() -> void:
	shop_menu.visible=false
	_open_ledger()

func _open_relationship_from_menu() -> void:
	shop_menu.visible=false
	_open_relationship()

func _open_leads_from_menu() -> void:
	shop_menu.visible=false
	_open_leads()

func _request_intuition() -> void:
	if intuition_http==null or current.is_empty() or session_id.is_empty():return
	if bool(current.get("closed",false)):
		_set_progress("THIS ENCOUNTER HAS ALREADY ENDED")
		return
	if intuition_http.get_http_client_status() not in [HTTPClient.STATUS_DISCONNECTED,HTTPClient.STATUS_CONNECTED]:
		return
	intuition_request_session=session_id
	intuition_request_turn=int(current.get("turn",0))
	var err:Error=intuition_http.request(game_url+"/intuition/"+session_id)
	if err!=OK:
		_set_progress("INTUITION COULD NOT CONNECT")

func _on_intuition_response(result: int, code: int, _headers: PackedStringArray, body: PackedByteArray) -> void:
	if session_id!=intuition_request_session or current.is_empty() or int(current.get("turn",-1))!=intuition_request_turn:
		return # Ignore reads from a previous encounter or previous turn.
	var data:Variant=JSON.parse_string(body.get_string_from_utf8())
	if result!=HTTPRequest.RESULT_SUCCESS or code!=200 or not (data is Dictionary):
		_set_progress("INTUITION IS UNAVAILABLE · CONVERSATION STILL WORKS")
		return
	if intuition_panel==null:return
	var outward:String=str(current.get("emotion","neutral")).capitalize()
	intuition_title.text="YOUR INSTINCT · "+str(data.get("confidence","low")).to_upper()
	intuition_text.text="OUTWARD: "+outward+"\n\nPOSSIBLY: "+str(data.get("title","Uncertain"))+"\n"+str(data.get("impression",""))+"\n\n"+str(data.get("disclaimer","This might be wrong."))
	intuition_panel.visible=true
	intuition_panel.move_to_front()

func _toggle_gallery() -> void:
	if visitor_gallery==null:return
	visitor_gallery.visible=not visitor_gallery.visible
	if visitor_gallery.visible:
		visitor_gallery.move_to_front()
		inventory_panel.visible=false

func _on_gallery_choose(npc_id: String, _era: String) -> void:
	# NPC selection uses the existing authoritative encounter endpoint;
	# no client-side creation of inventory, state, or relationships.
	if busy or awaiting_transcription or microphone_active:
		_set_progress("FINISH CURRENT INPUT BEFORE SWITCHING VISITORS")
		return
	selected_era="mixed"
	if era_pick!=null:era_pick.select(0)
	_refresh_npc_choices()
	var index: int=visible_npc_ids.find(npc_id)
	if index>=0:
		npc_pick.select(index+1)
		visitor_gallery.visible=false
		_begin_encounter()

func _choose_visitor_quick(npc_id: String) -> void:
	if busy or awaiting_transcription or microphone_active:return
	_on_gallery_choose(npc_id,"")

func _open_trade_desk() -> void:
	if trade_desk_panel==null or current.is_empty():return
	trade_desk_panel.visible=true
	trade_desk_panel.move_to_front()
	var data:Variant=current.get("trade_desk")
	if data is Dictionary:
		trade_desk_panel.display_report(data)
	trade_desk_panel.set_busy(busy or not dialogue_job_id.is_empty())

func _send_trade_desk_action(action_id:String) -> void:
	if busy or not dialogue_job_id.is_empty() or current.is_empty() or bool(current.get("closed",false)):
		return
	if not action_id in ["examine","check_origin","appraise"]:return
	if hermes.is_busy():hermes.stop(false)
	_reset_speech_sync()
	busy=true
	trade_desk_panel.set_busy(true)
	turn_started_ms=Time.get_ticks_msec()
	var payload:Dictionary={"session_id":session_id,"turn":expected_turn,"action":action_id}
	var err:Error=game_http.request(game_url+"/trade-desk/action",PackedStringArray(["Content-Type: application/json"]),HTTPClient.METHOD_POST,JSON.stringify(payload))
	if err!=OK:
		busy=false
		trade_desk_panel.set_busy(false)
		_set_progress("TRADE DESK REQUEST DID NOT START")
	else:
		request_kind="trade_desk_action"
		_set_progress("EXAMINING ITEM EVIDENCE...")

func _send_encounter_action(action_id: String) -> void:
	if busy or not dialogue_job_id.is_empty() or current.is_empty() or bool(current.get("closed",false)):
		return
	var living: Variant=current.get("living_encounter")
	if not (living is Dictionary):return
	if hermes.is_busy():hermes.stop(false)
	_reset_speech_sync()
	busy=true
	turn_started_ms=Time.get_ticks_msec()
	var payload:Dictionary={"session_id":session_id,"turn":expected_turn,"action":action_id}
	var err:Error=game_http.request(game_url+"/encounter/action",PackedStringArray(["Content-Type: application/json"]),HTTPClient.METHOD_POST,JSON.stringify(payload))
	if err!=OK:
		busy=false
		_set_progress("COULD NOT START ENCOUNTER ACTION")
	else:
		request_kind="encounter_action"
		_set_progress("INVESTIGATING THE ITEM...")

func _refresh_living() -> void:
	var living:Variant=current.get("living_encounter")
	var active:bool=living is Dictionary and not bool(current.get("closed",false))
	for key in action_buttons:
		var btn:Button=action_buttons[key]
		btn.disabled=not active or busy or not dialogue_job_id.is_empty()
	if not active:
		if case_title!=null:case_title.text=""
		return
	var case:Dictionary=living
	case_title.text="✦  "+str(case.get("title","A visitor's story"))
	case_title.tooltip_text=str(case.get("motive",""))+"\n"+"\n".join(PackedStringArray(case.get("insights",[])))
	for entry in case.get("actions",[]):
		if entry is Dictionary and action_buttons.has(str(entry.get("id",""))):
			var btn:Button=action_buttons[str(entry["id"])]
			btn.disabled=bool(entry.get("disabled",false)) or busy
	if bool(case.get("lead_awarded",false)):
		case_title.text="✦  LEAD DISCOVERED · "+str(case.get("title",""))

func _open_leads() -> void:
	if leads_panel==null:return
	leads_panel.visible=true
	leads_panel.move_to_front()
	leads_text.text="Loading discovered world leads..."
	if leads_http.get_http_client_status() in [HTTPClient.STATUS_DISCONNECTED,HTTPClient.STATUS_CONNECTED]:
		leads_http.request(game_url+"/leads")

func _on_leads_response(result:int,code:int,_h:PackedStringArray,body:PackedByteArray)->void:
	if result!=HTTPRequest.RESULT_SUCCESS or code!=200:
		leads_text.text="Unable to retrieve the local shop leads."
		return
	var j:Variant=JSON.parse_string(body.get_string_from_utf8())
	if not (j is Dictionary):return
	var entries:Array=j.get("leads",[])
	if entries.is_empty():
		leads_text.text="No world leads yet. Ask a visitor about the origin of an object, then offer assistance."
		return
	var lines:PackedStringArray=PackedStringArray()
	for lead in entries.slice(-9):
		lines.append("DAY %d · %s" % [int(lead.get("day",0)),str(lead.get("title",""))])
		lines.append("  "+str(lead.get("description","")))
		lines.append("")
	leads_text.text="\n".join(lines)

func _open_ledger() -> void:
	shop_ledger_panel.visible=true
	shop_ledger_panel.move_to_front()
	_refresh_shop_ledger()

func _open_relationship() -> void:
	relationship_panel.visible=true
	relationship_panel.move_to_front()
	_refresh_relationship_journal()

func _replay_voice() -> void:
	if dialogue.is_empty() or hermes.is_busy() or current.is_empty():return
	var old: String=dialogue
	_reset_speech_sync()
	_start_dialogue(old,false)

func _refresh_inventory_placeholder() -> void:
	for child in list_container.get_children():child.queue_free()
	for i in range(8):
		var l:=Label.new();l.text="⋯";l.custom_minimum_size=Vector2(240,43);list_container.add_child(l)

func _populate_inventory(catalog: Dictionary) -> void:
	for child in list_container.get_children():child.queue_free()
	var stock: Array = catalog.get("items",[])
	for item in stock:
		var count: int = int(item.get("stock",0))
		var title: String = str(item.get("name","Item"))
		var amount: int = int(item.get("price",0))
		var b:=_button(list_container,"%s  %s  ·  %dg   ×%d" % [str(item.get("icon","◈")),title,amount,count],Rect2(0,0,256,41))
		b.custom_minimum_size=Vector2(255,40)
		b.size_flags_horizontal=Control.SIZE_EXPAND_FILL
		# Empty shelves can still be inspected and replenished.
		b.disabled=false
		b.pressed.connect(_inspect_item.bind(item))

func _inspect_item(item: Dictionary) -> void:
	inspected_item=item.duplicate()
	detail_label.text="%s · Stock %d\n%s" % [str(item.get("name","")),int(item.get("stock",0)),str(item.get("description",""))]
	_update_add_trade_button()
	_update_restock_button()

func _update_add_trade_button() -> void:
	if add_trade_button==null:return
	var item_id: String=str(inspected_item.get("id",""))
	var own: bool=not item_id.is_empty() and int(inspected_item.get("stock",0))>0
	var same_item: bool=item_id==str(current.get("item",{}).get("id",""))
	var is_staged: bool=staged_bonus_items.has(item_id)
	add_trade_button.disabled=not own or same_item or (staged_bonus_items.size()>=2 and not is_staged)
	add_trade_button.text="− REMOVE FROM TRADE" if is_staged else "＋ ADD ITEM TO TRADE"
	add_trade_button.tooltip_text="This item remains in your shelves until a bundle is confirmed."

func _update_restock_button() -> void:
	if restock_button==null:return
	var item_id: String=str(inspected_item.get("id",""))
	var unit_price: int=int(inspected_item.get("restock_cost",0))
	var count: int=int(inspected_item.get("stock",0))
	var wallet: int=int(shop_ledger_data.get("gold",0))
	restock_button.text="RESTOCK 1 · %d GOLD" % unit_price if unit_price>0 else "RESTOCK · SELECT AN ITEM"
	restock_button.disabled=restock_busy or item_id.is_empty() or unit_price<1 or count>=12 or wallet<unit_price
	restock_button.tooltip_text="Purchase one real shelf unit from supplies (maximum stock: 12)."

func _restock_inspected() -> void:
	if restock_busy or restock_http==null or inspected_item.is_empty():return
	var item_id: String=str(inspected_item.get("id",""))
	if item_id.is_empty():return
	restock_busy=true
	_update_restock_button()
	var body: String=JSON.stringify({"item_id":item_id,"quantity":1})
	var err: Error=restock_http.request(game_url+"/restock",PackedStringArray(["Content-Type: application/json"]),HTTPClient.METHOD_POST,body)
	if err!=OK:
		restock_busy=false
		_update_restock_button()
		quick_status.text="SUPPLY PURCHASE NOT SENT · TRY AGAIN"

func _on_restock_result(result: int,code: int,_headers: PackedStringArray,body: PackedByteArray) -> void:
	restock_busy=false
	var parsed: Variant=JSON.parse_string(body.get_string_from_utf8())
	if result==HTTPRequest.RESULT_SUCCESS and code==200 and parsed is Dictionary:
		quick_status.text="RESTOCKED · %s · −%d GOLD" % [str(parsed.get("name","Item")),int(parsed.get("gold_spent",0))]
		inspected_item["stock"]=int(parsed.get("stock",0))
		shop_ledger_data=parsed.get("ledger",{}).duplicate()
		shop_ledger_data["gold"]=int(parsed.get("gold_remaining",0))
		gold_label.text="%d GOLD" % int(parsed.get("gold_remaining",0))
	else:
		var error_msg: String=str(parsed.get("detail","Supply purchase failed")) if parsed is Dictionary else "Supply purchase failed"
		quick_status.text=error_msg.substr(0,66)
	_update_restock_button()
	_refresh_shop_ledger()
	call_deferred("_refresh_catalog")

func _refresh_shop_ledger() -> void:
	if shop_ledger_text==null:return
	if shop_ledger_data.is_empty():return
	var market: Dictionary=shop_ledger_data.get("market",{})
	shop_ledger_text.text="DAY %d    ·    %s\n\nShop Reputation       %d / 100\nCompleted Deals       %d\nCash Earned           %d GOLD\nCash Spent on Goods   %d GOLD\nRestock Costs         %d GOLD\nNet Cash Flow         %+d GOLD\nStock Value           %d GOLD\n\nTODAY'S MARKET: %s\nVisitors value this item more; supplies cost more." % [
		int(shop_ledger_data.get("day",1)),str(shop_ledger_data.get("shop_rank","Shopkeeper")),
		int(shop_ledger_data.get("reputation",50)),int(shop_ledger_data.get("deals",0)),
		int(shop_ledger_data.get("earned_gold",0)),int(shop_ledger_data.get("purchases_gold",0)),
		int(shop_ledger_data.get("supplies_gold",0)),int(shop_ledger_data.get("net_trade_cash",0)),
		int(shop_ledger_data.get("stock_value",0)),str(market.get("name","None"))]

func _stage_inspected_item() -> void:
	var item_id: String=str(inspected_item.get("id",""))
	if item_id.is_empty():return
	if staged_bonus_items.has(item_id):
		staged_bonus_items.erase(item_id)
	elif staged_bonus_items.size()<2 and item_id!=str(current.get("item",{}).get("id","")):
		staged_bonus_items.append(item_id)
	_update_add_trade_button()
	if not staged_bonus_items.is_empty():
		quick_status.text="STAGED: %s · include in offer" % ", ".join(PackedStringArray(staged_bonus_items))
	else:
		quick_status.text="Trade extras cleared"

func _on_era_selected(index: int) -> void:
	selected_era=["mixed","fantasy","modern"][index]
	_refresh_npc_choices()

func _refresh_npc_choices() -> void:
	if npc_pick == null:return
	npc_pick.clear()
	npc_pick.add_item("Random visitor")
	visible_npc_ids.clear()
	var roster: Array=NPC_IDS
	if selected_era == "fantasy":roster=FANTASY_IDS
	elif selected_era == "modern":roster=MODERN_IDS
	for person in roster:
		visible_npc_ids.append(person)
		npc_pick.add_item(person.capitalize())
	npc_pick.select(0)

func _load_settings() -> void:
	var cfg:=ConfigFile.new()
	if cfg.load(save_path)==OK:
		game_url=str(cfg.get_value("server","game_url",game_url))
		hermes_url=str(cfg.get_value("server","hermes_url",hermes_url))
		engine=str(cfg.get_value("voice","engine",engine))
		sound_on=bool(cfg.get_value("voice","enabled",sound_on))
		selected_era=str(cfg.get_value("game","era",selected_era))
		shop_theme=str(cfg.get_value("ui","backdrop",shop_theme))
		text_pace_scale=clampf(float(cfg.get_value("dialogue","text_pace_scale",1.0)),0.7,1.5)
		performance_intensity=clampf(float(cfg.get_value("dialogue","emphasis_intensity",1.0)),0.5,1.5)
		# Open mic is opt-in on every launch; never silently re-enable recording.
	voice_timing_factors=cfg.get_value("voice","caption_calibration",{})
	if not (voice_timing_factors is Dictionary):voice_timing_factors={}
	if engine not in ["qwen","chatterbox","kokoro"]:engine="qwen"
	if selected_era not in ["mixed","fantasy","modern"]:selected_era="mixed"
	if shop_theme not in ["jade","dynasty"]:shop_theme="jade"

func apply_settings() -> void:
	hermes.base_url=hermes_url

func _toggle_settings() -> void:
	settings_panel.visible=not settings_panel.visible

func _apply_settings_from_ui() -> void:
	game_url=game_address.text.strip_edges().trim_suffix("/")
	hermes_url=hermes_address.text.strip_edges().trim_suffix("/")
	var old_engine: String=engine
	engine=["qwen","chatterbox","kokoro"][engine_pick.selected]
	if engine!=old_engine:
		voice_lock.clear()
		voice_lock_session=""
	sound_on=voices_check.button_pressed
	apply_settings()
	_check_voice_health()
	shop_theme="jade" if theme_pick==null or theme_pick.selected==0 else "dynasty"
	if shop_wallpaper!=null:
		shop_wallpaper.texture=load("res://assets/shop_bg_v100_jade_atelier.jpg") if shop_theme=="jade" else load("res://assets/shop_bg_v061_dynasty.png")
	var cfg:=ConfigFile.new()
	cfg.set_value("ui","backdrop",shop_theme)
	cfg.set_value("server","game_url",game_url)
	cfg.set_value("server","hermes_url",hermes_url)
	cfg.set_value("voice","engine",engine)
	cfg.set_value("voice","enabled",sound_on)
	cfg.set_value("game","era",selected_era)
	cfg.set_value("dialogue","text_pace_scale",text_pace_scale)
	cfg.set_value("dialogue","emphasis_intensity",performance_intensity)
	# Open microphone state intentionally isn't persisted between sessions.
	cfg.save(save_path)
	settings_panel.visible=false
	_check_health()
	if not current.is_empty():_set_progress("ENGINE: %s · Voice %s" % [engine.to_upper(),"ON" if sound_on else "OFF"])

func _check_health() -> void:
	if health_http.get_http_client_status() != HTTPClient.STATUS_DISCONNECTED and health_http.get_http_client_status() != HTTPClient.STATUS_CONNECTED:
		return
	var err: Error = health_http.request(game_url+"/health")
	if err != OK:
		engine_status.text="GAME SERVICE OFFLINE"
		game_online=false

func _refresh_catalog() -> void:
	# Only one HTTPRequest operation may run at a time. Coalesce refreshes
	# triggered by encounter/AI completions without losing the latest stock.
	if catalog_request_in_flight:
		catalog_refresh_pending=true
		return
	var err: Error=catalog_http.request(game_url+"/catalog")
	if err==OK:
		catalog_request_in_flight=true
	elif err==ERR_BUSY:
		catalog_refresh_pending=true
	else:
		push_warning("Inventory refresh unavailable (Godot error %d)." % int(err))

func _begin_encounter() -> void:
	if intuition_panel!=null:intuition_panel.visible=false
	intuition_request_session=""
	staged_bonus_items.clear()
	inspected_item.clear()
	if trade_desk_panel!=null:trade_desk_panel.visible=false
	if busy or microphone_active or awaiting_transcription:
		return
	if not session_id.is_empty():
		_end_thinking()
		if not dialogue_job_id.is_empty():
			interrupt_http.request(game_url+"/interrupt",PackedStringArray(["Content-Type: application/json"]),HTTPClient.METHOD_POST,JSON.stringify({"session_id":session_id,"heard_text":_heard_fragment()}))
			dialogue_job_id=""
		hermes.stop(false)
		_reset_speech_sync()
		was_interrupted=false
		pending_interrupt=false
		pending_heard_text=""
		typewriter_running=false
		dialogue_label.visible_characters=dialogue.length()
	busy=true
	next_button.disabled=true
	var body: Dictionary = {"era":selected_era}
	if npc_pick != null and npc_pick.selected>0 and npc_pick.selected-1<visible_npc_ids.size():
		body["npc_id"]=visible_npc_ids[npc_pick.selected-1]
	var err: Error = game_http.request(game_url+"/encounter",PackedStringArray(["Content-Type: application/json"]),HTTPClient.METHOD_POST,JSON.stringify(body))
	if err != OK:
		busy=false
		next_button.disabled=false
		_set_progress("GAME SERVICE OFFLINE · Run start_windows.ps1")
	else:
		request_kind="encounter"
		_set_progress("A VISITOR ENTERS THE SHOP...")

func _on_game_response(result: int,code: int,_headers: PackedStringArray,body: PackedByteArray) -> void:
	busy=false
	next_button.disabled=false
	var json: Variant = JSON.parse_string(body.get_string_from_utf8())
	if result!=HTTPRequest.RESULT_SUCCESS or code not in [200,202] or not (json is Dictionary):
		var detail: String = "HTTP %d" % code
		if json is Dictionary: detail=str(json.get("detail",detail))
		_set_progress("GAME ERROR · " + detail)
		if trade_desk_panel!=null:trade_desk_panel.set_busy(false)
		send_button.disabled=false
		return
	var response: Dictionary = json
	var arrival: bool=request_kind=="encounter"
	if code==202 and response.has("job_id"):
		# The bargain is already validated and applied, but no AI audio has returned yet.
		# Permit mic/text while this job waits so the user can barge in.
		dialogue_job_id=str(response.get("job_id",""))
		poll_elapsed=0.0
		current=response.get("scene",{})
		current["ai_mode"]="exodia"
		current["line"]=""
		_reset_speech_sync()
		dialogue=""
		dialogue_label.text=""
		typewriter_running=false
		session_id=str(current.get("session_id",""))
		expected_turn=int(response.get("turn",0))+1
		_update_display(false)
		_refresh_catalog()
		# Current scene has updated but the response has not arrived yet.
		# Liu Xue's separately painted poses are not spatially registered.
		# Keep her current pose during a short AI wait; the thought bubble
		# provides the thinking reaction without a double-face jump.
		if str(current.get("customer",{}).get("id",""))!="liu_xue":
			_show_portrait(str(current.get("customer",{}).get("id","aldric")),"thinking")
		mood_label.text="Thinking..."
		_enter_thinking()
		return
	current=response
	session_id=str(response.get("session_id",""))
	if debug_panel.visible: _request_debug()
	expected_turn=int(response.get("turn",0))+1
	_update_display(arrival)
	_refresh_catalog()
	if trade_desk_panel!=null:
		var report:Variant=current.get("trade_desk")
		if report is Dictionary and trade_desk_panel.visible:
			trade_desk_panel.display_report(report)
		trade_desk_panel.set_busy(false)
	_rearm_open_mic()

func _poll_dialogue() -> void:
	if dialogue_job_id.is_empty():return
	if poll_http.get_http_client_status() not in [HTTPClient.STATUS_DISCONNECTED,HTTPClient.STATUS_CONNECTED]:return
	poll_request_job_id=dialogue_job_id
	var err: Error=poll_http.request(game_url+"/dialogue/"+dialogue_job_id)
	if err==OK:poll_waiting=true

func _on_poll_response(result: int,code: int,_headers: PackedStringArray,body: PackedByteArray) -> void:
	poll_waiting=false
	if poll_request_job_id!=dialogue_job_id or dialogue_job_id.is_empty():return
	var job: Variant=JSON.parse_string(body.get_string_from_utf8())
	if result!=HTTPRequest.RESULT_SUCCESS or code!=200 or not (job is Dictionary):
		_set_progress("EXODIA STATUS UNAVAILABLE · YOU CAN STILL NEGOTIATE")
		return
	var state_name: String=str(job.get("state",""))
	if state_name=="working" and early_job_id.is_empty() and not dialogue_job_id.is_empty():
		var candidate: String=str(job.get("early_sentence",""))
		if not candidate.is_empty() and sound_on:
			_begin_early_speech(candidate)
	if state_name=="answered" and job.get("response") is Dictionary:
		dialogue_job_id=""
		var answer: Dictionary=job.get("response",{})
		if str(answer.get("session_id",""))!=session_id or int(answer.get("turn",-1))!=expected_turn-1:
			return # stale generation from a previously interrupted turn
		_end_thinking()
		current=answer
		if answer.get("performance") is Dictionary:
			var previous_stt_ms: int=int(timing.get("stt_ms",0))
			timing=answer.get("performance",{}).duplicate()
			if previous_stt_ms>0:timing["stt_ms"]=previous_stt_ms
			timing["client_wait_ms"]=Time.get_ticks_msec()-turn_started_ms
		last_engine_provider=str(timing.get("provider",last_engine_provider))
		engine_status.text="OFFLINE" if str(timing.get("source",""))=="offline_fallback" else last_engine_provider.to_upper()
		_refresh_timing()
		if str(answer.get("ai_mode", "")) == "offline_fallback":
			current["ai_error"] = str(job.get("error", "Exodia did not provide a usable line"))
		_update_display(false)
		_refresh_catalog()
	elif state_name=="cancelled":
		_reset_speech_sync()
		_end_thinking()
		dialogue_job_id=""
		_set_progress("INTERRUPTED · YOUR TURN")
	elif state_name=="failed":
		_reset_speech_sync()
		_end_thinking()
		dialogue_job_id=""
		_set_progress("EXODIA UNAVAILABLE · GAMEPLAY STILL RUNNING")

func _update_display(arrival: bool) -> void:
	if intuition_panel!=null:intuition_panel.visible=false
	var customer: Dictionary = current.get("customer",{})
	var item: Dictionary=current.get("item",{})
	var player: Dictionary=current.get("player",{})
	var id: String=str(customer.get("id","aldric"))
	var expression: String=str(current.get("emotion","neutral"))
	_show_portrait(id,expression)
	var item_path: String="res://assets/item_%s.png" % str(item.get("id",""))
	if ResourceLoader.exists(item_path):item_art.texture=load(item_path)
	var visitor_name: String=str(customer.get("name","Customer"))
	hero_name.text=visitor_name
	hero_name.add_theme_font_size_override("font_size",25 if visitor_name.length()>17 else 30)
	dialogue_nameplate.text=visitor_name
	dialogue_nameplate.add_theme_font_size_override("font_size",19 if visitor_name.length()>15 else 24)
	hero_title.text=str(customer.get("title","Traveler"))
	mood_label.text=str(current.get("emotion","neutral")).capitalize()
	var disposition_color: Color=Color("#f4d07b") if expression in ["happy","amused","delighted","friendly"] else Color("#f38c8e") if expression in ["furious","angry","annoyed","offended"] else Color("#ddaffb") if expression in ["skeptical","suspicious"] else CREAM
	mood_label.add_theme_color_override("font_color",disposition_color)
	cue_label.text=str(current.get("cue","")).substr(0,92)
	var relationship: Dictionary=current.get("relationship",{})
	var prior_visits: int=int(relationship.get("visits",0))
	cue_label.tooltip_text=("Returning visitor · %d previous visits · F9 for memories" % prior_visits) if prior_visits>0 else "First visit · F9 for memories"
	_refresh_relationship_journal()
	_refresh_living()
	item_label.text="%s  %s" % [str(item.get("icon","✦")),str(item.get("name",""))]
	price_label.text="%d GOLD" % int(item.get("price",0))
	offer_label.text="%d GOLD" % int(current.get("offer",0))
	trade_label.text="VISITOR %s" % ["BUYING FROM YOU" if current.get("kind")=="buy" else "SELLING TO YOU"]
	var pending_trade: Variant=current.get("pending_trade")
	if pending_trade is Dictionary:
		var pending: Dictionary=pending_trade
		var shown_items: Array=pending.get("items",[])
		var figure: String=str(pending.get("cash","—"))
		quick_status.text=("BUNDLE: %s gold + %s · %s" % [figure,", ".join(PackedStringArray(shown_items)),
			"CONFIRM TRADE" if bool(pending.get("ready",false)) else "DISCUSSING"]) if not shown_items.is_empty() else ("SOCIAL TERMS · %s gold · %s" % [figure,"SAY YES TO SETTLE" if bool(pending.get("ready",false)) else "DECLINED"])
	elif not current.get("closed",false):
		quick_status.text="Optional: Shelves → Add Item to Trade"
	gold_label.text="%d GOLD" % int(player.get("gold",450))
	day_label.text="DAY %d" % int(player.get("day",1))
	if arrival:
		actor_arrived_at=elapsed
		portrait.rotation_degrees=0.0
		_play_scene_sfx("sfx_shop_bell_v062.wav",-14.0)
		_play_arrival_foley()
		portrait.modulate.a=0.0
		portrait.position=base_portrait_pos+Vector2(140,0)
		portrait.scale=Vector2(0.94,0.94)
		var tw:=create_tween().set_parallel(true)
		tw.tween_property(portrait,"modulate:a",1.0,0.47)
		tw.tween_property(portrait,"position:x",base_portrait_pos.x,0.68).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
		tw.tween_property(portrait,"scale",Vector2.ONE,0.60)
	# Expression updates never zoom the illustrated portrait.
	if current.get("event")=="walkout":
		_play_scene_sfx("sfx_customer_footsteps_v061.wav",-23.0)
		if str(current.get("emotion","")) in ["furious","annoyed","angry","offended"]:
			_impact_counter()
	elif current.get("event")=="rejected" and str(current.get("emotion","")) in ["furious","annoyed"]:
		_impact_counter()
	if current.get("event")=="deal":
		staged_bonus_items.clear()
		quick_status.text="DEAL · %d gold · %s" % [int(current.get("transaction",{}).get("price",0)),str(current.get("transaction",{}).get("item","Item"))]
	elif current.get("event")=="walkout":
		quick_status.text="VISITOR DEPARTED · Choose Next Visitor"
	if current.get("closed",false):
		entry.editable=false
		send_button.disabled=true
		next_button.disabled=false
	else:
		entry.editable=true
		send_button.disabled=false
		entry.grab_focus()
	_start_dialogue(str(current.get("line","")),arrival)

func _start_dialogue(line: String, arrival: bool) -> void:
	if line.is_empty():return
	_end_thinking()
	var mood: String=str(current.get("emotion","neutral"))
	var matching_early: bool=early_playback and not early_sentence.is_empty() and line.begins_with(early_sentence)
	if early_playback and not matching_early:
		# The completed response differs from the preview. Stop rather than
		# replaying a potentially contradictory sentence as authoritative speech.
		hermes.stop(false)
		_reset_speech_sync()
	var was_visible: int=maxi(0,int(dialogue_label.visible_characters))
	dialogue=line
	pop_effect.reset()
	last_reveal=0
	dialogue_label.bbcode_enabled=true
	dialogue_label.text="[revealpop]"+_emotion_bbcode(line,mood)+"[/revealpop]"
	_show_portrait(str(current.get("customer",{}).get("id","aldric")),_visual_mood(line,mood))
	_tint_dialogue_frame(_visual_mood(line,mood))
	if not matching_early:
		dialogue_label.modulate.a=0.42
		var reveal_tween:=create_tween()
		reveal_tween.tween_property(dialogue_label,"modulate:a",1.0,0.24)
	if matching_early:
		queued_tail=line.substr(early_sentence.length()).strip_edges()
		dialogue_label.visible_characters=mini(was_visible,early_sentence.length())
		while next_performance_cue<performance_cues.size() and int(performance_cues[next_performance_cue].get("end",99999))<=dialogue_label.visible_characters:
			next_performance_cue+=1
		typewriter_running=false
		if early_finished:
			_start_queued_tail()
	else:
		dialogue_label.visible_characters=0
		typewriter_count=0
		typewriter_rate=21.0 if arrival else 24.0
		typewriter_running=not sound_on
		if sound_on:
			_speak_segment(line, mood, 0)
	var narrator_label: String = "LIVING ENCOUNTER · GAME" if current.get("ai_mode") == "game_authoritative" else last_engine_provider.to_upper()+" · LIVE" if current.get("ai_mode") == "exodia" else "OFFLINE FALLBACK · SCRIPTED"
	if current.has("ai_error"):
		narrator_label += " · " + str(current.get("ai_error", "")).substr(0,90)
	_set_progress("%s · %s / %s" % [current.get("customer",{}).get("name","NPC").to_upper(),mood.to_upper(),narrator_label])

func _reset_speech_sync() -> void:
	speech_sync=false
	speech_segment=""
	speech_offset=0
	early_sentence=""
	early_job_id=""
	early_playback=false
	early_finished=false
	queued_tail=""

func _begin_early_speech(sentence: String) -> void:
	if not sentence.ends_with(".") and not sentence.ends_with("!") and not sentence.ends_with("?"):
		return
	if hermes.is_busy():return
	early_sentence=sentence
	early_job_id=dialogue_job_id
	early_playback=true
	early_finished=false
	_end_thinking()
	dialogue=sentence
	pop_effect.reset()
	dialogue_label.bbcode_enabled=true
	dialogue_label.text="[revealpop]"+_emotion_bbcode(sentence,str(current.get("emotion","neutral")))+"[/revealpop]"
	dialogue_label.visible_characters=0
	typewriter_running=false
	if not _speak_segment(sentence,str(current.get("emotion","neutral")),0):
		_reset_speech_sync()
		_enter_thinking()

func _lock_voice_profile() -> void:
	var sid: String=str(current.get("session_id",""))
	if sid==voice_lock_session and not voice_lock.is_empty():return
	var voice: Dictionary=current.get("voice",{})
	var profile_id: String=str(voice.get("chatterbox",""))
	# Compatibility with historical game IDs that do not exist in the current
	# Hermes Studio manifest. Resolve ONCE per encounter, never per turn.
	var preset_aliases: Dictionary={"m04_silas_rogue":"m06_finn_rogue",
		"m05_roderic_hunter":"m09_thane_guard",
		"m06_fenwick_merchant":"m04_marcus_merchant"}
	if not hermes_profiles.has(profile_id):
		profile_id=str(preset_aliases.get(profile_id,profile_id))
	var preset: Dictionary=hermes_profiles.get(profile_id,{})
	var voice_id: String=""
	if engine=="qwen":voice_id=str(preset.get("qwen",voice.get("voice","Vivian")))
	elif engine=="kokoro":voice_id=str(preset.get("kokoro",voice.get("kokoro","af_heart")))
	else:voice_id=profile_id if not profile_id.is_empty() else str(voice.get("chatterbox","default"))
	var instruction: String=str(preset.get("instruct","Speak naturally at a comfortable conversational pace."))
	# The Hermes V3 server pitch-shifts via naive resampling when speed != 1.0
	# for Qwen/Chatterbox. Keep it at natural speed unless Hermes adds
	# pitch-preserving time-stretch support. Lock one profile per encounter.
	var preset_pace: float=float(preset.get("speed",1.0))
	var pace: float=1.0
	if str(current.get("customer",{}).get("id",""))=="liu_xue":
		# Sohee is Korean-oriented in Qwen's built-in voice family.
		# Vivian is the existing Chinese-compatible Hermes/Qwen option.
		if engine=="qwen":voice_id="Vivian"
		instruction="Native Mandarin Chinese woman. Natural conversational tempo and clear native Mandarin articulation; English fragments only in English."
		pace=1.0
	voice_lock={"engine":engine,"id":voice_id,"profile":profile_id,"speed":pace,"preset_speed":preset_pace,"instruct":instruction,
		"archetype":str(voice.get("reaction","female_warm")),"mood":"neutral"}
	voice_lock_session=sid
	_update_voice_inspector()
	_refresh_timing()

func _speak_segment(line: String, _mood: String, offset: int) -> bool:
	_lock_voice_profile()
	var config: Dictionary=voice_lock
	voice_requested_ms=Time.get_ticks_msec()
	# Deliberately freeze the TTS mood per encounter. Emotion is conveyed by
	# the portrait/text instead; varying TTS mood was changing vocal identity.
	var ok: bool=hermes.speak(line,str(config.get("engine",engine)),str(config.get("id","Vivian")),
		str(config.get("mood","neutral")),str(config.get("instruct","Speak naturally.")),
		str(config.get("archetype","female_warm")),float(config.get("speed",1.0)))
	if ok:
		speech_sync=true
		speech_segment=line
		speech_offset=offset
		segment_time_weights=_build_speech_times(line)
		typewriter_running=false
	else:
		speech_sync=false
		typewriter_running=true
		typewriter_count=float(maxi(0,dialogue_label.visible_characters))
		_set_progress("TEXT MODE · Hermes unavailable")
	_refresh_timing()
	return ok

func _build_speech_times(line: String) -> PackedFloat32Array:
	# Speech-aware reveal estimates. English is timed by characters/words;
	# Chinese by glyphs; punctuation gets deliberate micro-pauses.
	var times:=PackedFloat32Array()
	var elapsed_s: float=0.0
	for n in range(line.length()):
		var glyph: String=line.substr(n,1)
		var cp: int=glyph.unicode_at(0)
		var increment: float=0.072
		if cp>=0x3400 and cp<=0x9FFF:
			increment=0.235
		elif glyph==" " or glyph=="\n":
			increment=0.025
		elif glyph in [".","!","?","。","！","？"]:
			increment=0.20
		elif glyph in [",",";",":","，","、","；","："]:
			increment=0.125
		elif glyph=="…":
			increment=0.18
		elif cp>=48 and cp<=57:
			increment=0.105
		elapsed_s+=increment*text_pace_scale
		times.append(elapsed_s)
	return times

func _speech_count_at(seconds: float) -> int:
	var count: int=0
	for i in range(segment_time_weights.size()):
		if segment_time_weights[i] <= seconds:
			count=i+1
		else:break
	return count

func _caption_timing_factor() -> float:
	# Word timestamps are not supplied by Hermes. Calibrate the weighted
	# caption timeline from the actual PCM duration, never network elapsed.
	var key: String=str(voice_lock.get("engine",""))+"/"+str(voice_lock.get("id",""))
	var past: float=clampf(float(voice_timing_factors.get(key,1.08)),0.55,2.2)
	if hermes.stream_is_complete() and segment_time_weights.size()>0:
		var predicted: float=segment_time_weights[segment_time_weights.size()-1]
		var actual: float=hermes.total_audio_seconds()
		if actual>0.25 and predicted>0.05:
			return clampf(actual/predicted,0.48,2.5)
	return past

func _learn_voice_pacing() -> void:
	if segment_time_weights.is_empty():return
	var generated: float=hermes.total_audio_seconds()
	var estimated: float=segment_time_weights[segment_time_weights.size()-1]
	if generated<0.4 or estimated<0.25:return
	var key: String=str(voice_lock.get("engine",""))+"/"+str(voice_lock.get("id",""))
	var previous: float=clampf(float(voice_timing_factors.get(key,1.08)),0.55,2.2)
	var observation: float=clampf(generated/estimated,0.55,2.2)
	voice_timing_factors[key]=lerpf(previous,observation,0.38)
	voice_sentences+=1
	var cfg:=ConfigFile.new()
	cfg.load(save_path)
	cfg.set_value("voice","caption_calibration",voice_timing_factors)
	cfg.save(save_path)

func _start_queued_tail() -> void:
	if queued_tail.is_empty():
		early_playback=false
		return
	var remainder: String=queued_tail
	queued_tail=""
	early_playback=false
	# Whitespace is counted in the full text; the remainder begins at its first
	# actual character, so it is never pronounced twice.
	var offset: int=dialogue.length()-remainder.length()
	_speak_segment(remainder,str(current.get("emotion","neutral")),offset)

func _visual_mood(line: String, mood: String) -> String:
	# The actual portrait responds to a spoken line, without mutating trade AI.
	if mood in ["furious", "annoyed", "angry", "offended"]:
		return "annoyed"
	if mood in ["happy", "delighted", "excited"]:
		return "amused"
	var lower: String = line.to_lower()
	if lower.contains("ridiculous") or lower.contains("outrageous") or lower.contains("无礼") or lower.contains("荒唐") or lower.contains("太贵了") or lower.contains("高啊"):
		return "annoyed"
	if lower.contains("wonderful") or lower.contains("amazing") or lower.contains("太棒") or lower.contains("喜欢"):
		return "amused"
	if lower.contains("really?") or lower.contains("perhaps") or lower.contains("真的吗") or lower.contains("再想想"):
		return "skeptical"
	return mood

func _tint_dialogue_frame(mood: String) -> void:
	if dialogue_frame == null:
		return
	var theme_color: Color=Color("#ffc86d")
	if mood in ["annoyed", "angry", "furious", "offended"]:
		theme_color=Color("#ff737c")
	elif mood in ["skeptical", "suspicious"]:
		theme_color=Color("#c99cf9")
	elif mood in ["amused", "happy", "delighted"]:
		theme_color=Color("#ffe394")
	elif mood in ["sad", "nervous"]:
		theme_color=Color("#8fb4db")
	var original: StyleBoxFlat=dialogue_frame.get_theme_stylebox("panel") as StyleBoxFlat
	if original == null:
		return
	var sb: StyleBoxFlat=original.duplicate() as StyleBoxFlat
	sb.border_color=theme_color
	sb.shadow_color=Color(theme_color.r,theme_color.g,theme_color.b,0.27)
	sb.shadow_size=10
	dialogue_frame.add_theme_stylebox_override("panel",sb)
	# Affect only the translucent, illustrated lighting layer—not the portrait
	# or base shop art. Color is a quiet mood cue, not a full-screen flash.
	if atmosphere_overlay!=null:
		var ambient_tint: Color=Color.WHITE
		if mood in ["annoyed","angry","furious","offended"]:
			ambient_tint=Color(1.0,0.81,0.82,atmosphere_overlay.modulate.a)
		elif mood in ["skeptical","suspicious"]:
			ambient_tint=Color(0.82,0.85,1.0,atmosphere_overlay.modulate.a)
		elif mood in ["amused","happy","delighted"]:
			ambient_tint=Color(1.0,1.0,0.88,atmosphere_overlay.modulate.a)
		else:
			ambient_tint=Color(1.0,1.0,1.0,atmosphere_overlay.modulate.a)
		var light_tween:=create_tween()
		light_tween.tween_property(atmosphere_overlay,"modulate:r",ambient_tint.r,0.45)
		light_tween.parallel().tween_property(atmosphere_overlay,"modulate:g",ambient_tint.g,0.45)
		light_tween.parallel().tween_property(atmosphere_overlay,"modulate:b",ambient_tint.b,0.45)

func _emotion_bbcode(line: String, mood: String) -> String:
	# One local performance director for actual dialogue AND the F8 studio.
	# Rendering markup never enters Exodia prompts, Hermes TTS, or game state.
	var plan: Dictionary=DialogueDirector.perform(line,mood,performance_intensity)
	performance_cues=plan.get("cues",[])
	next_performance_cue=0
	performance_impact_played=false
	var categories: Array=plan.get("categories",[])
	last_emphasis_categories=", ".join(PackedStringArray(categories)) if not categories.is_empty() else "none (natural text)"
	return str(plan.get("bbcode",line))

func _toggle_performance_studio() -> void:
	if performance_studio == null:
		return
	performance_studio.visible=not performance_studio.visible
	if performance_studio.visible:
		performance_studio.move_to_front()

func _set_performance_intensity(value: float) -> void:
	performance_intensity=clampf(value,0.5,1.5)
	var cfg:=ConfigFile.new()
	cfg.load(save_path)
	cfg.set_value("dialogue","emphasis_intensity",performance_intensity)
	cfg.save(save_path)

func _fire_performance_cues(visible_now: int) -> void:
	# Cue is triggered by words becoming visible, NOT by the moment Exodia replies.
	# Avoid animations during interrupted or stale responses.
	while next_performance_cue<performance_cues.size():
		var cue: Dictionary=performance_cues[next_performance_cue]
		if visible_now<int(cue.get("end",99999)):
			break
		next_performance_cue+=1
		var first: int=clampi(int(cue.get("start",0)),0,dialogue.length())
		var last: int=clampi(int(cue.get("end",first)),first,dialogue.length())
		_act_out_cue(str(cue.get("kind","gold")), dialogue.substr(first,last-first))

func _act_out_cue(kind: String, phrase: String="") -> void:
	if current.is_empty() or portrait==null:
		return
	var category: String=""
	if kind=="anger":category="annoyed"
	elif kind in ["flirt","delight","agreement"]:category="amused"
	elif kind in ["doubt","persuade"]:category="skeptical"
	elif kind=="sad":category="skeptical"
	if not category.is_empty():
		_show_portrait(str(current.get("customer",{}).get("id","aldric")),category)
	var symbols: Dictionary={"anger":"!!","gold":"✦","persuade":"➶","doubt":"?", "delight":"✧","flirt":"♥","agreement":"✓","sad":"☂"}
	var colors: Dictionary={"anger":Color("#ff697e"),"gold":Color("#ffe39c"),"persuade":Color("#72e8ff"),"doubt":Color("#dab3ff"),"delight":Color("#ffe5ac"),"flirt":Color("#ffb3df"),"agreement":Color("#b3ffc9"),"sad":Color("#8fbbdf")}
	# Cinematic phrase pop: visibly performs the actual word, not just a symbol.
	# It is triggered when the word is *spoken*, and never changes the trade state.
	if is_instance_valid(active_word_pop):
		active_word_pop.queue_free()
	var popup:=Label.new()
	var words: String=phrase.strip_edges()
	if words.length()>27:words=words.substr(0,26)+"…"
	if kind=="anger":words=words.to_upper()
	popup.text=(words if not words.is_empty() else str(symbols.get(kind,"✧")))+"  "+str(symbols.get(kind,"✧"))
	popup.position=Vector2(390,540)
	popup.size=Vector2(600,70)
	popup.horizontal_alignment=HORIZONTAL_ALIGNMENT_CENTER
	popup.mouse_filter=Control.MOUSE_FILTER_IGNORE
	popup.add_theme_font_size_override("font_size",39 if kind in ["anger","delight","gold"] else 34)
	popup.add_theme_color_override("font_color",colors.get(kind,GOLD))
	popup.add_theme_color_override("font_outline_color",Color("#16071c"))
	popup.add_theme_constant_override("outline_size",9)
	popup.pivot_offset=Vector2(300,35)
	popup.scale=Vector2(0.69,0.69)
	popup.modulate.a=0.0
	add_child(popup)
	active_word_pop=popup
	var tw:=create_tween().bind_node(popup).set_parallel(true)
	tw.tween_property(popup,"scale",Vector2(1.08,1.08),0.22).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tw.tween_property(popup,"position:y",481.0,0.70).set_trans(Tween.TRANS_CUBIC)
	tw.tween_property(popup,"modulate:a",1.0,0.11)
	tw.chain().tween_property(popup,"modulate:a",0.0,0.28).set_delay(0.32)
	tw.chain().tween_callback(popup.queue_free)
	if dialogue_frame!=null:
		var pulse:=create_tween()
		dialogue_frame.self_modulate=colors.get(kind,GOLD).lerp(Color.WHITE,0.60)
		pulse.tween_property(dialogue_frame,"self_modulate",Color.WHITE,0.42)
	if kind=="anger" and not performance_impact_played:
		performance_impact_played=true
		_impact_counter()

func _play_arrival_foley() -> void:
	if not sound_on or arrival_foley==null:return
	var active_session: String=session_id
	get_tree().create_timer(0.55).timeout.connect(func():
		if active_session!=session_id:return
		var path: String="res://assets/sfx_customer_footsteps_v061.wav"
		if ResourceLoader.exists(path):
			arrival_foley.stream=load(path)
			arrival_foley.play()
	)
	get_tree().create_timer(1.65).timeout.connect(func():
		if active_session!=session_id:return
		_play_scene_sfx("sfx_counter_settle_v062.wav",-20.0)
	)

func _play_scene_sfx(filename: String, db: float=-15.0) -> void:
	if not sound_on or scene_fx==null:return
	var path: String="res://assets/"+filename
	if not ResourceLoader.exists(path):return
	scene_fx.stop()
	scene_fx.stream=load(path)
	scene_fx.volume_db=db
	scene_fx.play()

func _impact_counter() -> void:
	_play_scene_sfx("sfx_counter_settle_v062.wav",-11.0)
	if dialogue_label==null:return
	impact_active=true
	var tween:=create_tween()
	for x in [8.0,-7.0,5.0,-4.0,2.0,0.0]:
		tween.tween_property(dialogue_label,"position:x",dialogue_origin.x+x,0.036)
	tween.tween_callback(func():impact_active=false)

func _on_text_advanced(now: int) -> void:
	# Soft felt-typing accent: maximum ~7 clicks/second, independent of FPS.
	last_reveal=now
	if not sound_on or typing_fx==null:return
	var ms: int=Time.get_ticks_msec()
	if ms-last_type_tick_ms<120:return
	if not typing_fx.playing:
		last_type_tick_ms=ms
		typing_fx.play()

func _refresh_reaction_fx(_delta: float) -> void:
	# Word-level motion is implemented in RichTextLabel's [shake]/[wave] tags.
	# Scene shake is event-driven so reading never jitters for no reason.
	pass

func _adjust_text_pace(amount: float) -> void:
	text_pace_scale=clampf(snappedf(text_pace_scale+amount,0.05),0.7,1.5)
	if speech_sync:
		segment_time_weights=_build_speech_times(speech_segment)
	var cfg:=ConfigFile.new()
	cfg.load(save_path)
	cfg.set_value("dialogue","text_pace_scale",text_pace_scale)
	cfg.set_value("dialogue","emphasis_intensity",performance_intensity)
	cfg.save(save_path)
	_set_progress("TEXT TIMING %.2fx · F6 slower / F7 faster" % text_pace_scale)
	_refresh_timing()

func _set_progress(message: String) -> void:
	progress_label.text=message

func _send_quick(text: String) -> void:
	if busy or current.is_empty() or bool(current.get("closed",false)):return
	entry.text=text
	_send_text()

func _quick_accept() -> void:
	_send_quick("Deal! I accept your offer.")

func _quick_counter() -> void:
	if current.is_empty() or busy or bool(current.get("closed",false)):return
	var offered: int=int(current.get("offer",0))
	var adjustment: int=10 if str(current.get("kind","buy"))=="buy" else -10
	var draft: int=maxi(1,offered+adjustment)
	entry.text="I propose %d gold. Can we agree on that?" % draft
	entry.grab_focus()
	entry.caret_column=entry.text.length()
	_set_progress("COUNTER OFFER DRAFT · EDIT AMOUNT THEN PRESS SEND")

func _quick_list_price() -> void:
	if current.is_empty():return
	if str(current.get("kind","buy"))=="sell":
		_send_quick("What is the best price you are willing to sell it for?")
	else:
		_send_quick("What is the most you would be willing to pay for this item?")

func _quick_end() -> void:
	_send_quick("No deal. Please leave my shop.")

func _on_enter_submit(_line: String) -> void:_send_text()

func _send_text() -> void:
	if busy or awaiting_transcription or current.is_empty() or bool(current.get("closed",false)):
		return
	var words: String=entry.text.strip_edges()
	if words.is_empty():return
	if hermes.is_busy() or typewriter_running or not dialogue_job_id.is_empty():
		_barge_in()
		_play_interrupt_reaction()
	entry.clear()
	turn_started_ms=Time.get_ticks_msec()
	timing={"input_chars":words.length(),"provider":"browser"}
	_enter_thinking()
	busy=true
	send_button.disabled=true
	var request: Dictionary={"session_id":session_id,"turn":expected_turn,"text":words,"interrupt_before":pending_interrupt,"heard_text":pending_heard_text}
	# Selected shelf items are included only when the player actually proposes a
	# bundle. Ordinary banter never quietly turns staged items into an offer.
	var wants_bundle: bool=false
	var lowered: String=words.to_lower()
	for phrase in ["gold", "offer", "trade", "bundle", "include", "throw in", "confirm trade", "confirm bundle"]:
		if lowered.contains(phrase):wants_bundle=true
	if wants_bundle and not staged_bonus_items.is_empty():
		request["bonus_items"]=staged_bonus_items.duplicate()
	var err: Error=game_http.request(game_url+"/talk",PackedStringArray(["Content-Type: application/json"]),HTTPClient.METHOD_POST,JSON.stringify(request))
	if err!=OK:
		_end_thinking()
		busy=false
		send_button.disabled=false
		entry.text=words
		_set_progress("GAME SERVICE OFFLINE; YOUR MESSAGE WAS NOT SENT")
		return
	request_kind="talk"
	pending_interrupt=false
	pending_heard_text=""
	_set_progress("EXODIA IS PREPARING THE NEXT TURN...")

func _heard_fragment() -> String:
	if dialogue.is_empty():return ""
	var count: int=int(dialogue_label.visible_characters)
	if count<0:count=dialogue.length()
	return dialogue.substr(0,mini(count,220)).strip_edges()

func _barge_in() -> void:
	if current.is_empty() or bool(current.get("closed",false)):
		return
	var interrupted_speech: bool=hermes.is_busy() or typewriter_running or not dialogue_job_id.is_empty()
	if not interrupted_speech:return
	pending_heard_text=_heard_fragment()
	pending_interrupt=true
	if hermes.is_busy():hermes.stop(false)
	_reset_speech_sync()
	dialogue_job_id="" # discard late Exodia/HTTP polling responses locally
	_end_thinking()
	typewriter_running=false
	was_interrupted=true
	mood_label.text="Interrupted!"
	_set_progress("INTERRUPTED · THE CUSTOMER LOOKS STARTLED...")

func _mic_down() -> void:
	if open_mic_enabled:return
	if busy or current.is_empty() or bool(current.get("closed",false)) or awaiting_transcription:return
	_barge_in()
	microphone_active=microphone.begin()
	if microphone_active:
		mic_button.text="RELEASE TO SEND"
		_set_progress("LISTENING TO YOUR VOICE... RELEASE TO TRANSCRIBE")

func _mic_up() -> void:
	if open_mic_enabled:return
	if not microphone_active:return
	microphone_active=false
	mic_button.text="HOLD TO TALK"
	microphone.finish()
	_play_interrupt_reaction()

func _play_interrupt_reaction() -> void:
	if not was_interrupted or current.is_empty():return
	was_interrupted=false
	var voice: Dictionary=current.get("voice",{})
	var archetype: String=str(voice.get("reaction","female_warm"))
	var tag: String="groan" if str(current.get("emotion","")) in ["furious","annoyed","suspicious"] else "gasp"
	if reaction_http.get_http_client_status() == HTTPClient.STATUS_DISCONNECTED or reaction_http.get_http_client_status() == HTTPClient.STATUS_CONNECTED:
		reaction_http.request(hermes_url+"/reaction/"+archetype+"/"+tag)

func _on_capture_finished(wav: PackedByteArray) -> void:
	microphone_active=false
	_play_interrupt_reaction()
	stt_started_ms=Time.get_ticks_msec()
	awaiting_transcription=true
	send_button.disabled=true
	_set_progress("TRANSCRIBING YOUR VOICE...")
	var err: Error=stt_http.request_raw(game_url+"/transcribe",PackedStringArray(["Content-Type: audio/wav"]),HTTPClient.METHOD_POST,wav)
	if err != OK:
		awaiting_transcription=false
		send_button.disabled=false
		_set_progress("MIC NETWORK ERROR · TYPE YOUR REPLY")
		_rearm_open_mic()

func _on_transcribed(result: int,code: int,_headers: PackedStringArray,body: PackedByteArray) -> void:
	awaiting_transcription=false
	send_button.disabled=false
	var response: Variant=JSON.parse_string(body.get_string_from_utf8())
	if result!=HTTPRequest.RESULT_SUCCESS or code!=200 or not (response is Dictionary):
		var detail: String="Local Whisper STT unavailable. Install requirements-stt-windows.txt."
		if response is Dictionary:detail=str(response.get("detail",detail))
		_set_progress(detail)
		_rearm_open_mic()
		return
	if response.has("stt_ms"):
		timing["stt_ms"]=int(response.get("stt_ms",0))
	_refresh_timing()
	var words: String=str(response.get("text","")).strip_edges()
	if words.is_empty():
		_set_progress("NO CLEAR SPEECH DETECTED. TRY AGAIN.")
	else:
		entry.text=words
		_send_text()
	_rearm_open_mic()

func _on_capture_failed(message: String) -> void:
	microphone_active=false
	mic_button.text="HOLD TO TALK"
	_set_progress(message)
	_rearm_open_mic()

func _on_health_response(result: int,code: int,_headers: PackedStringArray,body: PackedByteArray) -> void:
	var response: Variant=JSON.parse_string(body.get_string_from_utf8())
	game_online=result==HTTPRequest.RESULT_SUCCESS and code==200 and response is Dictionary
	if game_online:
		offline_ai=str(response.get("ai_mode","offline"))=="offline"
		last_engine_provider=str(response.get("exodia_provider","deepseek"))
		engine_status.text="OFFLINE" if offline_ai else last_engine_provider.to_upper()
		engine_status.tooltip_text="Exodia dialogue + Hermes speech (external service)"
		engine_status.add_theme_color_override("font_color",GREEN if not offline_ai else GOLD)
	else:
		engine_status.text="OFFLINE"
		engine_status.tooltip_text="Game backend unavailable. Launch start_windows.ps1."
		engine_status.add_theme_color_override("font_color",RED)

func _on_catalog_response(result: int,code: int,_headers: PackedStringArray,body: PackedByteArray) -> void:
	catalog_request_in_flight=false
	if result==HTTPRequest.RESULT_SUCCESS and code==200:
		var response: Variant=JSON.parse_string(body.get_string_from_utf8())
		if response is Dictionary:
			shop_ledger_data=response.get("ledger",{}).duplicate()
			shop_ledger_data["gold"]=int(response.get("player",{}).get("gold",0))
			last_catalog_stock=response.get("items",[]).duplicate()
			_populate_inventory(response)
			if not inspected_item.is_empty():
				for item in last_catalog_stock:
					if str(item.get("id",""))==str(inspected_item.get("id","")):
						inspected_item=item.duplicate()
						break
				_update_restock_button()
			_refresh_shop_ledger()
	if catalog_refresh_pending:
		catalog_refresh_pending=false
		# Defer until HTTPRequest fully returns from its completion callback.
		call_deferred("_refresh_catalog")

func _on_interrupt_response(_result: int,_code: int,_headers: PackedStringArray,_body: PackedByteArray) -> void:
	pass

func _on_audio_started() -> void:
	voice_active=true
	voice_started_ms=Time.get_ticks_msec()
	var origin: String = "ENCOUNTER ACTION" if current.get("ai_mode") == "game_authoritative" else last_engine_provider.to_upper()+" LIVE" if current.get("ai_mode") == "exodia" else "SCRIPTED FALLBACK"
	_set_progress("VOICE PLAYING · %s · %s · MIC / TYPE TO INTERRUPT" % [engine.to_upper(),origin])

func _on_first_packet(ms: int) -> void:
	timing["hermes_first_pcm_ms"]=ms
	_refresh_timing()
	var origin: String = "ENCOUNTER ACTION" if current.get("ai_mode") == "game_authoritative" else last_engine_provider.to_upper()+" LIVE" if current.get("ai_mode") == "exodia" else "SCRIPTED FALLBACK"
	_set_progress("HERMES FIRST PCM · %d ms · %s · %s" % [ms,engine.to_upper(),origin])

func _on_audio_finished() -> void:
	_learn_voice_pacing()
	# Diagnose the actual generated playback length rather than altering pitch
	# behind the user's back. Slow delivery is often a TTS model behavior, not
	# an Exodia latency or network latency problem.
	var telemetry: Dictionary=hermes.audio_telemetry()
	var heard: float=float(telemetry.get("heard_s",0.0))
	if heard>0.20 and not speech_segment.is_empty():
		measured_voice_glyphs_per_second=float(speech_segment.length())/heard
		measured_voice_diagnostic="PCM STREAM STARVED — compare Mac /stream" if int(telemetry.get("underruns",0))>0 else "AUDIO CLOCK DRIFT — check mixer" if float(telemetry.get("playback_drift_s",0.0))>0.45 else "SLOW SOURCE PCM — compare Hermes Studio" if measured_voice_glyphs_per_second<(3.0 if str(current.get("customer",{}).get("id",""))=="liu_xue" else 7.0) else "Natural-speed PCM · pitch unchanged"
	voice_active=false
	if voice_started_ms>0:
		timing["spoken_ms"]=Time.get_ticks_msec()-voice_started_ms
	_refresh_timing()
	if speech_sync:
		# Complete only the segment just heard. A queued continuation starts
		# after the early segment has fully drained.
		dialogue_label.visible_characters=mini(dialogue.length(),speech_offset+speech_segment.length())
		_fire_performance_cues(maxi(0,dialogue_label.visible_characters))
		speech_sync=false
	if early_playback:
		early_finished=true
		if not queued_tail.is_empty():
			_start_queued_tail()
	elif typewriter_running:
		typewriter_rate=maxf(typewriter_rate,70.0)
	var origin: String = "ENCOUNTER ACTION" if current.get("ai_mode") == "game_authoritative" else last_engine_provider.to_upper()+" LIVE" if current.get("ai_mode") == "exodia" else "SCRIPTED FALLBACK"
	_set_progress("YOUR TURN · %s · TYPE OR HOLD MIC" % origin)

func _on_audio_failed(reason: String) -> void:
	voice_active=false
	speech_sync=false
	typewriter_running=true
	typewriter_count=float(maxi(0,int(dialogue_label.visible_characters)))
	if early_playback:
		early_playback=false
		early_sentence=""
		early_job_id=""
	_set_progress("VOICE UNAVAILABLE · TEXT CONTINUES · %s" % reason.substr(0,78))

func _on_reaction_response(result: int,code: int,_headers: PackedStringArray,body: PackedByteArray) -> void:
	if result != HTTPRequest.RESULT_SUCCESS or code!=200:return
	var effect_sound: AudioStreamWAV=AudioStreamWAV.load_from_buffer(body)
	if effect_sound!=null:
		reaction_player.stream=effect_sound
		reaction_player.play()

func _hide_relationship_panel() -> void:
	relationship_panel.visible=false

func _refresh_relationship_journal() -> void:
	if relationship_text==null:
		return
	var customer: Dictionary=current.get("customer",{})
	var relation: Dictionary=current.get("relationship",{})
	var name_value: String=str(customer.get("name","None"))
	var visits: int=int(relation.get("visits",0))
	var deals: int=int(relation.get("deals",0))
	var last: String=str(relation.get("last_outcome","none"))
	var lines: Array[String]=[
		"Visitor: " + name_value,
		"Previous visits: %d   ·   Completed deals: %d" % [visits,deals],
		"Last encounter: " + last,
		"",
		"CONVERSATION NOTES (PLAYER-STATED)",
	]
	var notes: Array=relation.get("notes",[])
	if notes.is_empty():
		lines.append("No saved social moments yet.")
	else:
		for note in notes:
			lines.append("• " + str(note))
	lines.append("")
	if relation.get("social_roleplay")!=null:
		lines.append("PLAYFUL SOCIAL AGREEMENT: " + str(relation.get("social_roleplay")))
	lines.append("Social roleplay is fictional; no outside-world obligation or item transfer.")
	relationship_text.text="\n".join(PackedStringArray(lines))

func _request_debug() -> void:
	if session_id.is_empty():return
	# Dev inspector is an explicitly restricted server endpoint; no secrets in normal gameplay.
	var probe:=HTTPRequest.new()
	add_child(probe)
	probe.request_completed.connect(func(_r:int,code:int,_h:PackedStringArray,bytes:PackedByteArray):
		if code==200:
			var j:Variant=JSON.parse_string(bytes.get_string_from_utf8())
			if j is Dictionary:
				debug_text.text="NPC: %s\nTrade: %s\nPatience: %d / 100\nTrust: %d / 100\nHidden reservation: %d gold\nNPC cash: %d gold\nCurrent quote: %d gold\nTurn: %d\nInterruptions: %d\nOutcome: %s" % [j.get("npc_id",""),j.get("kind",""),j.get("patience",0),j.get("trust",0),j.get("reservation",0),j.get("wallet",0),j.get("offer",0),j.get("turn",0),j.get("interrupts",0),str(j.get("outcome","none"))]
		else:
			debug_text.text="Developer stats unavailable. Set LIVING_COUNTER_DEBUG=1 and connect to game server via 127.0.0.1."
		probe.queue_free()
	)
	probe.request(game_url+"/debug/"+session_id)


func _read_art_approval(visitor_id: String) -> Dictionary:
	# The generator/reviewer sets approvals ONLY after independent RGBA files,
	# visual identity audit, and a native Godot portrait playtest.
	var file:=FileAccess.open("res://assets/character_art_status_v123.json",FileAccess.READ)
	if file==null:return {}
	var parsed: Variant=JSON.parse_string(file.get_as_text())
	if not parsed is Dictionary:return {}
	var item: Variant=parsed.get(visitor_id,{})
	return item if item is Dictionary else {}

func _show_portrait(id: String, emotion: String, review_override: bool = false) -> void:
	# Runtime acting is always production-approved art. F2 alone may stage
	# unapproved original candidate portraits for visual review.
	if not review_override:
		portrait_review_active=false
	var expressive: String="neutral"
	if emotion in ["thinking","nervous","consider"]:expressive="thinking"
	elif emotion in ["curious","inquisitive"]:expressive="curious"
	elif emotion in ["happy","amused","friendly"]:expressive="amused"
	elif emotion in ["delighted","excited","celebrate","elated","ecstatic"]:expressive="delighted"
	elif emotion in ["flirting","flirty","blush","flustered","bashful"]:expressive="flustered"
	elif emotion in ["suspicious","wary"]:expressive="suspicious"
	elif emotion in ["skeptical","doubtful","counter"]:expressive="skeptical"
	elif emotion in ["furious","angry","outraged"]:expressive="angry"
	elif emotion in ["annoyed","offended","impatient"]:expressive="annoyed"
	elif emotion in ["surprised","shocked","startled"]:expressive="surprised"
	elif emotion in ["sad","sorrowful","disappointed"]:expressive="sad"
	portrait_requested_expression=expressive
	var actually_displayed: String=expressive
	var fallback_reason: String="MATCHED_EXPRESSION"
	if portrait!=null:
		base_portrait_pos=Vector2(110,29)
		portrait.size=Vector2(914,740)
		portrait.pivot_offset=Vector2(457,715)
	var path: String="res://assets/vn_%s_%s.png" % [id,expressive]
	if review_override and id in REJECTED_ART_IDS:
		fallback_reason="UNAPPROVED_REVIEW_CANDIDATE"
		var preview_path: String=ART_REVIEW_ROOT + "vn_%s_%s.png" % [id,expressive]
		if ResourceLoader.exists(preview_path):
			path=preview_path
		else:
			portrait_asset_status="REVIEW_CANDIDATE_MISSING"
			_set_progress("ART REVIEW: %s NOT READY · NO FILE" % expressive.to_upper())
			return
	elif id in REJECTED_ART_IDS:
		# Owner-rejected low-resolution bust crops must never be stretched into
		# the hero area. Only manually signed-off 12-state production rigs can
		# replace the existing neutral preview; see art/status_v123.json.
		var approval: Dictionary=_read_art_approval(id)
		if not bool(approval.get("approved",false)):
			if id in LIVE_PORTRAIT_TRIAL_IDS:
				# V1.2.4.4: five native-size individual candidates, shown in
				# ordinary encounters for owner evaluation, NOT art approval.
				# Do not fall through to the legacy low-resolution reaction busts.
				var selected_trial: String=expressive
				if expressive not in LIVE_PORTRAIT_TRIAL_STATES:
					# An honest nearest-state fallback until the other seven
					# independent masters exist.
					if expressive in ["suspicious", "angry"]:
						selected_trial="skeptical" if expressive=="suspicious" else "annoyed"
					elif expressive in ["delighted", "flustered"]:
						selected_trial="amused"
					elif expressive in ["curious", "surprised"]:
						selected_trial="thinking"
					else:
						selected_trial="neutral"
				actually_displayed=selected_trial
				path="res://assets/vn_%s_%s.png" % [id,selected_trial]
				fallback_reason="FIVE_STATE_TRIAL_NOT_APPROVED" if expressive==selected_trial else "TRIAL_NEAREST_STATE_NOT_APPROVED"
				if not ResourceLoader.exists(path):
					actually_displayed="neutral"
					fallback_reason="TRIAL_ASSET_MISSING_NEUTRAL"
					path="res://assets/vn_%s_neutral.png" % id
			else:
				actually_displayed="neutral"
				fallback_reason="REJECTED_ART_LOCKED_TO_NEUTRAL"
				path="res://assets/vn_%s_neutral.png" % id
	if not ResourceLoader.exists(path) and id in ["liu_xue","safiya","elara_veyne","rin_kaede","master_chen","yuna_seo","felix_rowe"]:
		path="res://assets/vn_%s_neutral.png" % id
		actually_displayed="neutral"
		fallback_reason="EXPRESSION_FILE_MISSING"
	if not ResourceLoader.exists(path):
		# Legacy character rigs until high-resolution portrait rollout is complete.
		var legacy: String=emotion
		if emotion=="thinking":legacy="nervous"
		path="res://assets/customer_%s_%s.png" % [id,legacy]
		if not ResourceLoader.exists(path):
			path="res://assets/customer_%s_neutral.png" % id
			actually_displayed="neutral"
			fallback_reason="LEGACY_EXPRESSION_MISSING"
	if not ResourceLoader.exists(path):
		portrait.texture=null
		if reaction_card!=null:reaction_card.visible=false
		selected_expression="missing"
		portrait_asset_status="NO_VALID_PORTRAIT_FILE"
		portrait_asset_path=path
		return
	if ResourceLoader.exists(path):
		portrait.stretch_mode=TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		var next_texture: Texture2D=load(path)
		if portrait.texture!=next_texture:
			# V0.9.5: Never overlay independently drawn full-size portraits.
			# The previous child-layer crossfade caused double faces/zoom flashes.
			# A single instant texture swap keeps the focal silhouette stable.
			for child in portrait.get_children():
				if child is TextureRect:
					child.queue_free()
			portrait.texture=next_texture
	_update_v121_reaction(id,expressive)
	selected_expression=actually_displayed
	portrait_asset_status=fallback_reason
	portrait_asset_path=path
	if reaction_glyph!=null and expressive in ["amused","annoyed","skeptical"]:
		reaction_glyph.text="✦" if expressive=="amused" else "!" if expressive=="annoyed" else "?"
		reaction_glyph.add_theme_color_override("font_color",Color("#f7d27e") if expressive=="amused" else Color("#fd7e83") if expressive=="annoyed" else Color("#d2a5fa"))
		reaction_glyph.visible=true
		reaction_glyph.modulate.a=0.0
		var fx:=create_tween()
		fx.tween_property(reaction_glyph,"modulate:a",1.0,0.13)
		fx.tween_property(reaction_glyph,"modulate:a",0.0,0.62).set_delay(0.26)

func _update_v121_reaction(_id: String, _expression: String) -> void:
	# The old floating expression card created an unwanted second, low-res face.
	# It is retired; intuition and the real portrait are independent systems.
	if reaction_card!=null:reaction_card.visible=false

func _preview_v124_portrait() -> void:
	# Restricted to an actual current encounter; no AI call, economy action,
	# or side effects on the NPC's true visible/intuition state.
	if current.is_empty() or busy or portrait==null:
		return
	var visitor_id: String=str(current.get("customer",{}).get("id",""))
	if not visitor_id in REJECTED_ART_IDS:
		_set_progress("ART REVIEW · SELECT ONE OF THE SEVEN PENDING VISITORS")
		return
	# Cycle only original independently exported candidate files, never an
	# enlarged thumbnail or cropped expression sheet. Missing states are NOT
	# synthesized or silently substituted with the neutral artwork.
	var options: Array[String]=[]
	# Overlay installs can retain old, mismatched F2 studies on disk.
	# For the two live-review characters show ONLY the new five identity-locked
	# state masters rather than accidentally mixing an older review image.
	var candidate_states: Array=LIVE_PORTRAIT_TRIAL_STATES if visitor_id in LIVE_PORTRAIT_TRIAL_IDS else PORTRAIT_REVIEW_STATES
	for state in candidate_states:
		var asset: String=ART_REVIEW_ROOT + "vn_%s_%s.png" % [visitor_id,state]
		if ResourceLoader.exists(asset):
			options.append(state)
	if options.is_empty():
		_set_progress("ART REVIEW · %s · 0/12 CANDIDATES · ART BLOCKED" % visitor_id.to_upper())
		return
	reaction_test_index=(reaction_test_index+1)%options.size()
	var chosen: String=options[reaction_test_index]
	portrait_review_active=true
	_show_portrait(visitor_id,chosen,true)
	_set_progress("F2 ART REVIEW · %s · %s · %d/12 CANDIDATES · UNAPPROVED" % [visitor_id.to_upper(),chosen.to_upper(),options.size()])

func _preview_v121_reaction() -> void:
	# Backward compatible name for earlier hotkeys/tests.
	_preview_v124_portrait()

func _enter_thinking() -> void:
	if thinking_active:return
	thinking_active=true
	thinking_elapsed=0.0
	think_sfx_time=1.3
	if not current.is_empty():
		# Liu Xue's separately painted poses are not spatially registered.
		# Keep her current pose during a short AI wait; the thought bubble
		# provides the thinking reaction without a double-face jump.
		if str(current.get("customer",{}).get("id",""))!="liu_xue":
			_show_portrait(str(current.get("customer",{}).get("id","aldric")),"thinking")
		mood_label.text="Thinking..."
	dialogue=""
	dialogue_label.text="..."
	dialogue_label.visible_characters=-1
	typewriter_running=false
	_refresh_timing()

func _end_thinking() -> void:
	thinking_active=false
	thinking_player.stop()

func _refresh_timing() -> void:
	if quick_timing == null:return
	var seconds: float=thinking_elapsed if thinking_active else float(timing.get("client_wait_ms",0))/1000.0
	var prompt_size: int=int(timing.get("prompt_chars",0))+int(timing.get("instruction_chars",0))
	quick_timing.text="WAIT %.1fs  ·  PROMPT %s" % [seconds,str(prompt_size) if prompt_size>0 else "..."]
	if diagnostics_panel == null or diagnostics_text == null:return
	var origin: String=str(timing.get("source","pending"))
	var fallback: String=str(current.get("ai_error","none"))
	# Show the requested and actually loaded portrait first. Users must not
	# scroll through Hermes logs to find a forced neutral fallback.
	var portrait_customer: String=str(current.get("customer",{}).get("id","none"))
	diagnostics_text.text=("PORTRAIT · %s\nRequested: %s   Displayed: %s\nGate: %s\nFile: %s\n\nProvider: %s\nSource: %s\nInput: %d chars\nPrompt: %d chars\nInstructions: %d chars\nNPC output: %d chars\nGame wait: %.2fs\nExodia task: %.2fs\nHermes first PCM: %.2fs\nAudio played: %.2fs\nSTT: %.2fs\nFallback: %s" % [
		portrait_customer,portrait_requested_expression,selected_expression,portrait_asset_status,portrait_asset_path,
		str(timing.get("provider","unknown")),origin,int(timing.get("input_chars",0)),int(timing.get("prompt_chars",0)),
		int(timing.get("instruction_chars",0)),int(timing.get("output_chars",0)),
		float(timing.get("client_wait_ms",0))/1000.0,float(timing.get("exodia_total_ms",0))/1000.0,
		float(timing.get("hermes_first_pcm_ms",0))/1000.0,float(timing.get("spoken_ms",0))/1000.0,
		float(timing.get("stt_ms",0))/1000.0,fallback.substr(0,75)])
	if not voice_lock.is_empty():
		diagnostics_text.text+="\nVOICE: %s / %s" % [str(voice_lock.get("engine","?")),str(voice_lock.get("id","?"))]
		diagnostics_text.text+="\nHermes preset: %s  ·  sent: %.2fx (pitch-safe)" % [str(voice_lock.get("profile","?")),float(voice_lock.get("speed",1.0))]
		diagnostics_text.text+="\nPreset speed: %.2fx (not applied; changes pitch)" % float(voice_lock.get("preset_speed",1.0))
		diagnostics_text.text+="\nVoice instructions: %s" % str(voice_lock.get("instruct","?")).substr(0,86)
		diagnostics_text.text+="\nHermes model: %s" % str(hermes.last_server.get("model_id","unreported"))
		diagnostics_text.text+="\nHermes run: %s" % str(hermes.last_server.get("run_id","unreported"))
		diagnostics_text.text+="\nTTS mood locked: %s" % str(voice_lock.get("mood","neutral"))
		diagnostics_text.text+="\nExodia transport: %s" % str(timing.get("transport","unknown"))
		diagnostics_text.text+="\nNarration: %s" % str(timing.get("narration_mode","unknown"))
		diagnostics_text.text+="\nText timing: %.2fx (F6 slower, F7 faster)" % text_pace_scale
		diagnostics_text.text+="\nCaption PCM calibration: %.2fx" % _caption_timing_factor()
		diagnostics_text.text+="\nHermes connection: %s (F5 Voice Studio)" % ("ready" if voice_health_ok else "not verified")
		diagnostics_text.text+="\nEmphasis: %s (%.1fx)" % [last_emphasis_categories,performance_intensity]
	# Honest portrait diagnostics: reported emotion is not proof the art changed.
	if str(timing.get("exodia_profile", "")) == "game_dialogue_fast":
		diagnostics_text.text += "\nExodia profile: game_dialogue_fast"
		diagnostics_text.text += "\nQueue: %.2fs  Browser: %.2fs" % [float(timing.get("exodia_queue_wait_s",0)),float(timing.get("exodia_browser_setup_s",0))]
		diagnostics_text.text += "\nTyping: %.2fs  Submit: %.2fs" % [float(timing.get("exodia_typing_s",0)),float(timing.get("exodia_submit_s",0))]
		diagnostics_text.text += "\nFirst text: %.2fs  Full: %.2fs" % [float(timing.get("exodia_first_text_s",0)),float(timing.get("exodia_total_s",0))]


func _check_voice_health() -> void:
	if voice_health_http==null:return
	if voice_health_http.get_http_client_status() not in [HTTPClient.STATUS_DISCONNECTED,HTTPClient.STATUS_CONNECTED]:return
	voice_health_checked=false
	voice_health_ok=false
	var error: Error=voice_health_http.request(hermes_url.trim_suffix("/")+"/health")
	if error!=OK:
		voice_health_checked=true
		voice_health_ok=false
	_update_voice_inspector()

func _on_voice_health(result: int,code: int,_headers: PackedStringArray,_body: PackedByteArray) -> void:
	voice_health_checked=true
	voice_health_ok=(result==HTTPRequest.RESULT_SUCCESS and code==200)
	_update_voice_inspector()

func _update_voice_inspector() -> void:
	if voice_panel_text==null:return
	var telemetry: Dictionary=hermes.audio_telemetry()
	var profile: String=str(voice_lock.get("profile","not selected"))
	var vid: String=str(voice_lock.get("id","not selected"))
	var engine_name: String=str(voice_lock.get("engine",engine))
	var health: String="READY" if voice_health_ok else "CHECK CONNECTION" if voice_health_checked else "CONNECTING"
	voice_panel_text.text="Hermes server   %s\n\nVoice profile      %s\nEngine / speaker   %s · %s\nSpeed / pitch       %.2fx / 0.0 semitones\n\nPCM played          %.2fs\nPCM received       %.2fs\nMeasured caption    %.2fx\nPCM receive RMS     %.2f\nHermes audible peak %.2f\nStream underruns    %d\n\nModel / run         %s / %s\n\nF5 hides this panel. F4 shows API timing." % [
		health,profile,engine_name,vid,float(voice_lock.get("speed",1.0)),
		float(telemetry.get("heard_s",0)),float(telemetry.get("received_s",0)),
		_caption_timing_factor(),float(telemetry.get("level",0)),float(telemetry.get("audible_output_level",0)),int(telemetry.get("underruns",0)),
		str(hermes.last_server.get("model_id","unreported")),str(hermes.last_server.get("run_id","unreported"))]
	voice_panel_text.text+="\n\nSpeech pace         %.1f glyphs/sec\nPacing diagnosis    %s\nPCM sample rate     %d Hz\nPlayback drift      %.2fs\nLocked acting        %s" % [measured_voice_glyphs_per_second,measured_voice_diagnostic,int(telemetry.get("sample_rate",0)),float(telemetry.get("playback_drift_s",0.0)),str(voice_lock.get("instruct","none")).substr(0,100)]

func _toggle_open_mic() -> void:
	open_mic_enabled=not open_mic_enabled
	open_mic_button.text="OPEN MIC: ON" if open_mic_enabled else "OPEN MIC: OFF"
	mic_button.disabled=open_mic_enabled
	if open_mic_enabled:
		if not microphone.begin_open():
			open_mic_enabled=false
			mic_button.disabled=false
			open_mic_button.text="OPEN MIC: OFF"
			_set_progress("MICROPHONE UNAVAILABLE · TRY HOLD-TO-TALK")
		else:
			_set_progress("OPEN MIC LISTENING · SPEAK TO INTERRUPT")
	else:
		microphone.cancel()
		_set_progress("OPEN MIC OFF · HOLD TO TALK AVAILABLE")

func _on_open_mic_detected() -> void:
	# Activate barge-in at speech onset, without waiting for the user to finish.
	_barge_in()
	_set_progress("HEARING YOU · AUTO-SEND AFTER %.1fs SILENCE" % microphone.end_silence_seconds)

func _rearm_open_mic() -> void:
	if open_mic_enabled and not microphone.recording and not awaiting_transcription and not current.is_empty() and not bool(current.get("closed",false)):
		microphone.begin_open()
