from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import os, shutil
from dotenv import load_dotenv

load_dotenv()

from pipeline.audio_extractor import extract_audio
from pipeline.transcribe import transcribe_audio
from pipeline.segmenter import segment_transcript
from pipeline.scorer import score_segments
from pipeline.energy import compute_energy_scores
from pipeline.ranker import rank_segments
from pipeline.extractor import extract_clips

app = FastAPI(title="AttentionX")
os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")


@app.get("/")
def index():
    return FileResponse("static/index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    path = f"uploads/{file.filename}"
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"filename": file.filename, "path": path}


class ProcessRequest(BaseModel):
    filename: str


@app.post("/process")
def process(req: ProcessRequest):
    video_path = f"uploads/{req.filename}"
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video not found")

    # Step 1: Audio
    audio_path = extract_audio(video_path)

    # Step 2: Transcribe
    transcript = transcribe_audio(audio_path, model_size="base")
    if not transcript:
        raise HTTPException(status_code=422, detail="Transcription failed")

    # Step 3: Segment
    segments = segment_transcript(transcript, chunk_duration=45.0)

    # Step 4: Score
    segments = score_segments(segments)
    segments = compute_energy_scores(audio_path, segments)

    # Step 5: Rank
    segments = rank_segments(segments, top_n=5)

    # Step 6: Extract clips
    top_clips = extract_clips(video_path, segments, output_dir="outputs")

    return {
        "status": "done",
        "total_segments": len(segments),
        "clips": [
            {
                "rank": c["rank"],
                "start": round(c["start"], 2),
                "end": round(c["end"], 2),
                "text": c["text"][:160],
                "viral_score": round(c.get("viral_score", 0), 3),
                "energy_score": round(c.get("energy_score", 0), 3),
                "keyword_score": round(c.get("keyword_score", 0), 3),
                "clip_url": f"/outputs/clip_{c['rank']}.mp4",
            }
            for c in top_clips
        ],
    }
