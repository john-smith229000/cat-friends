# game/core/resource_manager.py

import pygame
from pathlib import Path

class ResourceManager:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent.parent
        self.assets_path = self.base_path / "assets"
        self._image_cache = {}

    def load_image(self, path_from_assets, scale=None): # <-- ADDED 'scale' PARAMETER
        """
        Loads a pygame.Surface from a path relative to the assets folder.
        If 'scale' is a tuple (width, height), the image will be scaled to that size.
        If 'scale' is a float, the image will be scaled by that factor.
        """
        # Create a unique cache key that includes the scale
        cache_key = (path_from_assets, scale) 

        if cache_key in self._image_cache:
            return self._image_cache[cache_key]
        
        full_path = self.assets_path / path_from_assets
        
        if not full_path.exists():
            raise FileNotFoundError(f"Asset not found at: {full_path}")
            
        try:
            image = pygame.image.load(str(full_path)).convert_alpha()
            
            # --- APPLY SCALING IF SPECIFIED ---
            if scale is not None:
                if isinstance(scale, tuple) and len(scale) == 2:
                    image = pygame.transform.scale(image, scale)
                elif isinstance(scale, (int, float)):
                    new_width = int(image.get_width() * scale)
                    new_height = int(image.get_height() * scale)
                    image = pygame.transform.scale(image, (new_width, new_height))
            # --- END SCALING ---

            self._image_cache[cache_key] = image # Cache the scaled image
            return image
        except pygame.error as e:
            print(f"Error loading image: {full_path}")
            raise e

# Create a single, global instance of the manager that can be imported anywhere
resources = ResourceManager()