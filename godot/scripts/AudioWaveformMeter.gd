extends Control
## Live amplitude-history display, not a decorative waveform texture.
## Receives microphone RMS or Godot's actual Hermes output-bus peaks.
## A history column is one visual/audio update (~16 ms at 60 FPS), not a phoneme.

@export var active_color: Color=Color("#55d7f3")
@export var idle_color: Color=Color("#b897c5")
@export var columns: int=44
var history: PackedFloat32Array=PackedFloat32Array()
var signal_active: bool=false
var smoothed_level: float=0.0

func _ready() -> void:
	mouse_filter=Control.MOUSE_FILTER_IGNORE
	for i in range(columns):history.append(0.0)
	queue_redraw()

func push_level(actual_level: float, is_active: bool) -> void:
	signal_active=is_active
	var level: float=clampf(actual_level,0.0,1.0) if is_active else 0.0
	# Attack/release envelope tracks the real signal, never invents a sine wave.
	smoothed_level=lerpf(smoothed_level,level,0.58 if level>smoothed_level else 0.21)
	# No random oscillation, no fabricated motion during silence.
	if history.size()>=columns:history.remove_at(0)
	history.append(level)
	queue_redraw()

func _draw() -> void:
	if size.x<8.0 or size.y<8.0:return
	var center: float=size.y*0.5
	var step: float=size.x/float(maxi(columns,1))
	var neutral: Color=idle_color if not signal_active else active_color
	# Dark glass panel includes an inset guide and softly lit signal center.
	draw_rect(Rect2(Vector2.ZERO,size),Color(0.02,0.025,0.05,0.55),true)
	for row in [0.22,0.50,0.78]:
		draw_line(Vector2(0,size.y*row),Vector2(size.x,size.y*row),Color(neutral.r,neutral.g,neutral.b,0.085),1.0,true)
	draw_line(Vector2(0,center),Vector2(size.x,center),Color(neutral.r,neutral.g,neutral.b,0.34),1.0,true)
	for i in range(history.size()):
		var raw_level: float=history[i]
		# RMS is often low at normal speech volume; compress range visually.
		var height: float=maxf(1.2,pow(raw_level,0.38)*(size.y*0.47))
		var p: Vector2=Vector2((float(i)+0.5)*step,center)
		var color: Color=neutral
		color.a=(0.55+0.45*clampf(raw_level*7.0,0,1)) if signal_active else 0.30
		draw_line(Vector2(p.x,p.y-height),Vector2(p.x,p.y+height),color,maxf(1.6,step*0.52),true)
