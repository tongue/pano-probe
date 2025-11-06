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
    
    def get_eight_directions(self, pano_id: str, zoom: int = 2) -> Optional[dict]:
        """
        Get 8 directional views (N, NE, E, SE, S, SW, W, NW) for complete 360° coverage
        
        Args:
            pano_id: Panorama ID
            zoom: Zoom level (default 2 for 2048x1024)
            
        Returns:
            Dict with 8 direction keys containing PIL Images
            or None if panorama fetch fails
        """
        full_pano = self.fetch_panorama(pano_id, zoom)
        
        if not full_pano:
            return None
        
        width, height = full_pano.size
        
        # Each view is 90° FOV = 1/4 of the width
        view_width = width // 4
        
        # 8 directions every 45°
        # Each step is 1/8 of the panorama width
        step = width // 8
        
        # Define 8 directions starting from north (center) going clockwise
        directions_config = [
            ('north', 0),      # 0°
            ('northeast', 1),  # 45°
            ('east', 2),       # 90°
            ('southeast', 3),  # 135°
            ('south', 4),      # 180°
            ('southwest', 5),  # 225°
            ('west', 6),       # 270°
            ('northwest', 7),  # 315°
        ]
        
        views = {}
        for direction, step_num in directions_config:
            # Calculate center position for this direction
            center = (step_num * step) % width
            
            # Calculate left edge (90° FOV centered on this direction)
            left = (center - view_width // 2) % width
            right = (left + view_width) % width
            
            if right > left:
                # No wrapping needed
                views[direction] = full_pano.crop((left, 0, right, height))
            else:
                # Wraps around - stitch two pieces
                new_view = Image.new('RGB', (view_width, height))
                # Right piece (from left to end)
                right_piece_width = width - left
                new_view.paste(full_pano.crop((left, 0, width, height)), (0, 0))
                # Left piece (from start to right)
                new_view.paste(full_pano.crop((0, 0, right, height)), (right_piece_width, 0))
                views[direction] = new_view
        
        print(f"✓ Extracted 8 directional views covering full 360°: {', '.join(views.keys())}")
        
        return views
    
    def get_four_directions(self, pano_id: str, zoom: int = 2) -> Optional[dict]:
        """
        Get 4 directional views (N, E, S, W) from the panorama
        DEPRECATED: Use get_eight_directions for better coverage
        
        Args:
            pano_id: Panorama ID
            zoom: Zoom level (default 2 for 2048x1024)
            
        Returns:
            Dict with keys 'north', 'east', 'south', 'west' containing PIL Images
            or None if panorama fetch fails
        """
        # Use 8-direction method and return subset
        eight_views = self.get_eight_directions(pano_id, zoom)
        if not eight_views:
            return None
        
        # Return only cardinal directions
        return {
            'north': eight_views['north'],
            'east': eight_views['east'],
            'south': eight_views['south'],
            'west': eight_views['west'],
        }

