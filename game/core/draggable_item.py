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
        self.home_pos = initial_pos
        self.mask = pygame.mask.from_surface(self.image)
        
        self.is_dragging = False
        self.offset_x = 0
        self.offset_y = 0

        self.visible = True # <-- ADDED VISIBILITY FLAG

    def handle_event(self, event):
        # ... (no changes in this method)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.rect.collidepoint(event.pos) and self.visible: # Can only drag if visible
                    self.is_dragging = True
                    self.offset_x = event.pos[0] - self.rect.x
                    self.offset_y = event.pos[1] - self.rect.y
        
        elif event.type == pygame.MOUSEBUTTONUP:
            pass
        
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                self.rect.x = event.pos[0] - self.offset_x
                self.rect.y = event.pos[1] - self.offset_y

    def update(self, dt):
        pass

    def draw(self, screen):
        """Draw the item to the screen only if it's visible."""
        if self.visible: # <-- CHECK VISIBILITY
            screen.blit(self.image, self.rect)

    def reset_position(self):
        """Resets the item to its home position."""
        self.rect.topleft = self.home_pos

    def hide(self):
        """Makes the item invisible."""
        self.visible = False

    def show(self):
        """Makes the item visible."""
        self.visible = True