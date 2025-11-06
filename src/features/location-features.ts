import { LocationFeatures, PlaceType, NominatimResponse, OverpassResponse } from '../types';
import { reverseGeocode } from '../api/nominatim';
import { getNearbyFeatures } from '../api/overpass';
import { getStreetViewMetadata } from '../api/streetview';

function determinePlaceType(geocode: NominatimResponse): PlaceType {
  const addr = geocode.address;
  if (addr.city) return 'city';
  if (addr.town) return 'town';
  if (addr.village) return 'village';
  if (addr.hamlet) return 'hamlet';
  return 'isolated';
}

function estimatePopulationDensity(geocode: NominatimResponse): number {
  const type = geocode.address;
  
  // Rough heuristic based on place type
  if (type.city) return 3; // Urban
  if (type.town) return 2; // Suburban
  if (type.village) return 1; // Rural
  return 0; // Remote
}

function calculateUrbanScore(osmFeatures: OverpassResponse): number {
  const buildings = osmFeatures.elements.filter(e => e.tags?.building).length;
  const roads = osmFeatures.elements.filter(e => e.tags?.highway).length;
  const pois = osmFeatures.elements.filter(e => e.tags?.amenity).length;
  
  // Simple scoring: more features = more urban
  const totalFeatures = buildings + roads + pois;
  
  if (totalFeatures > 50) return 3; // High urban
  if (totalFeatures > 20) return 2; // Medium urban
  if (totalFeatures > 5) return 1;  // Low urban
  return 0; // Rural/remote
}

export async function extractFeatures(
  lat: number, 
  lng: number, 
  panoId?: string
): Promise<LocationFeatures> {
  console.log(`🔍 Extracting features for: ${lat}, ${lng}`);
  
  // Run API calls in parallel (faster!)
  const [geocode, osmFeatures, svMetadata] = await Promise.all([
    reverseGeocode(lat, lng),
    getNearbyFeatures(lat, lng, 1000),
    panoId || import.meta.env.VITE_GOOGLE_MAPS_API_KEY 
      ? getStreetViewMetadata(lat, lng, panoId) 
      : Promise.resolve(null)
  ]);
  
  // Parse and structure the data
  const features: LocationFeatures = {
    panoId,
    lat,
    lng,
    
    // From Nominatim
    country: geocode.address.country || 'Unknown',
    countryCode: (geocode.address.country_code || 'XX').toUpperCase(),
    city: geocode.address.city || geocode.address.town,
    state: geocode.address.state,
    placeType: determinePlaceType(geocode),
    
    // From Overpass
    nearbyBuildingsCount: osmFeatures.elements.filter(e => e.tags?.building).length,
    nearbyRoadsCount: osmFeatures.elements.filter(e => e.tags?.highway).length,
    nearbyPOIsCount: osmFeatures.elements.filter(e => e.tags?.amenity || e.tags?.tourism).length,
    hasNamedLandmarks: osmFeatures.elements.some(e => e.tags?.name && e.tags?.tourism),
    naturalFeaturesCount: osmFeatures.elements.filter(e => e.tags?.natural).length,
    
    // From Street View
    imageDate: svMetadata?.date,
    copyright: svMetadata?.copyright,
    isTrekkerImagery: svMetadata?.copyright ? !svMetadata.copyright.includes('Google') : false,
    isHistoricalImagery: false, // TODO: compare imageDate to current
    
    // Calculated
    populationDensity: estimatePopulationDensity(geocode),
    urbanScore: calculateUrbanScore(osmFeatures),
  };
  
  return features;
}

