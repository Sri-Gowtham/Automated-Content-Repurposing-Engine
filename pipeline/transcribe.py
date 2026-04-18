import whisper


def transcribe_audio(audio_path: str, model_size: str = "base") -> list[dict]:
    """
    Transcribe an audio file using OpenAI Whisper.

    Args:
        audio_path: Path to the audio file to transcribe.
        model_size: Whisper model size to use (e.g. "tiny", "base", "small",
                    "medium", "large"). Defaults to "base".

    Returns:
        A list of segment dicts, each containing:
            - "start" (float): Segment start time in seconds.
            - "end"   (float): Segment end time in seconds.
            - "text"  (str):   Transcribed text, stripped of leading/trailing whitespace.
        Returns an empty list if transcription fails for any reason.
    """
    print(f"Transcribing with whisper-{model_size}...")

    try:
        model = whisper.load_model(model_size)
        result = model.transcribe(audio_path, word_timestamps=True, verbose=False)

        segments = [
            {
                "start": float(segment["start"]),
                "end":   float(segment["end"]),
                "text":  segment["text"].strip(),
            }
            for segment in result.get("segments", [])
        ]

        return segments

    except Exception as e:
        print(f"[transcribe_audio] Error during transcription: {e}")
        return []
