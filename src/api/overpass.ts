import { OverpassResponse } from '../types';

const FALLBACK_OVERPASS_URLS = [
  'https://overpass.kumi.systems/api/interpreter',
  'https://overpass-api.de/api/interpreter',
];

async function fetchWithTimeout(url: string, options: RequestInit, timeoutMs: number = 25000) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);
  
  try {
    const response = await fetch(url, { ...options, signal: controller.signal });
    clearTimeout(timeout);
    return response;
  } catch (error) {
    clearTimeout(timeout);
    throw error;
  }
}

async function retryFetch(
  urls: string[], 
  body: string, 
  maxRetries: number = 2
): Promise<Response | null> {
  for (const url of urls) {
    for (let attempt = 0; attempt < maxRetries; attempt++) {
      try {
        console.log(`🔄 Overpass attempt ${attempt + 1}/${maxRetries} on ${url.includes('kumi') ? 'kumi.systems' : 'overpass-api.de'}...`);
        
        const response = await fetchWithTimeout(url, {
          method: 'POST',
          body,
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        }, 25000); // 25 second timeout
        
        if (response.ok) {
          console.log('✅ Overpass API success!');
          return response;
        }
        
        // If 504/503/429, retry after delay
        if ([503, 504, 429].includes(response.status)) {
          const delay = Math.min(1000 * Math.pow(2, attempt), 5000); // Exponential backoff, max 5s
          console.warn(`⏳ Overpass returned ${response.status}, retrying in ${delay}ms...`);
          await new Promise(resolve => setTimeout(resolve, delay));
          continue;
        }
        
        // Other errors, don't retry
        break;
      } catch (error) {
        console.warn(`⚠️ Overpass attempt failed:`, error);
        if (attempt < maxRetries - 1) {
          const delay = Math.min(1000 * Math.pow(2, attempt), 3000);
          await new Promise(resolve => setTimeout(resolve, delay));
        }
      }
    }
  }
  return null;
}

export async function getNearbyFeatures(
  lat: number,
  lng: number,
  radiusMeters: number = 500 // Reduced from 1000m to 500m for faster queries
): Promise<OverpassResponse> {
  // Simplified query for faster results
  const query = `
    [out:json][timeout:20];
    (
      // Named buildings (landmarks) - most important
      way["name"]["building"](around:${radiusMeters},${lat},${lng});
      
      // Major roads only (highway types that matter for GeoGuessr)
      way["highway"~"^(motorway|trunk|primary|secondary)$"](around:${radiusMeters},${lat},${lng});
      
      // Key amenities only
      node["amenity"~"^(restaurant|cafe|shop|bank|hospital)$"](around:${radiusMeters},${lat},${lng});
      
      // Tourism landmarks
      node["tourism"](around:${radiusMeters},${lat},${lng});
    );
    out body;
  `;
  
  try {
    const body = `data=${encodeURIComponent(query)}`;
    const response = await retryFetch(FALLBACK_OVERPASS_URLS, body);
    
    if (!response) {
      console.warn('🚫 All Overpass attempts failed, returning empty results');
      return { elements: [] };
    }
    
    const data: OverpassResponse = await response.json();
    console.log(`📊 Overpass returned ${data.elements.length} features`);
    return data;
    
  } catch (error) {
    console.error('❌ Error fetching from Overpass API:', error);
    return { elements: [] };
  }
}

