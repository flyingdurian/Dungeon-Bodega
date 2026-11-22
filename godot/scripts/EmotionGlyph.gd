@tool
extends RichTextEffect
## Per-glyph emphasis as the character speaks. The style category is set on
## the [emote kind=gold] tag; BBCode handles font, outline and backing color.
## This effect gives phrases motion and illumination without shaking all text.
var bbcode: String = "emote"
# Read-only presentation envelope from the visitor's actual audio output.
# No new AI or TTS calls are made for typography.
var voice_energy: float=0.0
var voice_active: bool=false

func _process_custom_fx(char_fx: CharFXTransform) -> bool:
	var kind: String = str(char_fx.env.get("kind", "gold"))
	var t: float = char_fx.elapsed_time
	var i: float = float(char_fx.relative_index)
	var energy: float=clampf(sqrt(maxf(voice_energy,0.0))*1.5,0.0,1.0)
	var power: float=clampf(float(char_fx.env.get("power",1.0)),0.5,1.5)*(0.78+0.45*energy if voice_active else 0.78)
	if kind == "anger":
		char_fx.offset.x += sin(t * 29.0 + i * 1.93) * 3.2*power
		char_fx.offset.y += sin(t * 19.0 + i * 1.21) * 2.3*power - absf(sin(t*5.6+i*0.73))*3.1*power
		char_fx.color = char_fx.color.lerp(Color("#ff413b"), 0.24 + 0.24 * absf(sin(t * 8.0)))
	elif kind == "gold":
		char_fx.offset.y -= 2.0 + sin(t * 4.4 + i * 0.46) * 2.1*power
		char_fx.color = char_fx.color.lerp(Color("#fff1a8"), 0.10 + 0.14 * absf(sin(t * 3.5)))
	elif kind == "persuade":
		char_fx.offset.y += sin(t * 4.0 + i * 0.52) * 3.4*power
		char_fx.color = char_fx.color.lerp(Color("#b9faff"), 0.16 + 0.12 * absf(sin(t * 4.0)))
	elif kind in ["happy","delight"]:
		char_fx.offset.y -= absf(sin(t * 4.1 + i * 0.63)) * 4.4*power
		char_fx.color = char_fx.color.lerp(Color("#fff4ba"), 0.18)
	elif kind == "doubt":
		char_fx.offset.y += sin(t * 2.4 + i * 0.41) * 2.1*power
		char_fx.color = char_fx.color.lerp(Color("#e4c7ff"), 0.14)
	elif kind == "flirt":
		char_fx.offset.y -= absf(sin(t * 5.0 + i * 0.68)) * 3.7*power
		char_fx.color=char_fx.color.lerp(Color("#ffbfe5"),0.16+0.16*absf(sin(t*2.5)))
	elif kind == "sad":
		# Typography droops like a slow exhale and fades to desaturated blue.
		char_fx.offset.y += 2.1 + absf(sin(t*1.15+i*0.27))*3.8*power
		char_fx.color = char_fx.color.lerp(Color("#8faac9"),0.12+0.18*absf(sin(t*1.3)))
	elif kind == "agreement":
		char_fx.offset.y -= sin(t*3.1+i*0.36)*1.5*power
		char_fx.color=char_fx.color.lerp(Color("#dbffdf"),0.18)
	return true
