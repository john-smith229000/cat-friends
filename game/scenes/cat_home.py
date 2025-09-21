# game/scenes/cat_home.py

import pygame

from settings import *
from core.scene_manager import BaseScene
from core.resource_manager import resources
from entities.cat import Cat
from core.draggable_item import DraggableItem

class CatHomeScene(BaseScene):
    def __init__(self, scene_manager):
        super().__init__(scene_manager)
        
        self.background_image = resources.load_image("images/backgrounds/main.jpg")
        
        self.cat = Cat(
            cat_id="cat01",
            position=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 40)
        )
        
        food_image = resources.load_image("images/items/food/001.png", scale=0.5)
        food_home_pos = (SCREEN_WIDTH - food_image.get_width() - 50, SCREEN_HEIGHT - food_image.get_height() - 50)
        self.food_item = DraggableItem(food_image, food_home_pos)

        self.food_replenish_delay = 1.0
        self.food_replenish_timer = 0.0

        self.font = pygame.font.SysFont(DEFAULT_FONT_NAME, 30)
        self.instructions_surf = self.font.render("Drag food to cat! Click & Hold cat to pet! (ESC to exit)", True, WHITE)
        self.instructions_rect = self.instructions_surf.get_rect(center=(SCREEN_WIDTH / 2, 30))
        
        # --- NEW: HUD FONT ---
        self.hud_font = pygame.font.SysFont(DEFAULT_FONT_NAME, 24, bold=True)
        # --- END HUD FONT ---

    def handle_event(self, event):
        if self.food_item.visible:
            self.food_item.handle_event(event)
        self.cat.handle_event(event)

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.food_item.is_dragging:
                self.food_item.is_dragging = False
                if self.cat.collides_with_item(self.food_item):
                    self.cat.feed() 
                    self.cat.set_state("eat", force=True)
                    self.food_item.hide()
                    self.food_replenish_timer = self.food_replenish_delay
                else:
                    self.food_item.reset_position()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                from scenes.menu import MenuScene
                self.scene_manager.set_scene(MenuScene)

    def update(self, dt):
        self.cat.update(dt) # This now updates the cat's stats over time

        if self.food_replenish_timer > 0:
            self.food_replenish_timer -= dt
            if self.food_replenish_timer <= 0:
                self.food_item.reset_position()
                self.food_item.show()

        if self.food_item.is_dragging and self.cat.collides_with_item(self.food_item):
            if self.cat.state != "eat":
                self.cat.set_state("eat", force=True)

    def _draw_hud(self, screen):
        """Helper method to draw the stats HUD."""
        # --- HAPPINESS BAR ---
        hap_text = self.hud_font.render("Happiness", True, WHITE)
        screen.blit(hap_text, (20, 20))
        # Bar background
        pygame.draw.rect(screen, (50, 50, 50), (20, 50, 200, 25))
        # Bar foreground (width depends on stat)
        hap_width = (self.cat.happiness / self.cat.max_stat) * 200
        pygame.draw.rect(screen, (50, 200, 50), (20, 50, hap_width, 25))
        # Bar border
        pygame.draw.rect(screen, WHITE, (20, 50, 200, 25), 2)
        
        # --- HUNGER BAR ---
        hun_text = self.hud_font.render("Hunger", True, WHITE)
        screen.blit(hun_text, (20, 90))
        # Bar background
        pygame.draw.rect(screen, (50, 50, 50), (20, 120, 200, 25))
        # Bar foreground
        hun_width = (self.cat.hunger / self.cat.max_stat) * 200
        pygame.draw.rect(screen, (200, 150, 50), (20, 120, hun_width, 25))
        # Bar border
        pygame.draw.rect(screen, WHITE, (20, 120, 200, 25), 2)

    def draw(self, screen):
        screen.blit(pygame.transform.scale(self.background_image, (SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0))
        
        self.cat.draw(screen)
        self.food_item.draw(screen)
        
        pygame.draw.rect(screen, (0, 0, 0, 150), self.instructions_rect.inflate(20, 10))
        screen.blit(self.instructions_surf, self.instructions_rect)
        
        self._draw_hud(screen)