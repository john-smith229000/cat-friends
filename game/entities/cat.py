# game/entities/cat.py

import pygame
from pathlib import Path
import random

from core.animation import Animation
from core.resource_manager import resources
from settings import *

def colorize_image(image, color):
    """
    Tints a grayscale image with a color using fast blending.
    White areas become the target color, black stays black.
    """
    if not image or not color:
        return image
    
    # Create a copy to work with
    result = pygame.Surface(image.get_size(), pygame.SRCALPHA)
    result.fill((0, 0, 0, 0))
    
    # First, fill with the target color
    color_surface = pygame.Surface(image.get_size(), pygame.SRCALPHA)
    color_surface.fill((*color, 255))
    
    # Use the original image as a mask - multiply the color by the grayscale values
    # This makes white areas fully colored and black areas stay black
    result.blit(color_surface, (0, 0))
    result.blit(image, (0, 0), special_flags=pygame.BLEND_MULT)
    
    # Now we need to restore the alpha channel from the original
    # Create a surface to hold the result with proper alpha
    final = pygame.Surface(image.get_size(), pygame.SRCALPHA)
    final.fill((0, 0, 0, 0))
    
    # Blit the result using the original image's alpha as a mask
    final.blit(image, (0, 0))  # Get the alpha channel structure
    final.blit(result, (0, 0), special_flags=pygame.BLEND_PREMULTIPLIED)
    
    return final

def apply_shadow(base_image, shadow_image):
    """
    Applies shadow by multiplying only RGB, preserving alpha from base.
    Uses a workaround to avoid alpha multiplication issues.
    """
    if not base_image or not shadow_image:
        return base_image
    
    # Create a copy of the base image
    result = base_image.copy()
    
    # Convert shadow to RGB only (no alpha) to avoid alpha multiplication
    shadow_rgb = pygame.Surface(shadow_image.get_size(), pygame.SRCALPHA)
    shadow_rgb.fill((255, 255, 255, 255))  # Start with white
    shadow_rgb.blit(shadow_image, (0, 0))  # Blit shadow on top
    
    # Apply multiply blend - this will darken the result based on shadow
    result.blit(shadow_rgb, (0, 0), special_flags=pygame.BLEND_MULT)
    
    return result

class Cat:
    """
    Manages a cat's state, animations, and interactions.
    Appearance is dynamically composited from layers based on customization_data.
    """
    def __init__(self, position, initial_stats, scale=0.5):
        self.position = list(position)  # Make it mutable for movement
        self.scale = scale
        
        self.customization_data = initial_stats.get("customization", {})
        self.body_type = self.customization_data.get("body_type", "shorthair")
        self.unique_id = initial_stats.get("cat_id", "custom_cat")
        
        self.layers = self._load_layers()
        self.state = "idle"
        
        self.base_animation = Animation(self.layers['base']['idle'], 0.1, loop=True, pingpong=True)
        
        self.image = None
        self.scaled_image = None  # Store scaled version separately
        self.rect = None
        self.mask = None
        
        self.hunger = initial_stats.get("hunger", 80.0)
        self.happiness = initial_stats.get("happiness", 60.0)
        self.energy = initial_stats.get("energy", 100.0)
        self.max_stat = MAX_STAT_VALUE
        self.is_being_petted = False
        self.accessories = initial_stats.get("accessories", {})
        
        # Movement and animation
        self.velocity = [0, 0]
        self.target_position = None
        self.movement_speed = 100  # pixels per second

        self.idle_animation_timer = random.uniform(2, 7)
        self.is_playing_idle_sequence = False

        # --- Blink animation logic ---
        self.blink_timer = random.uniform(2.2, 7.4)
        self.is_blinking = False
        self.blink_duration = 0.20  # How long the blink itself lasts
        self.blink_duration_timer = 0.0

        # Initial composite
        self._composite_image()

    def update_customization(self, new_data):
        self.customization_data = new_data
        self._composite_image()

    def _load_layers(self):
        path_prefix = f"images/cats/custom/{self.body_type}"
        
        base_frames = []
        frame_path = resources.assets_path / path_prefix / "base" / "idle"
        if frame_path.is_dir():
            for frame_file in sorted(frame_path.glob("*.png")):
                relative_path = frame_file.relative_to(resources.assets_path)
                base_frames.append(resources.load_image(relative_path.as_posix()))
        
        if not base_frames:
            raise FileNotFoundError(f"No base animation frames found for '{self.body_type}' at {frame_path}")

        # Load all layer components
        layers = {
            "base": {"idle": base_frames},
        }
        
    # Try to load optional layers, but don't fail if they're missing
        optional_layers = {
            "shade": f"{path_prefix}/base/shade.png",
            "pattern": f"{path_prefix}/patterns/idle/01.png",
            "eye_color": f"{path_prefix}/eyes/idle/01_color.png",
            "eye_outline": f"{path_prefix}/eyes/idle/01.png",
            "eye_blink": f"{path_prefix}/eyes/idle/01_blink.png", 
            "mouth_color": f"{path_prefix}/mouth/idle/01_color.png",
            "mouth_outline": f"{path_prefix}/mouth/idle/01.png",
        }
        
        for layer_name, path in optional_layers.items():
            try:
                layers[layer_name] = resources.load_image(path)
            except (FileNotFoundError, pygame.error):
                print(f"Optional layer '{layer_name}' not found at {path}")
                layers[layer_name] = None
        
        return layers

    def _composite_image(self):
        """Creates the final cat image by layering and coloring the animation frames."""
        base_frame = self.base_animation.image
        if not base_frame: 
            return

        # Start with a transparent surface
        final_image = pygame.Surface(base_frame.get_size(), pygame.SRCALPHA)
        final_image.fill((0, 0, 0, 0))
        
        # 1. Apply base color to the base frame
        fill_color = self.customization_data.get("base_color", (200, 150, 100))
        
        # Method 1: Simple colorization using multiply blend
        # This assumes your base sprite is grayscale (white body, black outlines)
        color_layer = pygame.Surface(base_frame.get_size(), pygame.SRCALPHA)
        color_layer.fill((*fill_color, 255))
        
        # Copy the base frame
        colored_base = base_frame.copy()
        # Multiply with color (white becomes the color, black stays black)
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

        # 3. Apply shadow/shading using RGB multiply
        if self.layers.get("shade"):
            # The shade layer should be grayscale where white = no shadow, gray/black = shadow
            final_image = apply_shadow(final_image, self.layers["shade"])

        # 4. Apply facial features (these should already have their colors baked in)
        # Or colorize them if they're grayscale templates
        
        # Mouth
        nose_color = self.customization_data.get("nose_color", (255, 182, 193))
        if self.layers.get("mouth_color"):
            mouth_layer = pygame.Surface(self.layers["mouth_color"].get_size(), pygame.SRCALPHA)
            mouth_layer.fill((*nose_color, 255))
            
            colored_mouth = self.layers["mouth_color"].copy()
            colored_mouth.blit(mouth_layer, (0, 0), special_flags=pygame.BLEND_MULT)
            
            final_image.blit(colored_mouth, (0, 0))
        
        if self.layers.get("mouth_outline"):
            final_image.blit(self.layers["mouth_outline"], (0, 0))

        # Eyes
        if self.is_blinking and self.layers.get("eye_blink"):
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

        # Store the original unscaled image
        self.image = final_image
        
        # Apply scaling if needed
        if self.scale != 1.0:
            new_size = (int(final_image.get_width() * self.scale), 
                       int(final_image.get_height() * self.scale))
            self.scaled_image = pygame.transform.smoothscale(final_image, new_size)
        else:
            self.scaled_image = final_image
        
        # Update rect with scaled image size
        if self.rect is None:
            self.rect = self.scaled_image.get_rect(midbottom=self.position)
        else:
            # Preserve current position when updating image
            old_center = self.rect.center
            self.rect = self.scaled_image.get_rect(center=old_center)
        
        self.mask = pygame.mask.from_surface(self.scaled_image)

    def to_dict(self):
        """Exports the cat's current state to a savable dictionary."""
        return {
            "cat_id": self.unique_id,
            "hunger": self.hunger,
            "happiness": self.happiness,
            "energy": self.energy,
            "accessories": self.accessories,
            "customization": self.customization_data
        }

    def set_scale(self, new_scale):
        """Sets a new scale for the cat sprite."""
        self.scale = new_scale
        self._composite_image()
    
    def set_position(self, x, y):
        """Sets the cat's position directly."""
        self.position = [x, y]
        self.rect.center = self.position
    
    def move_to(self, target_x, target_y):
        """Sets a target position for the cat to move towards."""
        self.target_position = [target_x, target_y]
    
    def update(self, dt):
        """Updates the cat's animation, movement, and re-composites the image."""
        
        # Handle idle animation logic
        if self.state == "idle":
            self.idle_animation_timer -= dt
            if self.idle_animation_timer <= 0 and not self.is_playing_idle_sequence:
                self.is_playing_idle_sequence = True
                num_frames = len(self.base_animation.frames)
                # A full loop for ping-pong is (num_frames - 1) * 2
                frames_to_play = (num_frames - 1) * 2 + random.randint(0, num_frames - 1)
                self.base_animation.play(frames_to_play)

            if self.is_playing_idle_sequence and self.base_animation.is_done:
                self.is_playing_idle_sequence = False
                self.idle_animation_timer = random.uniform(1, 4)
            
            # Handle blink animation logic
            if not self.is_blinking:
                self.blink_timer -= dt
                if self.blink_timer <= 0:
                    self.is_blinking = True
                    self.blink_duration_timer = self.blink_duration
            else:
                self.blink_duration_timer -= dt
                if self.blink_duration_timer <= 0:
                    self.is_blinking = False
                    self.blink_timer = random.uniform(1, 5)
        
        
        # Update animation
        self.base_animation.update(dt)
        
        # Handle movement if there's a target
        if self.target_position:
            dx = self.target_position[0] - self.position[0]
            dy = self.target_position[1] - self.position[1]
            distance = (dx**2 + dy**2)**0.5
            
            if distance > 2:  # If not close enough
                # Normalize and apply speed
                self.velocity[0] = (dx / distance) * self.movement_speed
                self.velocity[1] = (dy / distance) * self.movement_speed
                
                # Update position
                self.position[0] += self.velocity[0] * dt
                self.position[1] += self.velocity[1] * dt
            else:
                # Reached target
                self.position = list(self.target_position)
                self.target_position = None
                self.velocity = [0, 0]
        
        # Update rect position
        self.rect.center = self.position
        
        # Re-composite the image
        self._composite_image()

    def draw(self, screen):
        """Draws the cat and its accessories on the screen."""
        if self.scaled_image:
            screen.blit(self.scaled_image, self.rect)
            
            head_accessory = self.accessories.get("head")
            if head_accessory:
                path = f"images/items/clothes/hats/{head_accessory}.png"
                try:
                    accessory_image = resources.load_image(path, scale=0.75 * self.scale)
                    accessory_pos = (self.rect.centerx - accessory_image.get_width() / 2, 
                                   self.rect.y - 15 * self.scale)
                    screen.blit(accessory_image, accessory_pos)
                except FileNotFoundError:
                    print(f"Warning: Accessory image not found at {path}")
                    
    def set_state(self, new_state, force=False):
        self.state = new_state

    def handle_event(self, event): pass
    def feed(self): pass
    def collides_with_item(self, item): return False