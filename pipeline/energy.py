import librosa
import numpy as np


def compute_energy_scores(audio_path: str, segments: list[dict]) -> list[dict]:
    """
    Compute and normalize RMS energy scores for each transcript segment.

    Args:
        audio_path: Path to the audio file.
        segments:   List of segment dicts with "start" and "end" keys (in seconds).

    Returns:
        The same list with an "energy_score" (float in [0.0, 1.0]) added to each dict.
        On any exception, all segments receive energy_score=0.0 and the list is returned.
    """
    try:
        y, sr = librosa.load(audio_path, sr=None)

        # --- Pass 1: compute raw RMS per segment ---
        rms_values: list[float] = []
        for segment in segments:
            start_sample = int(segment["start"] * sr)
            end_sample   = int(segment["end"]   * sr)
            y_seg = y[start_sample:end_sample]

            if y_seg.size == 0:
                rms_values.append(0.0)
            else:
                rms = float(np.sqrt(np.mean(y_seg ** 2)))
                rms_values.append(rms)

        # --- Pass 2: min-max normalization → [0.0, 1.0] ---
        rms_min = min(rms_values)
        rms_max = max(rms_values)
        rms_range = rms_max - rms_min

        for segment, rms in zip(segments, rms_values):
            if rms_range == 0.0:
                segment["energy_score"] = 0.0
            else:
                segment["energy_score"] = float((rms - rms_min) / rms_range)

        return segments

    except Exception as e:
        print(f"[compute_energy_scores] Error computing energy scores: {e}")
        for segment in segments:
            segment["energy_score"] = 0.0
        return segments
