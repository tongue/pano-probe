import { LocationFeatures } from '../types';

interface FeatureDisplayProps {
  features: LocationFeatures;
}

export function FeatureDisplay({ features }: FeatureDisplayProps) {
  return (
    <div className="feature-display">
      <h3>Extracted Features</h3>
      
      <div className="feature-cards">
        <div className="feature-card">
          <h4>📍 Location</h4>
          <div className="feature-items">
            <div className="feature-item">
              <span className="feature-key">Country:</span>
              <span className="feature-value">{features.country} ({features.countryCode})</span>
            </div>
            {features.city && (
              <div className="feature-item">
                <span className="feature-key">City:</span>
                <span className="feature-value">{features.city}</span>
              </div>
            )}
            <div className="feature-item">
              <span className="feature-key">Place Type:</span>
              <span className="feature-value">{features.placeType}</span>
            </div>
            <div className="feature-item">
              <span className="feature-key">Coordinates:</span>
              <span className="feature-value">
                {features.lat.toFixed(4)}, {features.lng.toFixed(4)}
              </span>
            </div>
          </div>
        </div>

        <div className="feature-card">
          <h4>🏘️ Environment</h4>
          <div className="feature-items">
            <div className="feature-item">
              <span className="feature-key">Urban Score:</span>
              <span className="feature-value">{features.urbanScore}/3</span>
            </div>
            <div className="feature-item">
              <span className="feature-key">Population Density:</span>
              <span className="feature-value">{features.populationDensity}/3</span>
            </div>
            <div className="feature-item">
              <span className="feature-key">Buildings Nearby:</span>
              <span className="feature-value">{features.nearbyBuildingsCount}</span>
            </div>
            <div className="feature-item">
              <span className="feature-key">Roads Nearby:</span>
              <span className="feature-value">{features.nearbyRoadsCount}</span>
            </div>
            <div className="feature-item">
              <span className="feature-key">POIs Nearby:</span>
              <span className="feature-value">{features.nearbyPOIsCount}</span>
            </div>
          </div>
        </div>

        <div className="feature-card">
          <h4>🎯 Points of Interest</h4>
          <div className="feature-items">
            <div className="feature-item">
              <span className="feature-key">Named Landmarks:</span>
              <span className="feature-value">
                {features.hasNamedLandmarks ? '✓ Yes' : '✗ No'}
              </span>
            </div>
            <div className="feature-item">
              <span className="feature-key">Natural Features:</span>
              <span className="feature-value">{features.naturalFeaturesCount}</span>
            </div>
          </div>
        </div>

        {(features.copyright || features.imageDate) && (
          <div className="feature-card">
            <h4>📷 Street View</h4>
            <div className="feature-items">
              {features.copyright && (
                <div className="feature-item">
                  <span className="feature-key">Copyright:</span>
                  <span className="feature-value">{features.copyright}</span>
                </div>
              )}
              {features.imageDate && (
                <div className="feature-item">
                  <span className="feature-key">Image Date:</span>
                  <span className="feature-value">{features.imageDate}</span>
                </div>
              )}
              <div className="feature-item">
                <span className="feature-key">Trekker Imagery:</span>
                <span className="feature-value">
                  {features.isTrekkerImagery ? '✓ Yes' : '✗ No'}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

