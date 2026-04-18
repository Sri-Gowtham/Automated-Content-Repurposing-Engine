"""
TASK 3 + 4: Audio Extraction & Speech-to-Text
Extracts audio from video → transcribes with Whisper → returns text + timestamps.
"""
import os
import subprocess
import whisper


def extract_audio(video_path: str, output_dir: str) -> str:
    """Extract audio from video file using ffmpeg. Returns path to .wav file."""
    os.makedirs(output_dir, exist_ok=True)
    audio_path = os.path.join(output_dir, "audio.wav")
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vn",                     # no video
        "-acodec", "pcm_s16le",    # PCM 16-bit LE
        "-ar", "16000",            # 16kHz for Whisper
        "-ac", "1",                # mono
        audio_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg audio extraction failed:\n{result.stderr}")
    return audio_path


def transcribe_audio(audio_path: str, model_size: str = "base") -> dict:
    """Transcribe audio using OpenAI Whisper. Returns text + timestamped segments."""
    model = whisper.load_model(model_size)
    result = model.transcribe(audio_path, verbose=False, word_timestamps=True)
    return {
        "text": result["text"].strip(),
        "segments": [
            {
                "id": seg["id"],
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"].strip(),
            }
            for seg in result["segments"]
        ],
        "language": result.get("language", "en"),
    }


def transcribe_video(video_path: str, output_dir: str, model_size: str = "base") -> dict:
    """Full pipeline: extract audio then transcribe. Returns audio_path + transcript."""
    audio_path = extract_audio(video_path, output_dir)
    transcript = transcribe_audio(audio_path, model_size)
    return {"audio_path": audio_path, **transcript}
