# VerifyAI — Autonomous Fake News Investigator

A multi-agent AI system that autonomously fact-checks claims using Gemini AI.
Built with **FastAPI + Python** backend and **Streamlit** frontend.

## Features
- 🔍 6 specialized autonomous agents
- 📱 WhatsApp forward detector & cleaner
- 🌐 Multilingual support (Hindi, Tamil, Telugu, Bengali, Marathi, etc.)
- 🌳 Claim decomposition tree
- 📊 Source credibility scoring
- 🖼️ Image/screenshot text extraction
- 📤 Shareable verdict cards
- ⚡ Live agent trace via SSE streaming

## Setup

### 1. Get API Keys
| Key | Where to get it |
|-----|----------------|
| Gemini API Key | https://aistudio.google.com/app/apikey |
| Google Search API Key | https://console.cloud.google.com/apis/credentials |
| Search Engine ID | https://programmablesearchengine.google.com |

### 2. Backend Setup
```bash
cd backend
cp .env.example .env
# Edit .env and fill in your 3 API keys

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
cd frontend_streamlit
pip install -r requirements.txt
streamlit run app.py --server.port 8501
```

### 4. Open in browser
Visit: http://localhost:8501

## Architecture
```
User Input (text/image)
    ↓
WhatsApp Detector → Language Agent → Claim Extractor
    ↓
Search Agent (Google Custom Search)
    ↓
Cross-Reference Agent → Credibility Scorer → Verdict Agent
    ↓
Streamed SSE events → Streamlit frontend (live agent trace)
```

## Agent Pipeline
1. **WhatsApp Detector** — Identifies & cleans forward noise
2. **Language Agent** — Detects language, switches entire agent system to that language
3. **Claim Extractor** — Breaks input into atomic verifiable claims + sub-claims
4. **Search Agent** — Queries Google Custom Search for each claim
5. **Cross-Reference Agent** — Matches claims vs sources (support/contradict)
6. **Credibility Scorer** — Assigns per-claim and overall verdicts with confidence
7. **Verdict Agent** — Generates final human-readable verdict in detected language
