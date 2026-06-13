import google.generativeai as genai
import json
import os
import re
import uuid

class ClaimExtractor:
    """Breaks the input text into atomic, verifiable claims and sub-claims (decomposition tree)."""

    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def extract(self, text: str, language_instruction: str) -> list:
        prompt = f"""
{language_instruction}

Analyze this text and extract all factual claims that can be verified.
For each main claim, also extract 2-3 specific sub-claims (concrete facts within it).

Text to analyze:
\"\"\"
{text}
\"\"\"

Respond ONLY with valid JSON in this exact format:
{{
  "claims": [
    {{
      "id": "c1",
      "text": "Main claim text here",
      "sub_claims": [
        {{"id": "c1a", "text": "Specific sub-claim 1"}},
        {{"id": "c1b", "text": "Specific sub-claim 2"}}
      ]
    }}
  ]
}}

Extract between 1 and 5 main claims. Be precise and factual. Do not invent claims not present in the text.
"""
        response = self.model.generate_content(prompt)
        raw = response.text.strip()
        # Strip markdown code fences if present
        raw = re.sub(r'^```json\s*', '', raw)
        raw = re.sub(r'\s*```$', '', raw)
        try:
            data = json.loads(raw)
            return data.get("claims", [])
        except json.JSONDecodeError:
            return [{"id": "c1", "text": text[:300], "sub_claims": []}]