# ⚡ ClipForge — AI Viral Clip Engine

> Turn hours of long-form video into viral 60-second clips — automatically.

![ClipForge Demo](https://img.shields.io/badge/Status-Live-brightgreen) ![Python](https://img.shields.io/badge/Python-3.10+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green) ![License](https://img.shields.io/badge/License-MIT-purple)

## 🎬 Demo Video
> 📹 **[Watch Live Demo on Google Drive](https://drive.google.com/file/d/1-lEvp3iOpVkgd_dgc-nZzt5WlE9QdKq-/view?usp=drive_link)**

---

## 🚀 What is ClipForge?

ClipForge is an AI-powered Automated Content Repurposing Engine built for the AttentionX AI Hackathon by UnsaidTalks.

It takes long-form videos (lectures, podcasts, workshops) and automatically:
- 🔍 Detects emotional peaks using audio energy analysis
- 🧠 Scores virality potential using NLP keyword detection
- ✂️ Extracts top 3–5 short clips using FFmpeg precision cutting
- 💬 Displays why each clip was selected with transparent scoring
- 📱 Outputs download-ready short-form video clips

---

## 🧠 Innovation: Dual-Signal Viral Scoring

ClipForge uses a proprietary dual-signal scoring algorithm:

Viral Score = (Audio Energy Score × 0.5) + (Keyword Score × 0.5)

| Signal | Method | Weight |
|--------|--------|--------|
| 🔊 Audio Energy | Librosa RMS loudness per segment | 50% |
| 💬 Power Keywords | NLP keyword matching (27 trigger words) | 50% |

---

## 🏗️ Architecture

Input Video → Audio Extractor (MoviePy) → Whisper STT → Segmenter → Dual Scorer → Ranker → FFmpeg Extractor → Output Clips

---

## 📁 Project Structure

clipforge/
├── main.py
├── pipeline/
│   ├── audio_extractor.py
│   ├── transcribe.py
│   ├── segmenter.py
│   ├── scorer.py
│   ├── energy.py
│   ├── ranker.py
│   └── extractor.py
├── static/
│   └── index.html
├── uploads/
├── outputs/
├── .env
└── requirements.txt

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + Uvicorn |
| Speech-to-Text | OpenAI Whisper (local) |
| Audio Analysis | Librosa |
| Video Processing | MoviePy + FFmpeg |
| Frontend | Vanilla HTML/CSS/JS |

---

## 🛠️ Setup & Run

1. Clone the repo:
git clone https://github.com/YOUR_USERNAME/clipforge.git
cd clipforge

2. Install dependencies:
pip install -r requirements.txt

3. Run the server:
uvicorn main:app --reload --host 0.0.0.0 --port 8000

4. Open browser:
http://localhost:8000

---

## 🎯 How to Use

1. Upload — Drag and drop any long-form video
2. Process — ClipForge analyzes and scores every segment
3. Download — Get your top viral clips ready to post

---

## 📊 Evaluation Alignment

| Criteria | How ClipForge Addresses It |
|---------|---------------------------|
| 🎯 Impact (20%) | Produces 3–5 real downloadable viral clips |
| 💡 Innovation (20%) | Dual-signal scoring: audio energy + NLP keywords |
| ⚙️ Technical Execution (20%) | Modular pipeline, clean code, structured folders |
| 🖥️ User Experience (25%) | Dark UI, drag-drop, progress steps, why-selected cards |
| 🎬 Presentation (15%) | Live demo video, clear README, step-by-step flow |

---

## 🔭 Future Scope

| Feature | Description |
|---------|-------------|
| 📐 Smart Vertical Crop | MediaPipe face tracking for 9:16 auto-crop |
| 💬 Karaoke Captions | Word-level timed subtitle overlays via FFmpeg |
| 🎣 Hook Headlines | GPT-generated scroll-stopping title overlays |
| 😊 Emotion Detection | Facial expression analysis for peak moments |
| 📤 Direct Publishing | TikTok / Reels / YouTube Shorts API integration |

---

## 👨‍💻 Built By

Built solo in 6 hours for the AttentionX AI Hackathon by UnsaidTalks.

---

## 📄 License

MIT License