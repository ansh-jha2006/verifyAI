import httpx
import os
from models.schemas import Source

KNOWN_CREDIBLE_DOMAINS = [
    "reuters.com", "apnews.com", "bbc.com", "bbc.co.uk", "theguardian.com",
    "ndtv.com", "thehindu.com", "hindustantimes.com", "indiatoday.in",
    "factcheck.org", "snopes.com", "altnews.in", "boomlive.in", "vishvasnews.com",
    "pib.gov.in", "who.int", "un.org", "nature.com", "science.org",
]

LOW_CREDIBILITY_DOMAINS = [
    "facebook.com", "whatsapp.com", "tiktok.com",
    "blogspot.com", "wordpress.com",
]

def score_domain(domain: str) -> float:
    domain_lower = domain.lower()
    for credible in KNOWN_CREDIBLE_DOMAINS:
        if credible in domain_lower:
            return 0.85 + (0.15 if "factcheck" in domain_lower or "snopes" in domain_lower or "altnews" in domain_lower or "boom" in domain_lower else 0.0)
    for low in LOW_CREDIBILITY_DOMAINS:
        if low in domain_lower:
            return 0.2
    if domain_lower.endswith(".gov") or domain_lower.endswith(".edu"):
        return 0.9
    return 0.5

class SearchAgent:
    """Searches the web for evidence related to each claim."""

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        self.engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        self.base_url = "https://www.googleapis.com/customsearch/v1"

    async def search(self, query: str, num_results: int = 5) -> list[Source]:
        params = {
            "key": self.api_key,
            "cx": self.engine_id,
            "q": query,
            "num": num_results,
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                resp = await client.get(self.base_url, params=params)
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                return []

        sources = []
        for item in data.get("items", []):
            domain = item.get("displayLink", "")
            sources.append(Source(
                url=item.get("link", ""),
                title=item.get("title", ""),
                snippet=item.get("snippet", ""),
                domain=domain,
                credibility_score=score_domain(domain),
            ))
        return sources

    async def search_for_claims(self, claims: list) -> list[Source]:
        all_sources = []
        seen_urls = set()
        for claim in claims[:3]:  # Limit to top 3 claims to avoid quota exhaustion
            query = claim.get("text", "")[:150]
            results = await self.search(query)
            for s in results:
                if s.url not in seen_urls:
                    all_sources.append(s)
                    seen_urls.add(s.url)
        return all_sources