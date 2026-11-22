extends Panel
## Native V1.2 inspectable 2D trade desk. No screenshot or fake 3D object.
## Authoritative condition, provenance and appraisal values come only from server.
signal action_requested(action: String)

const INK := Color("#220d2bee")
const GOLD := Color("#f2c77e")
const IVORY := Color("#fce9d3")
const QUIET := Color("#d1ad9f")

var report: Dictionary = {}
var viewing: String = "evidence"
var busy: bool = false
var item_image: TextureRect
var item_name: Label
var details: RichTextLabel
var summary: Label
var action_buttons: Dictionary = {}
var zoom: float = 1.0
var spin_degrees: float = 0.0

func _ready() -> void:
	position = Vector2(304,103)
	size = Vector2(783,636)
	mouse_filter = Control.MOUSE_FILTER_STOP
	var frame := StyleBoxFlat.new()
	frame.bg_color = INK
	frame.border_color = GOLD
	frame.set_border_width_all(3)
	frame.set_corner_radius_all(16)
	frame.shadow_color = Color(0.03,0.0,0.03,0.85)
	frame.shadow_size = 17
	add_theme_stylebox_override("panel",frame)
	_label("TRADE DESK  ·  OBJECT EVIDENCE",Vector2(25,14),Vector2(618,38),25,GOLD)
	_button("✕",Rect2(726,15,38,38)).pressed.connect(func(): visible=false)
	var divider := ColorRect.new()
	divider.color = Color("#805a67")
	divider.position=Vector2(23,63)
	divider.size=Vector2(736,1)
	divider.mouse_filter=Control.MOUSE_FILTER_IGNORE
	add_child(divider)
	item_name=_label("Choose an object",Vector2(32,81),Vector2(338,34),24,IVORY)
	var stage := Panel.new()
	stage.position=Vector2(27,125)
	stage.size=Vector2(356,341)
	var stage_box:=StyleBoxFlat.new()
	stage_box.bg_color=Color("#110b20")
	stage_box.border_color=Color("#795568")
	stage_box.set_border_width_all(1)
	stage_box.set_corner_radius_all(12)
	stage.add_theme_stylebox_override("panel",stage_box)
	add_child(stage)
	item_image=TextureRect.new()
	item_image.position=Vector2(64,34)
	item_image.size=Vector2(228,241)
	item_image.pivot_offset=item_image.size/2.0
	item_image.expand_mode=TextureRect.EXPAND_IGNORE_SIZE
	item_image.stretch_mode=TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	item_image.mouse_filter=Control.MOUSE_FILTER_IGNORE
	stage.add_child(item_image)
	_button("↶ ROTATE",Rect2(34,477,111,39)).pressed.connect(func():_rotate_art(-22.5))
	_button("ROTATE ↷",Rect2(152,477,111,39)).pressed.connect(func():_rotate_art(22.5))
	_button("ZOOM +",Rect2(270,477,111,39)).pressed.connect(_zoom_art)
	_label("2D preview · item art is not a 3D model",Vector2(31,524),Vector2(359,24),13,QUIET)
	for i in range(3):
		var names: Array[String]=["EVIDENCE","ORIGIN","APPRAISAL"]
		var keys: Array[String]=["evidence","origin","appraisal"]
		var key:String=keys[i]
		_button(names[i],Rect2(413+i*115,81,107,38)).pressed.connect(_show_tab.bind(key))
	details=RichTextLabel.new()
	details.position=Vector2(412,129)
	details.size=Vector2(344,325)
	details.bbcode_enabled=true
	details.add_theme_color_override("default_color",IVORY)
	details.add_theme_font_size_override("normal_font_size",17)
	details.scroll_active=true
	add_child(details)
	var labels: Array[String]=["EXAMINE","CHECK MARK","APPRAISE"]
	var actions: Array[String]=["examine","check_origin","appraise"]
	for i in range(3):
		var action:String=actions[i]
		var button:=_button(labels[i],Rect2(410+i*116,477,108,39))
		button.pressed.connect(func():action_requested.emit(action))
		action_buttons[action]=button
	summary=_label("Observations are nonbinding. Only a confirmed trade moves gold or stock.",Vector2(25,577),Vector2(731,40),15,QUIET)
	visible=false

func _label(value: String, pos: Vector2, dimensions: Vector2, font_size:int, tint:Color) -> Label:
	var label:=Label.new()
	label.text=value
	label.position=pos
	label.size=dimensions
	label.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
	label.add_theme_color_override("font_color",tint)
	label.add_theme_font_size_override("font_size",font_size)
	label.mouse_filter=Control.MOUSE_FILTER_IGNORE
	add_child(label)
	return label

func _button(value: String, bounds:Rect2) -> Button:
	var button:=Button.new()
	button.text=value
	button.position=bounds.position
	button.size=bounds.size
	button.add_theme_font_size_override("font_size",14)
	var normal:=StyleBoxFlat.new()
	normal.bg_color=Color("#40203e")
	normal.border_color=Color("#cba26e")
	normal.set_border_width_all(1)
	normal.set_corner_radius_all(8)
	button.add_theme_stylebox_override("normal",normal)
	var hover:=normal.duplicate() as StyleBoxFlat
	hover.bg_color=Color("#64345b")
	hover.border_color=GOLD
	button.add_theme_stylebox_override("hover",hover)
	add_child(button)
	return button

func set_busy(value: bool) -> void:
	busy=value
	_render()

func display_report(data:Dictionary) -> void:
	report=data.duplicate(true)
	var item_id:String=str(report.get("item_id",""))
	var path:String="res://assets/item_%s.png" % item_id
	item_image.texture=load(path) if ResourceLoader.exists(path) else null
	zoom=1.0
	spin_degrees=0.0
	item_image.scale=Vector2.ONE
	item_image.rotation_degrees=0.0
	_render()

func _rotate_art(amount:float) -> void:
	spin_degrees+=amount
	var t:=create_tween()
	t.tween_property(item_image,"rotation_degrees",spin_degrees,0.22).set_trans(Tween.TRANS_SINE)

func _zoom_art() -> void:
	zoom=1.0 if zoom>=1.45 else zoom+0.15
	var t:=create_tween()
	t.tween_property(item_image,"scale",Vector2(zoom,zoom),0.2)

func _show_tab(tab:String) -> void:
	viewing=tab
	_render()

func _render() -> void:
	if item_name==null or details==null:return
	item_name.text=str(report.get("item_name","Current item"))
	var notes:Array=report.get("notes",[])
	var condition:String=str(report.get("condition","Unexamined"))
	var provenance:String=str(report.get("provenance","Unverified"))
	var estimate:Variant=report.get("estimated_range")
	var lines:PackedStringArray=PackedStringArray()
	if viewing=="evidence":
		lines.append("[color=#f2c77e]CONDITION[/color]")
		lines.append(condition.capitalize())
		lines.append("")
		lines.append("[color=#f2c77e]VISIBLE NOTES[/color]")
		for note in notes:
			if str(note).begins_with("Condition:"):lines.append(str(note))
		if notes.is_empty():lines.append("Examine the object to reveal physical details.")
	elif viewing=="origin":
		lines.append("[color=#f2c77e]MAKER / PROVENANCE[/color]")
		lines.append(provenance.capitalize())
		lines.append("")
		for note in notes:
			if str(note).begins_with("Maker record:"):lines.append(str(note))
		if provenance=="Unverified":lines.append("Check the maker mark for a clue. This is not a certificate.")
	else:
		lines.append("[color=#f2c77e]APPRAISAL[/color]")
		if estimate is Array and estimate.size()==2:
			lines.append("[font_size=26]%d – %d GOLD[/font_size]" % [int(estimate[0]),int(estimate[1])])
			lines.append("Nonbinding estimate based on the observed condition and maker evidence.")
		else:lines.append("Examine the object, then request an estimated value range.")
	details.text="\n".join(lines)
	var done:Dictionary={}
	for action in report.get("actions",[]):
		if action is Dictionary:done[str(action.get("id",""))]=bool(action.get("done",false))
	for key in action_buttons:
		var btn:Button=action_buttons[key]
		btn.disabled=busy or bool(done.get(key,false))
	summary.text="Inspection is evidence, not an accepted price. Gold and stock are unchanged until confirmation."
