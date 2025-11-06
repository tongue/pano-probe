# Changelog

## [Unreleased] - 2025-11-06

### 📊 Verbose CLIP Analysis Mode

#### Added
- **Detailed Score Visualization**
  - All 28 CLIP prompt scores now visible in frontend
  - Organized into 10 meaningful categories
  - Color-coded score bars (green = active, gray = inactive)
  - Top 5 detected features quick view
  - Toggle button to show/hide detailed analysis

- **Enhanced UI Components**
  - Score bars with percentage display
  - Category highlighting for active features
  - Metadata grid (confidence, scene, raw score, prompts count)
  - Interactive expand/collapse functionality

- **New Documentation**
  - `VERBOSE_MODE.md` - Complete guide to verbose display

#### Changed
- **Backend API**
  - `CLIPAnalysisResponse` now includes `scores` dict with all 28 prompts
  - Frontend receives complete analysis data for transparency

- **Frontend Display**
  - `CLIPResults` component completely redesigned
  - Summary view + expandable detailed view
  - Much more informative and professional presentation
  - 200+ lines of new CSS for score visualization

#### Benefits
- **Complete Transparency**: See exactly what CLIP detected
- **Educational**: Learn how AI analyzes images
- **Debugging**: Validate difficulty predictions
- **Professional**: Impressive demo presentation

---

### 🎯 GeoGuessr Meta Features: 28 CLIP Prompts

#### Added
- **18 New CLIP Detection Prompts** (10 → 28 total)
  - **Road Features**: Bollards, yellow/white lines, roundabouts, km markers
  - **Infrastructure**: Street lights, power lines, license plates
  - **Environment**: Palm trees, snow, rice fields, desert
  - **National**: Country flags and symbols
  - **Street View**: Google car shadow/reflection detection

#### Changed
- **Enhanced Difficulty Scoring**
  - Bollards: -0.7 (country-specific clues!)
  - Flags: -1.3 (direct country identification)
  - KM markers: -0.6 (distance information)
  - License plates: -0.6 (region identification)
  - Street lights: -0.5 (design varies by country)
  - Environmental clues: -0.4 each (climate narrowing)

#### Impact
- **Much more GeoGuessr-specific**: Features experienced players actually use
- **Better difficulty predictions**: Captures meta knowledge
- **Comprehensive analysis**: 28 prompts cover all major clue types
- **Professional-grade**: Now detects bollards, plates, and regional indicators

---

### 🚀 Major Upgrade: Street View Tiles API Integration

#### Added
- **High-Resolution Image Analysis**
  - New `backend/streetview_tiles.py` module for fetching Street View tiles
  - 2048×1024 resolution images (3× better than before)
  - Automatic tile stitching for seamless panoramas
  - Support for zoom levels 0-5 (currently using zoom 2)

- **Interactive 360° Panorama Viewer**
  - New `src/components/InteractivePanorama.tsx` component
  - Full 360° drag-to-look-around functionality
  - Scroll-to-zoom support
  - Fullscreen mode
  - Uses Google Maps JavaScript API

- **Documentation**
  - New `TILES_API_UPGRADE.md` with complete technical details
  - Updated `CLIP_SETUP_GUIDE.md` with new API requirements
  - Added "Technical Features" section explaining benefits

#### Changed
- **Backend**
  - `backend/streetview_fetcher.py` now uses Tiles API internally
  - Maintains backward compatibility with same API interface
  - Better image quality for CLIP analysis

- **Frontend**
  - `src/App.tsx` uses `InteractivePanorama` instead of `PanoramaPreview`
  - `src/App.css` added styles for interactive panorama viewer
  - `src/components/ExampleLocations.tsx` now displays panoId instead of expected difficulty
  - `src/components/InteractivePanorama.tsx` gracefully handles missing panoId

#### Technical Benefits
1. **Better AI Analysis**: Higher resolution = more details for CLIP
2. **Newer Imagery**: Tiles API often has more recent panoramas
3. **Better UX**: Interactive viewer provides immersive experience
4. **Same Cost**: No price increase ($7 per 1,000 panoramas)

#### Requirements
- Google Maps API key must now have both:
  - Street View Static API enabled
  - Maps JavaScript API enabled

#### Performance
- Tile fetching: ~1-2 seconds (8 tiles at zoom 2)
- Stitching: < 0.1 seconds
- Minimal overhead compared to Static API

---

## Previous Changes

### [Initial Release] - 2025-11-05

#### Added
- Initial PanoProbe implementation
- CLIP AI integration for image analysis
- Heuristic-based difficulty scoring
- Ensemble analyzer combining AI + heuristics
- React frontend with Vite
- FastAPI backend with CLIP model
- OpenStreetMap and Nominatim integration
- Street View metadata fetching
- PanoId-based location input
- Example test locations
- Comprehensive setup guide

