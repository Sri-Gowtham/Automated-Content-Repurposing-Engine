import os
import ffmpeg

def extract_clips(video_path: str, segments: list, output_dir: str = "outputs") -> list:
    os.makedirs(output_dir, exist_ok=True)
    top = [s for s in segments if s.get("is_top")]
    results = []
    try:
        probe = ffmpeg.probe(video_path)
        duration = float(probe["format"]["duration"])
    except Exception:
        duration = 99999.0
    for seg in top:
        try:
            start = max(0.0, seg["start"] - 1.0)
            end = min(duration, seg["end"] + 1.0)
            out_path = os.path.join(output_dir, f"clip_{seg['rank']}.mp4")
            (
                ffmpeg
                .input(video_path, ss=start, to=end)
                .output(out_path, vcodec="libx264", acodec="aac", movflags="faststart")
                .overwrite_output()
                .run(quiet=True)
            )
            seg["clip_path"] = out_path
            print(f"Extracted clip_{seg['rank']}.mp4")
            results.append(seg)
        except Exception as e:
            print(f"Clip {seg['rank']} failed: {e}")
    return results
