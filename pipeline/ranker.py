def rank_segments(segments: list, top_n: int = 5) -> list:
    for seg in segments:
        ks = seg.get("keyword_score", 0.0)
        es = seg.get("energy_score", 0.0)
        seg["viral_score"] = round((ks * 0.5) + (es * 0.5), 4)
    segments.sort(key=lambda x: x["viral_score"], reverse=True)
    for i, seg in enumerate(segments):
        if i < top_n:
            seg["is_top"] = True
            seg["rank"] = i + 1
        else:
            seg["is_top"] = False
    print(f"Top {top_n} segments selected")
    return segments
