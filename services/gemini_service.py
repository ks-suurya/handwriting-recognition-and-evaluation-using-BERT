import google.generativeai as genai
from flask import current_app
import logging

logger = logging.getLogger(__name__)


class GeminiService:
    def __init__(self):
        self.model = None
        self._initialize_model()

    def _initialize_model(self):
        """Initialize Gemini AI model."""
        try:
            api_key = current_app.config.get('GEMINI_API_KEY')
            if not api_key:
                logger.warning("GEMINI_API_KEY not found in config")
                return

            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-pro")
            logger.info("Gemini AI model initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Gemini AI: {str(e)}")

    def correct_text(self, text):
        """Use Gemini AI to correct OCR text predictions."""
        if not self.model:
            logger.warning("Gemini model not available, returning original text")
            return text

        try:
            prompt = f"Correct any OCR errors in this text. Return only the corrected text without explanations:\n{text}"
            response = self.model.generate_content(prompt)

            if response and response.text:
                corrected_text = response.text.strip()
                logger.info(f"Text correction successful")
                return corrected_text
            else:
                logger.warning("Empty response from Gemini AI")
                return text

        except Exception as e:
            logger.error(f"Gemini AI correction failed: {str(e)}")
            return text

    def is_available(self):
        """Check if Gemini service is available."""
        return self.model is not None