def rank_segments(segments: list[dict], top_n: int = 5) -> list[dict]:
    """
    Score, rank, and tag transcript segments by viral potential.

    Args:
        segments: List of segment dicts, each with "keyword_score" and "energy_score".
        top_n:    Number of top segments to tag as viral candidates. Defaults to 5.

    Returns:
        The full list sorted by "viral_score" descending, with the following fields
        added to every segment:
            - "viral_score" (float): Weighted average of keyword and energy scores.
            - "is_top"      (bool):  True for the top_n highest-scoring segments.
            - "rank"        (int):   1-based rank for top segments; 0 for the rest.
    """
    # --- Compute viral score for every segment ---
    for segment in segments:
        segment["viral_score"] = (
            segment["keyword_score"] * 0.5
            + segment["energy_score"] * 0.5
        )

    # --- Sort descending by viral score ---
    segments.sort(key=lambda s: s["viral_score"], reverse=True)

    # --- Tag top_n segments with rank; mark the rest ---
    for i, segment in enumerate(segments):
        if i < top_n:
            segment["is_top"] = True
            segment["rank"]   = i + 1
        else:
            segment["is_top"] = False
            segment["rank"]   = 0

    print(f"Top {top_n} segments selected")
    return segments
