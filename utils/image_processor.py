import cv2
import numpy as np
from PIL import Image
import os


class ImageProcessor:

    @staticmethod
    def preprocess_image(image_path):
        """Preprocess image for better OCR results."""
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image at {image_path}")

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Adaptive thresholding
        binary = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )

        # Dilation to connect text regions
        kernel = np.ones((3, 3), np.uint8)
        dilated = cv2.dilate(binary, kernel, iterations=2)

        return image, gray, binary, dilated

    @staticmethod
    def find_text_regions(binary_image):
        """Detect text regions using contour detection."""
        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        boxes = [(y, y + h) for x, y, w, h in (cv2.boundingRect(c) for c in contours) if w > 20 and h > 10]

        if not boxes:
            return []

        boxes.sort()
        merged_boxes = []
        current_top, current_bottom = boxes[0]

        for box_top, box_bottom in boxes[1:]:
            if box_top - current_bottom < 20:
                current_bottom = max(current_bottom, box_bottom)
            else:
                merged_boxes.append((current_top, current_bottom))
                current_top, current_bottom = box_top, box_bottom

        merged_boxes.append((current_top, current_bottom))
        return merged_boxes

    @staticmethod
    def detect_words(binary_image):
        """Detect individual words in a binary image using contours."""
        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        word_boxes = [(x, y, x + w, y + h) for x, y, w, h in (cv2.boundingRect(c) for c in contours) if
                      w > 10 and h > 10]
        return sorted(word_boxes, key=lambda box: (box[1], box[0]))

    @staticmethod
    def save_processed_image(image, filename, folder):
        """Save processed image to specified folder."""
        filepath = os.path.join(folder, filename)
        cv2.imwrite(filepath, image)
        return filepath