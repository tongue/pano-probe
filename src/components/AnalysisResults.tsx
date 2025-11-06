import { useState } from 'react';
import { DifficultyResult } from '../types';

interface AnalysisResultsProps {
  result: DifficultyResult;
}

export function AnalysisResults({ result }: AnalysisResultsProps) {
  const [showBreakdown, setShowBreakdown] = useState(false);

  return (
    <div className="analysis-results">
      <div className="reasoning-section">
        <h3>Why This Score?</h3>
        <ul className="reasons-list">
          {result.reasons.map((reason, index) => (
            <li key={index}>{reason}</li>
          ))}
        </ul>
      </div>

      <button
        className="breakdown-toggle"
        onClick={() => setShowBreakdown(!showBreakdown)}
      >
        {showBreakdown ? '▼' : '▶'} Show Detailed Breakdown
      </button>

      {showBreakdown && (
        <div className="breakdown-section">
          <h4>Score Breakdown</h4>
          <div className="breakdown-grid">
            <div className="breakdown-item">
              <span className="breakdown-label">Geographic</span>
              <span className="breakdown-value">
                {result.breakdown.geographicScore > 0 ? '+' : ''}
                {result.breakdown.geographicScore.toFixed(1)}
              </span>
            </div>
            <div className="breakdown-item">
              <span className="breakdown-label">Urban/Rural</span>
              <span className="breakdown-value">
                {result.breakdown.urbanScore > 0 ? '+' : ''}
                {result.breakdown.urbanScore.toFixed(1)}
              </span>
            </div>
            <div className="breakdown-item">
              <span className="breakdown-label">Imagery Quality</span>
              <span className="breakdown-value">
                {result.breakdown.imageryScore > 0 ? '+' : ''}
                {result.breakdown.imageryScore.toFixed(1)}
              </span>
            </div>
            <div className="breakdown-item">
              <span className="breakdown-label">Uniqueness</span>
              <span className="breakdown-value">
                {result.breakdown.uniquenessScore > 0 ? '+' : ''}
                {result.breakdown.uniquenessScore.toFixed(1)}
              </span>
            </div>
          </div>
          <div className="raw-score">
            Raw Score: {result.rawScore.toFixed(2)} → Rounded to {result.difficulty}
          </div>
        </div>
      )}
    </div>
  );
}

