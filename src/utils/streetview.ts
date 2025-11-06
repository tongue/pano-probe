// Utility to get lat/lng from panoId using Google Street View Metadata API

export interface PanoMetadata {
  panoId: string;
  lat: number;
  lng: number;
  date?: string;
  copyright?: string;
}

export async function getPanoMetadata(panoId: string): Promise<PanoMetadata | null> {
  const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;
  
  if (!apiKey) {
    throw new Error('Google Maps API key is required. Please set VITE_GOOGLE_MAPS_API_KEY in .env file');
  }
  
  const url = `https://maps.googleapis.com/maps/api/streetview/metadata?pano=${panoId}&key=${apiKey}`;
  
  try {
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`Street View API error: ${response.status}`);
    }
    
    const data = await response.json();
    
    if (data.status !== 'OK') {
      console.error('Street View metadata not found for panoId:', panoId);
      return null;
    }
    
    return {
      panoId: data.pano_id || panoId,
      lat: data.location.lat,
      lng: data.location.lng,
      date: data.date,
      copyright: data.copyright,
    };
  } catch (error) {
    console.error('Error fetching pano metadata:', error);
    throw error;
  }
}

