"""
Audio Renderer
===============
Generates audio files from text using Text-to-Speech.

Install: pip install gtts
Optional: pip install pyttsx3 (offline TTS)
"""


class AudioRenderer:
    """Renders text to audio files."""

    def render(self, filepath, text="", lang="en", slow=False, engine="gtts", **kwargs):
        """
        Generate audio from text.
        
        Args:
            filepath: Output path (.mp3)
            text: Text to convert to speech
            lang: Language code (default: en)
            slow: Speak slowly
            engine: "gtts" (online) or "pyttsx3" (offline)
        """
        if engine == "gtts":
            return self._render_gtts(filepath, text, lang, slow)
        elif engine == "pyttsx3":
            return self._render_pyttsx3(filepath, text)
        else:
            raise ValueError(f"Unknown TTS engine: {engine}")

    def _render_gtts(self, filepath, text, lang, slow):
        """Google Text-to-Speech (requires internet)."""
        try:
            from gtts import gTTS
        except ImportError:
            raise ImportError("Install gTTS: pip install gtts")

        tts = gTTS(text=text, lang=lang, slow=slow)
        tts.save(filepath)
        
        return {
            "renderer": "gtts",
            "lang": lang,
            "text_length": len(text),
            "word_count": len(text.split())
        }

    def _render_pyttsx3(self, filepath, text):
        """Offline TTS using pyttsx3."""
        try:
            import pyttsx3
        except ImportError:
            raise ImportError("Install pyttsx3: pip install pyttsx3")

        engine = pyttsx3.init()
        engine.save_to_file(text, filepath)
        engine.runAndWait()
        
        return {
            "renderer": "pyttsx3",
            "text_length": len(text),
            "word_count": len(text.split())
        }
