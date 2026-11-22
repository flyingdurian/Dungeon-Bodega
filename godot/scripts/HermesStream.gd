class_name HermesStream
extends Node
## PCM16/mono HTTPClient progressive playback; compatible with Hermes /stream.
## One active stream only. Godot desktop target (HTTPClient restrictions vary on web).
signal audio_started()
signal audio_finished()
signal audio_failed(reason: String)
signal first_packet(ms: int)

@export var base_url: String = "http://127.0.0.1:8000"
@onready var player: AudioStreamPlayer = $AudioPlayer
var client: HTTPClient = null
var phase: String = "idle"
var elapsed: float = 0.0
var response_code: int = 0
var sample_rate: int = 24000
var pending_bytes: PackedByteArray = PackedByteArray()
var queue: Array = []
var queue_offset: int = 0
var received_samples: int = 0
var pushed_samples: int = 0
var source_done: bool = false
var playback: AudioStreamGeneratorPlayback = null
var started: bool = false
var first_packet_seen: bool = false
var buffer_capacity_frames: int = 0
var drain_silence_elapsed: float = 0.0
var request_body: String = ""
var last_error: String = ""
var error_buffer: PackedByteArray = PackedByteArray()
var last_request: Dictionary = {}
var last_server: Dictionary = {}
var voice_level: float = 0.0
var audio_underruns: int = 0
var _level_sum: float = 0.0
var _level_samples: int = 0
var _underrun_latched: bool = false
var last_played_seconds: float = 0.0
var last_received_seconds: float = 0.0
var last_underruns: int = 0
var last_ended_normally: bool = false
var playback_started_ms: int = 0
var last_playback_wall_s: float = 0.0
var last_playback_drift_s: float = 0.0
var sample_rate_from_header: bool = false
## Dedicated bus: peaks represent audio actually being rendered by Godot,
## not future PCM arriving over the network. No extra TTS calls are made.
const VISITOR_AUDIO_BUS: String="LivingCounterVisitorAudio"
var visitor_bus_index: int=-1

func _ready() -> void:
	visitor_bus_index=AudioServer.get_bus_index(VISITOR_AUDIO_BUS)
	if visitor_bus_index<0:
		visitor_bus_index=AudioServer.bus_count
		AudioServer.add_bus(visitor_bus_index)
		AudioServer.set_bus_name(visitor_bus_index,VISITOR_AUDIO_BUS)
		AudioServer.set_bus_send(visitor_bus_index,"Master")
	player.bus=VISITOR_AUDIO_BUS

func audible_output_level() -> float:
	if visitor_bus_index<0 or not started or not player.playing:return 0.0
	var left_db: float=AudioServer.get_bus_peak_volume_left_db(visitor_bus_index,0)
	var right_db: float=AudioServer.get_bus_peak_volume_right_db(visitor_bus_index,0)
	var amplitude: float=pow(10.0,maxf(left_db,right_db)/20.0)
	return clampf(amplitude,0.0,1.0)

func total_audio_seconds() -> float:
	return float(received_samples) / float(maxi(sample_rate, 1))

func stream_is_complete() -> bool:
	return source_done

func audio_telemetry() -> Dictionary:
	return {"received_s": total_audio_seconds() if started else last_received_seconds,
		"heard_s": heard_seconds() if started else last_played_seconds,
		"underruns": audio_underruns if started else last_underruns,
		"last_complete": last_ended_normally, "level": voice_level,
		"source_done": source_done, "audible_output_level":audible_output_level(), "engine": str(last_request.get("engine", "")),
		"voice": str(last_request.get("voice", "")),
		"sample_rate": sample_rate, "sample_rate_header": sample_rate_from_header,
		"playback_drift_s": maxf(0.0, (float(Time.get_ticks_msec()-playback_started_ms)/1000.0 - heard_seconds())) if started and playback_started_ms>0 else last_playback_drift_s,
		"playback_wall_s": float(Time.get_ticks_msec()-playback_started_ms)/1000.0 if started and playback_started_ms>0 else last_playback_wall_s}


# Approximate time actually consumed by the output device, not network time.
# Godot's generator has no per-word timestamps; use this for paced reveal only.
func heard_seconds() -> float:
	if not started or playback == null or sample_rate <= 0:
		return 0.0
	var buffered: int = buffer_capacity_frames - playback.get_frames_available()
	return maxf(0.0, float(pushed_samples - buffered) / float(sample_rate))

func is_busy() -> bool:
	return phase != "idle"

func speak(text: String, engine: String, voice_id: String, mood: String, instruct: String, archetype: String, profile_speed: float=1.0) -> bool:
	if text.strip_edges().is_empty():
		return false
	stop(false)
	var url: String = base_url.strip_edges().trim_prefix("http://").trim_suffix("/")
	if base_url.begins_with("https://"):
		audio_failed.emit("Prototype supports local http:// Hermes only")
		return false
	var endpoint: String = url.split("/")[0]
	var bits: PackedStringArray = endpoint.split(":")
	var host: String = bits[0]
	var port: int = int(bits[1]) if bits.size() > 1 else 8000
	if host.is_empty() or port < 1 or port > 65535:
		audio_failed.emit("Invalid Hermes address")
		return false
	var payload: Dictionary = {"engine":engine,"voice":voice_id,"input":text,"mood":mood,
		"instruct":instruct,"archetype":archetype,"speed":clampf(profile_speed,0.95,1.15),"pitch_shift":0.0,
		"temperature":0.45,"repetition_penalty":1.3,"streaming_interval":0.5,"stream_chunk_min":85}
	last_request={"engine":engine,"voice":voice_id,"mood":mood,"instruct":instruct,"speed":float(payload["speed"]),"pitch_shift":0.0}
	last_server.clear()
	voice_level=0.0
	last_played_seconds=0.0
	last_received_seconds=0.0
	last_underruns=0
	last_ended_normally=false
	playback_started_ms=0
	last_playback_wall_s=0.0
	last_playback_drift_s=0.0
	sample_rate_from_header=false
	sample_rate=24000
	audio_underruns=0
	_underrun_latched=false
	_level_sum=0.0
	_level_samples=0
	request_body = JSON.stringify(payload)
	client = HTTPClient.new()
	client.read_chunk_size = 8192
	var err: Error = client.connect_to_host(host, port)
	if err != OK:
		client = null
		audio_failed.emit("Hermes connection error: " + error_string(err))
		return false
	phase = "connecting"
	elapsed = 0.0
	response_code = 0
	pending_bytes.clear()
	queue.clear()
	queue_offset = 0
	received_samples = 0
	pushed_samples = 0
	source_done = false
	started = false
	first_packet_seen = false
	buffer_capacity_frames = 0
	drain_silence_elapsed = 0.0
	playback = null
	error_buffer.clear()
	last_error = ""
	return true

func stop(emit_finished: bool = false) -> void:
	var was_started: bool = started
	if was_started:
		last_played_seconds=heard_seconds()
		last_received_seconds=total_audio_seconds()
		last_underruns=audio_underruns
		last_ended_normally=emit_finished
		if playback_started_ms>0:
			last_playback_wall_s=float(Time.get_ticks_msec()-playback_started_ms)/1000.0
			last_playback_drift_s=maxf(0.0,last_playback_wall_s-last_played_seconds)
	if client != null:
		client.close()
	client = null
	phase = "idle"
	player.stop()
	playback = null
	pending_bytes.clear()
	queue.clear()
	queue_offset = 0
	started = false
	voice_level=0.0
	if emit_finished and was_started:
		audio_finished.emit()

func _fail(message: String) -> void:
	last_error = message
	stop(false)
	audio_failed.emit(message)

func _process(delta: float) -> void:
	if phase == "idle":
		return
	elapsed += delta
	if elapsed > 120.0:
		_fail("Hermes stream timed out")
		return
	if phase == "draining":
		_drain_queue()
		# Do NOT compare pushed audio duration to get_playback_position():
		# starting the generator before first PCM caused playback_position to
		# advance through silence, clipping the final syllable(s).
		# Finish only when every received sample has been pushed AND the
		# generator has consumed every frame from its ring buffer.
		if source_done and started and queue.size() == queue_offset and pushed_samples == received_samples:
			if playback != null and playback.get_frames_available() >= buffer_capacity_frames - 2:
				drain_silence_elapsed += delta
				if drain_silence_elapsed >= 0.12:
					stop(true)
			else:
				drain_silence_elapsed = 0.0
		return
	if client == null:
		return
	var err: Error = client.poll()
	if err != OK:
		_fail("Hermes socket closed / network error")
		return
	var status: int = client.get_status()
	if status in [HTTPClient.STATUS_CANT_CONNECT, HTTPClient.STATUS_CANT_RESOLVE, HTTPClient.STATUS_CONNECTION_ERROR, HTTPClient.STATUS_TLS_HANDSHAKE_ERROR]:
		_fail("Hermes server unreachable — confirm port 8000")
		return
	if phase == "connecting":
		if status == HTTPClient.STATUS_CONNECTED:
			var headers: PackedStringArray = PackedStringArray(["Content-Type: application/json","Accept: audio/pcm"])
			var sent: Error = client.request(HTTPClient.METHOD_POST,"/stream",headers,request_body)
			if sent != OK:
				_fail("Could not send voice request")
			else:
				phase = "requesting"
		return
	if phase == "requesting":
		if status in [HTTPClient.STATUS_BODY, HTTPClient.STATUS_CONNECTED] and client.has_response():
			response_code = client.get_response_code()
			var headers_dict: Dictionary = client.get_response_headers_as_dictionary()
			for key in headers_dict:
				var header_name: String=str(key).to_lower()
				if header_name == "x-sample-rate":
					sample_rate = max(8000,int(headers_dict[key]))
					sample_rate_from_header=true
				elif header_name == "x-run-id":
					last_server["run_id"] = str(headers_dict[key])
				elif header_name == "x-model-id":
					last_server["model_id"] = str(headers_dict[key])
				elif header_name == "x-active-engine":
					last_server["engine"] = str(headers_dict[key])
				elif header_name == "x-resolved-instruct":
					last_server["resolved_instruct"] = str(headers_dict[key]).substr(0,120)
				elif header_name == "x-model-state":
					last_server["model_state"] = str(headers_dict[key])
			if response_code == 200:
				var gen: AudioStreamGenerator = AudioStreamGenerator.new()
				gen.mix_rate = sample_rate
				gen.buffer_length = 1.20
				player.stream = gen
				# Avoid audible gaps when streaming packets arrive unevenly: prebuffer ~280ms.
				# Otherwise position advances during network/model silence.
			phase = "body"
	if phase == "body":
		if status == HTTPClient.STATUS_BODY:
			var bytes: PackedByteArray = client.read_response_body_chunk()
			if not bytes.is_empty():
				if response_code == 200:
					_ingest(bytes)
				else:
					error_buffer.append_array(bytes)
		elif status == HTTPClient.STATUS_CONNECTED or status == HTTPClient.STATUS_DISCONNECTED:
			if response_code != 200:
				_fail("Hermes HTTP %d: %s" % [response_code,error_buffer.get_string_from_utf8().substr(0,120)])
				return
			if received_samples == 0:
				_fail("Hermes returned no PCM samples")
				return
			if pending_bytes.size() > 0:
				_fail("Hermes returned an incomplete PCM sample")
				return
			source_done = true
			client.close()
			client = null
			phase = "draining"
	_drain_queue()

func _ingest(chunk: PackedByteArray) -> void:
	pending_bytes.append_array(chunk)
	var complete: int = pending_bytes.size() - (pending_bytes.size() % 2)
	for idx in range(0,complete,2):
		var value: float = float(pending_bytes.decode_s16(idx)) / 32768.0
		_level_sum += value * value
		_level_samples += 1
		if _level_samples >= 1024:
			voice_level = lerpf(voice_level, sqrt(_level_sum / float(_level_samples)), 0.52)
			_level_sum = 0.0
			_level_samples = 0
		queue.append(Vector2(value,value))
		received_samples += 1
	pending_bytes = pending_bytes.slice(complete,pending_bytes.size())
	if not first_packet_seen:
		first_packet_seen = true
		first_packet.emit(roundi(elapsed*1000))

func _drain_queue() -> void:
	if not started:
		# A modest 280ms prebuffer costs ~130ms beyond the previous build,
		# but protects the human voice against uneven Mac streaming chunks.
		if queue.size() - queue_offset < int(float(sample_rate)*0.28) and not source_done:
			return
		if queue.size() == queue_offset:
			return
		player.play()
		playback = player.get_stream_playback() as AudioStreamGeneratorPlayback
		if playback == null:
			_fail("Could not initialize Hermes audio generator")
			return
		buffer_capacity_frames = playback.get_frames_available()
		started = true
		playback_started_ms=Time.get_ticks_msec()
		audio_started.emit()
	if playback == null:
		return
	var available: int = playback.get_frames_available()
	# Count consecutive producer starvation as one event; do not interpret
	# ordinary completed-stream draining as a network underrun.
	var starved: bool=not source_done and available >= buffer_capacity_frames - 2 and queue.size() == queue_offset
	if starved and not _underrun_latched:
		audio_underruns += 1
	_underrun_latched=starved
	var count: int = mini(available, mini(4096, queue.size()-queue_offset))
	if count <= 0:
		return
	var frames: PackedVector2Array = PackedVector2Array()
	frames.resize(count)
	for i in range(count):
		frames[i] = queue[queue_offset+i]
	playback.push_buffer(frames)
	queue_offset += count
	pushed_samples += count
	if queue_offset > 16384:
		queue = queue.slice(queue_offset)
		queue_offset = 0
