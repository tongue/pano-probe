import { NominatimResponse } from '../types';

const BASE_URL = 'https://nominatim.openstreetmap.org/reverse';

// Rate limiting: Nominatim requires 1 request per second
let lastRequestTime = 0;
const MIN_REQUEST_INTERVAL = 1000; // 1 second

async function rateLimitedFetch(url: string): Promise<Response> {
  const now = Date.now();
  const timeSinceLastRequest = now - lastRequestTime;
  
  if (timeSinceLastRequest < MIN_REQUEST_INTERVAL) {
    const waitTime = MIN_REQUEST_INTERVAL - timeSinceLastRequest;
    await new Promise(resolve => setTimeout(resolve, waitTime));
  }
  
  lastRequestTime = Date.now();
  return fetch(url);
}

export async function reverseGeocode(lat: number, lng: number): Promise<NominatimResponse> {
  const url = `${BASE_URL}?lat=${lat}&lon=${lng}&format=json&zoom=10`;
  
  try {
    const response = await rateLimitedFetch(url);
    
    if (!response.ok) {
      throw new Error(`Nominatim API error: ${response.status}`);
    }
    
    const data: NominatimResponse = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching from Nominatim:', error);
    throw error;
  }
}

