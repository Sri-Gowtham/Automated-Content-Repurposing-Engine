POWER_WORDS = [
    "secret", "mistake", "shocking", "important", "never", "always",
    "truth", "hack", "fail", "win", "biggest", "critical", "key",
    "must", "avoid", "change", "why", "how", "best", "worst",
    "lesson", "reality", "exposed", "myth", "proven", "strategy"
]


def keyword_score(text: str) -> float:
    """
    Score a piece of text based on the presence of viral power words.

    Args:
        text: The text to score.

    Returns:
        A float in [0.0, 1.0]. Each matched power word contributes 0.15,
        capped at 1.0.
    """
    lowered = text.lower()
    count = sum(1 for word in POWER_WORDS if word in lowered)
    return min(1.0, count * 0.15)


def score_segments(segments: list[dict]) -> list[dict]:
    """
    Annotate each segment with a keyword virality score.

    Args:
        segments: List of segment dicts containing at least a "text" key.

    Returns:
        The same list with a "keyword_score" (float) field added to each dict.
    """
    for segment in segments:
        segment["keyword_score"] = keyword_score(segment["text"])
    return segments
