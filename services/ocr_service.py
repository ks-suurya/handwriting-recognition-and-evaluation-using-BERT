import json
import cv2
import numpy as np
from pathlib import Path
from flask import current_app
from htr_pipeline import read_page, DetectorConfig, LineClusteringConfig, ReaderConfig, PrefixTree
from app.utils.image_processor import ImageProcessor
from app.services.gemini_service import GeminiService
import logging

logger = logging.getLogger(__name__)


class OCRService:
    def __init__(self):
        self.prefix_tree = None
        self.sample_config = None
        self.gemini_service = GeminiService()
        self._initialize()

    def _initialize(self):
        """Initialize OCR service with configuration and word list."""
        try:
            # Load configuration
            config_path = current_app.config['CONFIG_PATH']
            with open(config_path) as f:
                self.sample_config = json.load(f)

            # Load word list
            words_path = current_app.config['WORDS_PATH']
            with open(words_path) as f:
                word_list = [w.strip().upper() for w in f.readlines()]
            self.prefix_tree = PrefixTree(word_list)

            logger.info("OCR service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize OCR service: {str(e)}")
            raise

    def process_image(self, image_path):
        """Process image and extract text with AI correction."""
        try:
            # Preprocess image
            original_img, gray, binary, dilated = ImageProcessor.preprocess_image(image_path)

            # Find text regions
            text_regions = ImageProcessor.find_text_regions(dilated)

            segmented_texts = []

            for idx, (top, bottom) in enumerate(text_regions, start=1):
                # Extract segment
                segment = original_img[top:bottom, :]
                segment_gray = cv2.cvtColor(segment, cv2.COLOR_BGR2GRAY)

                # Detect words in segment
                word_boxes = ImageProcessor.detect_words(binary[top:bottom, :])

                # Apply HTR pipeline
                read_lines = read_page(
                    segment_gray,
                    DetectorConfig(),
                    LineClusteringConfig(),
                    ReaderConfig(prefix_tree=self.prefix_tree)
                )

                # Extract recognized text
                recognized_text = "\n".join(
                    " ".join(word.text for word in line) for line in read_lines
                )

                # Apply AI correction
                corrected_text = self.gemini_service.correct_text(recognized_text)

                segmented_texts.append({
                    'question_id': f"Q{idx}",
                    'recognized_text': recognized_text,
                    'corrected_text': corrected_text,
                    'region': {'top': top, 'bottom': bottom},
                    'word_count': len(recognized_text.split()),
                    'confidence': self._calculate_confidence(recognized_text, corrected_text)
                })

                logger.info(f"Processed question {idx}: {len(recognized_text)} chars")

            return {
                'success': True,
                'total_questions': len(segmented_texts),
                'questions': segmented_texts,
                'processing_info': {
                    'original_size': original_img.shape,
                    'text_regions_found': len(text_regions),
                    'ai_correction_available': self.gemini_service.is_available()
                }
            }

        except Exception as e:
            logger.error(f"OCR processing failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def _calculate_confidence(self, original, corrected):
        """Calculate a simple confidence score based on text changes."""
        if original == corrected:
            return 0.95  # High confidence if no changes needed

        # Simple metric based on character differences
        changes = abs(len(original) - len(corrected))
        total_chars = max(len(original), len(corrected))

        if total_chars == 0:
            return 0.5

        confidence = max(0.3, 1.0 - (changes / total_chars))
        return round(confidence, 2)