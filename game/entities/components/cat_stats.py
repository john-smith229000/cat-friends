# entities/components/cat_stats.py
# ====================================

from settings import MAX_STAT_VALUE, HUNGER_DECAY_RATE, HAPPINESS_DECAY_RATE, HAPPINESS_INCREASE_RATE, FOOD_HUNGER_REPLENISH

class CatStats:
    """Manages all stat-related logic for a cat."""
    
    def __init__(self, initial_stats=None):
        self.hunger = initial_stats.get("hunger", 80.0) if initial_stats else 80.0
        self.happiness = initial_stats.get("happiness", 60.0) if initial_stats else 60.0
        self.energy = initial_stats.get("energy", 100.0) if initial_stats else 100.0
        self.max_stat = MAX_STAT_VALUE
    
    def update(self, dt, is_being_petted=False):
        """Updates all stats based on time and conditions."""
        # Natural decay
        self.hunger -= HUNGER_DECAY_RATE * dt
        self.happiness -= HAPPINESS_DECAY_RATE * dt

        # Happiness increase when being petted
        if is_being_petted:
            self.happiness += HAPPINESS_INCREASE_RATE * dt

        # Clamp values
        self.hunger = max(0, min(self.hunger, self.max_stat))
        self.happiness = max(0, min(self.happiness, self.max_stat))
        self.energy = max(0, min(self.energy, self.max_stat))
    
    def feed(self):
        """Increases hunger when fed."""
        self.hunger += FOOD_HUNGER_REPLENISH
        self.hunger = min(self.hunger, self.max_stat)
        print(f"Cat fed! Hunger is now {self.hunger:.1f}")
    
    def to_dict(self):
        """Returns stats as a dictionary for saving."""
        return {
            "hunger": self.hunger,
            "happiness": self.happiness,
            "energy": self.energy
        }