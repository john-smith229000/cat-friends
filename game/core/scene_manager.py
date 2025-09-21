# game/core/scene_manager.py

import pygame

class BaseScene:
    """
    A base template for all scenes.
    This defines the interface that the SceneManager expects.
    """
    def __init__(self, scene_manager):
        self.scene_manager = scene_manager

    def handle_event(self, event):
        """Handle user input and other events."""
        pass

    def update(self, dt):
        """Update game state for the scene."""
        pass

    def draw(self, screen):
        """Draw the scene to the screen."""
        pass

    def on_enter(self, data=None):
        """Called once when the scene becomes active. Can receive data."""
        pass

    def on_exit(self):
        """Called once when the scene is deactivated."""
        pass


class SceneManager:
    """
    Manages a stack of scenes, handling transitions and passing
    events, updates, and draw calls to the active scene.
    """
    def __init__(self, initial_scene_class):
        self.screen = pygame.display.get_surface()
        self.scenes = []
        # We start by pushing the initial scene, passing this manager instance to it
        self.push(initial_scene_class)

    def get_active_scene(self):
        return self.scenes[-1] if self.scenes else None

    def handle_event(self, event):
        if self.get_active_scene():
            self.get_active_scene().handle_event(event)

    def update(self, dt):
        if self.get_active_scene():
            self.get_active_scene().update(dt)

    def draw(self):
        if self.get_active_scene():
            self.get_active_scene().draw(self.screen)
        pygame.display.flip()

    def push(self, scene_class, data=None):
        """

        Pushes a new scene onto the stack, making it the active one.
        The previous scene is paused but remains in memory.
        """
        new_scene = scene_class(self)
        new_scene.on_enter(data)
        self.scenes.append(new_scene)

    def pop(self):
        """
        Removes the active scene from the stack.
        The scene below it on the stack becomes the new active scene.
        """
        if self.get_active_scene():
            self.get_active_scene().on_exit()
            return self.scenes.pop()

    def set_scene(self, scene_class, data=None):
        """
        Clears the scene stack and sets a new scene as the active one.
        This is useful for major transitions like going from the main menu to the game.
        """
        while self.scenes:
            self.pop()
        self.push(scene_class, data)