import { useEffect, useRef } from 'react';

interface InteractivePanoramaProps {
  panoId?: string;
  lat: number;
  lng: number;
}

export function InteractivePanorama({ panoId, lat, lng }: InteractivePanoramaProps) {
  const panoramaRef = useRef<HTMLDivElement>(null);
  const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || '';

  useEffect(() => {
    if (!apiKey) {
      return;
    }

    // Load Google Maps JavaScript API if not already loaded
    if (!(window as any).google) {
      const script = document.createElement('script');
      script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}`;
      script.async = true;
      script.onload = initPanorama;
      document.head.appendChild(script);
    } else {
      initPanorama();
    }

    function initPanorama() {
      if (panoramaRef.current && (window as any).google) {
        const google = (window as any).google;
        
        const options: any = {
          pov: {
            heading: 0,
            pitch: 0,
          },
          zoom: 1,
          addressControl: false,
          linksControl: true,
          panControl: true,
          enableCloseButton: false,
          fullscreenControl: true,
        };
        
        // Use panoId if available, otherwise use lat/lng
        if (panoId) {
          options.pano = panoId;
        } else {
          options.position = { lat, lng };
        }
        
        new google.maps.StreetViewPanorama(panoramaRef.current, options);
      }
    }
  }, [panoId, apiKey]);

  if (!apiKey) {
    return (
      <div className="interactive-panorama">
        <div className="panorama-placeholder">
          <p>📍 Location: {lat.toFixed(4)}, {lng.toFixed(4)}</p>
          {panoId && <p>🆔 Pano ID: {panoId}</p>}
          <p className="note">Add Google Maps API key to see interactive Street View</p>
        </div>
      </div>
    );
  }

  return (
    <div className="interactive-panorama">
      <h3>Interactive Street View</h3>
      <p className="preview-note">Drag to look around • Scroll to zoom</p>
      <div 
        ref={panoramaRef} 
        className="panorama-viewer"
      />
      <div className="panorama-info">
        <span>📍 {lat.toFixed(6)}, {lng.toFixed(6)}</span>
        {panoId && <span> • 🆔 {panoId}</span>}
      </div>
    </div>
  );
}

