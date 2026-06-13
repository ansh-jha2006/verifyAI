from models.schemas import InvestigationResult

VERDICT_COLORS = {
    "TRUE": "#22c55e",
    "FALSE": "#ef4444",
    "MISLEADING": "#f97316",
    "PARTIALLY_TRUE": "#eab308",
    "UNVERIFIABLE": "#6b7280",
}

VERDICT_ICONS = {
    "TRUE": "✅",
    "FALSE": "❌",
    "MISLEADING": "⚠️",
    "PARTIALLY_TRUE": "🔶",
    "UNVERIFIABLE": "❓",
}

def generate_card_data(result: InvestigationResult) -> dict:
    """Generate data for the shareable verdict card image."""
    verdict = result.overall_verdict.value
    return {
        "verdict": verdict,
        "verdict_label": verdict.replace("_", " "),
        "color": VERDICT_COLORS.get(verdict, "#6b7280"),
        "icon": VERDICT_ICONS.get(verdict, "❓"),
        "confidence": round(result.confidence_score * 100),
        "summary": result.verdict_summary[:200],
        "language": result.language_name,
        "claim_count": len(result.claims),
        "source_count": len(result.sources),
        "watermark": "Verified by VerifyAI · verifyai.app",
        "share_text": f"{VERDICT_ICONS.get(verdict)} This claim is {verdict.replace('_', ' ')} — Verified by VerifyAI with {round(result.confidence_score * 100)}% confidence. #VerifyAI #StopMisinformation",
    }