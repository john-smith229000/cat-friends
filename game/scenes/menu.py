# game/scenes/menu.py

import pygame
import sys

from settings import *
from core.scene_manager import BaseScene
from core.ui import Button
from scenes.cat_home import CatHomeScene # <-- IMPORT THE NEW SCENE

class MenuScene(BaseScene):
    def __init__(self, scene_manager):
        super().__init__(scene_manager)
        
        self.title_font = pygame.font.SysFont(DEFAULT_FONT_NAME, 72)
        self.title_surf = self.title_font.render(WINDOW_TITLE, True, BLACK)
        self.title_rect = self.title_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.2))
        
        # Button layout (no changes here)
        button_width = 200
        button_height = 50
        button_x = (SCREEN_WIDTH - button_width) / 2
        button_y_start = SCREEN_HEIGHT * 0.4
        button_spacing = 70
        
        self.buttons = [
            Button(
                rect=(button_x, button_y_start, button_width, button_height),
                text="Play",
                callback=self._on_play_clicked
            ),
            Button(
                rect=(button_x, button_y_start + button_spacing, button_width, button_height),
                text="Options",
                callback=self._on_options_clicked
            ),
            Button(
                rect=(button_x, button_y_start + button_spacing * 2, button_width, button_height),
                text="Exit",
                callback=self._on_exit_clicked
            )
        ]

    def handle_event(self, event):
        for button in self.buttons:
            button.handle_event(event)

    def draw(self, screen):
        screen.fill(BACKGROUND_COLOR)
        screen.blit(self.title_surf, self.title_rect)
        
        for button in self.buttons:
            button.draw(screen)
            
    # --- Button Callback Methods ---
    
    def _on_play_clicked(self):
        # This is the updated part!
        print("Play button clicked! Transitioning to Cat Home...")
        self.scene_manager.set_scene(CatHomeScene)

    def _on_options_clicked(self):
        print("Options button clicked!")
        # self.scene_manager.push(OptionsScene)

    def _on_exit_clicked(self):
        pygame.quit()
        sys.exit()