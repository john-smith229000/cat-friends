# game/scenes/customization.py

import pygame

from settings import *
from core.scene_manager import BaseScene
from core.ui import Button
from scenes.cat_home import CatHomeScene
from entities.cat import Cat

class CatCustomizationScene(BaseScene):
    def __init__(self, scene_manager, game):
        super().__init__(scene_manager, game)

        # Default cat appearance data
        self.cat_data = {
            "body_type": "standard",
            "base_color": (210, 180, 140),  # Default Tan
            "pattern_name": "stripes",
            "pattern_color": (139, 69, 19),   # Default Brown
            "eye_color_name": "blue",
            # Add default stats for a new cat
            "hunger": 80.0,
            "happiness": 60.0,
            "energy": 100.0
        }

        # --- UI Elements ---
        self.title_font = pygame.font.SysFont(DEFAULT_FONT_NAME, 72)
        self.title_surf = self.title_font.render("Customize Your Cat", True, BLACK)
        self.title_rect = self.title_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.2))

        self.confirm_button = Button(
            rect=((SCREEN_WIDTH / 2) - 100, SCREEN_HEIGHT * 0.8, 200, 50),
            text="Confirm",
            callback=self._on_confirm_clicked
        )
        
        # This is where the live cat preview will be rendered
        self.cat_preview_pos = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    def handle_event(self, event):
        self.confirm_button.handle_event(event)

    def draw(self, screen):
        screen.fill(BACKGROUND_COLOR)
        screen.blit(self.title_surf, self.title_rect)
        self.confirm_button.draw(screen)
        
        # Placeholder text for where the cat preview will go
        placeholder_font = pygame.font.SysFont(DEFAULT_FONT_NAME, 32)
        placeholder_surf = placeholder_font.render("[Cat Preview Here]", True, BLACK)
        placeholder_rect = placeholder_surf.get_rect(center=self.cat_preview_pos)
        pygame.draw.rect(screen, (200, 200, 200), placeholder_rect.inflate(40, 40))
        screen.blit(placeholder_surf, placeholder_rect)

    def _on_confirm_clicked(self):
        # Store the customized data in the game object
        self.game.cat_data = self.cat_data
        # Transition to the main game scene
        self.scene_manager.set_scene(CatHomeScene)