import os
from moviepy import AudioFileClip


def extract_audio(video_path: str, output_dir: str = "uploads") -> str:
    """
    Extract audio from a video file using moviepy and save as a .wav file.

    Args:
        video_path: Absolute or relative path to the input video file.
        output_dir: Directory where the extracted .wav will be saved.

    Returns:
        Path to the saved .wav file.

    Raises:
        RuntimeError: If audio extraction fails for any reason.
    """
    print(f"Extracting audio from {video_path}...")

    try:
        os.makedirs(output_dir, exist_ok=True)

        video_filename = os.path.splitext(os.path.basename(video_path))[0]
        output_path = os.path.join(output_dir, f"{video_filename}_audio.wav")

        audio_clip = AudioFileClip(video_path)
        audio_clip.write_audiofile(output_path, fps=16000, nbytes=2, codec="pcm_s16le", logger=None)
        audio_clip.close()

        return output_path

    except Exception as e:
        raise RuntimeError(f"Audio extraction failed for '{video_path}': {e}") from e
