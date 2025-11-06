import { DifficultyResult, CLIPAnalysis } from '../types';

/**
 * Combine heuristic and CLIP analyses into an ensemble prediction
 */
export function combineAnalyses(
  heuristicResult: DifficultyResult,
  clipAnalysis: CLIPAnalysis | null
): DifficultyResult {
  // If no CLIP analysis, return heuristic only
  if (!clipAnalysis) {
    return heuristicResult;
  }
  
  // Weighted average: 40% CLIP, 60% heuristics
  // (Heuristics more weighted since they're location-specific, CLIP is image-only)
  const clipWeight = 0.4;
  const heuristicWeight = 0.6;
  
  const combinedScore = 
    (clipAnalysis.difficulty * clipWeight) + 
    (heuristicResult.difficulty * heuristicWeight);
  
  const finalDifficulty = Math.round(combinedScore) as 1 | 2 | 3 | 4 | 5;
  
  // Combine confidence scores (take average)
  const combinedConfidence = (
    clipAnalysis.confidence * 0.5 + 
    heuristicResult.confidence * 0.5
  );
  
  // Merge reasons from both analyses
  const combinedReasons = [
    ...heuristicResult.reasons,
    ...clipAnalysis.insights.map(insight => `🤖 AI: ${insight}`)
  ];
  
  // Add comparison note
  const diff = Math.abs(clipAnalysis.difficulty - heuristicResult.difficulty);
  if (diff >= 2) {
    combinedReasons.push(
      `⚠️ AI and heuristics disagree (AI: ${clipAnalysis.difficulty}, Heuristic: ${heuristicResult.difficulty})`
    );
  }
  
  return {
    difficulty: finalDifficulty,
    confidence: combinedConfidence,
    reasons: combinedReasons,
    rawScore: combinedScore,
    breakdown: {
      ...heuristicResult.breakdown,
      // Add CLIP contribution to breakdown
    }
  };
}

/**
 * Get analysis method description
 */
export function getAnalysisMethod(hasClip: boolean): string {
  if (hasClip) {
    return 'Ensemble (AI + Heuristics)';
  }
  return 'Heuristics Only';
}

