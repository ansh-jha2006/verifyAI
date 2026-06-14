import re
from typing import Tuple

WHATSAPP_PATTERNS = [
    r'Forwarded many times',
    r'Forwarded\s+\d+\s+times?',
    r'^\[.*?\]\s*',           # [12/03/24, 10:23 AM]
    r'~\s*\w+',               # ~ ContactName
    r'👆👆👆',
    r'Share करो|Forward करो|शेयर करो',
    r'Please share|Pls share|Do share|Must share',
    r'Copy paste|Copy karo',
    r'viral karo|viral करो',
    r'\bFWD\b|\bFwd\b',
    r'‼️|‼|🚨|⚠️',
]

def detect_whatsapp_forward(text: str) -> Tuple[bool, list]:
    """Detect if text looks like a WhatsApp forward and return signals found."""
    signals = []
    for pattern in WHATSAPP_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
            signals.append(pattern)
    is_forward = len(signals) >= 1
    return is_forward, signals

def clean_whatsapp_text(text: str) -> str:
    """Strip WhatsApp metadata and noise from forwarded messages."""
    cleaned = text
    # Apply patterns one by one
    for pattern in WHATSAPP_PATTERNS:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE | re.MULTILINE)
    
    # Remove excessive whitespace
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    cleaned = re.sub(r' +', ' ', cleaned)
    
    # Clean up each line but keep them if they have any content
    lines = cleaned.split('\n')
    filtered = [l.strip() for l in lines if l.strip()]
    
    return '\n'.join(filtered).strip()