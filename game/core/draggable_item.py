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

        self.visible = True
    
    def update(self, dt):
        """Placeholder for future update logic if needed."""
        pass

    def start_drag(self, mouse_pos):
        """Begins the dragging process."""
        self.is_dragging = True
        self.offset_x = mouse_pos[0] - self.rect.x
        self.offset_y = mouse_pos[1] - self.rect.y

    def stop_drag(self):
        """Stops the dragging process."""
        self.is_dragging = False

    def handle_drag_motion(self, mouse_pos):
        """Updates the item's position while being dragged."""
        if self.is_dragging:
            self.rect.x = mouse_pos[0] - self.offset_x
            self.rect.y = mouse_pos[1] - self.offset_y

    def draw(self, screen):
        """Draw the item to the screen only if it's visible."""
        if self.visible:
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