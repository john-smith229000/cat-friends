# game/entities/components/cat_stats.py

from settings import (
    MAX_STAT_VALUE,
    HUNGER_DECAY_RATE,
    HAPPINESS_DECAY_RATE,
    HAPPINESS_INCREASE_RATE,
    FOOD_HUNGER_REPLENISH,
    ENERGY_DECAY_RATE,
    ENERGY_REPLENISH_RATE,
    WAKE_UP_HAPPINESS_PENALTY,
)


class CatStats:
    """Manages all stat-related logic for a cat."""

    def __init__(self, initial_stats=None):
        self.hunger = initial_stats.get("hunger", 80.0) if initial_stats else 80.0
        self.happiness = (
            initial_stats.get("happiness", 60.0) if initial_stats else 60.0
        )
        self.energy = initial_stats.get("energy", 100.0) if initial_stats else 100.0
        self.max_stat = MAX_STAT_VALUE

    def update(self, dt, is_being_petted=False, is_sleeping=False):
        """Updates all stats based on time and conditions."""
        # Natural decay
        self.hunger -= HUNGER_DECAY_RATE * dt
        self.happiness -= HAPPINESS_DECAY_RATE * dt

        # Energy management
        if is_sleeping:
            # Restore energy while sleeping
            self.energy += ENERGY_REPLENISH_RATE * dt
        else:
            # Drain energy while awake
            self.energy -= ENERGY_DECAY_RATE * dt

        # Happiness increase when being petted (works while sleeping too)
        if is_being_petted:
            self.happiness += HAPPINESS_INCREASE_RATE * dt

        # Clamp values
        self.hunger = max(0, min(self.hunger, self.max_stat))
        self.happiness = max(0, min(self.happiness, self.max_stat))
        self.energy = max(0, min(self.energy, self.max_stat))

    def is_exhausted(self):
        """Returns True if cat must sleep (energy at 0)."""
        return self.energy <= 0

    def is_tired(self):
        """Returns True if cat can choose to sleep (energy below 50)."""
        return self.energy < 50

    def is_fully_rested(self):
        """Returns True if cat is fully rested (energy at max)."""
        return self.energy >= self.max_stat

    def apply_wake_up_penalty(self):
        """Applies a happiness penalty for being woken up."""
        self.happiness -= WAKE_UP_HAPPINESS_PENALTY
        self.happiness = max(0, self.happiness)
        print(f"Cat woken up early! Happiness is now {self.happiness:.1f}")

    def feed(self):
        """Increases hunger when fed."""
        self.hunger += FOOD_HUNGER_REPLENISH
        self.hunger = min(self.hunger, self.max_stat)
        print(f"Cat fed! Hunger is now {self.hunger:.1f}")

    def to_dict(self):
        """Returns stats as a dictionary for saving."""
        return {"hunger": self.hunger, "happiness": self.happiness, "energy": self.energy}