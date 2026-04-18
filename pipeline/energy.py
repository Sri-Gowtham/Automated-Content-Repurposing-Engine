import numpy as np

def compute_energy_scores(audio_path: str, segments: list) -> list:
    try:
        import librosa
        print("Computing audio energy scores...")
        y, sr = librosa.load(audio_path, sr=None)
        rms_list = []
        for seg in segments:
            start_idx = int(seg["start"] * sr)
            end_idx = int(seg["end"] * sr)
            y_seg = y[start_idx:end_idx]
            if len(y_seg) == 0:
                rms_list.append(0.0)
            else:
                rms_list.append(float(np.sqrt(np.mean(y_seg ** 2))))
        mn, mx = min(rms_list), max(rms_list)
        for i, seg in enumerate(segments):
            if mx - mn < 1e-9:
                seg["energy_score"] = 0.5
            else:
                seg["energy_score"] = round((rms_list[i] - mn) / (mx - mn), 4)
        return segments
    except Exception as e:
        print(f"Energy scoring error: {e}")
        for seg in segments:
            seg["energy_score"] = 0.0
        return segments
