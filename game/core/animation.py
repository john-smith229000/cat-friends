# game/core/animation.py

import pygame

class Animation:
    """
    Manages a sequence of images for animation.
    Supports standard looping and ping-pong looping.
    """

    def __init__(self, frames, duration_per_frame, loop=True, pingpong=False):
        self.frames = frames
        self.masks = [pygame.mask.from_surface(frame) for frame in self.frames]
        self.duration = duration_per_frame # duration_per_frame should be in seconds
        self.loop = loop
        self.pingpong = pingpong
        
        self.frame_index = 0
        self.time_accumulator = 0.0
        self.direction = 1
        self.is_done = False # False means it's active or ready to start, True means it completed (if not looping)
        self.is_paused = True # Start paused
        self.frames_to_play = 0 # Number of frames to play when not looping continuously


    def reset(self):
        """Resets the animation to its first frame and makes it active."""
        self.frame_index = 0
        self.time_accumulator = 0.0
        self.direction = 1
        self.is_done = False # Resetting means it's no longer "done"
        self.is_paused = True

    def play(self, frame_count=None):
        """Starts playing the animation."""
        self.is_paused = False
        self.is_done = False
        if frame_count is not None:
            self.frames_to_play = frame_count
            self.loop = False # If we have a specific number of frames to play, it's not a continuous loop
        else:
            self.loop = True

    def pause(self):
        """Pauses the animation."""
        self.is_paused = True

    @property
    def image(self):
        """Returns the current frame's image surface."""
        if not self.frames: # Handle case of no frames
            return None
        return self.frames[self.frame_index]
    
    @property
    def mask(self):
        """Returns the current frame's mask."""
        return self.masks[self.frame_index]

    def update(self, dt):
        """
        Advances the animation based on delta time (dt).
        dt should be in seconds.
        """
        if self.is_paused or self.is_done:
            return

        self.time_accumulator += dt
        
        while self.time_accumulator >= self.duration:
            self.time_accumulator -= self.duration
            
            if not self.loop and self.frames_to_play <= 0:
                self.is_done = True
                self.pause()
                return

            self.frame_index += self.direction

            if not self.loop:
                self.frames_to_play -= 1


            if self.pingpong:
                if self.frame_index >= len(self.frames) - 1:
                    self.direction = -1
                elif self.frame_index <= 0:
                    self.direction = 1
                
                # This is the line that was causing the issue. By removing it, the animation will continue until frames_to_play is 0.


            elif self.frame_index >= len(self.frames):
                if self.loop:
                    self.frame_index = 0
                else:
                    self.frame_index = len(self.frames) - 1
                    self.is_done = True
                    self.pause()
                    return




    def is_playing(self):
        """Returns True if the animation is currently active (not done if non-looping)."""
        return not self.is_paused and not self.is_done