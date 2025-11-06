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
    # Organized by category for GeoGuessr relevance
    DIFFICULTY_PROMPTS = [
        # Text and signage
        "a photo with clear readable text and signs",
        "a photo with visible business signs and storefronts",
        "a photo with colored road signs",
        
        # Landmarks and architecture
        "a photo of a famous landmark or monument",
        "a photo with unique architecture",
        
        # Urban vs rural
        "a photo of a busy city street with many buildings",
        "a photo of a remote rural area",
        "a generic road with no distinctive features",
        "a highway or motorway with no landmarks",
        
        # Road features (country-specific clues!)
        "a photo with road bollards or marker posts",
        "a photo with yellow center line markings",
        "a photo with white dashed road lines",
        "a photo with a roundabout or traffic circle",
        "a photo with kilometer markers or mile markers",
        
        # Infrastructure
        "a photo with overhead power lines",
        "a photo with distinctive street lights or lamp posts",
        
        # Vehicles and street view specific
        "a photo with a visible license plate",
        "a photo with a Google Street View car shadow or reflection",
        
        # Environmental indicators (climate/region clues)
        "a photo with distinctive vegetation and plants",
        "a photo with palm trees",
        "a photo with snow on the ground",
        "a photo with desert landscape",
        "a photo with rice fields or paddy fields",
        
        # National symbols
        "a photo with country flags or national symbols",
        
        # Image quality
        "a blurry or low quality image"
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
        # Extract key indicators (threshold = 0.15 for most, 0.2 for generic)
        # Text and signage
        has_text = scores["a photo with clear readable text and signs"] > 0.15
        has_businesses = scores["a photo with visible business signs and storefronts"] > 0.15
        has_road_signs = scores["a photo with colored road signs"] > 0.15
        
        # Landmarks and architecture
        has_landmark = scores["a photo of a famous landmark or monument"] > 0.15
        has_unique_architecture = scores["a photo with unique architecture"] > 0.15
        
        # Urban vs rural
        is_urban = scores["a photo of a busy city street with many buildings"] > 0.15
        is_remote = scores["a photo of a remote rural area"] > 0.15
        is_generic = scores["a generic road with no distinctive features"] > 0.2
        is_highway = scores["a highway or motorway with no landmarks"] > 0.15
        
        # Road features (GeoGuessr gold!)
        has_bollards = scores["a photo with road bollards or marker posts"] > 0.15
        has_yellow_lines = scores["a photo with yellow center line markings"] > 0.15
        has_white_lines = scores["a photo with white dashed road lines"] > 0.15
        has_roundabout = scores["a photo with a roundabout or traffic circle"] > 0.15
        has_km_markers = scores["a photo with kilometer markers or mile markers"] > 0.15
        
        # Infrastructure
        has_power_lines = scores["a photo with overhead power lines"] > 0.15
        has_street_lights = scores["a photo with distinctive street lights or lamp posts"] > 0.15
        
        # Vehicles
        has_license_plate = scores["a photo with a visible license plate"] > 0.15
        has_streetview_car = scores["a photo with a Google Street View car shadow or reflection"] > 0.15
        
        # Environmental (climate/region indicators)
        has_vegetation = scores["a photo with distinctive vegetation and plants"] > 0.15
        has_palm_trees = scores["a photo with palm trees"] > 0.15
        has_snow = scores["a photo with snow on the ground"] > 0.15
        has_desert = scores["a photo with desert landscape"] > 0.15
        has_rice_fields = scores["a photo with rice fields or paddy fields"] > 0.15
        
        # National symbols
        has_flags = scores["a photo with country flags or national symbols"] > 0.15
        
        # Image quality
        is_blurry = scores["a blurry or low quality image"] > 0.15
        
        # Calculate difficulty score (1-5)
        difficulty_score = 3.0  # Start at medium
        
        # EASY indicators (decrease difficulty) - These help identify location
        
        # Very strong clues (almost instant identification)
        if has_landmark:
            difficulty_score -= 1.5  # Famous = instant recognition
        if has_flags:
            difficulty_score -= 1.3  # Country flag = big clue
        
        # Strong text-based clues
        if has_text:
            difficulty_score -= 1.0  # Readable text reveals language/names
        if has_businesses:
            difficulty_score -= 0.8  # Business names can be googled
        if has_road_signs:
            difficulty_score -= 0.7  # Road signs have country-specific styles
        
        # GeoGuessr-specific clues (meta knowledge)
        if has_bollards:
            difficulty_score -= 0.7  # Country-specific bollard styles
        if has_km_markers:
            difficulty_score -= 0.6  # Distance markers are helpful
        if has_license_plate:
            difficulty_score -= 0.6  # License plates reveal country/region
        if has_street_lights:
            difficulty_score -= 0.5  # Street light styles vary by country
        
        # Architecture and urban features
        if has_unique_architecture:
            difficulty_score -= 0.7  # Distinctive buildings narrow location
        if is_urban:
            difficulty_score -= 0.5  # Cities have more identifiable features
        
        # Environmental clues (narrow down climate/region)
        if has_palm_trees:
            difficulty_score -= 0.4  # Tropical/subtropical regions
        if has_snow:
            difficulty_score -= 0.4  # Cold climate regions
        if has_rice_fields:
            difficulty_score -= 0.4  # Asia, specific regions
        
        # Road markings (country-specific)
        if has_yellow_lines:
            difficulty_score -= 0.3  # Yellow lines common in US/some countries
        if has_roundabout:
            difficulty_score -= 0.3  # Common in Europe, Australia
        
        # HARD indicators (increase difficulty) - These make it harder
        
        if is_generic:
            difficulty_score += 1.2  # No distinctive features = could be anywhere
        if is_remote:
            difficulty_score += 1.0  # Sparse features in rural areas
        if is_highway:
            difficulty_score += 0.8  # Highways look similar everywhere
        if has_desert:
            difficulty_score += 0.6  # Desert = sparse features
        if is_blurry:
            difficulty_score += 0.5  # Can't see details clearly
        
        # Neutral features (informational but not strong indicators either way)
        # has_power_lines - almost everywhere, not distinctive
        # has_white_lines - very common, not country-specific
        # has_vegetation - too generic without specificity
        # has_streetview_car - confirms street view but doesn't help location
        
        # Clamp to 1-5
        difficulty = max(1, min(5, round(difficulty_score)))
        
        # Calculate confidence based on score certainty
        max_score = max(scores.values())
        confidence = min(1.0, max_score * 1.5)  # Scale up confidence
        
        # Generate insights
        insights = []
        
        # Very strong clues
        if has_landmark:
            insights.append("🏛️ Famous landmark detected")
        if has_flags:
            insights.append("🚩 Country flags or national symbols detected")
        
        # Text-based clues
        if has_text:
            insights.append("🔤 Readable text/signs detected")
        if has_businesses:
            insights.append("🏪 Business signs/storefronts detected")
        if has_road_signs:
            insights.append("🚸 Colored road signs detected")
        
        # GeoGuessr meta clues
        if has_bollards:
            insights.append("🚧 Road bollards/marker posts detected")
        if has_km_markers:
            insights.append("📏 Kilometer/mile markers detected")
        if has_license_plate:
            insights.append("🚗 License plate visible")
        if has_street_lights:
            insights.append("💡 Distinctive street lights detected")
        
        # Architecture and environment
        if has_unique_architecture:
            insights.append("🏗️ Distinctive architecture detected")
        if is_urban:
            insights.append("🏙️ Urban environment detected")
        if is_remote:
            insights.append("🏜️ Remote/rural area detected")
        
        # Environmental/climate indicators
        if has_palm_trees:
            insights.append("🌴 Palm trees detected (tropical/subtropical)")
        if has_snow:
            insights.append("❄️ Snow detected (cold climate)")
        if has_rice_fields:
            insights.append("🌾 Rice fields/paddy fields detected")
        if has_desert:
            insights.append("🏜️ Desert landscape detected")
        if has_vegetation:
            insights.append("🌿 Distinctive vegetation detected")
        
        # Road features
        if has_yellow_lines:
            insights.append("🟨 Yellow road markings detected")
        if has_roundabout:
            insights.append("🔄 Roundabout/traffic circle detected")
        
        # Infrastructure
        if has_power_lines:
            insights.append("⚡ Overhead power lines detected")
        
        # Negative indicators
        if is_generic:
            insights.append("🛣️ Generic road with no distinctive features")
        if is_highway:
            insights.append("🛤️ Highway/motorway detected")
        if is_blurry:
            insights.append("📷 Low image quality detected")
        
        # Informational
        if has_streetview_car:
            insights.append("📸 Street View car shadow/reflection visible")
        
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
            Aggregated analysis with same structure as analyze_image
        """
        if not images:
            return None
        
        # Analyze each image
        analyses = [self.analyze_image(img) for img in images]
        
        # Aggregate results
        avg_difficulty = np.mean([a["difficulty"] for a in analyses])
        avg_confidence = np.mean([a["confidence"] for a in analyses])
        avg_raw_score = np.mean([a["analysis"]["raw_difficulty_score"] for a in analyses])
        
        # Combine insights (unique only)
        all_insights = []
        for analysis in analyses:
            all_insights.extend(analysis["analysis"]["insights"])
        unique_insights = list(set(all_insights))
        
        # Aggregate scores (average across all views)
        aggregated_scores = {}
        for prompt in self.DIFFICULTY_PROMPTS:
            avg_score = np.mean([a["scores"][prompt] for a in analyses])
            aggregated_scores[prompt] = float(avg_score)
        
        # Aggregate binary features (true if detected in any view)
        has_text = any(a["analysis"]["has_text"] for a in analyses)
        has_landmark = any(a["analysis"]["has_landmark"] for a in analyses)
        is_generic = any(a["analysis"]["is_generic"] for a in analyses)
        is_urban = any(a["analysis"]["is_urban"] for a in analyses)
        
        # Most common scene type
        scene_types = [a["analysis"]["scene_type"] for a in analyses]
        most_common_scene = max(set(scene_types), key=scene_types.count)
        
        # Return in same format as analyze_image
        return {
            "difficulty": round(avg_difficulty),
            "confidence": avg_confidence,
            "scores": aggregated_scores,
            "analysis": {
                "difficulty": round(avg_difficulty),
                "confidence": avg_confidence,
                "has_text": has_text,
                "has_landmark": has_landmark,
                "is_generic": is_generic,
                "is_urban": is_urban,
                "scene_type": most_common_scene,
                "insights": unique_insights,
                "raw_difficulty_score": avg_raw_score
            },
            "individual_analyses": analyses,
            "num_views": len(images)
        }

