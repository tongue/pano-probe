import { useState } from 'react';
import { LocationInput } from './components/LocationInput';
import { ExampleLocations } from './components/ExampleLocations';
import { DifficultyDisplay } from './components/DifficultyDisplay';
import { AnalysisResults } from './components/AnalysisResults';
import { FeatureDisplay } from './components/FeatureDisplay';
import { extractFeatures } from './features/location-features';
import { analyzeDifficulty } from './analyzers/difficulty-analyzer';
import { AnalysisState } from './types';
import './App.css';

function App() {
  const [state, setState] = useState<AnalysisState>({
    loading: false,
    error: null,
    features: null,
    result: null,
  });

  const handleAnalyze = async (lat: number, lng: number) => {
    setState({
      loading: true,
      error: null,
      features: null,
      result: null,
    });

    try {
      // Extract features from the location
      const features = await extractFeatures(lat, lng);
      
      // Analyze difficulty based on features
      const result = analyzeDifficulty(features);
      
      setState({
        loading: false,
        error: null,
        features,
        result,
      });
    } catch (error) {
      setState({
        loading: false,
        error: error instanceof Error ? error.message : 'An error occurred during analysis',
        features: null,
        result: null,
      });
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🔍 PanoProbe</h1>
        <p className="tagline">AI-Powered GeoGuessr Difficulty Analyzer</p>
        <p className="subtitle">
          Analyze location difficulty using OpenStreetMap data, geographic features, and heuristics
        </p>
      </header>

      <main className="app-main">
        <section className="input-section">
          <LocationInput onAnalyze={handleAnalyze} loading={state.loading} />
          <ExampleLocations onSelectLocation={handleAnalyze} loading={state.loading} />
        </section>

        {state.loading && (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Analyzing location...</p>
            <p className="loading-detail">Fetching geographic data and calculating difficulty</p>
          </div>
        )}

        {state.error && (
          <div className="error-container">
            <h3>Error</h3>
            <p>{state.error}</p>
          </div>
        )}

        {state.result && state.features && !state.loading && (
          <section className="results-section">
            <DifficultyDisplay 
              difficulty={state.result.difficulty}
              confidence={state.result.confidence}
            />
            <AnalysisResults result={state.result} />
            <FeatureDisplay features={state.features} />
          </section>
        )}
      </main>

      <footer className="app-footer">
        <p>
          Built for hack day • Data from OpenStreetMap & Nominatim
        </p>
        <p className="footer-note">
          Future: Add computer vision (CLIP) and real player performance data
        </p>
      </footer>
    </div>
  );
}

export default App;

