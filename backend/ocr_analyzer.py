"""
OCR-based Text Detection
Complements CLIP by actually reading text from images
Uses EasyOCR for robust text detection in Street View images
"""

import easyocr
import numpy as np
from PIL import Image
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class OCRTextAnalyzer:
    """Detects and reads text from Street View images using EasyOCR"""
    
    def __init__(self, languages: List[str] = ['en'], gpu: bool = False):
        """
        Initialize OCR reader
        
        Args:
            languages: List of language codes (e.g., ['en', 'es', 'fr'])
            gpu: Use GPU acceleration if available
        """
        logger.info(f"Loading EasyOCR for languages: {languages}...")
        logger.info("⏳ First-time download may take a few minutes (~500MB)...")
        
        self.reader = easyocr.Reader(languages, gpu=gpu, verbose=False)
        
        logger.info("✓ EasyOCR loaded successfully!")
    
    def detect_text(self, image: Image.Image, min_confidence: float = 0.3) -> Dict:
        """
        Detect and read text from image
        
        Args:
            image: PIL Image
            min_confidence: Minimum confidence threshold for text detection
            
        Returns:
            Dict with text detection results
        """
        # Convert PIL to numpy array
        img_array = np.array(image)
        
        try:
            # Detect text
            results = self.reader.readtext(img_array)
            
            if not results:
                return {
                    'has_text': False,
                    'word_count': 0,
                    'confidence': 0.0,
                    'text_length': 0,
                    'detected_text': '',
                    'text_boxes': 0,
                    'raw_results': []
                }
            
            # Extract all detected text above confidence threshold
            all_text = []
            all_confidences = []
            filtered_results = []
            
            for (bbox, text, confidence) in results:
                if confidence > min_confidence:
                    all_text.append(text)
                    all_confidences.append(confidence)
                    filtered_results.append({
                        'text': text,
                        'confidence': confidence,
                        'bbox': bbox
                    })
            
            combined_text = ' '.join(all_text)
            word_count = len(combined_text.split())
            avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0
            
            # Determine if meaningful text is present
            # More lenient: even 2 words can be significant (e.g., "STOP SIGN")
            has_text = word_count >= 2 and avg_confidence > 0.35
            
            return {
                'has_text': has_text,
                'word_count': word_count,
                'confidence': avg_confidence,
                'text_length': len(combined_text),
                'detected_text': combined_text[:500],  # First 500 chars
                'text_boxes': len(all_text),
                'raw_results': filtered_results[:10]  # First 10 detections
            }
            
        except Exception as e:
            logger.error(f"Error in OCR detection: {e}")
            return {
                'has_text': False,
                'word_count': 0,
                'confidence': 0.0,
                'text_length': 0,
                'detected_text': '',
                'text_boxes': 0,
                'raw_results': []
            }
    
    def analyze_multiple_views(self, images: List[Image.Image]) -> Dict:
        """
        Analyze multiple views and aggregate text detection results
        
        Args:
            images: List of PIL Images
            
        Returns:
            Aggregated text detection results
        """
        if not images:
            return {
                'has_text': False,
                'total_words': 0,
                'avg_confidence': 0.0,
                'views_with_text': 0,
                'total_views': 0
            }
        
        results = []
        total_words = 0
        total_confidence = 0
        views_with_text = 0
        
        for i, image in enumerate(images):
            logger.info(f"🔍 OCR analyzing view {i+1}/{len(images)}...")
            result = self.detect_text(image)
            results.append(result)
            
            if result['has_text']:
                total_words += result['word_count']
                total_confidence += result['confidence']
                views_with_text += 1
                logger.info(f"  ✓ Found {result['word_count']} words (confidence: {result['confidence']:.0%})")
        
        avg_confidence = total_confidence / views_with_text if views_with_text > 0 else 0
        
        return {
            'has_text': views_with_text > 0,
            'total_words': total_words,
            'avg_confidence': avg_confidence,
            'views_with_text': views_with_text,
            'total_views': len(images),
            'individual_results': results
        }

