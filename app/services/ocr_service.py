import cv2
import numpy as np
import re
from flask import current_app
from htr_pipeline import read_page, DetectorConfig, LineClusteringConfig, ReaderConfig, PrefixTree
from app.services.gemini_service import GeminiService


class OCRService:
    def __init__(self):
        """
        Initializes the OCR service, loading the word list for the prefix tree.
        """
        self.gemini_service = GeminiService()
        try:
            with open(current_app.config['WORDS_PATH']) as f:
                word_list = [w.strip().upper() for w in f.readlines()]
            self.prefix_tree = PrefixTree(word_list)
        except Exception as e:
            print(f"Could not load words_alpha.txt: {e}")
            self.prefix_tree = None

    def process_image(self, image_path):
        """
        Processes a single image file to extract and correct handwritten text,
        attempting to segment answers by identifying question numbers.

        :param image_path: The local path to the image file to process.
        :return: A dictionary containing the processing results.
        """
        try:
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                raise FileNotFoundError(f"Image not found at path: {image_path}")

            # Use the HTR pipeline to read all text from the page
            read_lines = read_page(
                img,
                detector_config=DetectorConfig(),
                line_clustering_config=LineClusteringConfig(min_words_per_line=1),
                reader_config=ReaderConfig(decoder='best_path', prefix_tree=self.prefix_tree)
            )

            full_text = '\\n'.join([' '.join([word.text for word in line]) for line in read_lines])

            # This regex looks for patterns like "1.", "2a)", "3 b.", etc., at the start of a line.
            question_pattern = re.compile(r'^\s*(\d+\s*[a-zA-Z]?\s*[.)])', re.MULTILINE)

            # Split the text by the found patterns
            split_text = question_pattern.split(full_text)

            questions = []
            # The split results in [text_before, q1_marker, q1_text, q2_marker, q2_text, ...]
            # We iterate through the markers and their corresponding text.
            i = 1
            while i < len(split_text):
                question_id = re.sub(r'[^0-9a-zA-Z]', '', split_text[i])  # Clean up the ID
                recognized_text = split_text[i + 1].strip() if (i + 1) < len(split_text) else ""

                if recognized_text:
                    corrected_text = self.gemini_service.correct_ocr_text(recognized_text)
                    questions.append({
                        'question_id': question_id,
                        'recognized_text': recognized_text,
                        'corrected_text': corrected_text,
                        'word_count': len(recognized_text.split())
                    })
                i += 2

            # If no patterns were found, treat the whole text as one answer for "Q1"
            if not questions and full_text.strip():
                corrected_text = self.gemini_service.correct_ocr_text(full_text.strip())
                questions.append({
                    'question_id': '1',  # Default question ID
                    'recognized_text': full_text.strip(),
                    'corrected_text': corrected_text,
                    'word_count': len(full_text.strip().split())
                })

            return {
                'success': True,
                'total_questions': len(questions),
                'questions': questions
            }
        except Exception as e:
            print(f"Error in OCRService process_image: {e}")
            return {'success': False, 'error': str(e)}
