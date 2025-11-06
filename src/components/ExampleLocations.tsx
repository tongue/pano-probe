import { testLocations } from '../examples/test-locations';

interface ExampleLocationsProps {
  onSelectLocation: (panoId: string) => void;
  loading: boolean;
}

export function ExampleLocations({ onSelectLocation, loading }: ExampleLocationsProps) {
  return (
    <div className="example-locations">
      <h3>Quick Test Locations</h3>
      <div className="example-grid">
        {testLocations.map((location) => (
          <button
            key={location.panoId}
            className="example-button"
            onClick={() => onSelectLocation(location.panoId)}
            disabled={loading}
          >
            <span className="example-name">{location.name}</span>
            <span className="example-coords">
              {location.panoId}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}

