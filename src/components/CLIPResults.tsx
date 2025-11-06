import { useState } from 'react';
import { CLIPAnalysis } from '../types';
import { getDifficultyColor, getDifficultyLabel } from '../utils/helpers';

interface CLIPResultsProps {
  clipAnalysis: CLIPAnalysis;
}

interface PromptCategory {
  name: string;
  emoji: string;
  prompts: string[];
  description: string;
}

const PROMPT_CATEGORIES: PromptCategory[] = [
  {
    name: "Very Strong Clues",
    emoji: "🏆",
    prompts: [
      "a photo of a famous landmark or monument",
      "a photo with country flags or national symbols"
    ],
    description: "Almost instant identification"
  },
  {
    name: "Text-Based Clues",
    emoji: "📝",
    prompts: [
      "a photo with clear readable text and signs",
      "a photo with visible business signs and storefronts",
      "a photo with colored road signs"
    ],
    description: "Strong indicators from text and signage"
  },
  {
    name: "GeoGuessr Meta",
    emoji: "🚧",
    prompts: [
      "a photo with road bollards or marker posts",
      "a photo with kilometer markers or mile markers",
      "a photo with a visible license plate",
      "a photo with distinctive street lights or lamp posts"
    ],
    description: "Country-specific features players use"
  },
  {
    name: "Architecture & Urban",
    emoji: "🏗️",
    prompts: [
      "a photo with unique architecture",
      "a photo of a busy city street with many buildings"
    ],
    description: "Building styles and urban density"
  },
  {
    name: "Environmental",
    emoji: "🌍",
    prompts: [
      "a photo with palm trees",
      "a photo with snow on the ground",
      "a photo with rice fields or paddy fields",
      "a photo with desert landscape",
      "a photo with distinctive vegetation and plants"
    ],
    description: "Climate and regional indicators"
  },
  {
    name: "Road Features",
    emoji: "🛣️",
    prompts: [
      "a photo with yellow center line markings",
      "a photo with white dashed road lines",
      "a photo with a roundabout or traffic circle"
    ],
    description: "Road markings and infrastructure"
  },
  {
    name: "Infrastructure",
    emoji: "⚡",
    prompts: [
      "a photo with overhead power lines"
    ],
    description: "Utilities and infrastructure"
  },
  {
    name: "Street View Specific",
    emoji: "📸",
    prompts: [
      "a photo with a Google Street View car shadow or reflection"
    ],
    description: "Street View metadata"
  },
  {
    name: "Hard Indicators",
    emoji: "🔴",
    prompts: [
      "a generic road with no distinctive features",
      "a photo of a remote rural area",
      "a highway or motorway with no landmarks"
    ],
    description: "Features that make location harder"
  },
  {
    name: "Image Quality",
    emoji: "⚠️",
    prompts: [
      "a blurry or low quality image"
    ],
    description: "Image quality assessment"
  }
];

function ScoreBar({ score, threshold = 0.15 }: { score: number; threshold?: number }) {
  const percentage = Math.round(score * 100);
  const isActive = score > threshold;
  const color = isActive ? '#22c55e' : '#6b7280';
  
  return (
    <div className="score-bar-container">
      <div className="score-bar-bg">
        <div 
          className="score-bar-fill"
          style={{ 
            width: `${percentage}%`,
            backgroundColor: color
          }}
        />
      </div>
      <span className="score-percentage" style={{ color }}>
        {percentage}%
      </span>
    </div>
  );
}

export function CLIPResults({ clipAnalysis }: CLIPResultsProps) {
  const [showDetails, setShowDetails] = useState(true);
  const color = getDifficultyColor(clipAnalysis.difficulty);
  const label = getDifficultyLabel(clipAnalysis.difficulty);

  // Get top scores
  const topScores = clipAnalysis.scores 
    ? Object.entries(clipAnalysis.scores)
        .sort(([, a], [, b]) => b - a)
        .slice(0, 5)
    : [];

  return (
    <div className="clip-results">
      <div className="clip-header">
        <h3>🤖 AI Vision Analysis (CLIP)</h3>
        <button 
          className="toggle-details-btn"
          onClick={() => setShowDetails(!showDetails)}
        >
          {showDetails ? '📊 Hide Details' : '📊 Show Details'}
        </button>
      </div>

      {/* Summary View */}
      <div className="clip-summary">
        <div className="clip-score-container">
          <div className="clip-score">
            <span className="clip-score-number" style={{ color }}>
              {clipAnalysis.difficulty}
            </span>
            <span className="clip-score-label" style={{ color }}>
              {label}
            </span>
          </div>
          
          <div className="clip-meta-info">
            <div className="meta-item">
              <span className="meta-label">Confidence:</span>
              <span className="meta-value">{Math.round(clipAnalysis.confidence * 100)}%</span>
            </div>
            <div className="meta-item">
              <span className="meta-label">Scene:</span>
              <span className="meta-value">{clipAnalysis.sceneType}</span>
            </div>
            <div className="meta-item">
              <span className="meta-label">Raw Score:</span>
              <span className="meta-value">{clipAnalysis.rawDifficultyScore.toFixed(2)}</span>
            </div>
            <div className="meta-item">
              <span className="meta-label">Prompts:</span>
              <span className="meta-value">28</span>
            </div>
          </div>
        </div>

        {/* Top 5 Detected Features */}
        {topScores.length > 0 && (
          <div className="top-scores">
            <h4>🎯 Top 5 Detected Features:</h4>
            <div className="top-scores-list">
              {topScores.map(([prompt, score], index) => (
                <div key={prompt} className="top-score-item">
                  <span className="rank">#{index + 1}</span>
                  <span className="prompt-name">{prompt.replace('a photo ', '')}</span>
                  <ScoreBar score={score} />
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Quick Feature Tags */}
        <div className="clip-features">
          <h4>Quick View:</h4>
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
              {clipAnalysis.isGeneric ? '✓' : '✗'} Generic
            </span>
          </div>
        </div>
      </div>

      {/* Detailed Verbose View */}
      {showDetails && clipAnalysis.scores && (
        <div className="clip-detailed-scores">
          <h4>📋 Complete Analysis (28 Prompts):</h4>
          <p className="detail-explanation">
            Scores represent CLIP's confidence that each feature is present in the image.
            Active features (green) are above the 15% threshold.
          </p>
          
          {PROMPT_CATEGORIES.map((category) => {
            const categoryScores = category.prompts.map(prompt => ({
              prompt,
              score: clipAnalysis.scores![prompt] || 0
            }));
            
            const hasActiveFeatures = categoryScores.some(s => s.score > 0.15);
            
            return (
              <div key={category.name} className={`score-category ${hasActiveFeatures ? 'has-active' : ''}`}>
                <div className="category-header">
                  <h5>
                    {category.emoji} {category.name}
                  </h5>
                  <p className="category-desc">{category.description}</p>
                </div>
                
                <div className="category-prompts">
                  {categoryScores.map(({ prompt, score }) => (
                    <div key={prompt} className={`prompt-score ${score > 0.15 ? 'active' : ''}`}>
                      <div className="prompt-text">
                        {score > 0.15 && <span className="active-indicator">✓</span>}
                        <span className="prompt-label">{prompt}</span>
                      </div>
                      <ScoreBar score={score} />
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* AI Insights */}
      <div className="clip-insights">
        <h4>💡 AI Insights ({clipAnalysis.insights.length}):</h4>
        {clipAnalysis.insights.length > 0 ? (
          <ul className="insights-list">
            {clipAnalysis.insights.map((insight, index) => (
              <li key={index}>{insight}</li>
            ))}
          </ul>
        ) : (
          <p className="no-insights">No specific features detected above threshold</p>
        )}
      </div>
    </div>
  );
}
