# game/main.py

import pygame
import sys
import time

from settings import *
from core.scene_manager import SceneManager
from scenes.menu import MenuScene

class Game:
    def __init__(self):
        pygame.init()
        
        # Set window position before creating the display
        import os
        os.environ['SDL_VIDEO_WINDOW_POS'] = '100,100'
        
        pygame.display.set_caption(WINDOW_TITLE)
        
        # Create window with resizable flag - this allows proper maximize behavior
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        
        self.clock = pygame.time.Clock()
        self.last_time = time.time()
        self.running = True
        
        # Store cat data so it persists across scenes
        self.cat_data = None
        
        # Fullscreen tracking
        self.fullscreen = False
        self.windowed_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
        
        self.scene_manager = SceneManager(self, MenuScene)

    def run(self):
        """The main game loop."""
        while self.running:
            now = time.time()
            dt = now - self.last_time
            self.last_time = now

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.VIDEORESIZE:
                    # Handle window resize - update screen surface
                    if not self.fullscreen:  # Only handle resize in windowed mode
                        self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_f:
                        # F key for fullscreen
                        self.toggle_borderless_fullscreen()
                
                self.scene_manager.handle_event(event)

            self.scene_manager.update(dt)
            dirty_rects = self.scene_manager.draw()
            pygame.display.update(dirty_rects) # Pass the list of updated rects
            
            self.clock.tick(FPS)
            
        # This code runs only AFTER the game loop has stopped
        print("Game loop ended. Saving and quitting...")
        
        # Save cat data if we have any
        if self.cat_data:
            from core.save_manager import save_game
            save_game(self.cat_data)
            print("Game saved on exit!")
        
        # Also call on_quit on active scene for any other cleanup
        active_scene = self.scene_manager.get_active_scene()
        if active_scene and hasattr(active_scene, 'on_quit'):
            active_scene.on_quit()
            
        pygame.quit()
        sys.exit()
    
    def toggle_borderless_fullscreen(self):
        """Toggle between windowed and fullscreen mode"""
        
        if not self.fullscreen:
            # Store current window size
            self.windowed_size = self.screen.get_size()
            
            # Go to fullscreen using pygame.FULLSCREEN flag
            # Using (0, 0) lets pygame choose the best resolution
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.fullscreen = True
            
            # Get actual fullscreen size for debugging
            actual_size = self.screen.get_size()
            print(f"Switched to fullscreen: {actual_size[0]}x{actual_size[1]}")
            
        else:
            # Return to windowed mode
            self.screen = pygame.display.set_mode(
                self.windowed_size,
                pygame.RESIZABLE
            )
            pygame.display.set_caption(WINDOW_TITLE)
            self.fullscreen = False
            print(f"Returned to windowed: {self.windowed_size}")

if __name__ == '__main__':
    game = Game()
    game.run()