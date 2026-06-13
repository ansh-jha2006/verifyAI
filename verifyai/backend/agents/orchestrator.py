import asyncio
from typing import AsyncGenerator
import json

from agents.language_agent import LanguageAgent
from agents.claim_extractor import ClaimExtractor
from agents.search_agent import SearchAgent
from agents.cross_reference_agent import CrossReferenceAgent
from agents.credibility_scorer import CredibilityScorer
from agents.verdict_agent import VerdictAgent
from utils.whatsapp_cleaner import detect_whatsapp_forward, clean_whatsapp_text
from utils.verdict_card_generator import generate_card_data
from models.schemas import InvestigationResult, Claim, VerdictEnum, Source

class InvestigationOrchestrator:
    """
    Master orchestrator. Runs all agents in sequence and streams SSE events
    so the frontend can show live agent trace.
    """

    def __init__(self):
        self.language_agent = LanguageAgent()
        self.claim_extractor = ClaimExtractor()
        self.search_agent = SearchAgent()
        self.cross_reference_agent = CrossReferenceAgent()
        self.credibility_scorer = CredibilityScorer()
        self.verdict_agent = VerdictAgent()

    def _sse_event(self, agent: str, status: str, message: str, data: dict = None) -> str:
        payload = {"agent": agent, "status": status, "message": message, "data": data or {}}
        return f"data: {json.dumps(payload)}\n\n"

    async def investigate(self, text: str) -> AsyncGenerator[str, None]:
        # Step 1: WhatsApp Detection
        yield self._sse_event("WhatsApp Detector", "thinking", "Checking if this is a WhatsApp forward...")
        await asyncio.sleep(0.3)
        is_whatsapp, signals = detect_whatsapp_forward(text)
        cleaned_text = clean_whatsapp_text(text)
        yield self._sse_event(
            "WhatsApp Detector", "done",
            f"{'⚠️ WhatsApp forward detected!' if is_whatsapp else '✓ Not a WhatsApp forward'} Cleaned text extracted.",
            {"is_whatsapp": is_whatsapp, "signals": signals, "cleaned_text": cleaned_text}
        )

        # Step 2: Language Detection
        yield self._sse_event("Language Agent", "thinking", "Detecting language of the claim...")
        await asyncio.sleep(0.3)
        lang_info = self.language_agent.analyze(cleaned_text)
        yield self._sse_event(
            "Language Agent", "done",
            f"🌐 Language detected: {lang_info['name']} ({lang_info['native']}). Agent switching to {lang_info['name']} mode.",
            {"language_code": lang_info["code"], "language_name": lang_info["name"], "native": lang_info["native"]}
        )
        lang_instruction = lang_info["gemini_instruction"]

        # Step 3: Claim Extraction
        yield self._sse_event("Claim Extractor", "thinking", f"Extracting verifiable claims in {lang_info['name']}...")
        await asyncio.sleep(0.5)
        raw_claims = self.claim_extractor.extract(cleaned_text, lang_instruction)
        yield self._sse_event(
            "Claim Extractor", "done",
            f"🔍 Found {len(raw_claims)} main claim(s) with sub-claims decomposed.",
            {"claims": raw_claims}
        )

        # Step 4: Web Search
        yield self._sse_event("Search Agent", "thinking", "Searching the web for evidence...")
        await asyncio.sleep(0.5)
        sources = await self.search_agent.search_for_claims(raw_claims)
        yield self._sse_event(
            "Search Agent", "done",
            f"🌍 Found {len(sources)} source(s) across credible and low-credibility domains.",
            {"source_count": len(sources), "sources": [{"domain": s.domain, "title": s.title, "credibility_score": s.credibility_score} for s in sources]}
        )

        # Step 5: Cross-Reference
        yield self._sse_event("Cross-Reference Agent", "thinking", "Cross-referencing claims against sources...")
        await asyncio.sleep(0.5)
        cross_refs = self.cross_reference_agent.cross_reference(raw_claims, sources, lang_instruction)
        yield self._sse_event(
            "Cross-Reference Agent", "done",
            f"⚡ Cross-referenced {len(cross_refs)} claim(s) against {len(sources)} source(s).",
            {"cross_references": cross_refs}
        )

        # Step 6: Credibility Scoring
        yield self._sse_event("Credibility Scorer", "thinking", "Scoring credibility and assigning verdicts...")
        await asyncio.sleep(0.5)
        scoring_result = self.credibility_scorer.score(raw_claims, cross_refs, sources, lang_instruction)
        yield self._sse_event(
            "Credibility Scorer", "done",
            f"📊 Verdict: {scoring_result.get('overall_verdict')} with {scoring_result.get('confidence_score', 0)*100:.0f}% confidence.",
            {"verdict": scoring_result.get("overall_verdict"), "confidence": scoring_result.get("confidence_score")}
        )

        # Step 7: Final Verdict
        yield self._sse_event("Verdict Agent", "thinking", f"Writing final verdict in {lang_info['name']}...")
        await asyncio.sleep(0.5)
        final_summary = self.verdict_agent.summarize(scoring_result, cleaned_text, lang_instruction)
        scoring_result["verdict_summary"] = final_summary
        yield self._sse_event("Verdict Agent", "done", "✅ Investigation complete.", {})

        # Build full result
        claims_out = []
        per_claim = {c.get("claim_text", ""): c for c in scoring_result.get("per_claim_verdicts", [])}
        for rc in raw_claims:
            pcv = per_claim.get(rc.get("text", ""), {})
            sub = [Claim(id=sc["id"], text=sc["text"]) for sc in rc.get("sub_claims", [])]
            v = pcv.get("verdict", "UNVERIFIABLE")
            try:
                verdict_enum = VerdictEnum(v)
            except:
                verdict_enum = VerdictEnum.UNVERIFIABLE
            claims_out.append(Claim(
                id=rc.get("id", "c1"),
                text=rc.get("text", ""),
                sub_claims=sub,
                verdict=verdict_enum,
                confidence=pcv.get("confidence", 0.5),
                evidence=pcv.get("evidence", []),
            ))

        try:
            overall_verdict = VerdictEnum(scoring_result.get("overall_verdict", "UNVERIFIABLE"))
        except:
            overall_verdict = VerdictEnum.UNVERIFIABLE

        result = InvestigationResult(
            original_text=text,
            cleaned_text=cleaned_text,
            detected_language=lang_info["name"],
            language_name=lang_info["name"],
            claims=claims_out,
            sources=sources,
            overall_verdict=overall_verdict,
            confidence_score=scoring_result.get("confidence_score", 0.5),
            verdict_summary=final_summary,
            timeline=scoring_result.get("timeline", []),
            is_whatsapp_forward=is_whatsapp,
            shareable_card_data={},
        )
        result.shareable_card_data = generate_card_data(result)

        yield self._sse_event(
            "COMPLETE", "done", "Investigation finished",
            {"result": result.model_dump(mode="json")}
        )