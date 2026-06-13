from utils.language_detector import detect_language

class LanguageAgent:
    """Detects the language of input and configures all downstream agents to respond in that language."""

    def analyze(self, text: str) -> dict:
        lang_info = detect_language(text)
        return {
            "code": lang_info["code"],
            "name": lang_info["name"],
            "native": lang_info["native"],
            "gemini_instruction": lang_info["gemini_instruction"],
        }