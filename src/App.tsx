import { useState, useEffect } from 'react';
import { LocationInput } from './components/LocationInput';
import { ExampleLocations } from './components/ExampleLocations';
import { DifficultyDisplay } from './components/DifficultyDisplay';
import { AnalysisResults } from './components/AnalysisResults';
import { FeatureDisplay } from './components/FeatureDisplay';
import { CLIPResults } from './components/CLIPResults';
import { extractFeatures } from './features/location-features';
import { analyzeDifficulty } from './analyzers/difficulty-analyzer';
import { combineAnalyses } from './analyzers/ensemble-analyzer';
import { analyzeWithCLIP, checkBackendHealth } from './ai/clip-analyzer';
import { AnalysisState } from './types';
import './App.css';

function App() {
  const [state, setState] = useState<AnalysisState>({
    loading: false,
    error: null,
    features: null,
    result: null,
    clipAnalysis: null,
    backendAvailable: false,
  });

  // Check backend availability on mount
  useEffect(() => {
    checkBackendHealth().then(available => {
      setState(prev => ({ ...prev, backendAvailable: available }));
      if (available) {
        console.log('✅ CLIP backend is available');
      } else {
        console.log('⚠️ CLIP backend not available - using heuristics only');
      }
    });
  }, []);

  const handleAnalyze = async (lat: number, lng: number) => {
    setState({
      loading: true,
      error: null,
      features: null,
      result: null,
      clipAnalysis: null,
      backendAvailable: state.backendAvailable,
    });

    try {
      // Run both analyses in parallel
      const [features, clipAnalysis] = await Promise.all([
        extractFeatures(lat, lng),
        state.backendAvailable ? analyzeWithCLIP(lat, lng) : Promise.resolve(null)
      ]);
      
      // Get heuristic-based difficulty
      const heuristicResult = analyzeDifficulty(features);
      
      // Combine with CLIP if available
      const finalResult = clipAnalysis 
        ? combineAnalyses(heuristicResult, clipAnalysis)
        : heuristicResult;
      
      setState({
        loading: false,
        error: null,
        features,
        result: finalResult,
        clipAnalysis,
        backendAvailable: state.backendAvailable,
      });
    } catch (error) {
      setState({
        loading: false,
        error: error instanceof Error ? error.message : 'An error occurred during analysis',
        features: null,
        result: null,
        clipAnalysis: null,
        backendAvailable: state.backendAvailable,
      });
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🔍 PanoProbe</h1>
        <p className="tagline">AI-Powered GeoGuessr Difficulty Analyzer</p>
        <p className="subtitle">
          Analyze location difficulty using OpenStreetMap data, geographic features, and AI vision
        </p>
        {state.backendAvailable && (
          <div className="backend-status online">
            🤖 CLIP AI: Online
          </div>
        )}
        {!state.backendAvailable && (
          <div className="backend-status offline">
            ⚠️ CLIP AI: Offline (using heuristics only)
          </div>
        )}
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
            
            {state.clipAnalysis && (
              <CLIPResults clipAnalysis={state.clipAnalysis} />
            )}
            
            <AnalysisResults result={state.result} />
            <FeatureDisplay features={state.features} />
          </section>
        )}
      </main>

      <footer className="app-footer">
        <p>
          Built for hack day • Using: {state.clipAnalysis ? 'AI + Heuristics Ensemble' : 'Heuristics'}
        </p>
        <p className="footer-note">
          Data from OpenStreetMap, Nominatim {state.clipAnalysis ? '& CLIP Vision AI' : ''}
        </p>
      </footer>
    </div>
  );
}

export default App;

