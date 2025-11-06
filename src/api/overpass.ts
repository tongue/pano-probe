import { OverpassResponse } from '../types';

const OVERPASS_URL = 'https://overpass-api.de/api/interpreter';

export async function getNearbyFeatures(
  lat: number,
  lng: number,
  radiusMeters: number = 1000
): Promise<OverpassResponse> {
  // Query for interesting features around the location
  const query = `
    [out:json][timeout:10];
    (
      // Buildings with names (landmarks)
      way["name"]["building"](around:${radiusMeters},${lat},${lng});
      
      // Roads (indicates urban vs rural)
      way["highway"](around:${radiusMeters},${lat},${lng});
      
      // Points of interest
      node["amenity"](around:${radiusMeters},${lat},${lng});
      node["tourism"](around:${radiusMeters},${lat},${lng});
      
      // Natural features
      way["natural"](around:${radiusMeters},${lat},${lng});
    );
    out body;
  `;
  
  try {
    const response = await fetch(OVERPASS_URL, {
      method: 'POST',
      body: `data=${encodeURIComponent(query)}`,
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    
    if (!response.ok) {
      throw new Error(`Overpass API error: ${response.status}`);
    }
    
    const data: OverpassResponse = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching from Overpass API:', error);
    // Return empty result on error
    return { elements: [] };
  }
}

