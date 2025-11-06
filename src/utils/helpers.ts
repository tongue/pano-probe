// Parse coordinates from various input formats
export function parseCoordinates(input: string): { lat: number; lng: number } | null {
  // Try to match lat,lng format
  const coordPattern = /^(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)$/;
  const match = input.trim().match(coordPattern);
  
  if (match) {
    const lat = parseFloat(match[1]);
    const lng = parseFloat(match[2]);
    
    if (isValidCoordinate(lat, lng)) {
      return { lat, lng };
    }
  }
  
  // Try to extract from Google Maps URL
  const gmapsPattern = /@(-?\d+\.?\d*),(-?\d+\.?\d*)/;
  const gmapsMatch = input.match(gmapsPattern);
  
  if (gmapsMatch) {
    const lat = parseFloat(gmapsMatch[1]);
    const lng = parseFloat(gmapsMatch[2]);
    
    if (isValidCoordinate(lat, lng)) {
      return { lat, lng };
    }
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

