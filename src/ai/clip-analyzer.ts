// CLIP analyzer - calls Python backend with CLIP model

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
  scores?: Record<string, number>;  // All 28 prompt scores for verbose display
  analyzedImages?: Record<string, string>;  // Base64 encoded images for debugging (N,E,S,W)
}

export interface EnsembleAnalysis {
  clipAnalysis: CLIPAnalysis | null;
  combinedDifficulty: number;
  combinedConfidence: number;
  method: 'clip' | 'ensemble' | 'heuristic';
  reasoning: string[];
}

// Backend API configuration
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

export async function analyzeWithCLIP(
  lat: number, 
  lng: number,
  numViews: number = 1
): Promise<CLIPAnalysis | null> {
  try {
    console.log(`🤖 Calling CLIP backend for: ${lat}, ${lng}`);
    
    const response = await fetch(`${BACKEND_URL}/api/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ lat, lng, num_views: numViews }),
    });
    
    if (!response.ok) {
      if (response.status === 404) {
        console.warn('No Street View imagery available for this location');
        return null;
      }
      if (response.status === 503) {
        console.warn('CLIP backend not available');
        return null;
      }
      throw new Error(`Backend error: ${response.status}`);
    }
    
    const data: {
      clip_analysis: {
        difficulty: number;
        confidence: number;
        insights: string[];
        scene_type: string;
        has_text: boolean;
        has_landmark: boolean;
        is_generic: boolean;
        is_urban: boolean;
        raw_difficulty_score: number;
        scores?: Record<string, number>;
        analyzed_images?: Record<string, string>;
      }
    } = await response.json();
    
    console.log('✅ CLIP 360° analysis received:', data);
    
    return {
      hasText: data.clip_analysis.has_text,
      hasLandmark: data.clip_analysis.has_landmark,
      isGeneric: data.clip_analysis.is_generic,
      isUrban: data.clip_analysis.is_urban,
      sceneType: data.clip_analysis.scene_type,
      confidence: data.clip_analysis.confidence,
      difficulty: data.clip_analysis.difficulty,
      insights: data.clip_analysis.insights,
      rawDifficultyScore: data.clip_analysis.raw_difficulty_score,
      scores: data.clip_analysis.scores,
      analyzedImages: data.clip_analysis.analyzed_images,
    };
    
  } catch (error) {
    console.error('Error calling CLIP backend:', error);
    return null;
  }
}

// Check if backend is available
export async function checkBackendHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${BACKEND_URL}/health`, {
      method: 'GET',
      signal: AbortSignal.timeout(3000), // 3 second timeout
    });
    return response.ok;
  } catch (error) {
    console.warn('Backend not available:', error);
    return false;
  }
}

// Future prompts to use with CLIP:
export const CLIP_DIFFICULTY_PROMPTS = [
  "a photo with clear text and signs",
  "a photo of a famous landmark",
  "a generic road with no distinctive features",
  "a photo of a remote rural area",
  "a photo of a busy city street",
  "a photo with unique architecture",
  "a blurry low quality image",
  "a photo with distinctive vegetation"
];

// Example of how to combine CLIP with heuristics:
/*
export function combineAnalysis(
  heuristicResult: DifficultyResult,
  clipAnalysis: CLIPAnalysis
): DifficultyResult {
  const combinedScore = (
    heuristicResult.difficulty * 0.6 + 
    clipAnalysis.difficulty * 0.4
  );
  
  const reasons = [
    ...heuristicResult.reasons,
    clipAnalysis.hasText && 'AI detected readable text',
    clipAnalysis.hasLandmark && 'AI detected a landmark',
    clipAnalysis.isGeneric && 'AI indicates generic scenery',
  ].filter(Boolean);
  
  return {
    ...heuristicResult,
    difficulty: Math.round(combinedScore) as 1 | 2 | 3 | 4 | 5,
    reasons,
  };
}
*/

