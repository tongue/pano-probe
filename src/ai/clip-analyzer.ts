// Mock CLIP analyzer for future integration
// In production, this would call a backend service running CLIP model

export interface CLIPAnalysis {
  hasText: boolean;
  hasLandmark: boolean;
  isGeneric: boolean;
  sceneType: string;
  confidence: number;
  difficulty: number;
}

// This is a placeholder that returns mock results
// In a real implementation, this would:
// 1. Send the image to a backend service
// 2. Run CLIP inference with difficulty-related prompts
// 3. Return semantic understanding of the image
export async function analyzewithCLIP(imageUrl: string): Promise<CLIPAnalysis> {
  console.log('CLIP analysis not yet implemented. Using mock data.');
  console.log('Image URL:', imageUrl);
  
  // For future implementation:
  // const response = await fetch('/api/clip/analyze', {
  //   method: 'POST',
  //   body: JSON.stringify({ imageUrl }),
  //   headers: { 'Content-Type': 'application/json' }
  // });
  // return await response.json();
  
  // Mock response for now
  return {
    hasText: false,
    hasLandmark: false,
    isGeneric: true,
    sceneType: 'unknown',
    confidence: 0.5,
    difficulty: 3,
  };
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

