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
        self._pending_move = None # Store requested mouse position

        self.visible = True

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.rect.collidepoint(event.pos) and self.visible:
                    self.is_dragging = True
                    self.offset_x = event.pos[0] - self.rect.x
                    self.offset_y = event.pos[1] - self.rect.y
        
        elif event.type == pygame.MOUSEBUTTONUP:
            pass # Dragging state is handled in the scene
        
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                # Instead of moving here, just store the requested position
                self._pending_move = event.pos

    def update(self, dt):
        """Applies movement and saves the last position."""
        # Always save the position from the start of the frame
        self.last_rect = self.rect.copy()

        # Apply any movement that was requested from handle_event
        if self._pending_move:
            self.rect.x = self._pending_move[0] - self.offset_x
            self.rect.y = self._pending_move[1] - self.offset_y
            self._pending_move = None # Clear the pending move once applied

    def draw(self, screen):
        """Draw the item to the screen only if it's visible."""
        if self.visible:
            screen.blit(self.image, self.rect)
        return self.rect

    def reset_position(self):
        """Resets the item to its home position."""
        self.last_rect = self.rect.copy() # Update last_rect before moving
        self.rect.topleft = self.home_pos

    def hide(self):
        """Makes the item invisible."""
        self.visible = False

    def show(self):
        """Makes the item visible."""
        self.visible = True