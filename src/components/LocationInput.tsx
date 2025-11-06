import { useState } from 'react';
import { parseCoordinates } from '../utils/helpers';

interface LocationInputProps {
  onAnalyze: (lat: number, lng: number) => void;
  loading: boolean;
}

export function LocationInput({ onAnalyze, loading }: LocationInputProps) {
  const [input, setInput] = useState('');
  const [error, setError] = useState('');

  const handleAnalyze = () => {
    setError('');
    
    const coords = parseCoordinates(input);
    
    if (!coords) {
      setError('Invalid coordinates. Please enter lat,lng (e.g., 40.758, -73.9855) or paste a Google Maps URL');
      return;
    }
    
    onAnalyze(coords.lat, coords.lng);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !loading) {
      handleAnalyze();
    }
  };

  return (
    <div className="location-input-container">
      <div className="input-group">
        <input
          type="text"
          className="location-input"
          placeholder="Enter coordinates (lat, lng) or Google Maps URL"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={loading}
        />
        <button
          className="analyze-button"
          onClick={handleAnalyze}
          disabled={loading}
        >
          {loading ? 'Analyzing...' : 'Analyze'}
        </button>
      </div>
      {error && <div className="error-message">{error}</div>}
    </div>
  );
}

