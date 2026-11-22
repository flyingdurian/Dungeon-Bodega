class_name MicrophoneCapture
extends Node
## Local Windows microphone capture: manual push-to-talk OR experimental open-mic VAD.
## Emits WAV at Godot audio mix rate. Server handles transcription locally.
## Use headphones for open mic to avoid game-audio echo triggering a false barge-in.

signal capture_started()
signal speech_detected()
signal capture_finished(wav: PackedByteArray)
signal capture_failed(reason: String)

@onready var microphone_player: AudioStreamPlayer = $MicrophonePlayer
var effect: AudioEffectCapture
var bus_index: int = -1
var frames: Array[float] = []
var preroll: Array[float] = []
var recording: bool = false
var open_mode: bool = false
var speaking: bool = false
## Latest amplitude of microphone samples already captured for this session.
var live_rms: float = 0.0
var mix_rate: int = 48000
var onset_samples: int = 0
var silence_samples: int = 0

# Adjustable on the node; threshold is RMS relative to full-scale digital input.
@export_range(0.005,0.12,0.001) var speech_threshold: float = 0.018
@export_range(0.7,2.5,0.05) var end_silence_seconds: float = 1.20
const MAX_SECONDS: int = 12

func _ready() -> void:
	var mic_bus_name: String = "LivingCounterMic"
	bus_index = AudioServer.get_bus_index(mic_bus_name)
	if bus_index < 0:
		bus_index = AudioServer.bus_count
		AudioServer.add_bus(bus_index)
		AudioServer.set_bus_name(bus_index,mic_bus_name)
	AudioServer.set_bus_volume_db(bus_index,-80.0)
	effect = AudioEffectCapture.new()
	effect.buffer_length = 14.0
	AudioServer.add_bus_effect(bus_index,effect)
	microphone_player.bus=mic_bus_name
	microphone_player.stream=AudioStreamMicrophone.new()
	mix_rate=int(AudioServer.get_mix_rate())
	if mix_rate < 8000:
		mix_rate=48000

func begin() -> bool:
	return _begin(false)

func begin_open() -> bool:
	return _begin(true)

func _begin(automatic: bool) -> bool:
	if recording or effect == null:
		return false
	frames.clear()
	preroll.clear()
	onset_samples=0
	silence_samples=0
	open_mode=automatic
	speaking=false
	live_rms=0.0
	effect.clear_buffer()
	microphone_player.play()
	recording=true
	if not open_mode:
		capture_started.emit()
	return true

func _process(_delta: float) -> void:
	if not recording or effect == null:
		return
	var n: int = mini(4096,effect.get_frames_available())
	if n <= 0:
		return
	var samples: PackedVector2Array = effect.get_buffer(n)
	var mono: Array[float] = []
	var power: float = 0.0
	for f in samples:
		var v: float = clampf((f.x+f.y)*0.5,-1.0,1.0)
		mono.append(v)
		power += v*v
	var rms: float = sqrt(power/float(maxi(1,mono.size())))
	live_rms=rms
	if not open_mode:
		frames.append_array(mono)
	elif not speaking:
		preroll.append_array(mono)
		# Retain only ~250ms of lead-in so consonants are not clipped.
		if preroll.size() > int(mix_rate*0.25):
			preroll=preroll.slice(preroll.size()-int(mix_rate*0.25))
		if rms >= speech_threshold:
			onset_samples += mono.size()
		else:
			onset_samples = 0
		if onset_samples >= int(mix_rate*0.12):
			speaking=true
			frames=preroll.duplicate()
			preroll.clear()
			silence_samples=0
			speech_detected.emit() # Barge in at speech onset, not after silence timeout.
			capture_started.emit()
	else:
		frames.append_array(mono)
		if rms >= speech_threshold:
			silence_samples=0
		else:
			silence_samples += mono.size()
		if silence_samples >= int(mix_rate*end_silence_seconds):
			finish()
			return
	if frames.size() >= mix_rate*MAX_SECONDS:
		finish()

func cancel() -> void:
	recording=false
	microphone_player.stop()
	live_rms=0.0
	frames.clear()
	preroll.clear()
	open_mode=false
	speaking=false

func finish() -> void:
	if not recording:return
	var was_open: bool = open_mode
	recording=false
	open_mode=false
	speaking=false
	microphone_player.stop()
	live_rms=0.0
	if frames.size() < int(mix_rate*0.16):
		frames.clear()
		if not was_open:
			capture_failed.emit("Hold the microphone button a little longer")
		return
	var data: PackedByteArray = PackedByteArray()
	data.resize(frames.size()*2)
	for i in range(frames.size()):
		data.encode_s16(i*2,clampi(roundi(frames[i]*32767.0),-32768,32767))
	frames.clear()
	var wav: PackedByteArray = PackedByteArray()
	wav.resize(44)
	_write_text(wav,0,"RIFF")
	wav.encode_u32(4,36+data.size())
	_write_text(wav,8,"WAVE")
	_write_text(wav,12,"fmt ")
	wav.encode_u32(16,16)
	wav.encode_u16(20,1)
	wav.encode_u16(22,1)
	wav.encode_u32(24,mix_rate)
	wav.encode_u32(28,mix_rate*2)
	wav.encode_u16(32,2)
	wav.encode_u16(34,16)
	_write_text(wav,36,"data")
	wav.encode_u32(40,data.size())
	wav.append_array(data)
	capture_finished.emit(wav)

func _write_text(buffer: PackedByteArray, offset: int, value: String) -> void:
	var raw: PackedByteArray=value.to_ascii_buffer()
	for i in range(raw.size()):
		buffer[offset+i]=raw[i]
