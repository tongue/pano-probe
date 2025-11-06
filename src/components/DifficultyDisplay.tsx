import { getDifficultyColor, getDifficultyLabel } from '../utils/helpers';

interface DifficultyDisplayProps {
  difficulty: 1 | 2 | 3 | 4 | 5;
  confidence: number;
}

export function DifficultyDisplay({ difficulty, confidence }: DifficultyDisplayProps) {
  const color = getDifficultyColor(difficulty);
  const label = getDifficultyLabel(difficulty);
  const percentage = (difficulty / 5) * 100;

  return (
    <div className="difficulty-display">
      <div className="difficulty-header">
        <h2>Difficulty Score</h2>
        <span className="confidence-badge">
          Confidence: {Math.round(confidence * 100)}%
        </span>
      </div>
      
      <div className="difficulty-gauge">
        <div className="difficulty-number" style={{ color }}>
          {difficulty}
        </div>
        <div className="difficulty-label" style={{ color }}>
          {label}
        </div>
      </div>
      
      <div className="difficulty-bar-container">
        <div 
          className="difficulty-bar"
          style={{ 
            width: `${percentage}%`,
            backgroundColor: color
          }}
        />
      </div>
      
      <div className="difficulty-scale">
        <span>1 (Easy)</span>
        <span>5 (Hard)</span>
      </div>
    </div>
  );
}

