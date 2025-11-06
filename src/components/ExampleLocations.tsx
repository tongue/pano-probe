import { testLocations } from '../examples/test-locations';

interface ExampleLocationsProps {
  onSelectLocation: (lat: number, lng: number) => void;
  loading: boolean;
}

export function ExampleLocations({ onSelectLocation, loading }: ExampleLocationsProps) {
  return (
    <div className="example-locations">
      <h3>Quick Test Locations</h3>
      <div className="example-grid">
        {testLocations.map((location) => (
          <button
            key={location.name}
            className="example-button"
            onClick={() => onSelectLocation(location.lat, location.lng)}
            disabled={loading}
          >
            <span className="example-name">{location.name}</span>
            <span className="example-coords">
              {location.lat.toFixed(3)}, {location.lng.toFixed(3)}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}

