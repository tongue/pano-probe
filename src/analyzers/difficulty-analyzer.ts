import { DifficultyResult, LocationFeatures } from '../types';

function calculateConfidence(features: LocationFeatures): number {
  let confidence = 0.5; // Base confidence
  
  // More data = higher confidence
  if (features.copyright) confidence += 0.1;
  if (features.imageDate) confidence += 0.1;
  if (features.nearbyBuildingsCount > 0) confidence += 0.1;
  if (features.city) confidence += 0.1;
  if (features.hasNamedLandmarks) confidence += 0.2;
  
  return Math.min(1, confidence);
}

export function analyzeDifficulty(features: LocationFeatures): DifficultyResult {
  let score = 3.0; // Start at medium
  const reasons: string[] = [];
  
  // === GEOGRAPHIC DIFFICULTY ===
  let geoScore = 0;
  
  // Hard countries (few unique features)
  const hardCountries = ['RU', 'KZ', 'MN', 'BR', 'AU', 'CA'];
  if (hardCountries.includes(features.countryCode)) {
    geoScore += 0.8;
    reasons.push(`🌍 ${features.countryCode}: Large country with repetitive landscapes`);
  }
  
  // Easy countries (very distinctive)
  const easyCountries = ['JP', 'GB', 'NL', 'CH'];
  if (easyCountries.includes(features.countryCode)) {
    geoScore -= 0.5;
    reasons.push(`🌍 ${features.country}: Distinctive features`);
  }
  
  // === URBANIZATION SCORE ===
  let urbanScore = 0;
  
  if (features.urbanScore === 0) {
    urbanScore += 1.5;
    reasons.push(`🏜️ Isolated area (${features.nearbyBuildingsCount} buildings nearby)`);
  } else if (features.urbanScore === 3) {
    urbanScore -= 0.5;
    reasons.push(`🏙️ Urban area - more landmarks and signs`);
  }
  
  // Rural locations harder
  if (features.placeType === 'isolated' || features.placeType === 'hamlet') {
    urbanScore += 1;
    reasons.push(`📍 Very remote location`);
  }
  
  // === IMAGERY QUALITY ===
  let imageryScore = 0;
  
  if (features.isTrekkerImagery) {
    imageryScore += 1.5;
    reasons.push(`📷 Trekker imagery (often hiking trails or remote areas)`);
  }
  
  // Old imagery might be lower quality
  if (features.imageDate && features.imageDate < '2015') {
    imageryScore += 0.5;
    reasons.push(`📅 Older imagery (${features.imageDate})`);
  }
  
  // === UNIQUENESS SCORE ===
  let uniquenessScore = 0;
  
  if (features.hasNamedLandmarks) {
    uniquenessScore -= 1;
    reasons.push(`🏛️ Named landmarks nearby - easier to identify`);
  }
  
  if (features.nearbyPOIsCount > 10) {
    uniquenessScore -= 0.5;
    reasons.push(`📌 Many points of interest (${features.nearbyPOIsCount})`);
  }
  
  if (features.nearbyRoadsCount < 3) {
    uniquenessScore += 0.8;
    reasons.push(`🛤️ Few roads nearby - harder to navigate`);
  }
  
  // === CALCULATE FINAL SCORE ===
  const breakdown = {
    geographicScore: geoScore,
    urbanScore: urbanScore,
    imageryScore: imageryScore,
    uniquenessScore: uniquenessScore
  };
  
  const totalAdjustment = geoScore + urbanScore + imageryScore + uniquenessScore;
  score += totalAdjustment;
  
  // Clamp to 1-5
  const finalDifficulty = Math.min(5, Math.max(1, Math.round(score))) as 1 | 2 | 3 | 4 | 5;
  
  // Confidence based on how much data we have
  const confidence = calculateConfidence(features);
  
  return {
    difficulty: finalDifficulty,
    confidence,
    reasons,
    rawScore: score,
    breakdown
  };
}

