def segment_transcript(transcript: list[dict], chunk_duration: float = 30.0) -> list[dict]:
    """
    Group consecutive whisper transcript segments into time-bounded chunks.

    Args:
        transcript:     List of segment dicts with "start", "end", and "text" keys.
        chunk_duration: Maximum duration (in seconds) for each chunk. Defaults to 30.0.

    Returns:
        A list of chunk dicts, each containing:
            - "start"         (float): Start time of the first segment in the chunk.
            - "end"           (float): End time of the last segment in the chunk.
            - "text"          (str):   Joined text of all segments in the chunk.
            - "segment_index" (int):   Zero-based index of the chunk.
    """
    chunks: list[dict] = []
    current_segments: list[dict] = []

    for segment in transcript:
        if not current_segments:
            current_segments.append(segment)
            continue

        chunk_start = current_segments[0]["start"]
        projected_end = segment["end"]

        if (projected_end - chunk_start) <= chunk_duration:
            current_segments.append(segment)
        else:
            chunks.append({
                "start":         float(current_segments[0]["start"]),
                "end":           float(current_segments[-1]["end"]),
                "text":          " ".join(s["text"] for s in current_segments),
                "segment_index": len(chunks),
            })
            current_segments = [segment]

    if current_segments:
        chunks.append({
            "start":         float(current_segments[0]["start"]),
            "end":           float(current_segments[-1]["end"]),
            "text":          " ".join(s["text"] for s in current_segments),
            "segment_index": len(chunks),
        })

    print(f"Segmented into {len(chunks)} chunks")
    return chunks
