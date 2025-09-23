# game/core/draggable_item.py

import pygame

class DraggableItem:
    """
    Represents an item that can be picked up, dragged, and dropped.
    """
    def __init__(self, image, initial_pos):
        self.original_image = image
        self.image = image
        self.rect = self.image.get_rect(topleft=initial_pos)
        self.last_rect = self.rect.copy() # For dirty rect tracking
        self.home_pos = initial_pos
        self.mask = pygame.mask.from_surface(self.image)
        
        self.is_dragging = False
        self.offset_x = 0
        self.offset_y = 0

        self.visible = True
    
    def update(self, dt):
        """Saves the last position for dirty rect tracking."""
        # Always save the position from the start of the frame
        self.last_rect = self.rect.copy()

    def handle_drag_motion(self, mouse_pos):
        """Call this from the scene when the item should move during dragging."""
        if self.is_dragging:
            # Save the old position before moving
            old_rect = self.rect.copy()
            
            # Update to new position
            self.rect.x = mouse_pos[0] - self.offset_x
            self.rect.y = mouse_pos[1] - self.offset_y
            
            # Update last_rect to the old position so the draw method can clean it up
            self.last_rect = old_rect

    def draw(self, screen):
        """Draw the item to the screen only if it's visible."""
        if self.visible:
            screen.blit(self.image, self.rect)
        return self.rect

    def reset_position(self):
        """Resets the item to its home position."""
        self.rect.topleft = self.home_pos

    def hide(self):
        """Makes the item invisible."""
        self.visible = False

    def show(self):
        """Makes the item visible."""
        self.visible = True