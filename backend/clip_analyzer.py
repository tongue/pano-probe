"""
CLIP-based Location Analysis
Uses OpenAI's CLIP model to analyze Street View images for difficulty prediction
"""

import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
from typing import Dict, List
import numpy as np


class CLIPLocationAnalyzer:
    """Analyzes location difficulty using CLIP"""
    
    # Prompts designed to identify difficulty-related features
    DIFFICULTY_PROMPTS = [
        "a photo with clear readable text and signs",
        "a photo of a famous landmark or monument",
        "a generic road with no distinctive features",
        "a photo of a remote rural area",
        "a photo of a busy city street with many buildings",
        "a photo with unique architecture",
        "a blurry or low quality image",
        "a photo with distinctive vegetation and plants",
        "a highway or motorway with no landmarks",
        "a photo with visible business signs and storefronts"
    ]
    
    def __init__(self, model_name: str = "openai/clip-vit-base-patch32"):
        """
        Initialize CLIP model
        
        Args:
            model_name: Hugging Face model identifier
        """
        print(f"Loading CLIP model: {model_name}...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
        self.model = CLIPModel.from_pretrained(model_name).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(model_name)
        print("CLIP model loaded successfully!")
        
    def analyze_image(self, image: Image.Image) -> Dict:
        """
        Analyze a single image using CLIP
        
        Args:
            image: PIL Image
            
        Returns:
            Dictionary with analysis results
        """
        # Prepare inputs
        inputs = self.processor(
            text=self.DIFFICULTY_PROMPTS,
            images=image,
            return_tensors="pt",
            padding=True
        )
        
        # Move to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Get predictions
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits_per_image = outputs.logits_per_image
            probs = logits_per_image.softmax(dim=1)[0]
        
        # Create scores dictionary
        scores = {
            prompt: float(prob) 
            for prompt, prob in zip(self.DIFFICULTY_PROMPTS, probs)
        }
        
        # Analyze the scores
        analysis = self._interpret_scores(scores)
        
        return {
            "scores": scores,
            "analysis": analysis,
            "difficulty": analysis["difficulty"],
            "confidence": analysis["confidence"]
        }
    
    def _interpret_scores(self, scores: Dict[str, float]) -> Dict:
        """
        Interpret CLIP scores to determine difficulty
        
        Args:
            scores: Dictionary of prompt scores
            
        Returns:
            Analysis dictionary
        """
        # Extract key indicators
        has_text = scores["a photo with clear readable text and signs"] > 0.15
        has_landmark = scores["a photo of a famous landmark or monument"] > 0.15
        is_generic = scores["a generic road with no distinctive features"] > 0.2
        is_remote = scores["a photo of a remote rural area"] > 0.15
        is_urban = scores["a photo of a busy city street with many buildings"] > 0.15
        is_highway = scores["a highway or motorway with no landmarks"] > 0.15
        has_unique_architecture = scores["a photo with unique architecture"] > 0.15
        has_businesses = scores["a photo with visible business signs and storefronts"] > 0.15
        is_blurry = scores["a blurry or low quality image"] > 0.15
        
        # Calculate difficulty score (1-5)
        difficulty_score = 3.0  # Start at medium
        
        # Easy indicators (decrease difficulty)
        if has_text:
            difficulty_score -= 1.0
        if has_landmark:
            difficulty_score -= 1.5
        if is_urban:
            difficulty_score -= 0.5
        if has_unique_architecture:
            difficulty_score -= 0.7
        if has_businesses:
            difficulty_score -= 0.8
        
        # Hard indicators (increase difficulty)
        if is_generic:
            difficulty_score += 1.2
        if is_remote:
            difficulty_score += 1.0
        if is_highway:
            difficulty_score += 0.8
        if is_blurry:
            difficulty_score += 0.5
        
        # Clamp to 1-5
        difficulty = max(1, min(5, round(difficulty_score)))
        
        # Calculate confidence based on score certainty
        max_score = max(scores.values())
        confidence = min(1.0, max_score * 1.5)  # Scale up confidence
        
        # Generate insights
        insights = []
        if has_text:
            insights.append("🔤 Readable text/signs detected")
        if has_landmark:
            insights.append("🏛️ Famous landmark detected")
        if is_urban:
            insights.append("🏙️ Urban environment detected")
        if is_generic:
            insights.append("🛣️ Generic road/highway detected")
        if is_remote:
            insights.append("🏜️ Remote/rural area detected")
        if has_unique_architecture:
            insights.append("🏗️ Distinctive architecture detected")
        if has_businesses:
            insights.append("🏪 Business signs/storefronts detected")
        if is_blurry:
            insights.append("📷 Low image quality detected")
        
        # Determine scene type
        scene_type = self._get_scene_type(scores)
        
        return {
            "difficulty": difficulty,
            "confidence": confidence,
            "has_text": has_text,
            "has_landmark": has_landmark,
            "is_generic": is_generic,
            "is_urban": is_urban,
            "scene_type": scene_type,
            "insights": insights,
            "raw_difficulty_score": difficulty_score
        }
    
    def _get_scene_type(self, scores: Dict[str, float]) -> str:
        """Determine the primary scene type"""
        scene_scores = {
            "urban": scores["a photo of a busy city street with many buildings"],
            "rural": scores["a photo of a remote rural area"],
            "highway": scores["a highway or motorway with no landmarks"],
            "landmark": scores["a photo of a famous landmark or monument"],
        }
        
        return max(scene_scores, key=scene_scores.get)
    
    def analyze_multiple_views(self, images: List[Image.Image]) -> Dict:
        """
        Analyze multiple views and aggregate results
        
        Args:
            images: List of PIL Images
            
        Returns:
            Aggregated analysis
        """
        if not images:
            return None
        
        # Analyze each image
        analyses = [self.analyze_image(img) for img in images]
        
        # Aggregate results
        avg_difficulty = np.mean([a["difficulty"] for a in analyses])
        avg_confidence = np.mean([a["confidence"] for a in analyses])
        
        # Combine insights (unique only)
        all_insights = []
        for analysis in analyses:
            all_insights.extend(analysis["analysis"]["insights"])
        unique_insights = list(set(all_insights))
        
        return {
            "difficulty": round(avg_difficulty),
            "confidence": avg_confidence,
            "insights": unique_insights,
            "individual_analyses": analyses,
            "num_views": len(images)
        }

