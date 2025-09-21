# game/main.py

import pygame
import sys
import time

# Import our custom modules
from settings import *
from core.scene_manager import SceneManager
from scenes.menu import MenuScene  

# The old placeholder scene can be deleted from this file.

class Game:
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption(WINDOW_TITLE)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.last_time = time.time()
        
        # Initialize the Scene Manager with our new MenuScene
        self.scene_manager = SceneManager(MenuScene) # <-- USE THE NEW SCENE

    def run(self):
        """The main game loop."""
        while True:
            # Calculate delta time (dt) for frame-independent logic
            now = time.time()
            dt = now - self.last_time
            self.last_time = now

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # Pass the event to the active scene
                self.scene_manager.handle_event(event)

            # Update the active scene
            self.scene_manager.update(dt)

            # Draw the active scene and update the display
            self.scene_manager.draw()
            
            # Cap the frame rate
            self.clock.tick(FPS)

if __name__ == '__main__':
    game = Game()
    game.run()