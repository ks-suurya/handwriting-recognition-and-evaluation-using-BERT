import google.generativeai as genai
from flask import current_app

class GeminiService:
    def __init__(self):
        try:
            genai.configure(api_key=current_app.config['GEMINI_API_KEY'])
            self.model = genai.GenerativeModel("gemini-pro")
        except Exception as e:
            print(f"Failed to initialize Gemini AI: {e}")
            self.model = None

    def correct_ocr_text(self, text):
        if not self.model or not text:
            return text
        try:
            prompt = f"Correct any OCR or spelling errors in the following handwritten text. Only return the corrected text, nothing else:\n\n'{text}'"
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini correction failed: {e}")
            return text

    def evaluate_texts(self, ground_truth, recognized_text):
        if not self.model:
            return "Gemini model not available for evaluation."
        try:
            prompt = (
                f"Compare the following two texts and provide a brief evaluation.\n\n"
                f"Ground Truth: '{ground_truth}'\n"
                f"Recognized Text: '{recognized_text}'"
            )
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini evaluation failed: {e}")
            return "Evaluation failed due to an error."
