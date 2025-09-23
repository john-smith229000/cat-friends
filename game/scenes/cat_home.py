# game/scenes/cat_home.py

import pygame

from settings import *
from core.sound_manager import sounds
from core.ui import Button
from core.scene_manager import BaseScene
from core.resource_manager import resources
from entities.cat import Cat
from core.draggable_item import DraggableItem
import core.save_manager as save_manager
from scenes.wardrobe import WardrobeScene

class CatHomeScene(BaseScene):
    def __init__(self, scene_manager, game):
        super().__init__(scene_manager, game)
        
        # --- Simplified Cat Loading Logic ---
        self.cat = None
        self.background_x = 0
        self.background_y = 0 # New variable for vertical position
        self.background_y_offset = 600 # Shift the background down by this many pixels
        self.pan_speed = 200 # pixels per second
        self.zoom_factor = 2.5
        self.cat_world_x = 0
        self._recalculate_layout()
        self.dirty_rects = []
        self.force_redraw = True

        self.is_chatting = False
        self.chat_input_text = ""
        self.chat_response_text = ""
        self.chat_response_timer = 0.0
        self.chat_response_duration = 4.0

    def _recalculate_layout(self):
        current_width, current_height = self.game.screen.get_size()
        
        original_bg = resources.load_image("images/backgrounds/main.png")
        aspect_ratio = original_bg.get_width() / original_bg.get_height()
        scaled_height = int(current_height * self.zoom_factor)
        scaled_width = int(scaled_height * aspect_ratio)

        self.background_image = pygame.transform.smoothscale(original_bg, (scaled_width, scaled_height))
        self.max_pan_x = max(0, self.background_image.get_width() - current_width)
        max_pan_y = max(0, self.background_image.get_height() - current_height)

        # The cat's fixed position within the large background image
        self.cat_world_x = self.background_image.get_width() / 2

        # Center the background initially
        self.background_x = -self.max_pan_x / 2
        # Apply the vertical offset
        self.background_y = -min(self.background_y_offset, max_pan_y)
        
        food_image = resources.load_image("images/items/food/001.png", scale=0.5)
        food_home_pos = (current_width - food_image.get_width() - 50, current_height - food_image.get_height() - 50)
        self.food_item = DraggableItem(food_image, food_home_pos)

        self.font = pygame.font.SysFont(DEFAULT_FONT_NAME, 30)
        #self.instructions_surf = self.font.render("Drag food to cat! Click & Hold cat to pet! (ESC to exit)", True, WHITE)
        #self.instructions_rect = self.instructions_surf.get_rect(center=(current_width / 2, 30))
        
        self.hud_font = pygame.font.SysFont(DEFAULT_FONT_NAME, 24)
        self.hud_rect = pygame.Rect(15, 15, 210, 145)
        
        self.mirror_image = resources.load_image("images/ui_elements/mirror.png", scale=0.2)
        self.mirror_rect = self.mirror_image.get_rect(topleft=(20, 250))

        button_y = current_height - 60
        self.vol_down_button = Button(rect=(current_width - 240, button_y, 50, 50), text="-", callback=sounds.decrease_volume)
        self.mute_button = Button(rect=(current_width - 180, button_y, 80, 50), text="Mute", callback=self.toggle_mute_text)
        self.vol_up_button = Button(rect=(current_width - 90, button_y, 50, 50), text="+", callback=sounds.increase_volume)
        self.volume_buttons = [self.vol_down_button, self.mute_button, self.vol_up_button]

        # --- Chat UI Layout ---
        self.chat_font = pygame.font.SysFont(DEFAULT_FONT_NAME, 28)
        input_box_height = 40
        chat_box_width = 600
        start_x = (current_width - chat_box_width) / 2

        self.chat_input_rect = pygame.Rect(
            start_x, 
            current_height - input_box_height - 10, 
            chat_box_width, 
            input_box_height
        )
        self.chat_response_rect = None

        self.food_replenish_delay = 1.0
        self.food_replenish_timer = 0.0

        if self.cat:
            # If cat exists (e.g., on resize), update its position based on the new layout
            cat_y_pos = current_height * 0.65
            new_cat_screen_x = self.cat_world_x + self.background_x
            self.cat.set_position(new_cat_screen_x, cat_y_pos)

        self.force_redraw = True

    def toggle_mute_text(self):
        """Wrapper to toggle mute and update button text."""
        sounds.toggle_mute()
        if sounds.is_muted:
            self.mute_button.text = "Unmute"
        else:
            self.mute_button.text = "Mute"
        # We need to re-render the button's text surface
        self.mute_button.text_surf = self.mute_button.font.render(self.mute_button.text, True, self.mute_button.text_color)
        self.mute_button.text_rect = self.mute_button.text_surf.get_rect(center=self.mute_button.rect.center)
        self.force_redraw = True # Force a redraw to show text change

    def on_enter(self, data=None):
        if not pygame.mixer.music.get_busy():
            sounds.play_music("music/background_music.ogg")
        # This is now the ONLY place the cat is created.
        # It prioritizes data passed from the previous scene (like customization).
        initial_data = data or self.game.cat_data or save_manager.load_game() or {"customization": {}}
        
        # Store the final data back to the game object for persistence
        self.game.cat_data = initial_data

        # Create the cat with the correct, consistent position.
        current_height = self.game.screen.get_size()[1]
        cat_y_pos = current_height * 0.65 # Consistent relative position
        
        # Calculate initial screen position based on the background offset
        initial_cat_screen_x = self.cat_world_x + self.background_x

        self.cat = Cat(
            position=(initial_cat_screen_x, cat_y_pos),
            initial_stats=initial_data
        )
        # Force a full redraw on entering the scene
        self.force_redraw = True
    
    def on_resume(self):
        """Called when returning from another scene (like wardrobe)."""
        # Force a full redraw when returning from wardrobe
        self.force_redraw = True
        
        # Reload cat with updated data
        if self.game.cat_data and self.cat:
            # Update the existing cat with new data
            current_width, current_height = self.game.screen.get_size()
            cat_y_pos = current_height * 0.65
            
            # *** FIX: Calculate the cat's screen position the same way as on_enter ***
            resumed_cat_screen_x = self.cat_world_x + self.background_x
            
            # Create new cat with updated data and the CORRECT position
            self.cat = Cat(
                position=(resumed_cat_screen_x, cat_y_pos),
                initial_stats=self.game.cat_data
            )
        
    def on_quit(self):
        if self.cat:
            save_manager.save_game(self.cat.to_dict())
    
    def handle_mirror_click(self, mouse_pos):
        """Check if the mirror was clicked and open wardrobe."""
        if self.mirror_rect.collidepoint(mouse_pos):
            # Pass current cat data to wardrobe scene
            current_cat_data = self.cat.to_dict() if self.cat else self.game.cat_data
            self.scene_manager.push(WardrobeScene, data=current_cat_data)
            return True
        return False

    def handle_event(self, event):
        # --- 1. Handle Chat Input First ---
        # If we are chatting, all keyboard events go to the chat box.
        if self.is_chatting:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.chat_response_text = self.cat.get_chat_response(self.chat_input_text)
                    self.chat_response_timer = self.chat_response_duration
                    self.is_chatting = False
                    self.chat_input_text = ""
                    sounds.play_effect("effects/meow.wav")
                elif event.key == pygame.K_BACKSPACE:
                    self.chat_input_text = self.chat_input_text[:-1]
                elif event.key == pygame.K_ESCAPE:
                    self.is_chatting = False
                    self.chat_input_text = ""
                else:
                    self.chat_input_text += event.unicode
                self.force_redraw = True
            
            # CRITICAL: Stop processing other events while chatting.
            return 

        # --- 2. Handle Global Scene Events ---
        # These events are not blocked by the chat.
        if event.type == pygame.VIDEORESIZE:
            self._recalculate_layout()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                from scenes.menu import MenuScene
                self.scene_manager.set_scene(MenuScene)

        # --- 3. Handle UI and Game Object Events ---
        # These are processed if we are NOT chatting.
        self.cat.handle_event(event)
        for button in self.volume_buttons:
            button.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left-click
                if self.food_item.visible and self.food_item.rect.collidepoint(event.pos):
                    self.food_item.is_dragging = True
                    self.food_item.offset_x = event.pos[0] - self.food_item.rect.x
                    self.food_item.offset_y = event.pos[1] - self.food_item.rect.y
                else:
                    self.handle_mirror_click(event.pos)
            elif event.button == 3: # Right-click
                if self.cat.rect.collidepoint(event.pos):
                    sounds.play_effect("effects/meow.wav")
                    self.is_chatting = True
                    self.chat_input_text = ""
                    self.chat_response_text = ""
                    self.force_redraw = True
        
        elif event.type == pygame.MOUSEMOTION:
            if self.food_item.is_dragging:
                self.food_item.handle_drag_motion(event.pos)
                self.force_redraw = True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.food_item.is_dragging:
                self.food_item.is_dragging = False
                if self.cat.collides_with_item(self.food_item):
                    self.cat.feed()
                    self.food_item.hide()
                    sounds.play_effect("effects/eat.wav")
                else:
                    self.dirty_rects.append(self.food_item.rect.copy())
                    self.food_item.reset_position()
                self.force_redraw = True

    def update(self, dt):
        if self.chat_response_timer > 0:
            self.chat_response_timer -= dt
            if self.chat_response_timer <= 0:
                self.chat_response_text = ""
                self.force_redraw = True # Redraw to clear the text

        keys = pygame.key.get_pressed()
        panned = False
        if keys[pygame.K_LEFT]:
            self.background_x += self.pan_speed * dt
            panned = True
        if keys[pygame.K_RIGHT]:
            self.background_x -= self.pan_speed * dt
            panned = True
        
        # Clamp the background position to its limits
        self.background_x = max(-self.max_pan_x, min(0, self.background_x))

        if panned:
            # If we panned, update the cat's screen position
            new_cat_screen_x = self.cat_world_x + self.background_x
            self.cat.set_position(new_cat_screen_x, self.cat.position[1])
            self.force_redraw = True

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
    
    def _draw_chat_ui(self, screen):
        """Draws the chat input box and the cat's response."""
        # Draw the cat's response above its head
        if self.chat_response_timer > 0 and self.chat_response_text:
            response_surf = self.chat_font.render(self.chat_response_text, True, BLACK, (255, 255, 255, 200))
            self.chat_response_rect = response_surf.get_rect(midbottom=(self.cat.rect.centerx, self.cat.rect.top - 10))
            pygame.draw.rect(screen, (255, 255, 255, 200), self.chat_response_rect.inflate(10, 10), border_radius=8)
            screen.blit(response_surf, self.chat_response_rect)
        
        # Draw the input box if chatting
        if self.is_chatting:
            pygame.draw.rect(screen, WHITE, self.chat_input_rect, border_radius=5)
            pygame.draw.rect(screen, BLACK, self.chat_input_rect, 2, border_radius=5)
            input_surf = self.chat_font.render(self.chat_input_text, True, BLACK)
            screen.blit(input_surf, (self.chat_input_rect.x + 10, self.chat_input_rect.y + 5))
        
    def on_exit(self):
        if self.cat:
            self.game.cat_data = self.cat.to_dict()

    def draw(self, screen):
        # If a full redraw is needed, do it once and return
        if self.force_redraw:
            screen.blit(self.background_image, (self.background_x, self.background_y))
            self.cat.draw(screen)
            self.food_item.draw(screen)
            screen.blit(self.mirror_image, self.mirror_rect)
            self._draw_hud(screen)
            
            for button in self.volume_buttons:
                button.draw(screen)
                
            # FIX: Draw chat UI only once during full redraw
            self._draw_chat_ui(screen)
                
            self.force_redraw = False
            return [screen.get_rect()]

        # --- REVISED Dirty Rect Logic ---
        rects_to_update = []

        # 1. Add last known positions of ALL potentially overlapping items.
        rects_to_update.append(self.cat.last_rect)
        rects_to_update.append(self.food_item.last_rect)
        # Add the static UI elements' rects to ensure the area is cleaned
        # if the cat moves away from behind them.
        rects_to_update.append(self.mirror_rect)
        rects_to_update.append(self.hud_rect)

        for button in self.volume_buttons:
            rects_to_update.append(button.rect)

        # Add chat UI rects to be cleaned
        rects_to_update.append(self.chat_input_rect)
        if self.chat_response_rect:
             rects_to_update.append(self.chat_response_rect)

        # 2. Add any special one-time dirty rects.
        rects_to_update.extend(self.dirty_rects)
        self.dirty_rects = []

        # 3. Redraw the background ONCE over all dirty areas.
        # Filter out any None rects before iterating.
        for rect in filter(None, rects_to_update):
            screen.blit(self.background_image, rect, rect.move(-self.background_x, -self.background_y))

        # 4. Draw all entities and UI in their NEW positions, in the correct order.
        self.cat.draw(screen)
        self.food_item.draw(screen)
        screen.blit(self.mirror_image, self.mirror_rect)
        self._draw_hud(screen)

        for button in self.volume_buttons:
            button.draw(screen)
            
        # FIX: Draw chat UI only once during dirty rect updates
        self._draw_chat_ui(screen)

        # 5. Add the new positions to the final update list.
        rects_to_update.append(self.cat.rect)
        rects_to_update.append(self.food_item.rect)
        # The mirror and HUD rects are already in the list, so they will be updated.

        return [r for r in rects_to_update if r]