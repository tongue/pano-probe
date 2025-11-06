"""
Street View Tiles API Integration
Fetches higher resolution panoramas by downloading and stitching tiles
"""

import requests
from PIL import Image
from io import BytesIO
import math
from typing import Optional, Tuple


class StreetViewTilesAPI:
    """Fetches high-resolution Street View panoramas using Tiles API"""
    
    TILE_SIZE = 512  # Each tile is 512x512 pixels
    
    def __init__(self, api_key: str):
        """
        Initialize with API key
        
        Args:
            api_key: Google Maps API key
        """
        self.api_key = api_key
    
    def get_tile_dimensions(self, zoom: int) -> Tuple[int, int]:
        """
        Get the number of tiles (columns, rows) for a given zoom level
        
        Zoom levels:
        0: 1x1 (512x512)
        1: 2x1 (1024x512)
        2: 4x2 (2048x1024)
        3: 8x4 (4096x2048)
        4: 16x8 (8192x4096)
        5: 32x16 (16384x8192)
        
        Args:
            zoom: Zoom level (0-5)
            
        Returns:
            Tuple of (columns, rows)
        """
        cols = 2 ** zoom
        rows = 2 ** (zoom - 1) if zoom > 0 else 1
        return (cols, rows)
    
    def fetch_tile(self, pano_id: str, zoom: int, x: int, y: int) -> Optional[Image.Image]:
        """
        Fetch a single tile
        
        Args:
            pano_id: Panorama ID
            zoom: Zoom level
            x: Tile column
            y: Tile row
            
        Returns:
            PIL Image or None
        """
        url = f"https://streetviewpixels-pa.googleapis.com/v1/tile?cb_client=maps_sv.tactile&panoid={pano_id}&x={x}&y={y}&zoom={zoom}&nbt=1&fover=2"
        
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return Image.open(BytesIO(response.content))
            else:
                print(f"Failed to fetch tile ({x}, {y}): {response.status_code}")
                return None
        except Exception as e:
            print(f"Error fetching tile ({x}, {y}): {e}")
            return None
    
    def fetch_panorama(
        self, 
        pano_id: str, 
        zoom: int = 2,
        heading: int = 0,
        fov: int = 90
    ) -> Optional[Image.Image]:
        """
        Fetch a panorama view at specified heading and FOV
        
        For simplicity, we'll fetch the full panorama at the zoom level
        and then crop to the desired view. For zoom=2, this is 2048x1024.
        
        Args:
            pano_id: Panorama ID
            zoom: Zoom level (0-5), default 2 for 2048x1024
            heading: Camera heading (0-360), not used in simple implementation
            fov: Field of view, not used in simple implementation
            
        Returns:
            PIL Image or None
        """
        cols, rows = self.get_tile_dimensions(zoom)
        
        print(f"Fetching panorama: {cols}x{rows} tiles at zoom {zoom}")
        
        # Create empty image
        width = cols * self.TILE_SIZE
        height = rows * self.TILE_SIZE
        panorama = Image.new('RGB', (width, height))
        
        # Fetch and stitch tiles
        for y in range(rows):
            for x in range(cols):
                tile = self.fetch_tile(pano_id, zoom, x, y)
                if tile:
                    panorama.paste(tile, (x * self.TILE_SIZE, y * self.TILE_SIZE))
                else:
                    print(f"Warning: Missing tile at ({x}, {y})")
        
        print(f"✓ Panorama assembled: {width}x{height}px")
        
        # For simplicity, return the full panorama
        # A more advanced implementation would crop based on heading/FOV
        return panorama
    
    def get_front_view(self, pano_id: str, zoom: int = 2) -> Optional[Image.Image]:
        """
        Get the front-facing view of the panorama
        
        Args:
            pano_id: Panorama ID
            zoom: Zoom level (default 2 for 2048x1024)
            
        Returns:
            PIL Image centered on front view
        """
        full_pano = self.fetch_panorama(pano_id, zoom)
        
        if not full_pano:
            return None
        
        # The front view is typically the center portion of the panorama
        # For a 360° panorama, center is facing forward
        width, height = full_pano.size
        
        # Extract center portion (roughly 90° FOV = 1/4 of width)
        crop_width = width // 4
        left = (width - crop_width) // 2
        
        front_view = full_pano.crop((left, 0, left + crop_width, height))
        
        return front_view

