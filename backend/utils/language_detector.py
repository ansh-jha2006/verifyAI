from langdetect import detect, LangDetectException

LANGUAGE_MAP = {
    'hi': {'name': 'Hindi', 'native': 'हिन्दी', 'gemini_instruction': 'Respond entirely in Hindi (Devanagari script). All analysis, verdicts, and explanations must be in Hindi.'},
    'ta': {'name': 'Tamil', 'native': 'தமிழ்', 'gemini_instruction': 'Respond entirely in Tamil script. All analysis, verdicts, and explanations must be in Tamil.'},
    'te': {'name': 'Telugu', 'native': 'తెలుగు', 'gemini_instruction': 'Respond entirely in Telugu script. All analysis, verdicts, and explanations must be in Telugu.'},
    'bn': {'name': 'Bengali', 'native': 'বাংলা', 'gemini_instruction': 'Respond entirely in Bengali (Bangla) script. All analysis, verdicts, and explanations must be in Bengali.'},
    'mr': {'name': 'Marathi', 'native': 'मराठी', 'gemini_instruction': 'Respond entirely in Marathi (Devanagari script). All analysis, verdicts, and explanations must be in Marathi.'},
    'gu': {'name': 'Gujarati', 'native': 'ગુજરાતી', 'gemini_instruction': 'Respond entirely in Gujarati script. All analysis, verdicts, and explanations must be in Gujarati.'},
    'kn': {'name': 'Kannada', 'native': 'ಕನ್ನಡ', 'gemini_instruction': 'Respond entirely in Kannada script. All analysis, verdicts, and explanations must be in Kannada.'},
    'ml': {'name': 'Malayalam', 'native': 'മലയാളം', 'gemini_instruction': 'Respond entirely in Malayalam script. All analysis, verdicts, and explanations must be in Malayalam.'},
    'ur': {'name': 'Urdu', 'native': 'اردو', 'gemini_instruction': 'Respond entirely in Urdu (Nastaliq script). All analysis, verdicts, and explanations must be in Urdu.'},
    'en': {'name': 'English', 'native': 'English', 'gemini_instruction': 'Respond in clear, professional English.'},
}

def detect_language(text: str) -> dict:
    """Detect language and return full language info dict."""
    try:
        code = detect(text)
        info = LANGUAGE_MAP.get(code, LANGUAGE_MAP['en'])
        return {'code': code, **info}
    except LangDetectException:
        return {'code': 'en', **LANGUAGE_MAP['en']}