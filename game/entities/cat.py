# game/entities/cat.py 

import pygame
from core.animation import Animation
from entities.components.cat_rendering import CatRenderer
from entities.components.cat_stats import CatStats
from entities.components.cat_behavior import CatBehavior
from entities.components.cat_user_interactions import CatUserInteractions
from entities.components.cat_data import CatData
from entities.components.cat_chat import CatChat

class Cat:
    def __init__(self, position, initial_stats, scale=0.5, sleep_scale=None):
        self.data = CatData(initial_stats)
        self.stats = CatStats(initial_stats)
        self.behavior = CatBehavior(position)
        self.interactions = CatUserInteractions()
        self.renderer = CatRenderer(self.data.customization_data, self.data.body_type, scale, sleep_scale)
        self.chat = CatChat(initial_stats.get('name', 'kitty'))
        self.base_animation = Animation(self.renderer.layers['base']['idle'], 0.1, loop=False, pingpong=True)
        self.rect = None
        self.mask = None
        self.scale = scale
        self._update_visuals()

    def _update_visuals(self):
        """Updates the visual representation of the cat."""
        composed_image = self.renderer.compose_image(
            self.base_animation.image,
            self.interactions.is_blinking,
            self.interactions.is_being_petted,
            self.interactions.is_hovered_by_food,
            self.behavior.is_sleeping
        )
        
        if composed_image:
            # This is the crucial fix: Always create the visual rect using
            # the logical position as the center anchor. This ensures perfect sync.
            self.rect = composed_image.get_rect(center=self.behavior.position)
            self.mask = pygame.mask.from_surface(composed_image)

    def update(self, dt, update_stats=True):
        """Updates all cat systems."""
        if update_stats:
            # Check for automatic state changes
            if self.stats.is_exhausted() and not self.behavior.is_sleeping:
                if hasattr(self, 'bed_world_x') and hasattr(self, 'bed_world_y'):
                    self.start_sleeping(self.bed_world_x, self.bed_world_y)
            
            if self.behavior.is_sleeping and self.stats.is_fully_rested():
                self.wake_up()
            
            # Update all components
            self.stats.update(dt, self.interactions.is_being_petted, self.behavior.is_sleeping)
        
        self.behavior.update(dt) # This updates the logical position
        
        # Determine current state for interactions
        current_state = "SLEEPING" if self.behavior.is_sleeping else "MOVING" if self.behavior.target_position else "IDLE"
        self.interactions.update(dt, self.base_animation, current_state)
        
        if not self.behavior.is_sleeping:
            self.base_animation.update(dt)
        
        # Sync visuals at the end of the update cycle.
        # Note we no longer manually set self.rect.center here.
        self._update_visuals()


    def draw(self, screen):
        if self.renderer.scaled_image and self.rect:
            screen.blit(self.renderer.scaled_image, self.rect)
            if not self.behavior.is_sleeping:
                self.renderer.draw_accessories(screen, self.rect, self.data.accessories, self.scale)

    def handle_event(self, event):
        if self.behavior.is_sleeping and event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            if self.rect and self.rect.collidepoint(event.pos):
                # Return True if the poke woke the cat up
                return self.poke()
        self.interactions.handle_event(event, self.rect, self.mask, self.behavior.state)
        return False

    def poke(self):
        if self.behavior.is_sleeping and self.interactions.poke():
            self.wake_up(force=True)
            return True # Return True because the cat woke up
        return False

    def start_sleeping(self, bed_x, bed_y):
        if not self.behavior.is_sleeping:
            self.behavior.start_sleeping(bed_x, bed_y)
            self.interactions.start_sleeping()

    def wake_up(self, force=False):
        if self.behavior.is_sleeping:
            if force and not self.stats.is_fully_rested(): self.stats.apply_wake_up_penalty()
            self.behavior.wake_up()

    def set_position(self, x, y):
        self.behavior.set_position(x, y)
        if self.rect:
            self.rect.center = self.behavior.position
        self._update_visuals()

    def can_sleep(self): return self.stats.is_tired() and not self.behavior.is_sleeping
    def is_sleeping(self): return self.behavior.is_sleeping
    def get_chat_response(self, player_input): return "Zzz..." if self.is_sleeping() else self.chat.get_response(player_input)
    def feed(self):
        if not self.is_sleeping(): self.stats.feed()
    def set_food_hover(self, is_hovering):
        if not self.is_sleeping(): self.interactions.set_food_hover(is_hovering)
    def to_dict(self): return self.data.to_dict(self.stats, self.data.accessories, self.behavior.is_sleeping)
    def update_customization(self, new_data):
        self.data.update_customization(new_data); self.renderer.update_customization(new_data); self._update_visuals()

    def collides_with_item(self, item):
        if self.is_sleeping() or not self.rect or not self.rect.colliderect(item.rect): return False
        offset = (item.rect.x - self.rect.x, item.rect.y - self.rect.y)
        return self.mask.overlap(item.mask, offset) is not None
        
    @property
    def position(self): return self.behavior.position
    @property
    def energy(self): return self.stats.energy
    @property
    def happiness(self): return self.stats.happiness
    @property
    def hunger(self): return self.stats.hunger