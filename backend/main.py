from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from dotenv import load_dotenv
import os
import base64
import asyncio

load_dotenv()

from agents.orchestrator import InvestigationOrchestrator
from utils.image_extractor import extract_text_from_image
from utils.url_scraper import scrape_url_content

app = FastAPI(title="VerifyAI Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:5173"), "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = InvestigationOrchestrator()


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}


@app.post("/investigate/text")
async def investigate_text(text: str = Form(...)):
    """Stream investigation results for a text claim via SSE."""
    async def generator():
        async for event in orchestrator.investigate(text):
            yield event

    return StreamingResponse(
        generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        }
    )


@app.post("/investigate/url")
async def investigate_url(url: str = Form(...)):
    """Scrape content from a URL then stream investigation."""
    extracted_text = scrape_url_content(url)
    
    if extracted_text.startswith("Error scraping URL"):
        async def error_generator():
            import json
            yield f"data: {json.dumps({'agent': 'URL Scraper', 'status': 'error', 'message': extracted_text})}\n\n"
        return StreamingResponse(error_generator(), media_type="text/event-stream")

    async def generator():
        import json
        yield f"data: {json.dumps({'agent': 'URL Scraper', 'status': 'done', 'message': f'Extracted content from URL: {extracted_text[:80]}...', 'data': {'extracted_text': extracted_text}})}\n\n"
        async for event in orchestrator.investigate(extracted_text):
            yield event

    return StreamingResponse(
        generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        }
    )


@app.post("/investigate/image")
async def investigate_image(file: UploadFile = File(...)):
    """Extract text from uploaded image then stream investigation."""
    contents = await file.read()
    image_b64 = base64.b64encode(contents).decode()

    api_key = os.getenv("GEMINI_API_KEY")
    extracted_text = extract_text_from_image(image_b64, api_key)

    async def generator():
        import json
        yield f"data: {json.dumps({'agent': 'Image Extractor', 'status': 'done', 'message': f'Extracted text from image: {extracted_text[:80]}...', 'data': {'extracted_text': extracted_text}})}\n\n"
        async for event in orchestrator.investigate(extracted_text):
            yield event

    return StreamingResponse(
        generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        }
    )