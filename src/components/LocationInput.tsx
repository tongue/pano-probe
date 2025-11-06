import { useState } from 'react';
import { parsePanoId } from '../utils/helpers';

interface LocationInputProps {
  onAnalyze: (panoId: string) => void;
  loading: boolean;
}

export function LocationInput({ onAnalyze, loading }: LocationInputProps) {
  const [input, setInput] = useState('');
  const [error, setError] = useState('');

  const handleAnalyze = () => {
    setError('');
    
    const panoId = parsePanoId(input);
    
    if (!panoId) {
      setError('Invalid panorama ID. Please enter a panoId (22 characters) or paste a Google Maps Street View URL');
      return;
    }
    
    onAnalyze(panoId);
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
          placeholder="Enter panorama ID or paste Google Maps Street View URL"
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

