# PanoProbe Backend - CLIP Integration

Python FastAPI backend that provides AI-powered location difficulty analysis using OpenAI's CLIP model.

## Overview

This backend service:
- Fetches Street View panorama images from Google Maps API
- Analyzes images using CLIP (Vision Transformer)
- Detects visual features: text, landmarks, scene types
- Provides difficulty predictions based on visual analysis
- Integrates seamlessly with the React frontend

## Prerequisites

### Required
- Python 3.8 or higher
- pip or conda
- Google Maps API Key with Street View Static API enabled

### Hardware
- **Minimum**: 4GB RAM, modern CPU
- **Recommended**: 8GB+ RAM for faster inference
- **GPU**: Optional (will use CPU by default, which is fine for demo)

## Installation

### Step 1: Navigate to Backend Directory

```bash
cd backend
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Using venv
python -m venv venv

# Activate on Mac/Linux
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: This will download ~2GB of dependencies including PyTorch and the CLIP model. First-time installation takes 5-10 minutes.

### Step 4: Set Up Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# Copy example and edit
echo "GOOGLE_MAPS_API_KEY=your_api_key_here" > .env
echo "PORT=8000" >> .env
```

Or set environment variables directly:

```bash
export GOOGLE_MAPS_API_KEY=your_api_key_here
export PORT=8000
```

## Running the Backend

### Development Mode (with auto-reload)

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The server will start on `http://localhost:8000`

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Health Check

```bash
GET http://localhost:8000/
```

Response:
```json
{
  "status": "online",
  "clip_available": true,
  "streetview_available": true
}
```

### Detailed Health

```bash
GET http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "services": {
    "clip": "ready",
    "streetview": "ready"
  }
}
```

### Analyze Location

```bash
POST http://localhost:8000/api/analyze
Content-Type: application/json

{
  "lat": 40.758,
  "lng": -73.9855,
  "num_views": 1
}
```

Response:
```json
{
  "clip_analysis": {
    "difficulty": 1,
    "confidence": 0.87,
    "insights": [
      "🔤 Readable text/signs detected",
      "🏙️ Urban environment detected",
      "🏪 Business signs/storefronts detected"
    ],
    "scene_type": "urban",
    "has_text": true,
    "has_landmark": false,
    "is_generic": false,
    "is_urban": true,
    "raw_difficulty_score": 1.3
  },
  "combined_difficulty": 1,
  "combined_confidence": 0.87,
  "method": "clip",
  "reasoning": [
    "🔤 Readable text/signs detected",
    "🏙️ Urban environment detected"
  ]
}
```

### Test CLIP

```bash
POST http://localhost:8000/api/test-clip
```

Response:
```json
{
  "status": "ready",
  "model": "openai/clip-vit-base-patch32",
  "device": "cpu",
  "prompts_count": 10
}
```

## Architecture

### Files

- **`main.py`**: FastAPI application and endpoints
- **`clip_analyzer.py`**: CLIP model integration and analysis logic
- **`streetview_fetcher.py`**: Google Street View image fetching
- **`requirements.txt`**: Python dependencies

### Data Flow

```
Client Request (lat, lng)
    ↓
FastAPI Endpoint
    ↓
Street View Fetcher → Download panorama image
    ↓
CLIP Analyzer → Process image with vision model
    ↓
Difficulty Calculation → Interpret CLIP scores
    ↓
JSON Response → Return to frontend
```

### CLIP Analysis Process

1. **Image Acquisition**: Fetch panorama from Street View API
2. **Preprocessing**: Resize and normalize image for CLIP
3. **CLIP Inference**: Compare image against 10 difficulty-related prompts:
   - "a photo with clear readable text and signs"
   - "a photo of a famous landmark or monument"
   - "a generic road with no distinctive features"
   - "a photo of a remote rural area"
   - "a photo of a busy city street with many buildings"
   - "a photo with unique architecture"
   - "a blurry or low quality image"
   - "a photo with distinctive vegetation and plants"
   - "a highway or motorway with no landmarks"
   - "a photo with visible business signs and storefronts"
4. **Score Interpretation**: Convert CLIP similarities to difficulty (1-5)
5. **Insight Generation**: Generate human-readable explanations

## Performance

### First Request
- **Model Loading**: 3-5 seconds (one-time on startup)
- **Image Download**: 1-2 seconds
- **CLIP Inference**: 1-3 seconds (CPU)
- **Total**: ~5-10 seconds

### Subsequent Requests
- **Image Download**: 1-2 seconds
- **CLIP Inference**: 1-3 seconds
- **Total**: ~2-5 seconds

### GPU vs CPU
- **CPU**: 1-3 seconds per image (sufficient for demo)
- **GPU**: 0.1-0.5 seconds per image (if available)

## Troubleshooting

### "CLIP not initialized" Error

**Problem**: CLIP model failed to load

**Solutions**:
1. Check internet connection (needed for first download)
2. Ensure sufficient RAM (4GB minimum)
3. Check Python version (3.8+ required)
4. Reinstall transformers: `pip install --upgrade transformers torch`

### "Street View not available" Error

**Problem**: Missing or invalid Google Maps API key

**Solutions**:
1. Verify API key in `.env` file
2. Enable Street View Static API in Google Cloud Console
3. Check API key restrictions (should allow Street View)
4. Verify billing is enabled (free tier available)

### "No Street View imagery" Error

**Problem**: Location has no Street View coverage

**Solutions**:
- This is expected for some locations (middle of ocean, remote areas)
- Try a different location
- Frontend will fall back to heuristics-only analysis

### Slow Performance

**Problem**: Analysis taking >10 seconds

**Solutions**:
1. First request is always slower (model loading)
2. Ensure good internet for image download
3. Consider using GPU if available
4. Reduce `num_views` parameter (default: 1)

### Port Already in Use

**Problem**: Port 8000 is occupied

**Solutions**:
```bash
# Use different port
export PORT=8001
python main.py

# Or kill existing process
lsof -ti:8000 | xargs kill -9
```

## Development

### Adding New CLIP Prompts

Edit `clip_analyzer.py`:

```python
DIFFICULTY_PROMPTS = [
    "your new prompt here",
    # ... existing prompts
]
```

### Adjusting Difficulty Scoring

Edit `_interpret_scores()` in `clip_analyzer.py`:

```python
# Example: Make landmarks reduce difficulty more
if has_landmark:
    difficulty_score -= 2.0  # Was -1.5
```

### Testing Locally

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test analysis with example location
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"lat": 40.758, "lng": -73.9855}'
```

## Deployment

### Option 1: Local (Development)
Just run `python main.py` - suitable for hack day demos

### Option 2: Render.com (Recommended)
1. Push backend code to GitHub
2. Create new Web Service on Render
3. Set environment variables (GOOGLE_MAPS_API_KEY)
4. Deploy (auto-installs dependencies)
5. Update frontend `VITE_BACKEND_URL`

### Option 3: Railway.app
Similar to Render, supports Python out of the box

### Option 4: AWS Lambda + API Gateway
For production, use containerized Lambda with longer timeout

## Cost Estimates

### Development (Hack Day)
- CLIP Model: **$0** (open source)
- Street View: **$0-5** (~100 test requests)
- Server: **$0** (local)
- **Total: ~$0-5**

### Production (Monthly, 10k requests)
- CLIP: **$0** (self-hosted)
- Street View: **$70** (10k × $0.007)
- Server: **$7-20** (Render/Railway)
- **Total: ~$77-90/month**

## Security Notes

- **API Key**: Never commit `.env` to Git
- **CORS**: Configured for localhost by default
- **Rate Limiting**: Not implemented (add if deploying publicly)
- **Input Validation**: Basic validation present

## Next Steps

1. **Improve Prompts**: Fine-tune CLIP prompts for better accuracy
2. **Add Caching**: Cache results for frequently analyzed locations
3. **Multi-View Analysis**: Analyze multiple angles (set `num_views > 1`)
4. **GPU Support**: Add GPU inference for faster processing
5. **Batch Processing**: Support analyzing multiple locations at once

## Support

For issues or questions:
1. Check logs in terminal
2. Verify all dependencies installed
3. Test with curl/Postman before frontend
4. Check Google Maps API quota

## License

MIT License - Free to use and modify

