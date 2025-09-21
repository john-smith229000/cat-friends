# game/core/scene_manager.py

import pygame

class BaseScene:
    def __init__(self, scene_manager, game):
        self.scene_manager = scene_manager
        self.game = game

    def handle_event(self, event): pass
    def update(self, dt): pass
    def draw(self, screen): pass
    def on_enter(self, data=None): pass
    def on_exit(self): pass
    def on_quit(self): pass

class SceneManager:
    def __init__(self, game, initial_scene_class):
        self.game = game
        self.screen = pygame.display.get_surface()
        self.scenes = []
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
        new_scene = scene_class(self, self.game)
        new_scene.on_enter(data)
        self.scenes.append(new_scene)
        
    def pop(self):
        if self.get_active_scene():
            self.get_active_scene().on_exit()
            return self.scenes.pop()

    def set_scene(self, scene_class, data=None):
        while self.scenes:
            self.pop()
        self.push(scene_class, data)