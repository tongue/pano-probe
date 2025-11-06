// Core types for PanoProbe

export type PlaceType = 'city' | 'town' | 'village' | 'hamlet' | 'isolated';

export interface LocationFeatures {
  // Basic info
  panoId?: string;
  lat: number;
  lng: number;
  
  // Geographic context (from Nominatim)
  country: string;
  countryCode: string;
  city?: string;
  state?: string;
  placeType: PlaceType;
  
  // OpenStreetMap features (from Overpass)
  nearbyBuildingsCount: number;
  nearbyRoadsCount: number;
  nearbyPOIsCount: number;
  hasNamedLandmarks: boolean;
  naturalFeaturesCount: number;
  
  // Street View metadata (from Google)
  imageDate?: string;
  copyright?: string;
  isTrekkerImagery: boolean;
  isHistoricalImagery: boolean;
  
  // Calculated features
  populationDensity: number; // 0-3 scale
  elevation?: number;
  urbanScore: number; // Calculated from OSM data (0-3)
}

export interface DifficultyBreakdown {
  geographicScore: number;
  urbanScore: number;
  imageryScore: number;
  uniquenessScore: number;
}

export interface DifficultyResult {
  difficulty: 1 | 2 | 3 | 4 | 5;
  confidence: number; // 0-1
  reasons: string[];
  rawScore: number;
  breakdown: DifficultyBreakdown;
}

export interface NominatimResponse {
  address: {
    country?: string;
    country_code?: string;
    city?: string;
    town?: string;
    village?: string;
    hamlet?: string;
    state?: string;
    suburb?: string;
  };
  display_name?: string;
}

export interface OverpassElement {
  type: string;
  tags?: {
    name?: string;
    building?: string;
    highway?: string;
    amenity?: string;
    tourism?: string;
    natural?: string;
    [key: string]: string | undefined;
  };
}

export interface OverpassResponse {
  elements: OverpassElement[];
}

export interface StreetViewMetadata {
  panoId?: string;
  date?: string;
  copyright?: string;
  status: string;
  location?: {
    lat: number;
    lng: number;
  };
}

export interface TestLocation {
  name: string;
  lat: number;
  lng: number;
  expectedDifficulty: number;
}

export interface CLIPAnalysis {
  hasText: boolean;
  hasLandmark: boolean;
  isGeneric: boolean;
  isUrban: boolean;
  sceneType: string;
  confidence: number;
  difficulty: number;
  insights: string[];
  rawDifficultyScore: number;
}

export interface AnalysisState {
  loading: boolean;
  error: string | null;
  features: LocationFeatures | null;
  result: DifficultyResult | null;
  clipAnalysis: CLIPAnalysis | null;
  backendAvailable: boolean;
}

