# game/entities/cat.py

import pygame
from pathlib import Path

from core.animation import Animation
from core.resource_manager import resources
from settings import *

class Cat:
    """
    Manages a cat's state, animations, and interactions.
    This class is the "brain" and "body" of the cat.
    """
    def __init__(self, cat_id, position, initial_stats=None):
        self.cat_id = cat_id
        # ... (rest of initialization is mostly the same)
        self.animations = self._load_animations()
        self.state = "idle"
        self._previous_state = "idle"
        self.animation = self.animations.get(self.state)
        self.image = self.animation.image
        self.rect = self.image.get_rect(midbottom=position)
        self.mask = self.animation.mask
        self.is_being_petted = False
        self.max_stat = MAX_STAT_VALUE

        if initial_stats:
            # Load from save data
            self.hunger = initial_stats.get("hunger", 80.0)
            self.happiness = initial_stats.get("happiness", 60.0)
            print("Loaded cat stats from save.")
        else:
            # Start with default values for a new game
            self.hunger = 80.0
            self.happiness = 60.0
            print("Initialized new cat with default stats.")

        # Add a dictionary to store equipped accessories
        self.accessories = {}
        if initial_stats and "accessories" in initial_stats:
            self.accessories = initial_stats["accessories"]

    def to_dict(self):
        """Exports the cat's current state to a savable dictionary."""
        return {
            "cat_id": self.cat_id,
            "hunger": self.hunger,
            "happiness": self.happiness,
            "accessories": self.accessories,
        }


    def _load_animations(self):
        """
        Automatically discovers and loads animations from the cat's asset folder.
        Folders like 'idle', 'pet', 'eat' will be loaded as animations.
        """
        animations = {}
        cat_path = resources.assets_path / "images" / "cats" / self.cat_id
        
        if not cat_path.is_dir():
            raise FileNotFoundError(f"Cat asset directory not found: {cat_path}")

        for anim_folder in cat_path.iterdir():
            if anim_folder.is_dir():
                anim_name = anim_folder.name
                frames = []
                for frame_file in sorted(anim_folder.glob("*.png")):
                    frames.append(resources.load_image(frame_file.relative_to(resources.assets_path)))
                
                if frames:
                    is_pingpong = (anim_name == "idle") # Idle ping-pongs
                    # Pet and Eat are one-shot, so loop=False
                    is_loop = (anim_name == "idle" or anim_name == "pet") # Pet should loop while held, eat is one-shot
                    if anim_name == "eat": # Eat is definitely not looping while held
                        is_loop = False
                    elif anim_name == "pet": # Pet loops only while held
                        is_loop = True # Temporarily make it loop, we'll stop it from outside

                    animations[anim_name] = Animation(frames, 0.15, loop=is_loop, pingpong=is_pingpong)
        
        print(f"Loaded animations for '{self.cat_id}': {list(animations.keys())}")
        return animations

    def set_state(self, new_state, force=False):
        """
        Changes the cat's current animation state.
        'force=True' will override current state even if it's already set (useful for eat).
        """
        if self.state == new_state and not force and self.animation.is_playing():
            return
        
        # Save previous state only if we're not already in a temporary override state (like pet or eat)
        if self.state not in ["pet", "eat"] and new_state not in ["pet", "eat"]:
            self._previous_state = self.state
        elif self.state == "idle" and new_state in ["pet", "eat"]: # If going from idle to temp, save idle
             self._previous_state = "idle"

        if new_state not in self.animations:
            print(f"Warning: Animation '{new_state}' not found for cat '{self.cat_id}'. Reverting to idle.")
            new_state = "idle" # Fallback to idle if animation not found
        
        self.state = new_state
        self.animation = self.animations[self.state]
        self.animation.reset()
        # For temporary animations like 'eat', we explicitly set loop to False
        # For 'pet', we allow it to loop as long as held, managed by external input
        if new_state == "eat":
            self.animation.loop = False # Ensure eat is a one-shot
        elif new_state == "pet":
            self.animation.loop = True # Pet loops while held


    def handle_event(self, event):
        # --- UPDATED: Pixel-perfect check for petting ---
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                # We are inside the rectangle, now check the mask
                pos_in_mask = (event.pos[0] - self.rect.x, event.pos[1] - self.rect.y)
                if self.mask.get_at(pos_in_mask):
                    self.is_being_petted = True
                    self.set_state("pet")
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.is_being_petted:
                self.is_being_petted = False
                # If currently petting, revert to previous state
                if self.state == "pet":
                    self.set_state(self._previous_state)


    def update(self, dt):
        """Updates the cat's current animation."""
        # Decrease stats over time
        self.hunger -= HUNGER_DECAY_RATE * dt
        self.happiness -= HAPPINESS_DECAY_RATE * dt

        if self.is_being_petted:
            self.happiness += HAPPINESS_INCREASE_RATE * dt

        self.hunger = max(0, min(self.hunger, self.max_stat))
        self.happiness = max(0, min(self.happiness, self.max_stat))

        self.animation.update(dt)
        self.image = self.animation.image

        # If a one-shot animation finishes and we're not overriding it (e.g., still petting),
        # revert to the previous saved state.
        if self.animation.is_done and not self.animation.loop and self.state not in ["pet", "eat"]:
            self.set_state(self._previous_state)
        # Handle specifically pet animation
        if self.state == "pet" and not self.is_being_petted:
            if self.animation.is_done: # If it finished while still in pet state but not held
                self.set_state(self._previous_state)
            elif not self.animation.is_playing(): # If it somehow stopped
                self.set_state(self._previous_state)
        
        self.mask = self.animation.mask

        # If eat animation is done, revert
        if self.state == "eat" and self.animation.is_done:
            self.set_state(self._previous_state)

    def feed(self):
        """Increases hunger when fed."""
        self.hunger += FOOD_HUNGER_REPLENISH
        print(f"Cat fed! Hunger is now {self.hunger:.1f}")

    def draw(self, screen):
        """Draws the cat on the screen."""
        if self.image: # Only draw if image is loaded (animation.image could be None if no frames)
            screen.blit(self.image, self.rect)
        
        # Draw head accessory
            head_accessory = self.accessories.get("head")
            if head_accessory:
                # Path assumes a structure for accessories
                path = f"images/items/clothes/hats/{head_accessory}.png"
                try:
                    # NOTE: We add a hardcoded offset to position the hat.
                    # This might need adjusting per-hat or per-animation frame later.
                    accessory_image = resources.load_image(path, scale=0.75)
                    accessory_pos = (self.rect.centerx - accessory_image.get_width() / 2, self.rect.y - 15)
                    screen.blit(accessory_image, accessory_pos)
                except FileNotFoundError:
                    print(f"Warning: Accessory image not found at {path}")
    
    def collides_with_item(self, item):
        """Checks for pixel-perfect collision with a DraggableItem."""
        # Step 1: Fast rectangle check
        if not self.rect.colliderect(item.rect):
            return False
        
        # Step 2: Slower, pixel-perfect mask check
        offset = (item.rect.x - self.rect.x, item.rect.y - self.rect.y)
        return self.mask.overlap(item.mask, offset) is not None