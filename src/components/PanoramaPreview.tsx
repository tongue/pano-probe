interface PanoramaPreviewProps {
  lat: number;
  lng: number;
  panoId?: string;
}

export function PanoramaPreview({ lat, lng, panoId }: PanoramaPreviewProps) {
  // Google Street View Static API
  const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || '';
  
  // Generate Street View image URL
  const getStreetViewUrl = () => {
    if (!apiKey) {
      return null;
    }
    
    // Use panoId if available for exact match, otherwise use lat/lng
    const params = new URLSearchParams({
      size: '640x400',
      fov: '90',
      heading: '0',
      pitch: '0',
      key: apiKey
    });
    
    if (panoId) {
      params.set('pano', panoId);
    } else {
      params.set('location', `${lat},${lng}`);
    }
    
    return `https://maps.googleapis.com/maps/api/streetview?${params.toString()}`;
  };

  const imageUrl = getStreetViewUrl();

  if (!imageUrl) {
    return (
      <div className="panorama-preview">
        <div className="panorama-placeholder">
          <p>📍 Location: {lat.toFixed(4)}, {lng.toFixed(4)}</p>
          {panoId && <p>🆔 Pano ID: {panoId}</p>}
          <p className="note">Add Google Maps API key to see Street View preview</p>
        </div>
      </div>
    );
  }

  return (
    <div className="panorama-preview">
      <h3>Street View Preview</h3>
      <p className="preview-note">This is what CLIP AI analyzes</p>
      <div className="panorama-container">
        <img 
          src={imageUrl} 
          alt={`Street View panorama`}
          className="panorama-image"
          onError={(e) => {
            const target = e.target as HTMLImageElement;
            target.style.display = 'none';
            const parent = target.parentElement;
            if (parent) {
              parent.innerHTML = '<div class="panorama-error">⚠️ No Street View imagery available for this location</div>';
            }
          }}
        />
      </div>
      <div className="panorama-info">
        <span>📍 {lat.toFixed(6)}, {lng.toFixed(6)}</span>
        {panoId && <span> • 🆔 {panoId}</span>}
      </div>
    </div>
  );
}

