import base64
import google.generativeai as genai
import os
from PIL import Image
import io

def extract_text_from_image(image_base64: str, api_key: str) -> str:
    """Use Gemini Vision to extract text from an uploaded image (screenshot, meme, etc.)."""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    image_data = base64.b64decode(image_base64)
    image = Image.open(io.BytesIO(image_data))

    response = model.generate_content([
        "Extract ALL text from this image exactly as it appears. Include text in any language. "
        "If this is a WhatsApp screenshot, include all message text. "
        "Output only the extracted text, nothing else.",
        image
    ])
    return response.text.strip()