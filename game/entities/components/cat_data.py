# game/entities/components/cat_data.py

class CatData:
    """Handles data serialization and persistence for cats."""
    
    def __init__(self, initial_stats=None):
        self.unique_id = initial_stats.get("cat_id", "custom_cat") if initial_stats else "custom_cat"
        self.customization_data = initial_stats.get("customization", {}) if initial_stats else {}
        self.body_type = self.customization_data.get("body_type", "shorthair")
        self.accessories = initial_stats.get("accessories", {}) if initial_stats else {}
    
    def update_customization(self, new_data):
        """Updates customization data."""
        self.customization_data = new_data
    
    def to_dict(self, stats, accessories=None, is_sleeping=False):
        """Exports all cat data to a savable dictionary."""
        return {
            "cat_id": self.unique_id,
            "hunger": stats.hunger,
            "happiness": stats.happiness,
            "energy": stats.energy,
            "accessories": accessories or self.accessories,
            "customization": self.customization_data,
            "is_sleeping": is_sleeping
        }