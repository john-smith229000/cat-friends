# game/entities/components/cat_behavior.py

class CatBehavior:
    """Manages movement, positioning, and basic AI behaviors."""
    
    def __init__(self, initial_position):
        self.position = list(initial_position)
        self.velocity = [0, 0]
        self.target_position = None
        self.movement_speed = 100  # pixels per second
        self.state = "idle"
        self.is_sleeping = False
    
    def set_position(self, x, y):
        """Sets the cat's position directly."""
        self.position = [x, y]
    
    def move_to(self, target_x, target_y):
        """Sets a target position for the cat to move towards."""
        self.target_position = [target_x, target_y]
    
    def start_sleeping(self, bed_x, bed_y):
        """Initiates sleep state and moves cat to bed."""
        if not self.is_sleeping:
            self.position = [bed_x, bed_y]  # Immediately move to bed
            self.is_sleeping = True
            self.state = "sleeping"
            self.target_position = None # Clear any movement target
    
    def wake_up(self):
        """Wakes the cat up by changing its state."""
        if self.is_sleeping:
            self.is_sleeping = False
            self.state = "idle"
    
    def update(self, dt):
        """Updates movement and position."""
        if self.is_sleeping:
            return
            
        if self.target_position:
            dx = self.target_position[0] - self.position[0]
            dy = self.target_position[1] - self.position[1]
            distance = (dx**2 + dy**2)**0.5
            
            if distance > 2:
                self.velocity[0] = (dx / distance) * self.movement_speed
                self.velocity[1] = (dy / distance) * self.movement_speed
                self.position[0] += self.velocity[0] * dt
                self.position[1] += self.velocity[1] * dt
            else:
                self.position = list(self.target_position)
                self.target_position = None
                self.velocity = [0, 0]