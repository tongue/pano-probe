# PanoProbe Quick Start Guide

## 🚀 Ready to Run in 30 Seconds

The project is **fully implemented and ready to use**. All dependencies are installed.

## Start Development Server

```bash
cd /Users/jb/tongue/pano-probe
npm run dev
```

Then open http://localhost:5173 in your browser.

## Try It Out

### Option 1: Use Example Locations
Click any of the pre-loaded buttons:
- Times Square, NYC
- Siberian Highway
- Tokyo Shibuya
- Australian Outback
- Swiss Alps Village

### Option 2: Enter Custom Coordinates
Type coordinates in the format: `40.758, -73.9855`

### Option 3: Paste Google Maps URL
Copy any Google Maps URL and paste it in the input box.

## What You'll See

1. **Loading State** - Spinner while fetching data (2-3 seconds)
2. **Difficulty Score** - Big number (1-5) with color coding
3. **Reasoning** - Why it got that score (country, urban level, features)
4. **Breakdown** - Detailed scoring factors
5. **Features** - All extracted geographic data

## Testing the Demo

### Easy Location (Score 1-2)
Try: `40.7580, -73.9855` (Times Square)
- Should show: Urban area, many POIs, landmarks

### Hard Location (Score 4-5)
Try: `61.5, 105.3` (Siberian Highway)
- Should show: Isolated, few features, repetitive landscape

## Optional: Add Google API Key

For Street View metadata (image dates, copyright):

1. Create `.env` file:
```
VITE_GOOGLE_MAPS_API_KEY=your_key_here
```

2. Restart the dev server

Note: App works fine without this!

## Production Build

```bash
npm run build      # Creates dist/ folder
npm run preview    # Preview production build
```

## Architecture Overview

```
User enters coordinates
    ↓
Parallel API calls:
  - Nominatim (geocoding)
  - Overpass (OSM features)
  - Street View (optional)
    ↓
Feature extraction
    ↓
Difficulty analysis
    ↓
Display results
```

## Key Files to Understand

- `src/App.tsx` - Main application logic
- `src/features/location-features.ts` - Feature extraction
- `src/analyzers/difficulty-analyzer.ts` - Scoring algorithm
- `src/components/` - UI components

## Troubleshooting

**API taking too long?**
- Nominatim rate limits to 1 req/sec (normal)
- Overpass might be slow sometimes (retry)

**Can't parse coordinates?**
- Format: `lat, lng` with comma
- Or paste full Google Maps URL

**Need help?**
- Check README.md for full documentation
- Check IMPLEMENTATION_SUMMARY.md for architecture

## Demo Script Location

See README.md section: "Demo Script (5-minute presentation)"

---

**You're all set!** The project is production-ready. 🎉

Run `npm run dev` and start analyzing locations!

