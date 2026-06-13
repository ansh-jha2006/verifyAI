import google.generativeai as genai
import os

class VerdictAgent:
    """Produces the final human-readable summary in the detected language."""

    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def summarize(self, verdict_data: dict, original_text: str, language_instruction: str) -> str:
        prompt = f"""
{language_instruction}

You are writing the final public-facing verdict for a fact-check report.

Original claim: {original_text[:300]}
Verdict: {verdict_data.get('overall_verdict')}
Confidence: {verdict_data.get('confidence_score', 0) * 100:.0f}%
Analysis: {verdict_data.get('verdict_summary', '')}

Write a clear, 3-4 sentence verdict explanation that:
1. States the verdict plainly
2. Explains WHY in simple terms anyone can understand
3. Mentions what evidence was found
4. Gives practical advice (e.g., "Do not share this forward")

Write ONLY in the language specified. Be direct and clear.
"""
        response = self.model.generate_content(prompt)
        return response.text.strip()