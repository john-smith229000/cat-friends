# game/scenes/accessory.py

import pygame

from settings import *
from core.scene_manager import BaseScene
from core.ui import Button
from entities.cat import Cat
from core.resource_manager import resources

class AccessoryScene(BaseScene):
    def __init__(self, scene_manager, game):
        super().__init__(scene_manager, game)
        self.cat_preview = None
        
        # --- UI Elements ---
        self.title_font = pygame.font.SysFont(DEFAULT_FONT_NAME, 52)
        self.title_surf = self.title_font.render("Accessorize!", True, BLACK)
        self.title_rect = self.title_surf.get_rect(center=(SCREEN_WIDTH / 2, 50))

        self.back_button = Button(
            rect=(SCREEN_WIDTH - 170, SCREEN_HEIGHT - 70, 150, 50),
            text="Back",
            callback=self._on_back_clicked
        )
        
        # --- Accessory Data ---
        # In the future, this could be loaded from a file
        self.accessories = {
            "head": ["hat1", "hat2"]
        }
        self.current_indices = {
            "head": 0 # Start with "None"
        }
        self.head_options = ["None"] + self.accessories["head"]

        # --- Options UI ---
        self.option_font = pygame.font.SysFont(DEFAULT_FONT_NAME, 32)
        
        # Head Accessory Selector
        self.head_label = self.option_font.render("Head:", True, BLACK)
        self.head_left_arrow = Button(rect=(300, 150, 40, 40), text="<", callback=lambda: self._change_accessory("head", -1))
        self.head_right_arrow = Button(rect=(560, 150, 40, 40), text=">", callback=lambda: self._change_accessory("head", 1))

    def on_enter(self, data=None):
        """Called when the scene is pushed onto the stack."""
        if data:
            # We don't have the full custom cat system yet, so we'll use a default cat_id
            # and apply the accessories from the data passed in.
            self.cat_preview = Cat(
                cat_id="cat01",
                position=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100),
                initial_stats=data
            )
            # Set the initial index based on the currently worn accessory
            current_head_accessory = data.get("accessories", {}).get("head")
            if current_head_accessory in self.head_options:
                self.current_indices["head"] = self.head_options.index(current_head_accessory)


    def handle_event(self, event):
        self.back_button.handle_event(event)
        self.head_left_arrow.handle_event(event)
        self.head_right_arrow.handle_event(event)

    def update(self, dt):
        if self.cat_preview:
            self.cat_preview.update(dt)

    def draw(self, screen):
        # We don't clear the screen, so it draws over the CatHomeScene
        # Create a semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        # Draw UI
        screen.blit(self.title_surf, self.title_rect)
        self.back_button.draw(screen)

        # Draw Head options
        screen.blit(self.head_label, (220, 155))
        self.head_left_arrow.draw(screen)
        self.head_right_arrow.draw(screen)
        
        # Draw the name of the current accessory
        current_head_name = self.head_options[self.current_indices["head"]]
        head_name_surf = self.option_font.render(current_head_name.replace("_", " ").title(), True, WHITE)
        head_name_rect = head_name_surf.get_rect(center=(450, 170))
        screen.blit(head_name_surf, head_name_rect)

        if self.cat_preview:
            self.cat_preview.draw(screen)
            
    def _change_accessory(self, slot, direction):
        if slot == "head":
            max_index = len(self.head_options) - 1
            self.current_indices[slot] += direction
            # Wrap around
            if self.current_indices[slot] > max_index:
                self.current_indices[slot] = 0
            elif self.current_indices[slot] < 0:
                self.current_indices[slot] = max_index
            
            # Update the cat preview
            selected_accessory = self.head_options[self.current_indices[slot]]
            if selected_accessory == "None":
                 self.cat_preview.accessories[slot] = None
            else:
                 self.cat_preview.accessories[slot] = selected_accessory

    def _on_back_clicked(self):
        # Update the main game's cat data before leaving
        if self.cat_preview:
            self.game.cat_data = self.cat_preview.to_dict()
        self.scene_manager.pop()