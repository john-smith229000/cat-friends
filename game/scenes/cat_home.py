# game/scenes/cat_home.py

import pygame

from settings import *
from core.scene_manager import BaseScene
from core.resource_manager import resources
from entities.cat import Cat
from core.draggable_item import DraggableItem
import core.save_manager as save_manager
# from scenes.menu import MenuScene  <-- REMOVED FROM HERE
from scenes.accessory import AccessoryScene

class CatHomeScene(BaseScene):
    def __init__(self, scene_manager, game):
        super().__init__(scene_manager, game)
        
        # --- Simplified Cat Loading Logic ---
        initial_data = self.game.cat_data or save_manager.load_game() or {"customization": {}}
        self.cat = Cat(
            position=(self.game.screen.get_width() / 2, self.game.screen.get_height() - 40),
            initial_stats=initial_data
        )
        self._recalculate_layout()


    def _recalculate_layout(self):
        current_width, current_height = self.game.screen.get_size()
        
        self.background_image = resources.load_image("images/backgrounds/main.jpg", scale=(current_width, current_height))
        
        food_image = resources.load_image("images/items/food/001.png", scale=0.5)
        food_home_pos = (current_width - food_image.get_width() - 50, current_height - food_image.get_height() - 50)
        self.food_item = DraggableItem(food_image, food_home_pos)

        self.font = pygame.font.SysFont(DEFAULT_FONT_NAME, 30)
        self.instructions_surf = self.font.render("Drag food to cat! Click & Hold cat to pet! (ESC to exit)", True, WHITE)
        self.instructions_rect = self.instructions_surf.get_rect(center=(current_width / 2, 30))
        
        self.hud_font = pygame.font.SysFont(DEFAULT_FONT_NAME, 24, bold=True)
        
        self.mirror_image = resources.load_image("images/ui_elements/mirror.png", scale=0.5)
        self.mirror_rect = self.mirror_image.get_rect(topleft=(20, 250))

        self.food_replenish_delay = 1.0
        self.food_replenish_timer = 0.0

    def on_enter(self, data=None):
        if self.game.cat_data:
            self.cat = Cat(
                position=(self.game.screen.get_width() / 2, self.game.screen.get_height() - 40),
                initial_stats=self.game.cat_data
            )
     
    def on_quit(self):
        if self.cat:
            save_manager.save_game(self.cat.to_dict())

    def handle_event(self, event):
        if event.type == pygame.VIDEORESIZE:
            self._recalculate_layout()
            
        if self.food_item.visible:
            self.food_item.handle_event(event)
        self.cat.handle_event(event)

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.food_item.is_dragging:
                self.food_item.is_dragging = False
            
            if self.mirror_rect.collidepoint(event.pos):
                self.scene_manager.push(AccessoryScene, data=self.cat.to_dict())

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                from scenes.menu import MenuScene # <-- MOVED HERE
                self.scene_manager.set_scene(MenuScene)

    def update(self, dt):
        self.cat.update(dt)

    def _draw_hud(self, screen):
        # Happiness Bar
        hap_text = self.hud_font.render("Happiness", True, WHITE)
        screen.blit(hap_text, (20, 20))
        pygame.draw.rect(screen, (50, 50, 50), (20, 50, 200, 25))
        hap_width = (self.cat.happiness / self.cat.max_stat) * 200
        pygame.draw.rect(screen, (50, 200, 50), (20, 50, hap_width, 25))
        pygame.draw.rect(screen, WHITE, (20, 50, 200, 25), 2)
        
        # Hunger Bar
        hun_text = self.hud_font.render("Hunger", True, WHITE)
        screen.blit(hun_text, (20, 90))
        pygame.draw.rect(screen, (50, 50, 50), (20, 120, 200, 25))
        hun_width = (self.cat.hunger / self.cat.max_stat) * 200
        pygame.draw.rect(screen, (200, 150, 50), (20, 120, hun_width, 25))
        pygame.draw.rect(screen, WHITE, (20, 120, 200, 25), 2)
        
    def on_exit(self):
        if self.cat:
            self.game.cat_data = self.cat.to_dict()

    def draw(self, screen):
        screen.blit(self.background_image, (0, 0))
        self.cat.draw(screen)
        self.food_item.draw(screen)
        screen.blit(self.mirror_image, self.mirror_rect)
        
        pygame.draw.rect(screen, (0, 0, 0, 150), self.instructions_rect.inflate(20, 10))
        screen.blit(self.instructions_surf, self.instructions_rect)
        
        self._draw_hud(screen)