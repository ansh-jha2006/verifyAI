import os
import sys

# Add the current directory to sys.path for robust import resolution
# This helps editors like VS Code/Cursor find nested modules in the 'backend' folder
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from dotenv import load_dotenv
import base64
import asyncio
import json

load_dotenv()

from agents.orchestrator import InvestigationOrchestrator
from utils.image_extractor import extract_text_from_image
from utils.url_scraper import scrape_url_content

app = FastAPI(title="VerifyAI Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:8501"), "*"],
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
            yield {"data": json.dumps(event)}
    return EventSourceResponse(generator())


@app.post("/investigate/url")
async def investigate_url(url: str = Form(...)):
    """Scrape content from a URL then stream investigation."""
    async def generator():
        # Move blocking call inside the generator
        loop = asyncio.get_event_loop()
        extracted_text = await loop.run_in_executor(None, scrape_url_content, url)
        
        if extracted_text.startswith("Error scraping URL"):
            yield {
                "data": json.dumps({'agent': 'URL Scraper', 'status': 'error', 'message': extracted_text})
            }
            return

        yield {
            "data": json.dumps({'agent': 'URL Scraper', 'status': 'done', 'message': f'Extracted content from URL: {extracted_text[:80]}...', 'data': {'extracted_text': extracted_text}})
        }
        
        async for event in orchestrator.investigate(extracted_text):
            yield {"data": json.dumps(event)}

    return EventSourceResponse(generator())


@app.post("/investigate/image")
async def investigate_image(file: UploadFile = File(...)):
    """Extract text from uploaded image then stream investigation."""
    contents = await file.read()
    image_b64 = base64.b64encode(contents).decode()

    async def generator():
        api_key = os.getenv("GEMINI_API_KEY")
        loop = asyncio.get_event_loop()
        
        try:
            extracted_text = await loop.run_in_executor(None, extract_text_from_image, image_b64, api_key)
        except Exception as e:
            yield {
                "data": json.dumps({'agent': 'Image Extractor', 'status': 'error', 'message': f'Error extracting text: {str(e)}'})
            }
            return

        yield {
            "data": json.dumps({'agent': 'Image Extractor', 'status': 'done', 'message': f'Extracted text from image: {extracted_text[:80]}...', 'data': {'extracted_text': extracted_text}})
        }
        
        async for event in orchestrator.investigate(extracted_text):
            yield {"data": json.dumps(event)}

    return EventSourceResponse(generator())
