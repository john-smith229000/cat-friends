# game/entities/components/cat_rendering.py

import pygame
from core.resource_manager import resources

def colorize_image(image, color):
    """Tints a grayscale image with a color using fast blending."""
    if not image or not color:
        return image
    
    result = pygame.Surface(image.get_size(), pygame.SRCALPHA)
    result.fill((0, 0, 0, 0))
    
    color_surface = pygame.Surface(image.get_size(), pygame.SRCALPHA)
    color_surface.fill((*color, 255))
    
    result.blit(color_surface, (0, 0))
    result.blit(image, (0, 0), special_flags=pygame.BLEND_MULT)
    
    final = pygame.Surface(image.get_size(), pygame.SRCALPHA)
    final.fill((0, 0, 0, 0))
    final.blit(image, (0, 0))
    final.blit(result, (0, 0), special_flags=pygame.BLEND_PREMULTIPLIED)
    
    return final

def apply_shadow(base_image, shadow_image):
    """Applies shadow by multiplying only RGB, preserving alpha from base."""
    if not base_image or not shadow_image:
        return base_image
    
    result = base_image.copy()
    shadow_rgb = pygame.Surface(shadow_image.get_size(), pygame.SRCALPHA)
    shadow_rgb.fill((255, 255, 255, 255))
    shadow_rgb.blit(shadow_image, (0, 0))
    result.blit(shadow_rgb, (0, 0), special_flags=pygame.BLEND_MULT)
    
    return result

class CatRenderer:
    """Handles all visual rendering and image composition for a cat."""
    
    def __init__(self, customization_data, body_type="shorthair", scale=0.5, sleep_scale=None):
        self.customization_data = customization_data
        self.body_type = body_type
        self.scale = scale
        
        self.layers = self._load_layers()
        self.image = None
        self.scaled_image = None
        self.sleep_image = None  # Store the sleep image
        self.sleep_scale = sleep_scale if sleep_scale is not None else scale
    
    def _load_layers(self):
        """Loads all visual layers for the cat."""
        path_prefix = f"images/cats/custom/{self.body_type}"
        
        # Load base animation frames
        base_frames = []
        frame_path = resources.assets_path / path_prefix / "base" / "idle"
        if frame_path.is_dir():
            for frame_file in sorted(frame_path.glob("*.png")):
                relative_path = frame_file.relative_to(resources.assets_path)
                base_frames.append(resources.load_image(relative_path.as_posix()))
        
        if not base_frames:
            raise FileNotFoundError(f"No base animation frames found for '{self.body_type}' at {frame_path}")

        layers = {"base": {"idle": base_frames}}
        
        # Load sleep image
        sleep_path = f"{path_prefix}/base/sleep/001.png"
        try:
            layers["sleep"] = resources.load_image(sleep_path)
        except (FileNotFoundError, pygame.error):
            # If no sleep image, use first idle frame as fallback
            layers["sleep"] = base_frames[0] if base_frames else None
            print(f"Warning: Sleep image not found at {sleep_path}, using idle frame")
        
        # Load optional layers
        optional_layers = {
            "shade": f"{path_prefix}/base/shade.png",
            "pattern": f"{path_prefix}/patterns/idle/01.png",
            "eye_color": f"{path_prefix}/eyes/idle/01_color.png",
            "eye_outline": f"{path_prefix}/eyes/idle/01.png",
            "eye_blink": f"{path_prefix}/eyes/idle/01_blink.png", 
            "mouth_color": f"{path_prefix}/mouth/idle/01_color.png",
            "mouth_outline": f"{path_prefix}/mouth/idle/01.png",
            "mouth_eat": f"{path_prefix}/mouth/eat/01.png",
        }
        
        for layer_name, path in optional_layers.items():
            try:
                layers[layer_name] = resources.load_image(path)
            except (FileNotFoundError, pygame.error):
                layers[layer_name] = None
        
        return layers
    
    def update_customization(self, new_data):
        """Updates customization data and forces re-composition."""
        self.customization_data = new_data
    
    def compose_sleep_image(self):
        """Creates the sleeping cat image."""
        if not self.layers.get("sleep"):
            return None
        
        base_frame = self.layers["sleep"]
        final_image = pygame.Surface(base_frame.get_size(), pygame.SRCALPHA)
        final_image.fill((0, 0, 0, 0))
        
        # Apply base color to sleep image
        fill_color = self.customization_data.get("base_color", (200, 150, 100))
        color_layer = pygame.Surface(base_frame.get_size(), pygame.SRCALPHA)
        color_layer.fill((*fill_color, 255))
        
        colored_base = base_frame.copy()
        colored_base.blit(color_layer, (0, 0), special_flags=pygame.BLEND_MULT)
        final_image.blit(colored_base, (0, 0))
        
        # NOTE: Do not apply pattern or shadow, as those are designed for the idle pose
        # and will not align with the sleeping pose. This ensures the correct sleep sprite is shown.
        
        # Scale the image
        if self.sleep_scale != 1.0:
            new_size = (int(final_image.get_width() * self.sleep_scale), 
                       int(final_image.get_height() * self.sleep_scale))
            return pygame.transform.smoothscale(final_image, new_size)
        return final_image
    
    def compose_image(self, base_frame, is_blinking=False, is_being_petted=False, is_hovered_by_food=False, is_sleeping=False):
        """Creates the final cat image by layering and coloring components."""
        # If sleeping, return the sleep image
        if is_sleeping:
            if not self.sleep_image:
                self.sleep_image = self.compose_sleep_image()
            self.scaled_image = self.sleep_image
            self.image = self.sleep_image
            return self.scaled_image
        
        # Otherwise, compose normal image
        if not base_frame:
            return None

        final_image = pygame.Surface(base_frame.get_size(), pygame.SRCALPHA)
        final_image.fill((0, 0, 0, 0))
        
        # 1. Apply base color
        fill_color = self.customization_data.get("base_color", (200, 150, 100))
        color_layer = pygame.Surface(base_frame.get_size(), pygame.SRCALPHA)
        color_layer.fill((*fill_color, 255))
        
        colored_base = base_frame.copy()
        colored_base.blit(color_layer, (0, 0), special_flags=pygame.BLEND_MULT)
        final_image.blit(colored_base, (0, 0))
        
        # 2. Apply pattern if present
        pattern_color = self.customization_data.get("pattern_color")
        if pattern_color and self.layers.get("pattern"):
            pattern_layer = pygame.Surface(self.layers["pattern"].get_size(), pygame.SRCALPHA)
            pattern_layer.fill((*pattern_color, 255))
            
            colored_pattern = self.layers["pattern"].copy()
            colored_pattern.blit(pattern_layer, (0, 0), special_flags=pygame.BLEND_MULT)
            final_image.blit(colored_pattern, (0, 0))

        # 3. Apply shadow/shading
        if self.layers.get("shade"):
            final_image = apply_shadow(final_image, self.layers["shade"])

        # 4. Apply facial features
        self._apply_mouth(final_image, is_hovered_by_food)
        self._apply_eyes(final_image, is_blinking, is_being_petted)

        # Store and scale the image
        self.image = final_image
        if self.scale != 1.0:
            new_size = (int(final_image.get_width() * self.scale), 
                       int(final_image.get_height() * self.scale))
            self.scaled_image = pygame.transform.smoothscale(final_image, new_size)
        else:
            self.scaled_image = final_image
        
        return self.scaled_image
    
    def _apply_mouth(self, final_image, is_hovered_by_food):
        """Applies mouth graphics to the final image."""
        # Draw mouth outline
        if is_hovered_by_food and self.layers.get("mouth_eat"):
            final_image.blit(self.layers["mouth_eat"], (0, 0))
        elif self.layers.get("mouth_outline"):
            final_image.blit(self.layers["mouth_outline"], (0, 0))

        # Draw colorized nose
        nose_color = self.customization_data.get("nose_color", (255, 182, 193))
        if self.layers.get("mouth_color"):
            mouth_layer = pygame.Surface(self.layers["mouth_color"].get_size(), pygame.SRCALPHA)
            mouth_layer.fill((*nose_color, 255))
            
            colored_mouth = self.layers["mouth_color"].copy()
            colored_mouth.blit(mouth_layer, (0, 0), special_flags=pygame.BLEND_MULT)
            final_image.blit(colored_mouth, (0, 0))
    
    def _apply_eyes(self, final_image, is_blinking, is_being_petted):
        """Applies eye graphics to the final image."""
        if (is_blinking or is_being_petted) and self.layers.get("eye_blink"):
            final_image.blit(self.layers["eye_blink"], (0, 0))
        else:
            eye_color = self.customization_data.get("eye_color", (70, 150, 220))
            if self.layers.get("eye_color"):
                eye_layer = pygame.Surface(self.layers["eye_color"].get_size(), pygame.SRCALPHA)
                eye_layer.fill((*eye_color, 255))
                
                colored_eyes = self.layers["eye_color"].copy()
                colored_eyes.blit(eye_layer, (0, 0), special_flags=pygame.BLEND_MULT)
                final_image.blit(colored_eyes, (0, 0))
            
            if self.layers.get("eye_outline"):
                final_image.blit(self.layers["eye_outline"], (0, 0))
    
    def draw_accessories(self, screen, rect, accessories, scale):
        """Enhanced accessory drawing with better positioning and scaling."""
        # Head accessories (hats, etc.)
        head_accessory = accessories.get("head")
        if head_accessory:
            path = f"images/items/clothes/hats/{head_accessory}.png"
            try:
                # Scale the accessory appropriately based on cat scale
                accessory_scale = 0.2 * scale  # Reduced from 0.75 for better proportion
                accessory_image = resources.load_image(path, scale=accessory_scale)
                
                # Better positioning calculation - higher up and more centered
                accessory_pos = (
                    rect.centerx - (accessory_image.get_width()+10), 
                    rect.y - 25 * scale  # Moved up more
                )
                screen.blit(accessory_image, accessory_pos)
            except FileNotFoundError:
                print(f"Warning: Accessory image not found at {path}")
        
        # Body accessories (future: collars, shirts, etc.)
        body_accessory = accessories.get("body")
        if body_accessory:
            path = f"images/items/clothes/body/{body_accessory}.png"
            try:
                accessory_image = resources.load_image(path, scale=scale)
                # Position on cat's body
                accessory_pos = (
                    rect.centerx - accessory_image.get_width() / 2,
                    rect.centery - accessory_image.get_height() / 2
                )
                screen.blit(accessory_image, accessory_pos)
            except FileNotFoundError:
                print(f"Warning: Body accessory image not found at {path}")
        
        # Other accessories (future: bows, jewelry, etc.)
        other_accessory = accessories.get("accessories")
        if other_accessory:
            path = f"images/items/clothes/accessories/{other_accessory}.png"
            try:
                accessory_image = resources.load_image(path, scale=0.5 * scale)  # Smaller scale
                # Position as needed
                accessory_pos = (
                    rect.centerx - accessory_image.get_width() / 2,
                    rect.bottom - 30 * scale
                )
                screen.blit(accessory_image, accessory_pos)
            except FileNotFoundError:
                print(f"Warning: Accessory image not found at {path}")