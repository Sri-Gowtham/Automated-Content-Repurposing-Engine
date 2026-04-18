POWER_WORDS = [
    "secret","mistake","shocking","important","never","always",
    "truth","hack","fail","win","biggest","critical","key",
    "must","avoid","change","why","how","best","worst",
    "lesson","reality","exposed","myth","proven","strategy","warning"
]

def keyword_score(text: str) -> float:
    lower = text.lower()
    count = sum(1 for w in POWER_WORDS if w in lower)
    return min(1.0, count * 0.15)

def score_segments(segments: list) -> list:
    for seg in segments:
        seg["keyword_score"] = keyword_score(seg["text"])
    return segments
