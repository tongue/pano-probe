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
    name: "Text & Language",
    emoji: "📝",
    prompts: [
      "a photo with clear readable text and signs",
      "a photo with visible business signs and storefronts",
      "a photo with colored road signs",
      "a photo with Cyrillic alphabet text",
      "a photo with Arabic or Hebrew script",
      "a photo with Chinese, Japanese, or Korean characters",
      "a photo with Thai or Southeast Asian script",
      "a photo with street name signs",
      "a photo with advertising billboards"
    ],
    description: "Text and script detection (instant region ID!)"
  },
  {
    name: "Road Surface & Infrastructure",
    emoji: "🛣️",
    prompts: [
      "a photo with road bollards or marker posts",
      "a photo with yellow center line markings",
      "a photo with white dashed road lines",
      "a photo with a roundabout or traffic circle",
      "a photo with kilometer markers or mile markers",
      "a photo of a dirt or unpaved road",
      "a photo of a cobblestone or brick paved road",
      "a photo of a red dirt road",
      "a photo with metal guardrails or crash barriers",
      "a photo with wooden guardrails",
      "a photo with concrete road barriers",
      "a photo with painted curbs or road edges",
      "a photo with chevron curve warning signs",
      "a photo with diagonal striped crosswalks",
      "a photo with parallel line crosswalks"
    ],
    description: "Road features & guardrails (expert GeoGuessr meta!)"
  },
  {
    name: "Architecture & Buildings",
    emoji: "🏗️",
    prompts: [
      "a photo with unique architecture",
      "a photo with brick buildings",
      "a photo with wooden houses",
      "a photo with concrete apartment blocks",
      "a photo with terracotta or tile roofs",
      "a photo with flat concrete roofs",
      "a photo with corrugated metal roofs",
      "a photo with modern glass buildings",
      "a photo with old historical buildings",
      "a photo of a European city with old architecture",
      "a photo of a narrow village street"
    ],
    description: "Building materials and architectural styles"
  },
  {
    name: "Utility & Infrastructure",
    emoji: "⚡",
    prompts: [
      "a photo with overhead power lines",
      "a photo with distinctive street lights or lamp posts",
      "a photo with wooden utility poles",
      "a photo with concrete utility poles",
      "a photo with electrical transformers on poles",
      "a photo with tram or trolley wires overhead",
      "a photo with sidewalks and pedestrian paths",
      "a photo with street parking spaces"
    ],
    description: "Utility poles and infrastructure (continent ID!)"
  },
  {
    name: "Environment & Vegetation",
    emoji: "🌍",
    prompts: [
      "a photo with distinctive vegetation and plants",
      "a photo with palm trees",
      "a photo with snow on the ground",
      "a photo with desert landscape",
      "a photo with rice fields or paddy fields",
      "a photo with tropical vegetation and humidity",
      "a photo with coniferous forest",
      "a photo with olive trees or Mediterranean plants",
      "a photo with mountains in the background",
      "a photo with flat plains landscape",
      "a photo with vineyards or grape fields",
      "a photo with wheat or grain fields",
      "a photo of a coastal or beach setting"
    ],
    description: "Climate, vegetation, and geographic features"
  },
  {
    name: "Vehicles & Transport",
    emoji: "🚗",
    prompts: [
      "a photo with a visible license plate",
      "a photo with a Google Street View car shadow or reflection",
      "a photo with a tuk-tuk or auto rickshaw",
      "a photo with pickup trucks",
      "a photo with motorcycles or scooters"
    ],
    description: "Regional vehicles (tuk-tuks = instant Asia!)"
  },
  {
    name: "Urban Characteristics",
    emoji: "🏙️",
    prompts: [
      "a photo of a busy city street with many buildings",
      "a photo of a remote rural area",
      "a generic road with no distinctive features",
      "a highway or motorway with no landmarks",
      "a photo with a wide multi-lane boulevard",
      "a photo of an Asian city with neon signs",
      "a photo of a North American suburb with large houses"
    ],
    description: "Urban vs. rural and regional city styles"
  },
  {
    name: "Street Furniture & Misc",
    emoji: "🪑",
    prompts: [
      "a photo with distinctive mailboxes or postal boxes",
      "a photo with public trash bins or waste containers",
      "a photo with benches or street seating",
      "a photo with bus stops or transit shelters",
      "a photo with red and white striped posts"
    ],
    description: "Street furniture and miscellaneous features"
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

  // Calculate total prompts dynamically
  const totalPrompts = PROMPT_CATEGORIES.reduce((sum, cat) => sum + cat.prompts.length, 0);
  
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

      {/* DEBUG: Show all 8 analyzed images (complete 360° coverage) */}
      {clipAnalysis.analyzedImages && (
        <div className="analyzed-image-debug">
          <h4>🔄 Complete 360° Analysis - All 8 Directions (Debug View):</h4>
          <p className="debug-note" style={{ marginBottom: '1rem' }}>
            CLIP analyzed 8 directions (every 45°) at HIGH RESOLUTION for complete coverage.
            Each view is 90° FOV at 2048×4096 resolution (zoom 4). No gaps, overlapping views!
          </p>
          <div className="eight-directions-grid">
            {['north', 'northeast', 'east', 'southeast', 'south', 'southwest', 'west', 'northwest'].map((direction) => (
              clipAnalysis.analyzedImages![direction] && (
                <div key={direction} className="direction-view">
                  <h5>{direction.toUpperCase().replace('NORTH', 'N').replace('SOUTH', 'S').replace('EAST', 'E').replace('WEST', 'W')}</h5>
                  <img 
                    src={`data:image/jpeg;base64,${clipAnalysis.analyzedImages![direction]}`}
                    alt={`${direction} view`}
                    className="clip-debug-image-small"
                  />
                </div>
              )
            ))}
          </div>
          <p className="debug-note">
            Scores shown below are averages across all 8 high-res views using 76 expert-level prompts!
            Features detected in ANY direction are marked as present.
            4× resolution + comprehensive prompts = CLIP can identify scripts, guardrails, poles, roofs, vegetation, and ALL GeoGuessr meta clues!
          </p>
        </div>
      )}

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
              <span className="meta-value">{totalPrompts}</span>
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
          <h4>📋 Complete Analysis ({totalPrompts} Expert-Level Prompts):</h4>
          <p className="detail-explanation">
            Scores represent CLIP's confidence that each feature is present in the image.
            Active features (green) are above the 15% threshold. Organized by category for expert GeoGuessr analysis.
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
