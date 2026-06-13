import google.generativeai as genai
import json
import os
import re

class CrossReferenceAgent:
    """Cross-references claims against found sources to find confirmations and contradictions."""

    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def cross_reference(self, claims: list, sources: list, language_instruction: str) -> list:
        sources_text = "\n".join([
            f"- [{s.domain}] {s.title}: {s.snippet}"
            for s in sources[:8]
        ])

        claims_text = "\n".join([f"- {c.get('text', '')}" for c in claims])

        prompt = f"""
{language_instruction}

You are a fact-checker. Cross-reference these claims against the provided sources.

CLAIMS:
{claims_text}

SOURCES FOUND:
{sources_text}

For each claim, determine:
1. Is it supported, contradicted, or unverifiable based on the sources?
2. Which source(s) support or contradict it?

Respond ONLY with valid JSON:
{{
  "cross_references": [
    {{
      "claim_text": "...",
      "status": "SUPPORTED" | "CONTRADICTED" | "UNVERIFIABLE" | "PARTIALLY_SUPPORTED",
      "evidence": ["source snippet or quote that supports/contradicts"],
      "supporting_domains": ["domain1.com"]
    }}
  ]
}}
"""
        response = self.model.generate_content(prompt)
        raw = response.text.strip()
        raw = re.sub(r'^```json\s*', '', raw)
        raw = re.sub(r'\s*```$', '', raw)
        try:
            return json.loads(raw).get("cross_references", [])
        except:
            return []