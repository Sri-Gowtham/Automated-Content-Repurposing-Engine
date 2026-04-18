import os

import ffmpeg


def extract_clips(
    video_path: str,
    segments: list[dict],
    output_dir: str = "outputs",
) -> list[dict]:
    """
    Extract short video clips around the top-ranked segments using ffmpeg.

    Args:
        video_path: Path to the source video file.
        segments:   Full list of ranked segment dicts (as returned by rank_segments).
                    Only segments where "is_top" is True are processed.
        output_dir: Directory to write extracted clips into. Created if absent.

    Returns:
        List of top segments (is_top == True) with "clip_path" (str) added to
        each successfully extracted segment. Segments that fail ffmpeg extraction
        are still included in the return list but will not have "clip_path" set.
    """
    os.makedirs(output_dir, exist_ok=True)

    top_segments = [s for s in segments if s.get("is_top") is True]

    for segment in top_segments:
        start       = max(0.0, segment["start"] - 1.0)
        end         = segment["end"] + 1.0
        output_path = os.path.join(output_dir, f"clip_{segment['rank']}.mp4")

        try:
            stream = ffmpeg.input(video_path, ss=start, to=end)
            stream = ffmpeg.output(
                stream,
                output_path,
                vcodec="libx264",
                acodec="aac",
                movflags="faststart",
            )
            ffmpeg.run(stream, overwrite_output=True, quiet=True)

            segment["clip_path"] = output_path
            print(f"Extracted clip_{segment['rank']}.mp4")

        except ffmpeg.Error as e:
            print(f"[extract_clips] ffmpeg error on clip_{segment['rank']}: {e}")

    return top_segments
