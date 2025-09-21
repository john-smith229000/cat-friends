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
        self._recalculate_layout() # Initial layout setup

        # --- Accessory Data ---
        self.accessories = { "head": ["hat1", "hat2"] }
        self.current_indices = { "head": 0 }
        self.head_options = ["None"] + self.accessories["head"]

    def _recalculate_layout(self):
        """Recalculates the position of all UI elements based on current screen size."""
        current_width, current_height = self.game.screen.get_size()

        self.title_font = pygame.font.SysFont(DEFAULT_FONT_NAME, 52)
        self.title_surf = self.title_font.render("Accessorize!", True, BLACK)
        self.title_rect = self.title_surf.get_rect(center=(current_width / 2, 50))

        self.back_button = Button(
            rect=(current_width - 170, current_height - 70, 150, 50),
            text="Back",
            callback=self._on_back_clicked
        )
        
        self.option_font = pygame.font.SysFont(DEFAULT_FONT_NAME, 32)
        self.head_label = self.option_font.render("Head:", True, BLACK)
        self.head_left_arrow = Button(rect=(current_width/2 - 150, 150, 40, 40), text="<", callback=lambda: self._change_accessory("head", -1))
        self.head_right_arrow = Button(rect=(current_width/2 + 110, 150, 40, 40), text=">", callback=lambda: self._change_accessory("head", 1))


    def handle_event(self, event):
        if event.type == pygame.VIDEORESIZE:
            self._recalculate_layout() # <-- Recalculate on resize

        self.back_button.handle_event(event)
        self.head_left_arrow.handle_event(event)
        self.head_right_arrow.handle_event(event)

    # ... (rest of the file is unchanged) ...
    def on_enter(self, data=None):
        if data:
            self.cat_preview = Cat(
                cat_id="cat01",
                position=(self.game.screen.get_width() / 2, self.game.screen.get_height() / 2 + 100),
                initial_stats=data
            )
            current_head_accessory = data.get("accessories", {}).get("head")
            if current_head_accessory in self.head_options:
                self.current_indices["head"] = self.head_options.index(current_head_accessory)

    def update(self, dt):
        if self.cat_preview:
            self.cat_preview.update(dt)

    def draw(self, screen):
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        screen.blit(self.title_surf, self.title_rect)
        self.back_button.draw(screen)

        screen.blit(self.head_label, (self.game.screen.get_width()/2 - 230, 155))
        self.head_left_arrow.draw(screen)
        self.head_right_arrow.draw(screen)
        
        current_head_name = self.head_options[self.current_indices["head"]]
        head_name_surf = self.option_font.render(current_head_name.replace("_", " ").title(), True, WHITE)
        head_name_rect = head_name_surf.get_rect(center=(self.game.screen.get_width()/2, 170))
        screen.blit(head_name_surf, head_name_rect)

        if self.cat_preview:
            self.cat_preview.draw(screen)
            
    def _change_accessory(self, slot, direction):
        if slot == "head":
            max_index = len(self.head_options) - 1
            self.current_indices[slot] += direction
            if self.current_indices[slot] > max_index:
                self.current_indices[slot] = 0
            elif self.current_indices[slot] < 0:
                self.current_indices[slot] = max_index
            
            selected_accessory = self.head_options[self.current_indices[slot]]
            if selected_accessory == "None":
                 self.cat_preview.accessories[slot] = None
            else:
                 self.cat_preview.accessories[slot] = selected_accessory

    def _on_back_clicked(self):
        if self.cat_preview:
            self.game.cat_data = self.cat_preview.to_dict()
        self.scene_manager.pop()