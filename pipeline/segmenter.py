def segment_transcript(transcript: list, chunk_duration: float = 25.0) -> list:
    if not transcript:
        return []
    chunks = []
    current = []
    for seg in transcript:
        current.append(seg)
        duration = current[-1]["end"] - current[0]["start"]
        if duration >= chunk_duration:
            chunks.append({
                "start": current[0]["start"],
                "end": current[-1]["end"],
                "text": " ".join(s["text"] for s in current),
                "segment_index": len(chunks)
            })
            current = []
    if current:
        chunks.append({
            "start": current[0]["start"],
            "end": current[-1]["end"],
            "text": " ".join(s["text"] for s in current),
            "segment_index": len(chunks)
        })
    print(f"Segmented into {len(chunks)} chunks")
    return chunks
