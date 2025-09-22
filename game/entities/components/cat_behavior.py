# game/entities/components/cat_behavior.py

class CatBehavior:
    """Manages movement, positioning, and basic AI behaviors."""
    
    def __init__(self, initial_position):
        self.position = list(initial_position)
        self.velocity = [0, 0]
        self.target_position = None
        self.movement_speed = 100  # pixels per second
        self.state = "idle"
    
    def set_position(self, x, y):
        """Sets the cat's position directly."""
        self.position = [x, y]
    
    def move_to(self, target_x, target_y):
        """Sets a target position for the cat to move towards."""
        self.target_position = [target_x, target_y]
    
    def update(self, dt):
        """Updates movement and position."""
        if self.target_position:
            dx = self.target_position[0] - self.position[0]
            dy = self.target_position[1] - self.position[1]
            distance = (dx**2 + dy**2)**0.5
            
            if distance > 2:  # If not close enough
                # Normalize and apply speed
                self.velocity[0] = (dx / distance) * self.movement_speed
                self.velocity[1] = (dy / distance) * self.movement_speed
                
                # Update position
                self.position[0] += self.velocity[0] * dt
                self.position[1] += self.velocity[1] * dt
            else:
                # Reached target
                self.position = list(self.target_position)
                self.target_position = None
                self.velocity = [0, 0]
    
    def set_state(self, new_state, force=False):
        """Changes the cat's behavioral state."""
        self.state = new_state
