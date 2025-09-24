# game/entities/components/cat_user_interactions.py

import pygame
import random
from core.sound_manager import sounds


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

        # Wake up logic
        self.pokes_to_wake = 0
        self.poke_count = 0

    def handle_event(self, event, rect, mask, cat_state):
        """Processes user input events."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and rect.collidepoint(event.pos):
                # Pixel-perfect check for petting
                pos_in_mask = (event.pos[0] - rect.x, event.pos[1] - rect.y)
                if mask and mask.get_at(pos_in_mask):
                    self.is_being_petted = True
                    # Petting a sleeping cat is quieter
                    if not cat_state == "SLEEPING":
                        sounds.play_effect("effects/purr.wav")

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.is_being_petted:
                self.is_being_petted = False

    def update(self, dt, base_animation, cat_state):
        """Updates interaction-related animations and timers."""
        # Don't do idle animations if sleeping or moving
        if cat_state != "IDLE":
            self.is_playing_idle_sequence = False
            if base_animation.is_playing():
                base_animation.pause()
            return

        # Handle idle animation logic
        self.idle_animation_timer -= dt
        if self.idle_animation_timer <= 0 and not self.is_playing_idle_sequence:
            self.is_playing_idle_sequence = True
            num_frames = len(base_animation.frames)
            # Play a random number of frames to make idle more dynamic
            frames_to_play = random.randint(num_frames // 2, (num_frames -1) * 2)
            base_animation.play(frames_to_play)

        if self.is_playing_idle_sequence and base_animation.is_done:
            self.is_playing_idle_sequence = False
            self.idle_animation_timer = random.uniform(2, 7)

        # Handle blink animation logic (only if not being petted and idle)
        if not self.is_being_petted and cat_state == "IDLE":
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

    def start_sleeping(self):
        """Resets poke counter when sleep begins."""
        self.pokes_to_wake = 2
        self.poke_count = 0
        print(f"Cat needs {self.pokes_to_wake} pokes to wake up.")

    def poke(self):
        """Increments poke count and returns True if cat should wake up."""
        if self.pokes_to_wake > 0:
            self.poke_count += 1
            sounds.play_effect("effects/poke.wav")
            print(f"Poke {self.poke_count}/{self.pokes_to_wake}")
            if self.poke_count >= self.pokes_to_wake:
                return True
        return False