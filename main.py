import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

from pipeline.audio_extractor import extract_audio
from pipeline.transcribe import transcribe_audio
from pipeline.segmenter import segment_transcript
from pipeline.scorer import score_segments
from pipeline.energy import compute_energy_scores
from pipeline.ranker import rank_segments
from pipeline.extractor import extract_clips

app = FastAPI(title="ClipForge")
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
    try:
        audio_path = extract_audio(video_path)
        transcript = transcribe_audio(audio_path, model_size="base")
        if not transcript:
            raise HTTPException(status_code=422, detail="Transcription failed — no speech detected")
        segments = segment_transcript(transcript, chunk_duration=25.0)
        segments = score_segments(segments)
        segments = compute_energy_scores(audio_path, segments)
        segments = rank_segments(segments, top_n=3)
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
                    "clip_url": f"/outputs/clip_{c['rank']}.mp4"
                }
                for c in top_clips
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
