// Parse panoId from various input formats
export function parsePanoId(input: string): string | null {
  const trimmed = input.trim();
  
  // Direct panoId (22 characters, alphanumeric with _ and -)
  const panoIdPattern = /^[A-Za-z0-9_-]{22}$/;
  if (panoIdPattern.test(trimmed)) {
    return trimmed;
  }
  
  // Extract from Google Maps URL (format: !1s{panoId})
  const urlPattern = /!1s([A-Za-z0-9_-]{22})/;
  const urlMatch = trimmed.match(urlPattern);
  if (urlMatch) {
    return urlMatch[1];
  }
  
  // Extract from data parameter in URL
  const dataPattern = /[?&]data=[^&]*!1s([A-Za-z0-9_-]{22})/;
  const dataMatch = trimmed.match(dataPattern);
  if (dataMatch) {
    return dataMatch[1];
  }
  
  return null;
}

export function isValidCoordinate(lat: number, lng: number): boolean {
  return lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180;
}

export function formatNumber(num: number, decimals: number = 2): string {
  return num.toFixed(decimals);
}

export function getDifficultyColor(difficulty: number): string {
  if (difficulty <= 2) return '#22c55e'; // green
  if (difficulty === 3) return '#eab308'; // yellow
  if (difficulty === 4) return '#f97316'; // orange
  return '#ef4444'; // red
}

export function getDifficultyLabel(difficulty: number): string {
  switch (difficulty) {
    case 1: return 'Very Easy';
    case 2: return 'Easy';
    case 3: return 'Medium';
    case 4: return 'Hard';
    case 5: return 'Very Hard';
    default: return 'Unknown';
  }
}

