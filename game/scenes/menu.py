# game/scenes/menu.py

import pygame

from settings import *
from core.scene_manager import BaseScene
from core.ui import Button
from scenes.cat_home import CatHomeScene
from scenes.customization import CatCustomizationScene # <-- Import new scene
import core.save_manager as save_manager # <-- Import save manager

class MenuScene(BaseScene):
    def __init__(self, scene_manager, game):
        super().__init__(scene_manager, game)
        
        # Get current screen dimensions
        current_width, current_height = self.game.screen.get_size()
        
        self.title_font = pygame.font.SysFont(DEFAULT_FONT_NAME, 72)
        self.title_surf = self.title_font.render(WINDOW_TITLE, True, BLACK)
        self.title_rect = self.title_surf.get_rect(center=(current_width / 2, current_height * 0.2)) # <-- CORRECTED
        
        # --- Dynamic Button Creation ---
        self.buttons = []
        button_width, button_height = 200, 50
        button_x = (current_width - button_width) / 2 # <-- CORRECTED
        button_y_start = current_height * 0.4 # <-- CORRECTED
        button_spacing = 70

        # Check if a save file exists
        self.save_exists = save_manager.load_game() is not None
        
        if self.save_exists:
            # Show Continue and New Game
            self.buttons.append(
                Button(rect=(button_x, button_y_start, button_width, button_height), text="Continue", callback=self._on_continue_clicked)
            )
            self.buttons.append(
                Button(rect=(button_x, button_y_start + button_spacing, button_width, button_height), text="New Game", callback=self._on_new_game_clicked)
            )
        else:
            # Only show New Game
            self.buttons.append(
                Button(rect=(button_x, button_y_start, button_width, button_height), text="New Game", callback=self._on_new_game_clicked)
            )
            
        # Exit button is always present
        exit_y = button_y_start + (2 * button_spacing if self.save_exists else button_spacing)
        self.buttons.append(
            Button(rect=(button_x, exit_y, button_width, button_height), text="Exit", callback=self._on_exit_clicked)
        )

    def handle_event(self, event):
        for button in self.buttons:
            button.handle_event(event)

    def draw(self, screen):
        screen.fill(BACKGROUND_COLOR)
        screen.blit(self.title_surf, self.title_rect)
        for button in self.buttons:
            button.draw(screen)

    def _on_continue_clicked(self):
        # Load game data from save file and go to home scene
        self.game.cat_data = save_manager.load_game()
        self.scene_manager.set_scene(CatHomeScene)

    def _on_new_game_clicked(self):
        # Go to the customization scene
        self.scene_manager.set_scene(CatCustomizationScene)

    def _on_exit_clicked(self):
        pygame.event.post(pygame.event.Event(pygame.QUIT))