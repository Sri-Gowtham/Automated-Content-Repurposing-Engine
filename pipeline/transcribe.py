import whisper

def transcribe_audio(audio_path: str, model_size: str = "base") -> list:
    print(f"Transcribing with whisper-{model_size}...")
    try:
        model = whisper.load_model(model_size)
        result = model.transcribe(audio_path, word_timestamps=True, verbose=False)
        segments = []
        for seg in result.get("segments", []):
            segments.append({
                "start": float(seg["start"]),
                "end": float(seg["end"]),
                "text": seg["text"].strip()
            })
        print(f"Transcribed {len(segments)} segments")
        return segments
    except Exception as e:
        print(f"Transcription error: {e}")
        return []
