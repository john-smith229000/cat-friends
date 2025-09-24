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

        # The dictionary that stores the cat's appearance
        self.cat_data = {
            "body_type": "shorthair",
            "base_color": (230, 210, 190),     # Default Beige
            "pattern_color": (90, 70, 50),     # Default Dark Brown
            "eye_color": (87, 255, 250),       # Default Blue
            "nose_color": (255, 180, 200),     # Default Pink
            # Default stats for a new cat
            "hunger": 100.0, "happiness": 70.0, "energy": 100.0
        }
        
        # Create the cat instance that we will show on screen
        self.cat_preview = Cat((self.game.screen.get_width() / 2, self.game.screen.get_height() / 2), {"customization": self.cat_data})
        
        # Pre-defined color palettes
        self.palettes = {
            "base": [(230, 210, 190), (100, 100, 100), (255, 255, 255), (240, 180, 100), (50, 50, 50)],
            "pattern": [(90, 70, 50), (200, 200, 200), (50, 50, 50), (200, 100, 50), None], # None = no pattern
            "eyes": [(87, 255, 250), (80, 200, 80), (230, 200, 90), (150, 100, 230)]
        }
        
        self.current_selection = "base" # Tracks which category is being edited
        self._recalculate_layout()

    def _recalculate_layout(self):
        """Creates and positions all UI elements based on the current screen size."""
        current_width, current_height = self.game.screen.get_size()
        
        self.title_font = pygame.font.SysFont(DEFAULT_FONT_NAME, 72)
        self.title_surf = self.title_font.render("Create Your Cat", True, BLACK)
        self.title_rect = self.title_surf.get_rect(center=(current_width / 2, 100))

        # --- Category Buttons ---
        self.category_buttons = [
            Button(rect=(100, 200, 200, 50), text="Fur Color", callback=lambda: self.set_selection("base")),
            Button(rect=(100, 270, 200, 50), text="Pattern Color", callback=lambda: self.set_selection("pattern")),
            Button(rect=(100, 340, 200, 50), text="Eye Color", callback=lambda: self.set_selection("eyes"))
        ]

        # --- Color Palette Buttons ---
        self.color_buttons = []
        x_start, y_start, size, padding = 100, 450, 40, 10
        active_palette = self.palettes.get(self.current_selection, [])
        
        for i, color in enumerate(active_palette):
            x = x_start + (i % 5) * (size + padding)
            y = y_start + (i // 5) * (size + padding)
            btn = Button(rect=(x, y, size, size), text="", callback=self.make_color_callback(color))
            
            if color is None: # Special case for "None" button
                btn.color_normal = (50, 50, 50)
                btn.text_surf = pygame.font.SysFont(DEFAULT_FONT_NAME, 30).render("X", True, WHITE)
                btn.text_rect = btn.text_surf.get_rect(center=btn.rect.center)
            else:
                btn.color_normal = color
                btn.color_hover = tuple(min(c + 30, 255) for c in color)
                btn.color_pressed = tuple(max(c - 30, 0) for c in color)
            self.color_buttons.append(btn)
        
        # --- Confirm Button ---
        self.confirm_button = Button(rect=(current_width - 250, current_height - 100, 200, 50), text="Confirm", callback=self._on_confirm)

    def set_selection(self, selection):
        """Changes the active category and rebuilds the color palette."""
        self.current_selection = selection
        self._recalculate_layout()

    def make_color_callback(self, color):
        """Creates a callback function that knows which color to apply."""
        def callback():
            if self.current_selection == "base":
                self.cat_data["base_color"] = color
            elif self.current_selection == "pattern":
                self.cat_data["pattern_color"] = color
            elif self.current_selection == "eyes":
                self.cat_data["eye_color"] = color
            # Update the cat preview with the new color
            self.cat_preview.update_customization(self.cat_data)
        return callback

    def handle_event(self, event):
        if event.type == pygame.VIDEORESIZE:
            self._recalculate_layout()
            # Also update preview position
            self.cat_preview.set_position(self.game.screen.get_width() / 2, self.game.screen.get_height() / 2)

        for btn in self.category_buttons + self.color_buttons + [self.confirm_button]:
            btn.handle_event(event)

    def update(self, dt):
        self.cat_preview.update(dt)

    def draw(self, screen):
        screen.fill(BACKGROUND_COLOR)
        screen.blit(self.title_surf, self.title_rect)
        self.cat_preview.draw(screen)
        for btn in self.category_buttons + self.color_buttons + [self.confirm_button]:
            btn.draw(screen)
        return [screen.get_rect()]

    def _on_confirm(self):
        """Finalizes the cat and moves to the main game scene, passing data directly."""
        final_cat_data = {"customization": self.cat_data}
        # We no longer set self.game.cat_data here. We pass it directly.
        self.scene_manager.set_scene(CatHomeScene, data=final_cat_data)