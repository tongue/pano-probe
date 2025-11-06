# 🤖 CLIP Integration Setup Guide

Complete guide to get PanoProbe running with full AI-powered CLIP analysis.

## Quick Start Checklist

- [ ] Python 3.8+ installed
- [ ] Google Maps API key obtained
- [ ] Backend dependencies installed
- [ ] Backend server running
- [ ] Frontend configured
- [ ] Test analysis working

## Step-by-Step Setup

### Part 1: Get Google Maps API Key (15 minutes)

#### 1. Create Google Cloud Project

1. Go to https://console.cloud.google.com
2. Click "Select a project" → "New Project"
3. Name it "PanoProbe" (or anything you like)
4. Click "Create"

#### 2. Enable Required APIs

1. In the console, go to "APIs & Services" → "Library"
2. Enable these APIs:
   - **Street View Static API** (for metadata and fallback)
   - **Maps JavaScript API** (for interactive panorama viewer)
3. For each API:
   - Search for it
   - Click on it
   - Click "Enable"

#### 3. Create API Key

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "API Key"
3. Copy the API key (looks like: `AIzaSyAbc123...`)
4. Click "Restrict Key" (recommended):
   - API restrictions: Select both:
     - "Street View Static API"
     - "Maps JavaScript API"
   - Save

#### 4. Enable Billing (Required)

1. Go to "Billing" in the console
2. Link a payment method
3. **Don't worry**: Google provides $200/month free credit
4. Street View costs ~$7 per 1,000 requests
5. For testing: ~100 requests = ~$0.70

**Cost for Hack Day**: Expect $0-5 total

---

### Part 2: Backend Setup (10 minutes)

#### 1. Open Terminal and Navigate

```bash
cd /Users/jb/tongue/pano-probe/backend
```

#### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

Your prompt should now show `(venv)`.

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This downloads ~2GB of packages. Takes 5-10 minutes. Get coffee! ☕

**What's being installed**:
- FastAPI (web framework)
- PyTorch (ML framework)
- Transformers (Hugging Face, includes CLIP)
- Pillow (image processing)
- Requests (HTTP client)

#### 4. Create .env File

```bash
echo "GOOGLE_MAPS_API_KEY=your_actual_api_key_here" > .env
echo "PORT=8000" >> .env
```

**Replace `your_actual_api_key_here` with your actual API key!**

#### 5. Test Backend

```bash
python main.py
```

You should see:
```
Loading CLIP model: openai/clip-vit-base-patch32...
Using device: cpu
CLIP model loaded successfully!
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**First startup takes 30-60 seconds** (downloading CLIP model - 350MB)

#### 6. Verify It Works

Open a new terminal and test:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "services": {
    "clip": "ready",
    "streetview": "ready"
  }
}
```

✅ **Backend is ready!**

---

### Part 3: Frontend Setup (2 minutes)

#### 1. Open New Terminal

```bash
cd /Users/jb/tongue/pano-probe
```

#### 2. (Optional) Configure Backend URL

If backend is on a different port or machine:

```bash
echo "VITE_BACKEND_URL=http://localhost:8000" > .env
```

Default is `http://localhost:8000`, so this is optional.

#### 3. Start Frontend

```bash
npm run dev
```

#### 4. Open Browser

Go to: http://localhost:5173

You should see:
- **Green badge**: "🤖 CLIP AI: Online" (if backend is running)
- **Yellow badge**: "⚠️ CLIP AI: Offline" (if backend is not running)

---

### Part 4: Test the Full System (5 minutes)

#### Test 1: Easy Location (Times Square)

1. Enter coordinates: `40.758, -73.9855`
2. Click "Analyze"
3. Wait 5-10 seconds (first request is slower)
4. You should see:
   - **Main difficulty score** (probably 1-2)
   - **🤖 AI Vision Analysis (CLIP)** section with:
     - CLIP's difficulty prediction
     - Visual features detected (text, urban, etc.)
     - AI insights
   - **Why This Score?** section with combined reasoning
   - **Extracted Features** from OSM/Nominatim

#### Test 2: Hard Location (Siberian Highway)

1. Enter coordinates: `61.5, 105.3`
2. Click "Analyze"
3. Should see:
   - Difficulty 4-5
   - CLIP detects: generic road, remote area
   - Heuristics detect: Russia, isolated, few features

#### Test 3: Use Example Buttons

Click "Tokyo Shibuya Crossing" - should get:
- Difficulty 2
- CLIP detects: urban, text, distinctive
- Fast analysis (2-3 seconds)

---

## Troubleshooting

### Backend Won't Start

**Error: "CLIP not initialized"**

Solution:
```bash
# Reinstall dependencies
pip install --upgrade torch transformers

# Try again
python main.py
```

**Error: "Port 8000 already in use"**

Solution:
```bash
# Kill existing process
lsof -ti:8000 | xargs kill -9

# Or use different port
export PORT=8001
python main.py
```

### Frontend Shows "CLIP AI: Offline"

**Check 1**: Is backend running?
```bash
# In backend terminal, you should see:
# "Uvicorn running on http://0.0.0.0:8000"
```

**Check 2**: Test backend directly
```bash
curl http://localhost:8000/health
```

**Check 3**: Check browser console (F12 → Console tab)
- Look for errors
- Should see: "✅ CLIP backend is available"

### Analysis Returns 404

**Error**: "No Street View imagery available"

This means Google has no Street View for that location. Try:
- Different coordinates
- Known locations (cities, tourist spots)
- Use example locations

### Analysis is Slow

**First request**: 5-10 seconds (model loading + image download)
**Subsequent requests**: 2-5 seconds (just image + inference)

If consistently slow (>10 seconds):
1. Check internet speed (images are ~500KB each)
2. Backend logs should show timing
3. Consider adding GPU (optional)

### Different Results Than Expected

This is normal! CLIP and heuristics analyze different things:
- **CLIP**: Only what's visible in the image
- **Heuristics**: Geographic context, OSM data, location metadata
- **Ensemble**: Weighted combination (40% CLIP, 60% heuristics)

The disagreement is actually interesting - shows what each method sees!

---

## Understanding the Results

### Difficulty Display (Top)
- **Main Score**: Ensemble prediction (1-5)
- **Confidence**: How certain the system is
- **Progress Bar**: Visual representation

### 🤖 AI Vision Analysis (If Backend Online)
- **CLIP Score**: What AI sees in the image
- **Scene Type**: urban/rural/highway/landmark
- **Feature Tags**: Binary detection (✓/✗)
  - Text/Signs: Readable text visible
  - Landmark: Famous place detected
  - Urban: City environment
  - Generic: Non-distinctive scene
- **AI Insights**: Natural language explanations

### Why This Score? (Reasoning)
- Combines both CLIP and heuristic reasons
- Items marked "🤖 AI:" came from CLIP
- Other items from heuristics
- May show disagreement warning if AI and heuristics differ significantly

### Extracted Features (Bottom)
- Geographic data from Nominatim
- OSM features (buildings, roads, POIs)
- Calculated scores (urban score, population density)

---

## Technical Features

### High-Resolution Image Analysis (Tiles API)

PanoProbe uses the **Street View Tiles API** instead of the basic Static API for superior image quality:

**Benefits:**
- 📸 **2048×1024 resolution** (vs 640×640 static)
- 🎯 **Better CLIP analysis** - More details = better AI understanding
- 🆕 **Newer panoramas** - Tiles API often has more recent imagery
- 💰 **Same cost** - $7 per 1,000 panoramas

**How It Works:**
1. Backend fetches multiple 512×512 tiles at zoom level 2
2. Tiles are stitched into a 2048×1024 front-view panorama
3. CLIP analyzes this high-resolution image
4. Result: Much more accurate feature detection

### Interactive 360° Panorama Viewer

The frontend displays a fully interactive Street View panorama:

**Features:**
- 🔄 **Drag to look around** - Full 360° view
- 🔍 **Scroll to zoom** - Get closer to details
- 🗺️ **Pan controls** - Explore the location
- 🎬 **Fullscreen mode** - Immersive viewing

This viewer uses the **Google Maps JavaScript API** to embed the actual Street View panorama, giving you the same experience as Google Maps but integrated into the analysis results.

---

## Advanced Configuration

### Multiple Views

Edit frontend request to analyze multiple angles:

```typescript
// In src/ai/clip-analyzer.ts
analyzeWithCLIP(lat, lng, 4)  // Analyze 4 directions
```

This makes analysis more robust but 4x slower.

### Adjust Ensemble Weights

Edit `src/analyzers/ensemble-analyzer.ts`:

```typescript
// Default: 40% CLIP, 60% heuristics
const clipWeight = 0.5;        // Give CLIP more weight
const heuristicWeight = 0.5;
```

### Add Custom CLIP Prompts

Edit `backend/clip_analyzer.py`:

```python
DIFFICULTY_PROMPTS = [
    "your new prompt here",
    # ... existing prompts
]
```

Then restart backend.

---

## Performance Optimization

### Faster Inference (If you have GPU)

Backend automatically uses GPU if available:

```bash
# Check if GPU is detected
python -c "import torch; print(torch.cuda.is_available())"
```

If True: CLIP will be 10x faster (~0.1-0.5s per image)

### Caching Results

For production, add Redis caching:

```python
# In backend/main.py
@lru_cache(maxsize=1000)
def cached_analysis(lat, lng):
    # ... analysis code
```

---

## Costs Summary

### Google Maps API

| Usage | Cost | Free Tier |
|-------|------|-----------|
| 100 requests (testing) | $0.70 | Within $200 credit |
| 1,000 requests (demo) | $7 | Within $200 credit |
| 10,000 requests/month | $70 | Need to pay |

### Server Hosting

| Platform | Cost | Notes |
|----------|------|-------|
| Local (hack day) | $0 | Run on your machine |
| Render.com | $7/mo | Easy deployment |
| Railway.app | $5/mo | Similar to Render |
| AWS Lambda | $0-10/mo | Pay per use |

### Total Hack Day Cost: $0-5

---

## Success Checklist

After setup, you should be able to:

- [x] See "🤖 CLIP AI: Online" in green
- [x] Analyze Times Square → Get difficulty 1-2
- [x] See CLIP analysis section with insights
- [x] Analyze Siberian Highway → Get difficulty 4-5
- [x] See combined reasoning (AI + heuristics)
- [x] Analysis completes in 2-10 seconds
- [x] No errors in browser console or backend logs

---

## Next Steps

**For Hack Day Demo**:
1. Test with 5-10 diverse locations
2. Note interesting AI insights
3. Show cases where CLIP and heuristics disagree
4. Demonstrate "ensemble is smarter than either alone"

**For Production**:
1. Add caching (Redis)
2. Deploy backend to cloud (Render/Railway)
3. Add rate limiting
4. Collect user feedback
5. Fine-tune CLIP prompts based on results

---

## Demo Tips

**Great demo locations**:
- **Times Square** (40.758, -73.9855) - Shows AI detecting text/signs
- **Eiffel Tower** (48.8584, 2.2945) - Shows landmark detection
- **Generic Highway** (61.5, 105.3) - Shows high difficulty
- **Tokyo Shibuya** (35.6595, 139.7004) - Shows distinctive features

**What to highlight**:
- "AI analyzes the actual image, not just location data"
- "CLIP detects text, landmarks, scene types automatically"
- "Ensemble combines computer vision + geographic data"
- "No ML training needed - using pre-trained CLIP"
- "Free and open source (except Street View API)"

---

## Need Help?

1. **Backend logs**: Check terminal running `python main.py`
2. **Frontend logs**: Browser console (F12)
3. **Test APIs separately**: Use curl/Postman
4. **Check firewall**: Ensure port 8000 accessible
5. **Verify Python**: `python --version` should be 3.8+

**Ready to demo!** 🚀

