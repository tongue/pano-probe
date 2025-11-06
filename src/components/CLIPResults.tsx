import { CLIPAnalysis } from '../types';
import { getDifficultyColor, getDifficultyLabel } from '../utils/helpers';

interface CLIPResultsProps {
  clipAnalysis: CLIPAnalysis;
}

export function CLIPResults({ clipAnalysis }: CLIPResultsProps) {
  const color = getDifficultyColor(clipAnalysis.difficulty);
  const label = getDifficultyLabel(clipAnalysis.difficulty);

  return (
    <div className="clip-results">
      <div className="clip-header">
        <h3>🤖 AI Vision Analysis (CLIP)</h3>
        <span className="clip-confidence">
          Confidence: {Math.round(clipAnalysis.confidence * 100)}%
        </span>
      </div>

      <div className="clip-score-container">
        <div className="clip-score">
          <span className="clip-score-number" style={{ color }}>
            {clipAnalysis.difficulty}
          </span>
          <span className="clip-score-label" style={{ color }}>
            {label}
          </span>
        </div>
        
        <div className="clip-scene-info">
          <div className="scene-type">
            <span className="label">Scene:</span>
            <span className="value">{clipAnalysis.sceneType}</span>
          </div>
        </div>
      </div>

      <div className="clip-features">
        <h4>Visual Features Detected:</h4>
        <div className="feature-tags">
          <span className={`feature-tag ${clipAnalysis.hasText ? 'active' : 'inactive'}`}>
            {clipAnalysis.hasText ? '✓' : '✗'} Text/Signs
          </span>
          <span className={`feature-tag ${clipAnalysis.hasLandmark ? 'active' : 'inactive'}`}>
            {clipAnalysis.hasLandmark ? '✓' : '✗'} Landmark
          </span>
          <span className={`feature-tag ${clipAnalysis.isUrban ? 'active' : 'inactive'}`}>
            {clipAnalysis.isUrban ? '✓' : '✗'} Urban
          </span>
          <span className={`feature-tag ${clipAnalysis.isGeneric ? 'active' : 'inactive'}`}>
            {clipAnalysis.isGeneric ? '✓' : '✗'} Generic Scene
          </span>
        </div>
      </div>

      <div className="clip-insights">
        <h4>AI Insights:</h4>
        <ul className="insights-list">
          {clipAnalysis.insights.map((insight, index) => (
            <li key={index}>{insight}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}

