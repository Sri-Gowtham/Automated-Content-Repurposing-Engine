"""
TASK 5 + 6 + 7 + 8: Segmentation, Keyword Scoring, Audio Energy, Ranking
Groups Whisper segments into 15-30s chunks, scores them, ranks top clips.
"""
import math
import librosa
import numpy as np

# ─── TASK 5: Segmentation ────────────────────────────────────────────────────

CHUNK_MIN = 15.0   # seconds
CHUNK_MAX = 30.0   # seconds

VIRAL_KEYWORDS = {
    "secret": 3, "mistake": 3, "shocking": 3, "important": 2,
    "revealed": 2, "truth": 2, "never": 2, "always": 1, "hack": 2,
    "tip": 1, "trick": 2, "warning": 3, "biggest": 2, "best": 1,
    "worst": 2, "incredible": 2, "amazing": 1, "viral": 2, "hidden": 2,
    "exclusive": 2, "breaking": 3, "critical": 2, "urgent": 3,
    "avoid": 2, "danger": 3, "wrong": 2, "genius": 2, "insane": 2,
}


def build_chunks(whisper_segments: list) -> list:
    """
    Merge Whisper word-level segments into 15-30s chunks.
    Returns list of dicts: {start, end, text, segment_ids}
    """
    chunks = []
    current = None

    for seg in whisper_segments:
        if current is None:
            current = {
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"],
                "segment_ids": [seg["id"]],
            }
        else:
            span = seg["end"] - current["start"]
            if span <= CHUNK_MAX:
                current["end"] = seg["end"]
                current["text"] += " " + seg["text"]
                current["segment_ids"].append(seg["id"])
            else:
                # close current, start new
                if (current["end"] - current["start"]) >= CHUNK_MIN:
                    chunks.append(current)
                current = {
                    "start": seg["start"],
                    "end": seg["end"],
                    "text": seg["text"],
                    "segment_ids": [seg["id"]],
                }

    if current and (current["end"] - current["start"]) >= CHUNK_MIN:
        chunks.append(current)

    for i, c in enumerate(chunks):
        c["chunk_id"] = i

    return chunks


# ─── TASK 6: Keyword Scoring ─────────────────────────────────────────────────

def keyword_score(text: str) -> float:
    """Return viral keyword score for a chunk of text."""
    words = text.lower().split()
    score = 0.0
    for word in words:
        clean = word.strip(".,!?\"'")
        score += VIRAL_KEYWORDS.get(clean, 0)
    return score


# ─── TASK 7: Audio Energy Detection ─────────────────────────────────────────

def audio_energy_scores(audio_path: str, chunks: list) -> list:
    """
    Load audio with librosa, compute RMS energy per chunk window.
    Adds 'energy_score' to each chunk in-place. Returns updated chunks.
    """
    try:
        y, sr = librosa.load(audio_path, sr=None, mono=True)
        duration = librosa.get_duration(y=y, sr=sr)

        for chunk in chunks:
            start_sample = int(min(chunk["start"], duration - 0.01) * sr)
            end_sample = int(min(chunk["end"], duration) * sr)
            segment_audio = y[start_sample:end_sample]

            if len(segment_audio) == 0:
                chunk["energy_score"] = 0.0
            else:
                rms = np.sqrt(np.mean(segment_audio ** 2))
                chunk["energy_score"] = float(rms)
    except Exception as e:
        print(f"[WARN] librosa energy detection failed: {e}")
        for chunk in chunks:
            chunk["energy_score"] = 0.0

    return chunks


# ─── TASK 8: Segment Ranking ─────────────────────────────────────────────────

def rank_segments(chunks: list, audio_path: str, top_n: int = 5) -> list:
    """
    Score + rank all chunks. Returns top_n chunks sorted by composite score.
    Scoring: keyword_score (weighted 0.6) + normalized energy (weighted 0.4)
    """
    for chunk in chunks:
        chunk["keyword_score"] = keyword_score(chunk["text"])

    chunks = audio_energy_scores(audio_path, chunks)

    # Normalize energy across chunks (0–1)
    energies = [c["energy_score"] for c in chunks]
    max_e = max(energies) if max(energies) > 0 else 1.0
    for chunk in chunks:
        chunk["energy_norm"] = chunk["energy_score"] / max_e

    # Normalize keyword score
    kw_scores = [c["keyword_score"] for c in chunks]
    max_k = max(kw_scores) if max(kw_scores) > 0 else 1.0
    for chunk in chunks:
        chunk["keyword_norm"] = chunk["keyword_score"] / max_k

    # Composite
    for chunk in chunks:
        chunk["score"] = round(
            0.6 * chunk["keyword_norm"] + 0.4 * chunk["energy_norm"], 4
        )

    ranked = sorted(chunks, key=lambda x: x["score"], reverse=True)
    return ranked[:top_n]
