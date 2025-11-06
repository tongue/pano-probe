import { StreetViewMetadata } from '../types';

const BASE_URL = 'https://maps.googleapis.com/maps/api/streetview/metadata';

// Get API key from environment (optional)
const API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || '';

export async function getStreetViewMetadata(
  lat: number,
  lng: number,
  panoId?: string
): Promise<StreetViewMetadata | null> {
  // If no API key, return null (Street View features will be unavailable)
  if (!API_KEY) {
    console.warn('Google Maps API key not configured. Street View metadata unavailable.');
    return null;
  }
  
  const params = panoId 
    ? `?pano=${panoId}&key=${API_KEY}`
    : `?location=${lat},${lng}&key=${API_KEY}`;
  
  try {
    const response = await fetch(BASE_URL + params);
    
    if (!response.ok) {
      throw new Error(`Street View API error: ${response.status}`);
    }
    
    const data = await response.json();
    
    return {
      panoId: data.pano_id,
      date: data.date,
      copyright: data.copyright,
      status: data.status,
      location: data.location,
    };
  } catch (error) {
    console.error('Error fetching from Street View API:', error);
    return null;
  }
}

