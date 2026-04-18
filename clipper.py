"""
TASK 9 + 10 + 11 + 12: Clip Generation, Smart Crop, Captions, Hook Headline
Cuts clips with ffmpeg, detects face with mediapipe, overlays captions & hook.
"""
import os
import subprocess
import json
import textwrap
import cv2
import numpy as np

# Target: 9:16 vertical (1080x1920 for full HD, use 608x1080 for speed)
VERTICAL_W = 608
VERTICAL_H = 1080

# Lazy import mediapipe to avoid AttributeError on some installs
_mp_face_detection = None
def _get_face_detection_module():
    global _mp_face_detection
    if _mp_face_detection is None:
        try:
            import mediapipe as mp
            _mp_face_detection = mp.solutions.face_detection
        except Exception as e:
            print(f"[WARN] mediapipe face detection unavailable: {e}")
            _mp_face_detection = None
    return _mp_face_detection


# ─── TASK 9: Clip Generation ─────────────────────────────────────────────────

def cut_clip(video_path: str, start: float, end: float, output_path: str) -> str:
    """Cut a raw clip using ffmpeg (fast stream copy where possible)."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    duration = end - start
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start),
        "-i", video_path,
        "-t", str(duration),
        "-c:v", "libx264", "-crf", "23", "-preset", "fast",
        "-c:a", "aac",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg clip failed:\n{result.stderr}")
    return output_path


# ─── TASK 10: Smart Cropping (Face-centered vertical) ───────────────────────

def detect_face_center(frame: np.ndarray):
    """Detect face center in an OpenCV frame using mediapipe. Returns (cx, cy) or None."""
    mp_fd = _get_face_detection_module()
    if mp_fd is None:
        return None
    try:
        with mp_fd.FaceDetection(
            model_selection=0, min_detection_confidence=0.5
        ) as detector:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = detector.process(rgb)
            if results.detections:
                d = results.detections[0]
                bb = d.location_data.relative_bounding_box
                h, w = frame.shape[:2]
                cx = int((bb.xmin + bb.width / 2) * w)
                cy = int((bb.ymin + bb.height / 2) * h)
                return cx, cy
    except Exception as e:
        print(f"[WARN] face detection error: {e}")
    return None


def smart_crop_clip(input_path: str, output_path: str) -> str:
    """
    Convert 16:9 clip to 9:16 with face-centered cropping.
    Samples a few frames to find stable face center, then applies ffmpeg crop+scale.
    """
    cap = cv2.VideoCapture(input_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Sample up to 10 frames spread across the clip
    sample_indices = [int(total_frames * i / 10) for i in range(1, 11)]
    cx_values = []

    for idx in sample_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if not ret:
            continue
        result = detect_face_center(frame)
        if result:
            cx_values.append(result[0])

    cap.release()

    # Determine crop X center
    if cx_values:
        face_cx = int(np.median(cx_values))
    else:
        face_cx = width // 2  # fallback to center

    # Compute crop width for 9:16 from original height
    crop_w = int(height * 9 / 16)
    crop_w = min(crop_w, width)

    # Clamp X so crop stays within frame
    crop_x = face_cx - crop_w // 2
    crop_x = max(0, min(crop_x, width - crop_w))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-vf", f"crop={crop_w}:{height}:{crop_x}:0,scale={VERTICAL_W}:{VERTICAL_H}",
        "-c:v", "libx264", "-crf", "23", "-preset", "fast",
        "-c:a", "aac",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg smart crop failed:\n{result.stderr}")
    return output_path


# ─── TASK 11: Dynamic Captions ───────────────────────────────────────────────

def _wrap_text(text: str, max_chars: int = 32) -> list[str]:
    return textwrap.wrap(text, width=max_chars)


def add_captions(input_path: str, output_path: str,
                 segments: list, clip_start: float) -> str:
    """
    Burn subtitles onto the clip using ffmpeg drawtext filter.
    segments: list of {start, end, text} from Whisper (absolute timings).
    clip_start: start time of this clip in the original video.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Build a temporary SRT file
    srt_path = input_path.replace(".mp4", "_captions.srt")
    with open(srt_path, "w", encoding="utf-8") as f:
        idx = 1
        for seg in segments:
            local_start = seg["start"] - clip_start
            local_end = seg["end"] - clip_start
            if local_end <= 0 or local_start < 0:
                continue
            local_start = max(0.0, local_start)

            def fmt(t):
                h = int(t // 3600)
                m = int((t % 3600) // 60)
                s = int(t % 60)
                ms = int((t % 1) * 1000)
                return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

            f.write(f"{idx}\n{fmt(local_start)} --> {fmt(local_end)}\n{seg['text']}\n\n")
            idx += 1

    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-vf", (
            f"subtitles={srt_path}:force_style='"
            "FontName=Arial,FontSize=20,PrimaryColour=&H00FFFFFF,"
            "OutlineColour=&H00000000,BorderStyle=3,Outline=2,"
            "Shadow=1,Alignment=2,MarginV=40'"
        ),
        "-c:v", "libx264", "-crf", "23", "-preset", "fast",
        "-c:a", "aac",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Clean temp SRT
    try:
        os.remove(srt_path)
    except Exception:
        pass

    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg caption burn failed:\n{result.stderr}")

    return output_path


# ─── TASK 12: Hook Headline Generation ───────────────────────────────────────

HOOK_TEMPLATES = [
    "🔥 You NEED to see this",
    "💡 This changes EVERYTHING",
    "⚡ Nobody talks about this",
    "🚨 Most people get this WRONG",
    "🎯 The SECRET most miss",
]

KEYWORD_HOOKS = {
    "secret": "🔥 The SECRET revealed",
    "mistake": "🚨 Biggest MISTAKE people make",
    "shocking": "😱 This is SHOCKING",
    "important": "⚡ This is CRITICAL",
    "warning": "⚠️ IMPORTANT warning",
    "hack": "💡 Life-changing HACK",
    "trick": "🎯 Pro TRICK exposed",
}


def generate_hook(text: str) -> str:
    """Pick a hook headline based on viral keywords in the text."""
    lower = text.lower()
    for kw, hook in KEYWORD_HOOKS.items():
        if kw in lower:
            return hook
    # Pick based on hash for variety
    idx = hash(text[:20]) % len(HOOK_TEMPLATES)
    return HOOK_TEMPLATES[idx]


def overlay_hook(input_path: str, output_path: str, hook_text: str) -> str:
    """Overlay a hook headline for the first 2.5 seconds using ffmpeg drawtext."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Escape special chars for ffmpeg drawtext
    escaped = hook_text.replace("'", "\\'").replace(":", "\\:")

    vf = (
        f"drawtext=text='{escaped}':"
        "fontcolor=white:fontsize=36:borderw=3:bordercolor=black:"
        "x=(w-text_w)/2:y=h*0.08:"
        "enable='between(t,0,2.5)'"
    )
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-vf", vf,
        "-c:v", "libx264", "-crf", "23", "-preset", "fast",
        "-c:a", "aac",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg hook overlay failed:\n{result.stderr}")
    return output_path


# ─── Full clip pipeline ──────────────────────────────────────────────────────

def process_clip(
    video_path: str,
    chunk: dict,
    all_segments: list,
    output_dir: str,
    clip_index: int,
) -> dict:
    """
    Full pipeline for one chunk:
    1. Cut raw clip
    2. Smart crop to vertical
    3. Burn captions
    4. Overlay hook headline
    Returns dict with paths and metadata.
    """
    base = os.path.join(output_dir, f"clip_{clip_index:02d}")
    os.makedirs(base, exist_ok=True)

    raw_path = os.path.join(base, "raw.mp4")
    cropped_path = os.path.join(base, "cropped.mp4")
    captioned_path = os.path.join(base, "captioned.mp4")
    final_path = os.path.join(base, "final.mp4")

    # Step 1: cut
    cut_clip(video_path, chunk["start"], chunk["end"], raw_path)

    # Step 2: smart crop
    try:
        smart_crop_clip(raw_path, cropped_path)
    except Exception as e:
        print(f"[WARN] Smart crop failed for clip {clip_index}: {e}. Using raw.")
        cropped_path = raw_path

    # Step 3: captions — filter Whisper segs that overlap this chunk
    relevant_segs = [
        s for s in all_segments
        if s["end"] > chunk["start"] and s["start"] < chunk["end"]
    ]
    try:
        add_captions(cropped_path, captioned_path, relevant_segs, chunk["start"])
    except Exception as e:
        print(f"[WARN] Captions failed for clip {clip_index}: {e}. Skipping captions.")
        captioned_path = cropped_path

    # Step 4: hook headline
    hook = generate_hook(chunk["text"])
    try:
        overlay_hook(captioned_path, final_path, hook)
    except Exception as e:
        print(f"[WARN] Hook overlay failed for clip {clip_index}: {e}.")
        final_path = captioned_path

    return {
        "clip_index": clip_index,
        "start": chunk["start"],
        "end": chunk["end"],
        "duration": round(chunk["end"] - chunk["start"], 2),
        "score": chunk.get("score", 0),
        "hook": hook,
        "text_preview": chunk["text"][:120],
        "final_path": final_path,
        "relative_path": os.path.relpath(final_path, output_dir),
    }
