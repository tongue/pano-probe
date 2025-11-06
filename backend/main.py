"""
PanoProbe Backend API
FastAPI server with CLIP integration for location difficulty analysis
"""

import os
import base64
from io import BytesIO
from PIL import Image
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
import logging

from clip_analyzer import CLIPLocationAnalyzer
from streetview_fetcher import StreetViewFetcher

# Try to import OCR - optional dependency
try:
    from ocr_analyzer import OCRTextAnalyzer
    OCR_AVAILABLE = True
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("EasyOCR not installed. Install with: pip install easyocr")
    OCRTextAnalyzer = None
    OCR_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)  # Back to INFO level
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="PanoProbe CLIP API",
    description="AI-powered location difficulty analysis using CLIP",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://geoguessr.local:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances (initialized on startup)
clip_analyzer: Optional[CLIPLocationAnalyzer] = None
streetview_fetcher: Optional[StreetViewFetcher] = None
ocr_analyzer: Optional[OCRTextAnalyzer] = None  # Single English-only OCR instance


# Request/Response models
class AnalysisRequest(BaseModel):
    lat: float
    lng: float
    num_views: int = 1  # Number of different angles to analyze


class CLIPAnalysisResponse(BaseModel):
    difficulty: int
    confidence: float
    insights: List[str]
    scene_type: str
    has_text: bool
    has_landmark: bool
    is_generic: bool
    is_urban: bool
    raw_difficulty_score: float
    scores: Dict[str, float]  # All 28 prompt scores for verbose display
    analyzed_images: Optional[Dict[str, str]] = None  # Base64 encoded images for debugging (N,E,S,W)


class EnsembleAnalysisResponse(BaseModel):
    clip_analysis: Optional[CLIPAnalysisResponse]
    combined_difficulty: int
    combined_confidence: float
    method: str  # "clip", "ensemble"
    reasoning: List[str]




@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    global clip_analyzer, streetview_fetcher, ocr_analyzer
    
    # Get API key from environment
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        logger.warning("GOOGLE_MAPS_API_KEY not set. Street View fetching will be disabled.")
    else:
        streetview_fetcher = StreetViewFetcher(api_key)
        logger.info("✓ Street View fetcher initialized")
    
    # Initialize CLIP model
    try:
        clip_analyzer = CLIPLocationAnalyzer()
        logger.info("✓ CLIP analyzer initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize CLIP: {e}")
        # Continue without CLIP - will return errors on analysis requests
    
    # Initialize English-only OCR (fast and simple!)
    if OCR_AVAILABLE and OCRTextAnalyzer:
        try:
            # Try GPU first (works on M1/M2 Macs and NVIDIA)
            import torch
            use_gpu = torch.cuda.is_available() or (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available())
            
            if use_gpu:
                logger.info("📝 Initializing English OCR with GPU acceleration...")
                try:
                    ocr_analyzer = OCRTextAnalyzer(languages=['en'], gpu=True)
                    logger.info("✓ English OCR ready with GPU! (will detect text presence even in other languages)")
                except Exception as gpu_error:
                    logger.warning(f"⚠️ GPU OCR failed ({gpu_error}), falling back to CPU...")
                    ocr_analyzer = OCRTextAnalyzer(languages=['en'], gpu=False)
                    logger.info("✓ English OCR ready with CPU (will detect text presence even in other languages)")
            else:
                logger.info("📝 Initializing English OCR (detects text in any language)...")
                ocr_analyzer = OCRTextAnalyzer(languages=['en'], gpu=False)
                logger.info("✓ English OCR ready! (will detect text presence even in other languages)")
        except Exception as e:
            logger.warning(f"⚠️ OCR initialization failed: {e}")
            logger.warning("Text detection will rely on CLIP only (less accurate)")
    else:
        logger.warning("⚠️ EasyOCR not installed")
        logger.warning("To enable OCR text detection, run: pip install easyocr")
        logger.warning("Text detection will rely on CLIP only (less accurate)")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "clip_available": clip_analyzer is not None,
        "streetview_available": streetview_fetcher is not None,
        "ocr_available": ocr_analyzer is not None,
        "ocr_type": "English-only (fast, detects text in any language)"
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "services": {
            "clip": "ready" if clip_analyzer else "unavailable",
            "streetview": "ready" if streetview_fetcher else "unavailable"
        }
    }


@app.post("/api/analyze", response_model=EnsembleAnalysisResponse)
async def analyze_location(request: AnalysisRequest):
    """
    Analyze a location using CLIP
    
    Args:
        request: Analysis request with lat/lng
        
    Returns:
        CLIP analysis results
    """
    if not clip_analyzer:
        raise HTTPException(status_code=503, detail="CLIP analyzer not available")
    
    if not streetview_fetcher:
        raise HTTPException(status_code=503, detail="Street View fetcher not available. Set GOOGLE_MAPS_API_KEY.")
    
    try:
        logger.info(f"🔄 Analyzing location with 360° coverage: {request.lat}, {request.lng}")
        
        # Get panoId from lat/lng first
        pano_id = streetview_fetcher.get_pano_id_from_location(request.lat, request.lng)
        
        if not pano_id:
            raise HTTPException(
                status_code=404,
                detail="No Street View imagery available for this location"
            )
        
        logger.info(f"📍 Found panoId: {pano_id}")
        
        # Fetch 360° views (N, NE, E, SE, S, SW, W, NW) at high resolution!
        # Zoom 4 = 8192×4096 (4× better than before!)
        # For maximum quality, change to zoom=5 (16384×8192, slower)
        views_dict = streetview_fetcher.fetch_360_views(pano_id, zoom=4)
        
        if not views_dict:
            raise HTTPException(
                status_code=404,
                detail="Failed to fetch 360° views"
            )
        
        # Convert dict to list of images for CLIP analysis
        # 8 directions for complete 360° coverage
        directions = ['north', 'northeast', 'east', 'southeast', 
                      'south', 'southwest', 'west', 'northwest']
        images = [views_dict[d] for d in directions if d in views_dict]
        
        logger.info(f"🤖 Analyzing {len(images)} directional views (full 360°) with CLIP...")
        
        # Analyze all 4 views with CLIP (aggregated)
        result = clip_analyzer.analyze_multiple_views(images)
        
        if not result:
            raise HTTPException(
                status_code=500,
                detail="CLIP analysis failed"
            )
        
        logger.info(f"✅ CLIP 360° analysis complete! Difficulty: {result['difficulty']}/5")
        
        # ENHANCE WITH OCR - Fast English-only text detection
        if ocr_analyzer:
            logger.info("📝 Running English OCR on all 8 views (detects text in any language)...")
            
            try:
                ocr_result = ocr_analyzer.analyze_multiple_views(images)
                
                if ocr_result['total_words'] > 0:
                    logger.info(f"✅ OCR complete! Found {ocr_result['total_words']} words in {ocr_result['views_with_text']}/8 views ({ocr_result['avg_confidence']:.0%} confidence)")
                    
                    # Override CLIP's text detection with OCR results (OCR is more accurate!)
                    result['analysis']['has_text'] = True
                    
                    # Add OCR insight
                    ocr_insight = f"📝 OCR: Found {ocr_result['total_words']} words in {ocr_result['views_with_text']}/8 views ({ocr_result['avg_confidence']:.0%} confidence)"
                    if ocr_insight not in result['analysis']['insights']:
                        result['analysis']['insights'].insert(0, ocr_insight)  # Add at top
                    
                    # Boost text-related CLIP scores with OCR confidence
                    result['scores']['a photo with clear readable text and signs'] = max(
                        result['scores']['a photo with clear readable text and signs'],
                        ocr_result['avg_confidence']
                    )
                    result['scores']['a photo with visible business signs and storefronts'] = max(
                        result['scores']['a photo with visible business signs and storefronts'],
                        ocr_result['avg_confidence'] * 0.8
                    )
                    
                    # Recalculate difficulty with enhanced text detection
                    if ocr_result['total_words'] > 10 and ocr_result['avg_confidence'] > 0.5:
                        old_difficulty = result['difficulty']
                        result['difficulty'] = max(1, result['difficulty'] - 1)
                        if result['difficulty'] != old_difficulty:
                            logger.info(f"  ↓ Difficulty adjusted {old_difficulty} → {result['difficulty']} (OCR found readable text)")
                            result['analysis']['insights'].append(f"⬇️ Difficulty reduced due to readable text")
                else:
                    logger.info("  No text detected by OCR")
            except Exception as e:
                logger.warning(f"⚠️ OCR analysis failed: {e}")
        else:
            logger.warning("  OCR not available - text detection relies on CLIP only")
        
        # Convert all images to base64 for debugging (TEMPORARY - for verification)
        # Lower quality for debug images to reduce bandwidth (they're large at zoom 4!)
        debug_images = {}
        for direction in directions:
            if direction in views_dict:
                buffered = BytesIO()
                # Resize to smaller size for debug display (1/2 scale)
                debug_img = views_dict[direction].copy()
                debug_img.thumbnail((1024, 2048), Image.Resampling.LANCZOS)
                debug_img.save(buffered, format="JPEG", quality=70)
                debug_images[direction] = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        # Create CLIP analysis response with all scores (now enhanced with OCR!)
        clip_response = CLIPAnalysisResponse(
            difficulty=result["difficulty"],
            confidence=result["confidence"],
            insights=result["analysis"]["insights"],
            scene_type=result["analysis"]["scene_type"],
            has_text=result["analysis"]["has_text"],
            has_landmark=result["analysis"]["has_landmark"],
            is_generic=result["analysis"]["is_generic"],
            is_urban=result["analysis"]["is_urban"],
            raw_difficulty_score=result["analysis"]["raw_difficulty_score"],
            scores=result["scores"],  # Aggregated scores from all 4 views
            analyzed_images=debug_images  # TEMPORARY: All 4 directions for debugging
        )
        
        # For now, just return CLIP results
        # Frontend will combine with heuristics
        return EnsembleAnalysisResponse(
            clip_analysis=clip_response,
            combined_difficulty=result["difficulty"],
            combined_confidence=result["confidence"],
            method="clip",
            reasoning=result["analysis"]["insights"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing location: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/api/test-clip")
async def test_clip():
    """
    Test endpoint to verify CLIP is working
    Returns model status and basic info
    """
    if not clip_analyzer:
        return {"status": "unavailable", "error": "CLIP not initialized"}
    
    return {
        "status": "ready",
        "model": "openai/clip-vit-base-patch32",
        "device": clip_analyzer.device,
        "prompts_count": len(clip_analyzer.DIFFICULTY_PROMPTS)
    }


if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment or default to 8000
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )

