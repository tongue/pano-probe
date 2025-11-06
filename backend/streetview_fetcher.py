"""
Street View Image Fetcher
Fetches panorama images from Google Street View Tiles API for higher resolution
"""

import os
import requests
from io import BytesIO
from PIL import Image
from typing import Optional
from streetview_tiles import StreetViewTilesAPI


class StreetViewFetcher:
    """Fetches Street View panorama images using Tiles API"""
    
    def __init__(self, api_key: str):
        """
        Initialize the fetcher with API key
        
        Args:
            api_key: Google Maps API key
        """
        self.api_key = api_key
        self.tiles_api = StreetViewTilesAPI(api_key)
        
    def get_pano_id_from_location(self, lat: float, lng: float) -> Optional[str]:
        """
        Get panorama ID from lat/lng coordinates
        
        Args:
            lat: Latitude
            lng: Longitude
            
        Returns:
            Panorama ID or None
        """
        url = f"https://maps.googleapis.com/maps/api/streetview/metadata"
        params = {
            'location': f'{lat},{lng}',
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'OK':
                    return data.get('pano_id')
            return None
        except Exception as e:
            print(f"Error getting pano ID: {e}")
            return None
    
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
        Fetch a high-resolution Street View panorama using Tiles API
        
        Args:
            lat: Latitude
            lng: Longitude
            size: Ignored (for compatibility)
            heading: Camera heading (0-360)
            pitch: Ignored (for compatibility)
            fov: Field of view (0-120)
            
        Returns:
            PIL Image (2048x1024) or None if not available
        """
        # Get panoId from location
        pano_id = self.get_pano_id_from_location(lat, lng)
        
        if not pano_id:
            print(f"No Street View panorama found at {lat}, {lng}")
            return None
        
        print(f"Found panoId: {pano_id}")
        
        # Fetch high-res panorama using Tiles API (zoom=2 gives 2048x1024)
        try:
            image = self.tiles_api.get_front_view(pano_id, zoom=2)
            return image
        except Exception as e:
            print(f"Error fetching panorama tiles: {e}")
            return None
    
    def fetch_multiple_views(
        self,
        lat: float,
        lng: float,
        headings: list[int] = [0, 90, 180, 270]
    ) -> list[Image.Image]:
        """
        Fetch multiple views from different angles
        Note: With Tiles API, we get the full panorama,
        so this just returns the front view multiple times.
        Could be enhanced to crop different angles from the full panorama.
        
        Args:
            lat: Latitude
            lng: Longitude  
            headings: List of camera headings to capture
            
        Returns:
            List of PIL Images
        """
        # For simplicity, just return the front view once
        img = self.fetch_panorama(lat, lng)
        return [img] if img else []
    
    def get_best_view(self, lat: float, lng: float) -> Optional[Image.Image]:
        """
        Get the best single view (high-resolution front view)
        
        Args:
            lat: Latitude
            lng: Longitude
            
        Returns:
            PIL Image (2048x1024) or None
        """
        return self.fetch_panorama(lat, lng)

