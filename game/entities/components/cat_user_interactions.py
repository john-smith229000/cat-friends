# entities/components/cat_user_interactions.py

import pygame
import random

class CatUserInteractions:
    """Handles all user interactions like petting, feeding, clicking."""
    
    def __init__(self):
        self.is_being_petted = False
        self.is_hovered_by_food = False
        
        # Idle animation logic
        self.idle_animation_timer = random.uniform(2, 7)
        self.is_playing_idle_sequence = False

        # Blink animation logic
        self.blink_timer = random.uniform(2.2, 7.4)
        self.is_blinking = False
        self.blink_duration = 0.20
        self.blink_duration_timer = 0.0
    
    def handle_event(self, event, rect, mask):
        """Processes user input events."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and rect.collidepoint(event.pos):
                # Pixel-perfect check
                pos_in_mask = (event.pos[0] - rect.x, event.pos[1] - rect.y)
                if mask and mask.get_at(pos_in_mask):
                    self.is_being_petted = True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.is_being_petted:
                self.is_being_petted = False
    
    def update(self, dt, base_animation):
        """Updates interaction-related animations and timers."""
        # Handle idle animation logic
        self.idle_animation_timer -= dt
        if self.idle_animation_timer <= 0 and not self.is_playing_idle_sequence:
            self.is_playing_idle_sequence = True
            num_frames = len(base_animation.frames)
            frames_to_play = (num_frames - 1) * 2 + random.randint(0, num_frames - 1)
            base_animation.play(frames_to_play)

        if self.is_playing_idle_sequence and base_animation.is_done:
            self.is_playing_idle_sequence = False
            self.idle_animation_timer = random.uniform(2, 7)
        
        # Handle blink animation logic (only if not being petted)
        if not self.is_being_petted:
            if not self.is_blinking:
                self.blink_timer -= dt
                if self.blink_timer <= 0:
                    self.is_blinking = True
                    self.blink_duration_timer = self.blink_duration
            else:
                self.blink_duration_timer -= dt
                if self.blink_duration_timer <= 0:
                    self.is_blinking = False
                    self.blink_timer = random.uniform(1, 5)
    
    def set_food_hover(self, is_hovering):
        """Sets the flag for when food is hovering over the cat."""
        self.is_hovered_by_food = is_hovering
