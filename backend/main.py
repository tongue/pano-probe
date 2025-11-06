"""
PanoProbe Backend API
FastAPI server with CLIP integration for location difficulty analysis
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
import logging

from clip_analyzer import CLIPLocationAnalyzer
from streetview_fetcher import StreetViewFetcher

# Configure logging
logging.basicConfig(level=logging.INFO)
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


class EnsembleAnalysisResponse(BaseModel):
    clip_analysis: Optional[CLIPAnalysisResponse]
    combined_difficulty: int
    combined_confidence: float
    method: str  # "clip", "ensemble"
    reasoning: List[str]


@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    global clip_analyzer, streetview_fetcher
    
    # Get API key from environment
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        logger.warning("GOOGLE_MAPS_API_KEY not set. Street View fetching will be disabled.")
    else:
        streetview_fetcher = StreetViewFetcher(api_key)
        logger.info("Street View fetcher initialized")
    
    # Initialize CLIP model
    try:
        clip_analyzer = CLIPLocationAnalyzer()
        logger.info("CLIP analyzer initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize CLIP: {e}")
        # Continue without CLIP - will return errors on analysis requests


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "clip_available": clip_analyzer is not None,
        "streetview_available": streetview_fetcher is not None
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
        logger.info(f"Analyzing location: {request.lat}, {request.lng}")
        
        # Fetch Street View image(s)
        if request.num_views > 1:
            # Multiple views
            headings = [i * (360 // request.num_views) for i in range(request.num_views)]
            images = streetview_fetcher.fetch_multiple_views(
                request.lat, 
                request.lng,
                headings=headings
            )
            
            if not images:
                raise HTTPException(
                    status_code=404, 
                    detail="No Street View imagery available for this location"
                )
            
            # Analyze multiple views
            result = clip_analyzer.analyze_multiple_views(images)
            
        else:
            # Single view
            image = streetview_fetcher.get_best_view(request.lat, request.lng)
            
            if not image:
                raise HTTPException(
                    status_code=404,
                    detail="No Street View imagery available for this location"
                )
            
            # Analyze single image
            result = clip_analyzer.analyze_image(image)
        
        # Create CLIP analysis response with all scores
        # Access nested structure from analyze_image result
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
            scores=result["scores"]  # Include all 28 prompt scores
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

