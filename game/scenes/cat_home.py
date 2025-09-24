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
        
        self.cat = None
        self.background_x = 0
        self.background_y = 0 
        self.background_y_offset = 600
        self.pan_speed = 200
        self.zoom_factor = 2.5
        
        self.cat_world_x = 0
        self.bed_world_x = 0
        self.bed_world_y = 0
        self.bed_rect = None
        self.bed_image = None

        self.paused = False
        self._recalculate_layout()

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

        self.background_x = -self.max_pan_x / 2
        self.background_y = -min(self.background_y_offset, max_pan_y)
        
        self.cat_world_x = self.background_image.get_width() / 2
        
        # CRITICAL FIX: Set bed position using midbottom anchor for consistency.
        self.bed_world_x = self.background_image.get_width() / 2 + 400
        self.bed_world_y = current_height * 0.57
        
        try:
            self.bed_image = resources.load_image("images/items/furniture/bed.png", scale=0.25)
        except:
            self.bed_image = pygame.Surface((200, 200), pygame.SRCALPHA); self.bed_image.fill((100, 50, 150, 100))
            print("Warning: Bed image not found, using placeholder")

        # Update bed rect position based on current pan.
        self.bed_rect = self.bed_image.get_rect(center=(self.bed_world_x + self.background_x, self.bed_world_y))
        
        food_image = resources.load_image("images/items/food/001.png", scale=0.5)
        food_home_pos = (current_width - food_image.get_width() - 50, current_height - food_image.get_height() - 50)
        self.food_item = DraggableItem(food_image, food_home_pos)
        
        self.hud_font = pygame.font.SysFont(DEFAULT_FONT_NAME, 24)
        self.mirror_image = resources.load_image("images/ui_elements/mirror.png", scale=0.3)
        self.mirror_rect = self.mirror_image.get_rect(topleft=(20, 250))

        button_y = current_height - 60
        self.volume_buttons = [
            Button(rect=(current_width - 240, button_y, 50, 50), text="-", callback=sounds.decrease_volume),
            Button(rect=(current_width - 180, button_y, 80, 50), text="Mute", callback=self.toggle_mute_text),
            Button(rect=(current_width - 90, button_y, 50, 50), text="+", callback=sounds.increase_volume)
        ]
        
        self.chat_font = pygame.font.SysFont(DEFAULT_FONT_NAME, 28)
        input_box_height = 40
        chat_box_width = 600
        self.chat_input_rect = pygame.Rect((current_width - chat_box_width) / 2, current_height - input_box_height - 10, chat_box_width, input_box_height)
        
        self.food_replenish_delay = 1.0
        self.food_replenish_timer = 0.0

        if self.cat:
            self.cat.bed_world_x = self.bed_world_x + self.background_x
            self.cat.bed_world_y = self.bed_world_y
            if not self.cat.is_sleeping():
                cat_y_pos = current_height * 0.63
                new_cat_screen_x = self.cat_world_x + self.background_x
                self.cat.set_position(new_cat_screen_x, cat_y_pos)
            else:
                self.cat.set_position(self.bed_rect.centerx, self.bed_world_y)

    def on_enter(self, data=None):
        if not pygame.mixer.music.get_busy():
            sounds.play_music("music/background_music.ogg")
            
        initial_data = data or self.game.cat_data or save_manager.load_game() or {}
        self.game.cat_data = initial_data

        current_height = self.game.screen.get_size()[1]
        
        # CRITICAL FIX: Use the consistent midbottom anchor point for correct height.
        cat_y_pos = current_height * 0.63
        initial_cat_screen_x = self.cat_world_x + self.background_x

        self.cat = Cat(position=(initial_cat_screen_x, cat_y_pos), initial_stats=initial_data, sleep_scale=0.25)
        
        self.cat.bed_world_x = self.bed_rect.centerx
        self.cat.bed_world_y = self.bed_world_y

        if initial_data.get("is_sleeping"):
            self.cat.start_sleeping(self.bed_rect.centerx, self.bed_world_y)

    def on_pause(self):
        self.paused = True
    
    def on_resume(self):
        if self.game.cat_data and self.cat:
            was_sleeping = self.cat.is_sleeping()
            current_height = self.game.screen.get_size()[1]
            cat_y_pos = current_height * 0.63
            
            if was_sleeping:
                position = (self.bed_rect.centerx, self.bed_world_y)
            else:
                position = (self.cat_world_x + self.background_x, cat_y_pos)
            
            self.cat = Cat(position=position, initial_stats=self.game.cat_data, sleep_scale=0.2)
            
            self.cat.bed_world_x = self.bed_rect.centerx
            self.cat.bed_world_y = self.bed_world_y
            
            if was_sleeping:
                self.cat.start_sleeping(self.bed_rect.centerx, self.bed_world_y)
    
    def on_exit(self):
        """Called when leaving the scene, ensures the game is saved."""
        if self.cat:
            self.game.cat_data = self.cat.to_dict()
            save_manager.save_game(self.game.cat_data)
        
    def handle_event(self, event):
        # 1. Handle active states like chatting first.
        if self.is_chatting:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    sounds.play_effect("effects/meow.wav")
                    self.chat_response_text = self.cat.get_chat_response(self.chat_input_text)
                    self.chat_response_timer = self.chat_response_duration
                    self.is_chatting = False
                    self.chat_input_text = ""
                elif event.key == pygame.K_BACKSPACE: self.chat_input_text = self.chat_input_text[:-1]
                elif event.key == pygame.K_ESCAPE: self.is_chatting = False; self.chat_input_text = ""
                else: self.chat_input_text += event.unicode
            return # Stop further event processing while typing.

        # 2. Pass events to UI buttons.
        for button in self.volume_buttons:
            button.handle_event(event)

        # 3. Handle MOUSEBUTTONDOWN with clear priority.
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check for a click ON THE CAT first.
            if self.cat.rect and self.cat.rect.collidepoint(event.pos):
                # If it's a right-click, check the cat's state BEFORE handling the event.
                if event.button == 3:
                    if self.cat.is_sleeping():
                        self.cat.handle_event(event) # It's a poke.
                    else:
                        sounds.play_effect("effects/meow.wav")
                        self.is_chatting = True # It's a chat request.
                else:
                    self.cat.handle_event(event) # It's a left-click for petting.
            
            # If the click was NOT on the cat, check other game objects.
            elif self.bed_rect.collidepoint(event.pos) and self.cat.can_sleep():
                self.cat.start_sleeping(self.bed_rect.centerx, self.bed_world_y)
            elif self.food_item.visible and self.food_item.rect.collidepoint(event.pos):
                self.food_item.is_dragging = True
                self.food_item.offset_x = event.pos[0] - self.food_item.rect.x
                self.food_item.offset_y = event.pos[1] - self.food_item.rect.y
            elif self.mirror_rect.collidepoint(event.pos) and not self.cat.is_sleeping():
                self.scene_manager.push(WardrobeScene, data=self.cat.to_dict())

        # 4. Handle all other event types.
        else:
            self.cat.handle_event(event) # Pass MOUSEUP, MOUSEMOTION, etc. to the cat.

        if event.type == pygame.VIDEORESIZE: self._recalculate_layout()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            from scenes.menu import MenuScene
            self.scene_manager.set_scene(MenuScene)
        if event.type == pygame.MOUSEMOTION and self.food_item.is_dragging:
            self.food_item.handle_drag_motion(event.pos)
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.food_item.is_dragging:
            self.food_item.is_dragging = False
            if self.cat.collides_with_item(self.food_item):
                self.cat.feed()
                self.food_item.hide()
                sounds.play_effect("effects/eat.wav")
            else:
                self.food_item.reset_position()

    def update(self, dt):
        if self.paused:
            return
        if self.chat_response_timer > 0: self.chat_response_timer -= dt
        keys = pygame.key.get_pressed(); panned = False
        if keys[pygame.K_LEFT]: self.background_x += self.pan_speed * dt; panned = True
        if keys[pygame.K_RIGHT]: self.background_x -= self.pan_speed * dt; panned = True
        self.background_x = max(-self.max_pan_x, min(0, self.background_x))
        
        was_sleeping = self.cat.is_sleeping()
        self.cat.update(dt)
        just_woke_up = was_sleeping and not self.cat.is_sleeping()

        if panned or just_woke_up:
            self.bed_rect.center = (self.bed_world_x + self.background_x, self.bed_world_y)
            self.cat.bed_world_x = self.bed_rect.centerx
            if self.cat.is_sleeping(): self.cat.set_position(self.bed_rect.centerx, self.bed_world_y)
            else: self.cat.set_position(self.cat_world_x + self.background_x, self.game.screen.get_height() * 0.63)

        self.food_item.update(dt)
        self.cat.set_food_hover(self.food_item.is_dragging and self.cat.collides_with_item(self.food_item))
        if not self.food_item.visible:
            self.food_replenish_timer += dt
            if self.food_replenish_timer >= self.food_replenish_delay: self.food_item.show(); self.food_item.reset_position(); self.food_replenish_timer = 0.0

    def draw(self, screen):
        # --- RENDER FIX: This simple full redraw prevents all disappearing bugs ---
        screen.blit(self.background_image, (self.background_x, self.background_y))
        if self.bed_image: screen.blit(self.bed_image, self.bed_rect)
        self.cat.draw(screen)
        self.food_item.draw(screen)
        screen.blit(self.mirror_image, self.mirror_rect)
        self._draw_hud(screen)
        for button in self.volume_buttons: button.draw(screen)
        self._draw_chat_ui(screen)
        return [screen.get_rect()]
    
    # --- Helper methods below ---

    def handle_bed_click(self, mouse_pos):
        if self.bed_rect and self.bed_rect.collidepoint(mouse_pos) and self.cat and self.cat.can_sleep():
            self.cat.start_sleeping(self.bed_rect.centerx, self.bed_world_y)
            sounds.play_effect("effects/purr.wav")
            return True
        return False
        
    def handle_mirror_click(self, mouse_pos):
        if self.mirror_rect.collidepoint(mouse_pos):
            self.scene_manager.push(WardrobeScene, data=self.cat.to_dict())
            return True
        return False
        
    def _draw_hud(self, screen):
        # Happiness Bar
        hap_text = self.hud_font.render("Happiness", True, WHITE)
        screen.blit(hap_text, (20, 20))
        pygame.draw.rect(screen, (50, 50, 50), (20, 50, 200, 25))
        hap_width = (self.cat.happiness / MAX_STAT_VALUE) * 200
        pygame.draw.rect(screen, (50, 200, 50), (20, 50, hap_width, 25))
        pygame.draw.rect(screen, WHITE, (20, 50, 200, 25), 2)
        
        # Hunger Bar
        hun_text = self.hud_font.render("Hunger", True, WHITE)
        screen.blit(hun_text, (20, 90))
        pygame.draw.rect(screen, (50, 50, 50), (20, 120, 200, 25))
        hun_width = (self.cat.hunger / MAX_STAT_VALUE) * 200
        pygame.draw.rect(screen, (200, 150, 50), (20, 120, hun_width, 25))
        pygame.draw.rect(screen, WHITE, (20, 120, 200, 25), 2)
        
        # Energy Bar
        energy_text = self.hud_font.render("Energy", True, WHITE)
        screen.blit(energy_text, (20, 160))
        pygame.draw.rect(screen, (50, 50, 50), (20, 190, 200, 25))
        energy_width = (self.cat.energy / MAX_STAT_VALUE) * 200
        energy_color = (50, 150, 200) if self.cat.energy > 50 else (200, 100, 50)
        pygame.draw.rect(screen, energy_color, (20, 190, energy_width, 25))
        pygame.draw.rect(screen, WHITE, (20, 190, 200, 25), 2)
    
    def _draw_chat_ui(self, screen):
        if self.chat_response_timer > 0 and self.chat_response_text:
            response_surf = self.chat_font.render(self.chat_response_text, True, BLACK, (255, 255, 255, 200))
            response_rect = response_surf.get_rect(midbottom=(self.cat.rect.centerx, self.cat.rect.top - 10))
            pygame.draw.rect(screen, (255, 255, 255, 200), response_rect.inflate(10, 10), border_radius=8)
            screen.blit(response_surf, response_rect)
        
        if self.is_chatting:
            pygame.draw.rect(screen, WHITE, self.chat_input_rect, border_radius=5)
            pygame.draw.rect(screen, BLACK, self.chat_input_rect, 2, border_radius=5)
            screen.blit(self.chat_font.render(self.chat_input_text, True, BLACK), (self.chat_input_rect.x + 10, self.chat_input_rect.y + 5))
        
    def on_quit(self):
        if self.cat: save_manager.save_game(self.cat.to_dict())
    
    def toggle_mute_text(self):
        sounds.toggle_mute()
        self.mute_button.text = "Unmute" if sounds.is_muted else "Mute"
        self.mute_button.text_surf = self.mute_button.font.render(self.mute_button.text, True, self.mute_button.text_color)
        self.mute_button.text_rect = self.mute_button.text_surf.get_rect(center=self.mute_button.rect.center)