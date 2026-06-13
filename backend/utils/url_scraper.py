import requests
from bs4 import BeautifulSoup
import re

def scrape_url_content(url: str) -> str:
    """
    Scrapes text content or social media metadata from a given URL.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Try to extract Social Media Metadata (Open Graph)
        # This is crucial for Instagram/Facebook/WhatsApp links where content is JS-rendered or hidden.
        og_description = soup.find("meta", property="og:description")
        og_title = soup.find("meta", property="og:title")
        
        social_text = ""
        if og_title:
            social_text += og_title["content"] + "\n"
        if og_description:
            social_text += og_description["content"]
            
        # If we found significant social media metadata, prioritize it
        if len(social_text) > 50 and any(domain in url.lower() for domain in ["instagram.com", "whatsapp.com", "facebook.com", "t.me", "x.com", "twitter.com"]):
            return social_text.strip()

        # 2. Fallback to general article scraping
        for script_or_style in soup(["script", "style", "nav", "footer", "header"]):
            script_or_style.decompose()
            
        text = soup.get_text(separator=' ')
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text[:4000]
    except Exception as e:
        return f"Error scraping URL: {str(e)}"
