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
        self.cat = None
        self._recalculate_layout()
        self.dirty_rects = []
        self.force_redraw = True

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

        if self.cat:
            # Use a relative Y position (e.g., 80% down the screen)
            new_cat_y = current_height * 0.75
            self.cat.set_position(current_width / 2, new_cat_y)

        self.force_redraw = True

    def on_enter(self, data=None):
        # This is now the ONLY place the cat is created.
        # It prioritizes data passed from the previous scene (like customization).
        initial_data = data or self.game.cat_data or save_manager.load_game() or {"customization": {}}
        
        # Store the final data back to the game object for persistence
        self.game.cat_data = initial_data

        # Create the cat with the correct, consistent position.
        current_width, current_height = self.game.screen.get_size()
        cat_y_pos = current_height * 0.75 # Consistent relative position

        self.cat = Cat(
            position=(current_width / 2, cat_y_pos),
            initial_stats=initial_data
        )
        # Force a full redraw on entering the scene
        self.force_redraw = True
     
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
                # Check for collision when food is dropped
                if self.cat.collides_with_item(self.food_item):
                    self.cat.feed()
                    self.food_item.hide() # <-- Food disappears here
                else:
                    self.food_item.reset_position() # Snap back if not on cat

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                from scenes.menu import MenuScene # <-- MOVED HERE
                self.scene_manager.set_scene(MenuScene)

    def update(self, dt):
        self.cat.update(dt)
        self.food_item.update(dt)

        # Check if the food item is being dragged and hovering over the cat
        if self.food_item.is_dragging:
            if self.cat.collides_with_item(self.food_item):
                self.cat.set_food_hover(True)
            else:
                self.cat.set_food_hover(False)
        else:
            # Ensure the hover state is off if not dragging
            self.cat.set_food_hover(False)

        # Check if we need to replenish the food
        if not self.food_item.visible:
            self.food_replenish_timer += dt
            if self.food_replenish_timer >= self.food_replenish_delay:
                self.food_item.show() # <-- Food reappears here
                self.food_item.reset_position()
                self.food_replenish_timer = 0.0

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
        # If a full redraw is needed (first frame or after resize)
        if self.force_redraw:
            screen.blit(self.background_image, (0, 0))
            # Draw all elements once
            self.cat.draw(screen)
            self.food_item.draw(screen)
            screen.blit(self.mirror_image, self.mirror_rect)
            instruction_bg_rect = self.instructions_rect.inflate(20, 10)
            pygame.draw.rect(screen, (0, 0, 0, 150), instruction_bg_rect)
            screen.blit(self.instructions_surf, self.instructions_rect)
            self._draw_hud(screen)
            
            self.force_redraw = False
            return [screen.get_rect()] # Return the whole screen rect to update everything

        # --- Normal Dirty Rect Logic for subsequent frames ---
        dirty_rects = []

        # Step 1: Clear the last known positions of moving objects
        dirty_rects.append(self.cat.last_rect)
        screen.blit(self.background_image, self.cat.last_rect, self.cat.last_rect)
        
        dirty_rects.append(self.food_item.last_rect)
        screen.blit(self.background_image, self.food_item.last_rect, self.food_item.last_rect)
        
        # Step 2: Draw everything and collect their new rects to be updated
        dirty_rects.append(self.cat.draw(screen))
        dirty_rects.append(self.food_item.draw(screen))
        
        # Redraw all static UI elements to prevent trails
        screen.blit(self.mirror_image, self.mirror_rect)
        dirty_rects.append(self.mirror_rect)
        
        instruction_bg_rect = self.instructions_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, 150), instruction_bg_rect)
        screen.blit(self.instructions_surf, self.instructions_rect)
        dirty_rects.append(instruction_bg_rect)
        
        hud_rect = pygame.Rect(20, 20, 200, 130)
        self._draw_hud(screen)
        dirty_rects.append(hud_rect)

        return dirty_rects