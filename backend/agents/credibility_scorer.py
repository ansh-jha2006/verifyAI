import google.generativeai as genai
import json
import os
import re

class CredibilityScorer:
    """Scores overall credibility and assigns per-claim verdicts."""

    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def score(self, claims: list, cross_references: list, sources: list, language_instruction: str) -> dict:
        xref_text = json.dumps(cross_references, indent=2)
        avg_source_credibility = (
            sum(s.credibility_score for s in sources) / len(sources)
            if sources else 0.3
        )

        prompt = f"""
{language_instruction}

You are an expert fact-checker. Based on the cross-reference analysis, provide final verdicts.

CROSS-REFERENCE RESULTS:
{xref_text}

Average source credibility score: {avg_source_credibility:.2f} (0=unreliable, 1=highly credible)

Assign verdicts. Use exactly these verdict labels:
- TRUE (claim is verified accurate)
- FALSE (claim is demonstrably false)
- MISLEADING (contains truth but is framed deceptively)
- PARTIALLY_TRUE (some parts true, some false)
- UNVERIFIABLE (not enough evidence either way)

Respond ONLY with valid JSON:
{{
  "overall_verdict": "TRUE|FALSE|MISLEADING|PARTIALLY_TRUE|UNVERIFIABLE",
  "confidence_score": 0.0-1.0,
  "verdict_summary": "2-3 sentence explanation of the overall verdict",
  "per_claim_verdicts": [
    {{"claim_text": "...", "verdict": "...", "confidence": 0.0-1.0, "evidence": ["..."]}}
  ],
  "timeline": [
    {{"step": 1, "action": "Claim extracted", "detail": "..."}},
    {{"step": 2, "action": "Web search performed", "detail": "X sources found"}},
    {{"step": 3, "action": "Cross-referenced", "detail": "..."}},
    {{"step": 4, "action": "Verdict assigned", "detail": "..."}}
  ]
}}
"""
        response = self.model.generate_content(prompt)
        raw = response.text.strip()
        
        # Robust JSON extraction
        json_match = re.search(r'\{.*\}', raw, re.DOTALL)
        if json_match:
            raw = json_match.group(0)
            
        try:
            return json.loads(raw)
        except:
            return {
                "overall_verdict": "UNVERIFIABLE",
                "confidence_score": 0.3,
                "verdict_summary": "Unable to determine verdict due to processing error.",
                "per_claim_verdicts": [],
                "timeline": [],
            }