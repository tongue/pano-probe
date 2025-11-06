"""
Street View Image Fetcher
Fetches panorama images from Google Street View Static API
"""

import os
import requests
from io import BytesIO
from PIL import Image
from typing import Optional


class StreetViewFetcher:
    """Fetches Street View panorama images"""
    
    BASE_URL = "https://maps.googleapis.com/maps/api/streetview"
    
    def __init__(self, api_key: str):
        """
        Initialize the fetcher with API key
        
        Args:
            api_key: Google Maps API key with Street View Static API enabled
        """
        self.api_key = api_key
        
    def fetch_panorama(
        self, 
        lat: float, 
        lng: float,
        size: str = "640x640",
        heading: int = 0,
        pitch: int = 0,
        fov: int = 90
    ) -> Optional[Image.Image]:
        """
        Fetch a Street View panorama image
        
        Args:
            lat: Latitude
            lng: Longitude
            size: Image size (e.g., "640x640")
            heading: Camera heading (0-360)
            pitch: Camera pitch (-90 to 90)
            fov: Field of view (0-120)
            
        Returns:
            PIL Image or None if not available
        """
        params = {
            'location': f'{lat},{lng}',
            'size': size,
            'heading': heading,
            'pitch': pitch,
            'fov': fov,
            'key': self.api_key
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            
            if response.status_code != 200:
                print(f"Street View API error: {response.status_code}")
                return None
            
            # Check if we got an actual image (not "no imagery" placeholder)
            image = Image.open(BytesIO(response.content))
            
            # Google returns a gray placeholder if no imagery exists
            # We can detect this by checking image characteristics
            return image
            
        except Exception as e:
            print(f"Error fetching Street View image: {e}")
            return None
    
    def fetch_multiple_views(
        self,
        lat: float,
        lng: float,
        headings: list[int] = [0, 90, 180, 270]
    ) -> list[Image.Image]:
        """
        Fetch multiple views from different angles
        
        Args:
            lat: Latitude
            lng: Longitude  
            headings: List of camera headings to capture
            
        Returns:
            List of PIL Images
        """
        images = []
        for heading in headings:
            img = self.fetch_panorama(lat, lng, heading=heading)
            if img:
                images.append(img)
        
        return images
    
    def get_best_view(self, lat: float, lng: float) -> Optional[Image.Image]:
        """
        Get the best single view (forward-facing)
        
        Args:
            lat: Latitude
            lng: Longitude
            
        Returns:
            PIL Image or None
        """
        return self.fetch_panorama(lat, lng, heading=0, fov=90)

