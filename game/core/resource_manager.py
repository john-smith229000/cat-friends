# game/core/resource_manager.py

import pygame
from pathlib import Path

class ResourceManager:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent.parent
        self.assets_path = self.base_path / "assets"
        self._image_cache = {}

    def load_image(self, path_from_assets, scale=None):
        cache_key = (path_from_assets, scale) 

        if cache_key in self._image_cache:
            return self._image_cache[cache_key]
        
        full_path = self.assets_path / path_from_assets
        
        # --- DEBUGGING PRINT STATEMENT ---
        # This will show us the exact path it's trying to find.
        print(f"Attempting to load: {full_path}")
        
        if not full_path.exists():
            # This will print a clear error if the path above is wrong.
            print(f"---!!! FAILED TO FIND FILE AT: {full_path}")
            raise FileNotFoundError(f"Asset not found at: {full_path}")
            
        try:
            image = pygame.image.load(str(full_path)).convert_alpha()
            
            if scale is not None:
                if isinstance(scale, tuple) and len(scale) == 2:
                    image = pygame.transform.scale(image, scale)
                elif isinstance(scale, (int, float)):
                    new_width = int(image.get_width() * scale)
                    new_height = int(image.get_height() * scale)
                    image = pygame.transform.scale(image, (new_width, new_height))

            self._image_cache[cache_key] = image
            return image
        except pygame.error as e:
            print(f"Error loading image: {full_path}")
            raise e

# Create a single, global instance
resources = ResourceManager()