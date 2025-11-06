interface PanoramaPreviewProps {
  lat: number;
  lng: number;
}

export function PanoramaPreview({ lat, lng }: PanoramaPreviewProps) {
  // Google Street View Static API
  const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || '';
  
  // Generate Street View image URL
  const getStreetViewUrl = () => {
    if (!apiKey) {
      return null;
    }
    
    const params = new URLSearchParams({
      size: '640x400',
      location: `${lat},${lng}`,
      fov: '90',
      heading: '0',
      pitch: '0',
      key: apiKey
    });
    
    return `https://maps.googleapis.com/maps/api/streetview?${params.toString()}`;
  };

  const imageUrl = getStreetViewUrl();

  if (!imageUrl) {
    return (
      <div className="panorama-preview">
        <div className="panorama-placeholder">
          <p>📍 Location: {lat.toFixed(4)}, {lng.toFixed(4)}</p>
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
          alt={`Street View at ${lat}, ${lng}`}
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
      </div>
    </div>
  );
}

