import os
import subprocess

def extract_audio(video_path: str, output_dir: str = "uploads") -> str:
    print(f"Extracting audio from {video_path}...")
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")
    os.makedirs(output_dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(video_path))[0]
    out_path = os.path.join(output_dir, f"{base}_audio.wav")
    try:
        subprocess.run([
            "ffmpeg", "-y", "-i", video_path,
            "-vn", "-acodec", "pcm_s16le",
            "-ar", "16000", "-ac", "1",
            out_path
        ], check=True, capture_output=True)
        print(f"Audio saved: {out_path}")
        return out_path
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Audio extraction failed: {e.stderr.decode()}")
