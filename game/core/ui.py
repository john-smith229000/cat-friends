# game/core/ui.py

import pygame
from settings import *
from core.sound_manager import sounds

class Button:
    """A simple, clickable button with text."""
    def __init__(self, rect, text, callback, font_name=DEFAULT_FONT_NAME, font_size=32):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        
        # Colors for different states
        self.color_normal = pygame.Color(100, 100, 120)  # Dark slate gray
        self.color_hover = pygame.Color(130, 130, 150)  # Lighter gray
        self.color_pressed = pygame.Color(80, 80, 100)   # Darker gray
        self.text_color = pygame.Color(255, 255, 255) # White
        
        self.font = pygame.font.SysFont(font_name, font_size)
        self.text_surf = self.font.render(text, True, self.text_color)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)
        
        self.is_hovered = False
        self.is_pressed = False

    def handle_event(self, event):
        """Processes a single event to update the button's state."""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered and event.button == 1:
                self.is_pressed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.is_hovered and self.is_pressed and event.button == 1:
                sounds.play_effect("effects/button_slash.wav")
                # Execute the callback function on click release
                self.callback()
            self.is_pressed = False

    def draw(self, screen):
        """Draws the button onto the given surface."""
        # Choose color based on state
        if self.is_pressed:
            color = self.color_pressed
        elif self.is_hovered:
            color = self.color_hover
        else:
            color = self.color_normal
            
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        screen.blit(self.text_surf, self.text_rect)