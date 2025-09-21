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

    def reset(self):
        """Resets the animation to its first frame and makes it active."""
        self.frame_index = 0
        self.time_accumulator = 0.0
        self.direction = 1
        self.is_done = False # Resetting means it's no longer "done"

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
        # If it's a non-looping animation and it's already done, do nothing.
        if self.is_done and not self.loop and not self.pingpong: # Pingpong might still need to update after 'done' if direction changes
            return

        self.time_accumulator += dt
        
        while self.time_accumulator >= self.duration: # Use while loop to catch up if dt is large
            self.time_accumulator -= self.duration
            self.frame_index += self.direction

            if self.pingpong:
                if self.frame_index >= len(self.frames) - 1:
                    self.direction = -1
                elif self.frame_index <= 0:
                    self.direction = 1
                
                # If ping-pong and we reached the start again, and it's not a loop, then it's done.
                if self.frame_index == 0 and self.direction == 1 and not self.loop:
                    self.is_done = True

            elif self.frame_index >= len(self.frames):
                if self.loop:
                    self.frame_index = 0
                else:
                    self.frame_index = len(self.frames) - 1
                    self.is_done = True # Mark as done if it's a non-looping animation that finished
                    return # Stop updating immediately after finishing


    def is_playing(self):
        """Returns True if the animation is currently active (not done if non-looping)."""
        return not self.is_done