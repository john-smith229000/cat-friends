# game/core/sound_manager.py

import pygame
from pathlib import Path

class SoundManager:
    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        self.base_path = Path(__file__).parent.parent.parent
        self.sounds_path = self.base_path / "assets" / "sounds"
        
        self._effects_cache = {}
        self._music_cache = {}

        self.music_volume = 0.5 # Default volume
        self.is_muted = False

    def set_music_volume(self, volume):
        """Sets the music volume, clamping between 0.0 and 1.0."""
        self.music_volume = max(0.0, min(1.0, volume))
        if not self.is_muted:
            pygame.mixer.music.set_volume(self.music_volume)

    def increase_volume(self, amount=0.1):
        """Increases music volume."""
        self.set_music_volume(self.music_volume + amount)

    def decrease_volume(self, amount=0.1):
        """Decreases music volume."""
        self.set_music_volume(self.music_volume - amount)

    def toggle_mute(self):
        """Toggles music mute on and off."""
        self.is_muted = not self.is_muted
        if self.is_muted:
            pygame.mixer.music.set_volume(0.0)
        else:
            pygame.mixer.music.set_volume(self.music_volume)

    def load_effect(self, path_from_sounds):
        if path_from_sounds in self._effects_cache:
            return self._effects_cache[path_from_sounds]
        
        full_path = self.sounds_path / path_from_sounds
        if not full_path.exists():
            print(f"---!!! FAILED TO FIND SOUND EFFECT AT: {full_path}")
            return None
            
        try:
            sound = pygame.mixer.Sound(str(full_path))
            self._effects_cache[path_from_sounds] = sound
            return sound
        except pygame.error as e:
            print(f"Error loading sound effect: {full_path}")
            raise e

    def play_effect(self, path_from_sounds, volume=1.0):
        sound = self.load_effect(path_from_sounds)
        if sound:
            sound.set_volume(volume)
            sound.play()

    def load_music(self, path_from_sounds):
        if path_from_sounds in self._music_cache:
            return self._music_cache[path_from_sounds]
            
        full_path = self.sounds_path / path_from_sounds
        if not full_path.exists():
            print(f"---!!! FAILED TO FIND MUSIC AT: {full_path}")
            return None
        
        self._music_cache[path_from_sounds] = str(full_path)
        return str(full_path)

    def play_music(self, path_from_sounds, loops=-1):
        music_path = self.load_music(path_from_sounds)
        if music_path:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(loops)

    def stop_music(self):
        pygame.mixer.music.stop()

# Create a single, global instance
sounds = SoundManager()