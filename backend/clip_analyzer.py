"""
CLIP-based Location Analysis
Uses OpenAI's CLIP model to analyze Street View images for difficulty prediction
"""

import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
from typing import Dict, List
import numpy as np
import time
import logging

logger = logging.getLogger(__name__)


class CLIPLocationAnalyzer:
    """Analyzes location difficulty using CLIP"""
    
    # Comprehensive GeoGuessr-focused prompts (75 total)
    # Organized by category for expert-level location identification
    DIFFICULTY_PROMPTS = [
        # === TEXT & LANGUAGE (10 prompts) ===
        "a photo with clear readable text and signs",
        "a photo with visible business signs and storefronts",
        "a photo with colored road signs",
        "a photo with Cyrillic alphabet text",
        "a photo with Arabic or Hebrew script",
        "a photo with Chinese, Japanese, or Korean characters",
        "a photo with Thai or Southeast Asian script",
        "a photo with street name signs",
        "a photo with advertising billboards",
        "a photo with country flags or national symbols",
        
        # === ROAD SURFACE & INFRASTRUCTURE (15 prompts) ===
        "a photo with road bollards or marker posts",
        "a photo with yellow center line markings",
        "a photo with white dashed road lines",
        "a photo with a roundabout or traffic circle",
        "a photo with kilometer markers or mile markers",
        "a photo of a dirt or unpaved road",
        "a photo of a cobblestone or brick paved road",
        "a photo of a red dirt road",
        "a photo with metal guardrails or crash barriers",
        "a photo with wooden guardrails",
        "a photo with concrete road barriers",
        "a photo with painted curbs or road edges",
        "a photo with chevron curve warning signs",
        "a photo with diagonal striped crosswalks",
        "a photo with parallel line crosswalks",
        
        # === ARCHITECTURE & BUILDINGS (12 prompts) ===
        "a photo of a famous landmark or monument",
        "a photo with unique architecture",
        "a photo with brick buildings",
        "a photo with wooden houses",
        "a photo with concrete apartment blocks",
        "a photo with terracotta or tile roofs",
        "a photo with flat concrete roofs",
        "a photo with corrugated metal roofs",
        "a photo with modern glass buildings",
        "a photo with old historical buildings",
        "a photo of a European city with old architecture",
        "a photo of a narrow village street",
        
        # === UTILITY & INFRASTRUCTURE (8 prompts) ===
        "a photo with overhead power lines",
        "a photo with distinctive street lights or lamp posts",
        "a photo with wooden utility poles",
        "a photo with concrete utility poles",
        "a photo with electrical transformers on poles",
        "a photo with tram or trolley wires overhead",
        "a photo with sidewalks and pedestrian paths",
        "a photo with street parking spaces",
        
        # === ENVIRONMENT & VEGETATION (13 prompts) ===
        "a photo with distinctive vegetation and plants",
        "a photo with palm trees",
        "a photo with snow on the ground",
        "a photo with desert landscape",
        "a photo with rice fields or paddy fields",
        "a photo with tropical vegetation and humidity",
        "a photo with coniferous forest",
        "a photo with olive trees or Mediterranean plants",
        "a photo with mountains in the background",
        "a photo with flat plains landscape",
        "a photo with vineyards or grape fields",
        "a photo with wheat or grain fields",
        "a photo of a coastal or beach setting",
        
        # === VEHICLES & TRANSPORT (5 prompts) ===
        "a photo with a visible license plate",
        "a photo with a Google Street View car shadow or reflection",
        "a photo with a tuk-tuk or auto rickshaw",
        "a photo with pickup trucks",
        "a photo with motorcycles or scooters",
        
        # === URBAN CHARACTERISTICS (7 prompts) ===
        "a photo of a busy city street with many buildings",
        "a photo of a remote rural area",
        "a generic road with no distinctive features",
        "a highway or motorway with no landmarks",
        "a photo with a wide multi-lane boulevard",
        "a photo of an Asian city with neon signs",
        "a photo of a North American suburb with large houses",
        
        # === STREET FURNITURE & MISC (5 prompts) ===
        "a photo with distinctive mailboxes or postal boxes",
        "a photo with public trash bins or waste containers",
        "a photo with benches or street seating",
        "a photo with bus stops or transit shelters",
        "a photo with red and white striped posts",
        
        # === IMAGE QUALITY (1 prompt) ===
        "a blurry or low quality image"
    ]
    
    def __init__(self, model_name: str = "openai/clip-vit-base-patch32"):
        """
        Initialize CLIP model
        
        Args:
            model_name: Hugging Face model identifier
        """
        print(f"Loading CLIP model: {model_name}...")
        
        # Detect best available device: CUDA (NVIDIA) > MPS (Apple Silicon) > CPU
        if torch.cuda.is_available():
            self.device = "cuda"
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            self.device = "mps"
        else:
            self.device = "cpu"
        
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
        # === TEXT & LANGUAGE ===
        has_text = scores["a photo with clear readable text and signs"] > 0.15
        has_businesses = scores["a photo with visible business signs and storefronts"] > 0.15
        has_road_signs = scores["a photo with colored road signs"] > 0.15
        has_cyrillic = scores["a photo with Cyrillic alphabet text"] > 0.15
        has_arabic = scores["a photo with Arabic or Hebrew script"] > 0.15
        has_cjk = scores["a photo with Chinese, Japanese, or Korean characters"] > 0.15
        has_thai = scores["a photo with Thai or Southeast Asian script"] > 0.15
        has_street_names = scores["a photo with street name signs"] > 0.15
        has_billboards = scores["a photo with advertising billboards"] > 0.15
        has_flags = scores["a photo with country flags or national symbols"] > 0.15
        
        # === ROAD SURFACE & INFRASTRUCTURE ===
        has_bollards = scores["a photo with road bollards or marker posts"] > 0.15
        has_yellow_lines = scores["a photo with yellow center line markings"] > 0.15
        has_white_lines = scores["a photo with white dashed road lines"] > 0.15
        has_roundabout = scores["a photo with a roundabout or traffic circle"] > 0.15
        has_km_markers = scores["a photo with kilometer markers or mile markers"] > 0.15
        is_dirt_road = scores["a photo of a dirt or unpaved road"] > 0.15
        is_cobblestone = scores["a photo of a cobblestone or brick paved road"] > 0.15
        is_red_dirt = scores["a photo of a red dirt road"] > 0.15
        has_metal_guardrails = scores["a photo with metal guardrails or crash barriers"] > 0.15
        has_wooden_guardrails = scores["a photo with wooden guardrails"] > 0.15
        has_concrete_barriers = scores["a photo with concrete road barriers"] > 0.15
        has_painted_curbs = scores["a photo with painted curbs or road edges"] > 0.15
        has_chevrons = scores["a photo with chevron curve warning signs"] > 0.15
        has_diagonal_crosswalk = scores["a photo with diagonal striped crosswalks"] > 0.15
        has_parallel_crosswalk = scores["a photo with parallel line crosswalks"] > 0.15
        
        # === ARCHITECTURE & BUILDINGS ===
        has_landmark = scores["a photo of a famous landmark or monument"] > 0.15
        has_unique_architecture = scores["a photo with unique architecture"] > 0.15
        has_brick_buildings = scores["a photo with brick buildings"] > 0.15
        has_wooden_houses = scores["a photo with wooden houses"] > 0.15
        has_concrete_apartments = scores["a photo with concrete apartment blocks"] > 0.15
        has_tile_roofs = scores["a photo with terracotta or tile roofs"] > 0.15
        has_flat_roofs = scores["a photo with flat concrete roofs"] > 0.15
        has_metal_roofs = scores["a photo with corrugated metal roofs"] > 0.15
        has_glass_buildings = scores["a photo with modern glass buildings"] > 0.15
        has_historical_buildings = scores["a photo with old historical buildings"] > 0.15
        is_european_city = scores["a photo of a European city with old architecture"] > 0.15
        is_village_street = scores["a photo of a narrow village street"] > 0.15
        
        # === UTILITY & INFRASTRUCTURE ===
        has_power_lines = scores["a photo with overhead power lines"] > 0.15
        has_street_lights = scores["a photo with distinctive street lights or lamp posts"] > 0.15
        has_wooden_poles = scores["a photo with wooden utility poles"] > 0.15
        has_concrete_poles = scores["a photo with concrete utility poles"] > 0.15
        has_transformers = scores["a photo with electrical transformers on poles"] > 0.15
        has_tram_wires = scores["a photo with tram or trolley wires overhead"] > 0.15
        has_sidewalks = scores["a photo with sidewalks and pedestrian paths"] > 0.15
        has_parking = scores["a photo with street parking spaces"] > 0.15
        
        # === ENVIRONMENT & VEGETATION ===
        has_vegetation = scores["a photo with distinctive vegetation and plants"] > 0.15
        has_palm_trees = scores["a photo with palm trees"] > 0.15
        has_snow = scores["a photo with snow on the ground"] > 0.15
        has_desert = scores["a photo with desert landscape"] > 0.15
        has_rice_fields = scores["a photo with rice fields or paddy fields"] > 0.15
        has_tropical = scores["a photo with tropical vegetation and humidity"] > 0.15
        has_coniferous = scores["a photo with coniferous forest"] > 0.15
        has_mediterranean = scores["a photo with olive trees or Mediterranean plants"] > 0.15
        has_mountains = scores["a photo with mountains in the background"] > 0.15
        has_plains = scores["a photo with flat plains landscape"] > 0.15
        has_vineyards = scores["a photo with vineyards or grape fields"] > 0.15
        has_grain_fields = scores["a photo with wheat or grain fields"] > 0.15
        is_coastal = scores["a photo of a coastal or beach setting"] > 0.15
        
        # === VEHICLES & TRANSPORT ===
        has_license_plate = scores["a photo with a visible license plate"] > 0.15
        has_streetview_car = scores["a photo with a Google Street View car shadow or reflection"] > 0.15
        has_tuktuk = scores["a photo with a tuk-tuk or auto rickshaw"] > 0.15
        has_pickup_trucks = scores["a photo with pickup trucks"] > 0.15
        has_motorcycles = scores["a photo with motorcycles or scooters"] > 0.15
        
        # === URBAN CHARACTERISTICS ===
        is_urban = scores["a photo of a busy city street with many buildings"] > 0.15
        is_remote = scores["a photo of a remote rural area"] > 0.15
        is_generic = scores["a generic road with no distinctive features"] > 0.2
        is_highway = scores["a highway or motorway with no landmarks"] > 0.15
        is_boulevard = scores["a photo with a wide multi-lane boulevard"] > 0.15
        is_asian_city = scores["a photo of an Asian city with neon signs"] > 0.15
        is_us_suburb = scores["a photo of a North American suburb with large houses"] > 0.15
        
        # === STREET FURNITURE & MISC ===
        has_mailboxes = scores["a photo with distinctive mailboxes or postal boxes"] > 0.15
        has_trash_bins = scores["a photo with public trash bins or waste containers"] > 0.15
        has_benches = scores["a photo with benches or street seating"] > 0.15
        has_bus_stops = scores["a photo with bus stops or transit shelters"] > 0.15
        has_striped_posts = scores["a photo with red and white striped posts"] > 0.15
        
        # === IMAGE QUALITY ===
        is_blurry = scores["a blurry or low quality image"] > 0.15
        
        # Calculate difficulty score (1-5)
        difficulty_score = 3.0  # Start at medium
        
        # ============ EASY INDICATORS (decrease difficulty) ============
        
        # === TIER 1: INSTANT IDENTIFICATION (Very strong clues) ===
        if has_landmark:
            difficulty_score -= 1.5  # Famous landmarks = instant recognition
        if has_flags:
            difficulty_score -= 1.3  # Country flags = direct country clue
        
        # === TIER 2: LANGUAGE & SCRIPT (Strong regional indicators) ===
        if has_cyrillic:
            difficulty_score -= 1.0  # Cyrillic = Russia/Eastern Europe
        if has_arabic:
            difficulty_score -= 1.0  # Arabic/Hebrew = Middle East
        if has_cjk:
            difficulty_score -= 1.0  # CJK = East Asia (China/Japan/Korea)
        if has_thai:
            difficulty_score -= 1.0  # Thai script = Southeast Asia
        if has_text:
            difficulty_score -= 0.8  # Readable text reveals language/names
        if has_street_names:
            difficulty_score -= 0.7  # Street names can be googled
        if has_businesses:
            difficulty_score -= 0.7  # Business names can be searched
        if has_road_signs:
            difficulty_score -= 0.6  # Road signs have country-specific styles
        if has_billboards:
            difficulty_score -= 0.4  # Billboards often have regional branding
        
        # === TIER 3: INFRASTRUCTURE (Expert GeoGuessr clues) ===
        # Guardrails (extremely country-specific!)
        if has_wooden_guardrails:
            difficulty_score -= 0.8  # Specific countries (e.g., Japan, Norway)
        if has_metal_guardrails:
            difficulty_score -= 0.6  # Style varies by country
        if has_concrete_barriers:
            difficulty_score -= 0.5  # Common in specific regions
        
        # Utility poles (country-specific styles)
        if has_wooden_poles:
            difficulty_score -= 0.6  # North America, some Europe
        if has_concrete_poles:
            difficulty_score -= 0.6  # Common in Eastern Europe, Asia
        if has_transformers:
            difficulty_score -= 0.5  # Styles vary by region
        
        # Road features (GeoGuessr gold!)
        if has_bollards:
            difficulty_score -= 0.7  # Country-specific bollard styles
        if has_chevrons:
            difficulty_score -= 0.6  # Very country-specific designs
        if has_striped_posts:
            difficulty_score -= 0.6  # European road markers
        if has_km_markers:
            difficulty_score -= 0.5  # Distance markers are helpful
        if has_tram_wires:
            difficulty_score -= 0.6  # Specific cities/countries
        
        # === TIER 4: ARCHITECTURE & BUILDINGS (Strong regional markers) ===
        if has_unique_architecture:
            difficulty_score -= 0.7  # Distinctive buildings narrow location
        if is_european_city:
            difficulty_score -= 0.8  # European architecture distinctive
        if has_tile_roofs:
            difficulty_score -= 0.6  # Mediterranean, Southern Europe
        if has_brick_buildings:
            difficulty_score -= 0.5  # Common in specific regions
        if has_wooden_houses:
            difficulty_score -= 0.5  # Nordic, rural areas
        if has_concrete_apartments:
            difficulty_score -= 0.5  # Eastern Europe, urban Asia
        if has_metal_roofs:
            difficulty_score -= 0.4  # Rural areas, developing countries
        if has_historical_buildings:
            difficulty_score -= 0.5  # Old cities, searchable
        if is_village_street:
            difficulty_score -= 0.4  # Small villages can be distinctive
        
        # === TIER 5: ENVIRONMENT & VEGETATION (Climate/region indicators) ===
        if has_palm_trees:
            difficulty_score -= 0.5  # Tropical/subtropical = narrows region
        if has_snow:
            difficulty_score -= 0.5  # Cold climate = narrows region
        if has_rice_fields:
            difficulty_score -= 0.6  # Asia, specific regions
        if has_mediterranean:
            difficulty_score -= 0.6  # Mediterranean basin
        if has_coniferous:
            difficulty_score -= 0.4  # Northern regions, mountains
        if has_tropical:
            difficulty_score -= 0.5  # Equatorial regions
        if has_vineyards:
            difficulty_score -= 0.6  # Wine regions (France, Italy, etc.)
        if is_coastal:
            difficulty_score -= 0.4  # Coastal areas more distinctive
        if has_mountains:
            difficulty_score -= 0.4  # Mountain ranges are distinctive
        
        # === TIER 6: VEHICLES & REGIONAL SPECIFICS ===
        if has_tuktuk:
            difficulty_score -= 0.9  # Asia-specific (Thailand, India, etc.)
        if has_license_plate:
            difficulty_score -= 0.6  # License plates reveal country/region
        if has_pickup_trucks:
            difficulty_score -= 0.3  # Common in Americas, Australia
        if has_motorcycles:
            difficulty_score -= 0.3  # Very common in Southeast Asia
        
        # === TIER 7: URBAN FEATURES (Location narrowing) ===
        if is_urban:
            difficulty_score -= 0.5  # Cities have more identifiable features
        if is_asian_city:
            difficulty_score -= 0.7  # Asian cities very distinctive
        if is_us_suburb:
            difficulty_score -= 0.6  # US suburbs have distinctive style
        if has_sidewalks:
            difficulty_score -= 0.3  # Developed areas
        if has_parking:
            difficulty_score -= 0.2  # Urban development indicator
        
        # === TIER 8: ROAD MARKINGS & CROSSWALKS (Country-specific) ===
        if has_yellow_lines:
            difficulty_score -= 0.4  # US, UK, some countries
        if has_roundabout:
            difficulty_score -= 0.4  # Europe, UK, Australia
        if has_diagonal_crosswalk:
            difficulty_score -= 0.5  # European style
        if has_parallel_crosswalk:
            difficulty_score -= 0.4  # American style
        if has_painted_curbs:
            difficulty_score -= 0.3  # Urban, specific countries
        
        # === TIER 9: STREET FURNITURE (Minor regional indicators) ===
        if has_mailboxes:
            difficulty_score -= 0.4  # Styles vary by country
        if has_street_lights:
            difficulty_score -= 0.4  # Street light styles vary by country
        if has_trash_bins:
            difficulty_score -= 0.3  # Regional designs
        if has_bus_stops:
            difficulty_score -= 0.3  # Transit infrastructure
        if has_benches:
            difficulty_score -= 0.2  # Minor urban indicator
        
        # ============ HARD INDICATORS (increase difficulty) ============
        
        # === TIER 1: EXTREMELY DIFFICULT ===
        if is_generic:
            difficulty_score += 1.3  # No distinctive features = could be anywhere
        if is_remote:
            difficulty_score += 1.0  # Sparse features in rural areas
        
        # === TIER 2: DIFFICULT ===
        if is_highway:
            difficulty_score += 0.9  # Highways look similar everywhere
        if is_dirt_road:
            difficulty_score += 0.7  # Unpaved roads lack features (but regional!)
        if is_red_dirt:
            difficulty_score += 0.5  # Red dirt is distinctive (Australia, Africa) but still sparse
        if has_desert:
            difficulty_score += 0.7  # Desert = sparse features
        if has_plains:
            difficulty_score += 0.6  # Flat open areas lack features
        
        # === TIER 3: QUALITY ISSUES ===
        if is_blurry:
            difficulty_score += 0.6  # Can't see details clearly
        
        # Note: Some road surfaces make things EASIER despite being less developed
        # Cobblestone is actually a GOOD clue (Europe) - don't increase difficulty
        if is_cobblestone:
            difficulty_score -= 0.5  # Cobblestone = old European cities
        
        # Clamp to 1-5
        difficulty = max(1, min(5, round(difficulty_score)))
        
        # Calculate confidence based on score certainty
        max_score = max(scores.values())
        confidence = min(1.0, max_score * 1.5)  # Scale up confidence
        
        # Generate insights (comprehensive edition!)
        insights = []
        
        # === TIER 1: INSTANT IDENTIFICATION ===
        if has_landmark:
            insights.append("🏛️ Famous landmark detected")
        if has_flags:
            insights.append("🚩 Country flags or national symbols detected")
        
        # === LANGUAGE & SCRIPT (Strong regional indicators) ===
        if has_cyrillic:
            insights.append("🇷🇺 Cyrillic script detected (Russia/Eastern Europe)")
        if has_arabic:
            insights.append("🕌 Arabic/Hebrew script detected (Middle East)")
        if has_cjk:
            insights.append("🏮 CJK characters detected (East Asia)")
        if has_thai:
            insights.append("🇹🇭 Thai/Southeast Asian script detected")
        if has_text:
            insights.append("🔤 Readable text/signs detected")
        if has_street_names:
            insights.append("🛣️ Street name signs detected")
        if has_businesses:
            insights.append("🏪 Business signs/storefronts detected")
        if has_road_signs:
            insights.append("🚸 Colored road signs detected")
        if has_billboards:
            insights.append("📢 Advertising billboards detected")
        
        # === INFRASTRUCTURE (Expert GeoGuessr clues) ===
        # Guardrails
        if has_wooden_guardrails:
            insights.append("🪵 Wooden guardrails detected (Japan/Nordic countries)")
        if has_metal_guardrails:
            insights.append("🛡️ Metal guardrails detected")
        if has_concrete_barriers:
            insights.append("🧱 Concrete barriers detected")
        
        # Utility poles
        if has_wooden_poles:
            insights.append("🪵 Wooden utility poles (North America/Europe)")
        if has_concrete_poles:
            insights.append("⚪ Concrete utility poles (Eastern Europe/Asia)")
        if has_transformers:
            insights.append("⚡ Electrical transformers on poles")
        if has_tram_wires:
            insights.append("🚋 Tram/trolley wires overhead")
        
        # Road features
        if has_bollards:
            insights.append("🚧 Road bollards/marker posts detected")
        if has_chevrons:
            insights.append("⚠️ Chevron curve warning signs")
        if has_striped_posts:
            insights.append("🔴⚪ Red & white striped posts (Europe)")
        if has_km_markers:
            insights.append("📏 Kilometer/mile markers detected")
        if has_street_lights:
            insights.append("💡 Distinctive street lights detected")
        
        # === ARCHITECTURE & BUILDINGS ===
        if has_unique_architecture:
            insights.append("🏗️ Distinctive architecture detected")
        if is_european_city:
            insights.append("🏰 European city architecture")
        if has_tile_roofs:
            insights.append("🟥 Terracotta/tile roofs (Mediterranean)")
        if has_brick_buildings:
            insights.append("🧱 Brick buildings")
        if has_wooden_houses:
            insights.append("🏡 Wooden houses (Nordic/rural)")
        if has_concrete_apartments:
            insights.append("🏢 Concrete apartment blocks")
        if has_metal_roofs:
            insights.append("🔩 Corrugated metal roofs")
        if has_flat_roofs:
            insights.append("⬜ Flat concrete roofs")
        if has_glass_buildings:
            insights.append("🏙️ Modern glass buildings")
        if has_historical_buildings:
            insights.append("🏛️ Historical/old buildings")
        if is_village_street:
            insights.append("🏘️ Narrow village street")
        
        # === ENVIRONMENT & VEGETATION ===
        if has_palm_trees:
            insights.append("🌴 Palm trees (tropical/subtropical)")
        if has_snow:
            insights.append("❄️ Snow detected (cold climate)")
        if has_rice_fields:
            insights.append("🌾 Rice fields/paddy fields (Asia)")
        if has_mediterranean:
            insights.append("🫒 Mediterranean vegetation (olives/etc)")
        if has_coniferous:
            insights.append("🌲 Coniferous forest (northern regions)")
        if has_tropical:
            insights.append("🌺 Tropical vegetation")
        if has_vineyards:
            insights.append("🍇 Vineyards/grape fields")
        if has_grain_fields:
            insights.append("🌾 Wheat/grain fields")
        if is_coastal:
            insights.append("🌊 Coastal/beach setting")
        if has_mountains:
            insights.append("⛰️ Mountains in background")
        if has_plains:
            insights.append("🌾 Flat plains landscape")
        if has_desert:
            insights.append("🏜️ Desert landscape")
        if has_vegetation:
            insights.append("🌿 Distinctive vegetation")
        
        # === VEHICLES & TRANSPORT ===
        if has_tuktuk:
            insights.append("🛺 Tuk-tuk/rickshaw (Southeast Asia)")
        if has_license_plate:
            insights.append("🚗 License plate visible")
        if has_pickup_trucks:
            insights.append("🚙 Pickup trucks")
        if has_motorcycles:
            insights.append("🏍️ Motorcycles/scooters (common)")
        
        # === URBAN CHARACTERISTICS ===
        if is_urban:
            insights.append("🏙️ Urban environment")
        if is_asian_city:
            insights.append("🏮 Asian city with neon signs")
        if is_us_suburb:
            insights.append("🏡 North American suburb")
        if is_boulevard:
            insights.append("🛣️ Wide multi-lane boulevard")
        if has_sidewalks:
            insights.append("🚶 Sidewalks/pedestrian paths")
        if has_parking:
            insights.append("🅿️ Street parking spaces")
        
        # === ROAD MARKINGS & CROSSWALKS ===
        if has_yellow_lines:
            insights.append("🟨 Yellow road markings")
        if has_roundabout:
            insights.append("🔄 Roundabout/traffic circle")
        if has_diagonal_crosswalk:
            insights.append("⬜ Diagonal striped crosswalk (European)")
        if has_parallel_crosswalk:
            insights.append("▦ Parallel line crosswalk (American)")
        if has_painted_curbs:
            insights.append("🎨 Painted curbs/road edges")
        
        # === ROAD SURFACE ===
        if is_dirt_road:
            insights.append("🛤️ Dirt/unpaved road")
        if is_cobblestone:
            insights.append("🪨 Cobblestone/brick road (old European)")
        if is_red_dirt:
            insights.append("🟥 Red dirt road (Australia/Africa)")
        
        # === STREET FURNITURE ===
        if has_mailboxes:
            insights.append("📮 Distinctive mailboxes")
        if has_trash_bins:
            insights.append("🗑️ Public trash bins")
        if has_benches:
            insights.append("🪑 Street benches")
        if has_bus_stops:
            insights.append("🚏 Bus stops/transit shelters")
        
        # === INFRASTRUCTURE (General) ===
        if has_power_lines:
            insights.append("⚡ Overhead power lines")
        
        # === NEGATIVE INDICATORS (Difficulty increasers) ===
        if is_generic:
            insights.append("⚪ Generic road (no distinctive features)")
        if is_remote:
            insights.append("🏜️ Remote/rural area")
        if is_highway:
            insights.append("🛤️ Highway/motorway")
        if is_blurry:
            insights.append("📷 Low image quality")
        
        # === INFORMATIONAL ===
        if has_streetview_car:
            insights.append("📸 Street View car visible")
        
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
            logger.warning("⚠️ No images provided to CLIP analyzer!")
            return None
        
        logger.info(f"🔍 CLIP analyzing {len(images)} images with {len(self.DIFFICULTY_PROMPTS)} prompts each...")
        logger.info(f"   Expected time: ~{len(images) * 5}s (5s per image)")
        
        # Analyze each image
        analyses = []
        total_start = time.time()
        
        for i, img in enumerate(images, 1):
            logger.info(f"  📸 Analyzing image {i}/{len(images)}...")
            start = time.time()
            
            try:
                analysis = self.analyze_image(img)
                elapsed = time.time() - start
                logger.info(f"    ✓ Image {i} done in {elapsed:.1f}s (Difficulty: {analysis['difficulty']}/5)")
                analyses.append(analysis)
            except Exception as e:
                logger.error(f"    ❌ Error analyzing image {i}: {e}")
                raise
        
        total_elapsed = time.time() - total_start
        logger.info(f"✅ All {len(images)} images analyzed in {total_elapsed:.1f}s")
        
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

