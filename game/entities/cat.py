# entities/cat.py (Refactored)

import pygame
from core.animation import Animation
from entities.components.cat_rendering import CatRenderer
from entities.components.cat_stats import CatStats
from entities.components.cat_behavior import CatBehavior
from entities.components.cat_user_interactions import CatUserInteractions
from entities.components.cat_data import CatData

class Cat:
    """
    Main cat class that coordinates all component systems.
    This is the public interface that other systems interact with.
    """
    def __init__(self, position, initial_stats, scale=0.5):
        # Initialize all components
        self.data = CatData(initial_stats)
        self.stats = CatStats(initial_stats)
        self.behavior = CatBehavior(position)
        self.interactions = CatUserInteractions()
        self.renderer = CatRenderer(self.data.customization_data, self.data.body_type, scale)
        
        # Animation setup
        self.base_animation = Animation(self.renderer.layers['base']['idle'], 0.1, loop=False, pingpong=True)
        
        # Rect and collision setup
        self.rect = None
        self.last_rect = None
        self.mask = None
        self.scale = scale
        
        # Initial image composition
        self._update_visuals()

    def _update_visuals(self):
        """Updates the visual representation of the cat."""
        composed_image = self.renderer.compose_image(
            self.base_animation.image,
            self.interactions.is_blinking,
            self.interactions.is_being_petted,
            self.interactions.is_hovered_by_food
        )
        
        if composed_image:
            # Update rect with scaled image size
            if self.rect is None:
                self.rect = composed_image.get_rect(midbottom=self.behavior.position)
            else:
                old_center = self.rect.center
                self.rect = composed_image.get_rect(center=old_center)
            
            self.mask = pygame.mask.from_surface(composed_image)

    def update(self, dt):
        """Updates all cat systems."""
        self.last_rect = self.rect.copy() if self.rect else None
        
        # Update all components
        self.stats.update(dt, self.interactions.is_being_petted)
        self.behavior.update(dt)
        self.interactions.update(dt, self.base_animation)
        self.base_animation.update(dt)
        
        # Update position and visuals
        if self.rect:
            self.rect.center = self.behavior.position
        self._update_visuals()

    def draw(self, screen):
        """Draws the cat and accessories."""
        if self.renderer.scaled_image:
            screen.blit(self.renderer.scaled_image, self.rect)
            self.renderer.draw_accessories(screen, self.rect, self.data.accessories, self.scale)

    def handle_event(self, event):
        """Delegates event handling to interaction component."""
        self.interactions.handle_event(event, self.rect, self.mask)

    # Public interface methods (maintaining compatibility)
    def feed(self):
        self.stats.feed()

    def set_food_hover(self, is_hovering):
        self.interactions.set_food_hover(is_hovering)

    def set_position(self, x, y):
        self.behavior.set_position(x, y)
        if self.rect:
            self.rect.center = self.behavior.position

    def move_to(self, target_x, target_y):
        self.behavior.move_to(target_x, target_y)

    def set_scale(self, new_scale):
        self.scale = new_scale
        self.renderer.scale = new_scale
        self._update_visuals()

    def update_customization(self, new_data):
        self.data.update_customization(new_data)
        self.renderer.update_customization(new_data)
        self._update_visuals()

    def to_dict(self):
        return self.data.to_dict(self.stats, self.data.accessories)

    def collides_with_item(self, item):
        """Checks for pixel-perfect collision with a DraggableItem."""
        if not self.rect.colliderect(item.rect):
            return False
        
        offset = (item.rect.x - self.rect.x, item.rect.y - self.rect.y)
        return self.mask.overlap(item.mask, offset) is not None

    # Property accessors for backward compatibility
    @property
    def hunger(self):
        return self.stats.hunger
    
    @property
    def happiness(self):
        return self.stats.happiness
    
    @property
    def energy(self):
        return self.stats.energy
    
    @property
    def max_stat(self):
        return self.stats.max_stat
    
    @property
    def position(self):
        return self.behavior.position
    
    @property
    def is_being_petted(self):
        return self.interactions.is_being_petted
    
    @property
    def accessories(self):
        return self.data.accessories
    
    @property
    def unique_id(self):
        return self.data.unique_id
    
    @property
    def customization_data(self):
        return self.data.customization_data