import { TestLocation } from '../types';

export const testLocations: TestLocation[] = [
  {
    name: "Times Square, NYC",
    lat: 40.758,
    lng: -73.9855,
    expectedDifficulty: 1 // Very easy
  },
  {
    name: "Siberian Highway",
    lat: 61.5,
    lng: 105.3,
    expectedDifficulty: 5 // Very hard
  },
  {
    name: "Tokyo Shibuya Crossing",
    lat: 35.6595,
    lng: 139.7004,
    expectedDifficulty: 2 // Easy-medium (Japan is distinctive)
  },
  {
    name: "Australian Outback",
    lat: -26.5,
    lng: 134.2,
    expectedDifficulty: 5 // Very hard
  },
  {
    name: "Swiss Alps Village",
    lat: 46.6183,
    lng: 8.0897,
    expectedDifficulty: 2 // Medium (distinctive but rural)
  }
];

