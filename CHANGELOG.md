# Changelog

## [Unreleased] - 2025-11-06

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

