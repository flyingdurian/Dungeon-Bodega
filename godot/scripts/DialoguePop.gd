@tool
extends RichTextEffect
## V0.6.4: reveal-aware per-glyph entrance tween. The old implementation
## sometimes armed glyphs while still hidden, so their entrance animation had
## already expired when the player saw them.
var bbcode: String = "revealpop"
var observed: Dictionary = {}
var visible_limit: int = 0

func reset() -> void:
	observed.clear()
	visible_limit = 0

func _process_custom_fx(char_fx: CharFXTransform) -> bool:
	var index: int=char_fx.relative_index
	if index >= visible_limit:
		return true
	var now: int=Time.get_ticks_msec()
	if not observed.has(index):
		observed[index]=now
	var age: float=float(now-int(observed[index]))/1000.0
	var t: float=clampf(age/0.24,0.0,1.0)
	var easing: float=1.0-pow(1.0-t,3.0)
	var spring: float=sin(t*PI)*pow(1.0-t,2.0)
	char_fx.offset.y -= (1.0-easing)*12.0 + spring*4.0
	var tint: Color=char_fx.color
	tint.a *= clampf(t*1.5,0.0,1.0)
	char_fx.color=tint
	return true
