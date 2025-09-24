# game/scenes/wardrobe.py

import pygame
import copy
from settings import *
from core.scene_manager import BaseScene
from core.ui import Button
from core.resource_manager import resources
from entities.cat import Cat

class WardrobeScene(BaseScene):
    """
    Scene for trying on and managing cat accessories.
    Accessed by clicking the mirror in cat_home.
    """
    def __init__(self, scene_manager, game):
        super().__init__(scene_manager, game)
        
        # Wardrobe categories and items
        self.wardrobe_items = {
            "head": ["hat1", "hat2"],  # Can be expanded
            "body": [],  # Future: shirts, collars, etc.
            "accessories": []  # Future: bows, jewelry, etc.
        }
        
        # Current selection states
        self.current_category = "head"
        self.current_indices = {"head": 0, "body": 0, "accessories": 0}
        
        # Get available options for each category (including "None")
        self.category_options = {}
        for category, items in self.wardrobe_items.items():
            self.category_options[category] = ["None"] + items
        
        # UI state
        self.cat_preview = None
        self.original_cat_data = None
        
        self._setup_ui()

    def _setup_ui(self):
        """Initialize UI elements that don't depend on screen size."""
        self.title_font = pygame.font.SysFont(DEFAULT_FONT_NAME, 52)
        self.category_font = pygame.font.SysFont(DEFAULT_FONT_NAME, 36)
        self.item_font = pygame.font.SysFont(DEFAULT_FONT_NAME, 28)
        self._recalculate_layout()

    def _recalculate_layout(self):
        """Recalculates UI layout based on current screen size."""
        current_width, current_height = self.game.screen.get_size()
        
        # Title
        self.title_surf = self.title_font.render("Wardrobe", True, WHITE)
        self.title_rect = self.title_surf.get_rect(center=(current_width / 2, 60))
        
        # Category selection buttons
        self.category_buttons = []
        category_y = 120
        category_spacing = 80
        category_names = list(self.wardrobe_items.keys())
        
        for i, category in enumerate(category_names):
            button_rect = (50, category_y + i * category_spacing, 150, 60)
            btn = Button(
                rect=button_rect, 
                text=category.title(), 
                callback=lambda cat=category: self._select_category(cat)
            )
            # Highlight current category
            if category == self.current_category:
                btn.color_normal = (80, 120, 160)
                btn.color_hover = (100, 140, 180)
            self.category_buttons.append(btn)
        
        # Item navigation buttons
        nav_y = current_height - 150
        self.prev_button = Button(
            rect=(current_width // 2 - 200, nav_y, 80, 50), 
            text="< Prev", 
            callback=self._previous_item
        )
        self.next_button = Button(
            rect=(current_width // 2 + 120, nav_y, 80, 50), 
            text="Next >", 
            callback=self._next_item
        )
        
        # Action buttons
        self.remove_button = Button(
            rect=(current_width // 2 - 45, nav_y + 60, 90, 40), 
            text="Remove", 
            callback=self._remove_current_item
        )
        
        # Exit buttons
        self.save_exit_button = Button(
            rect=(current_width - 180, current_height - 100, 160, 50), 
            text="Save & Exit", 
            callback=self._save_and_exit
        )
        self.cancel_button = Button(
            rect=(current_width - 180, current_height - 160, 160, 50), 
            text="Cancel", 
            callback=self._cancel_changes
        )

    def on_enter(self, data=None):
        """Called when entering the wardrobe scene."""
        if not data:
            return
        
        # Store original data for cancel functionality
        self.original_cat_data = copy.deepcopy(data)
        
        # Create cat preview with better positioning and scale
        current_width, current_height = self.game.screen.get_size()
        cat_pos = (current_width / 2 + 50, current_height * 0.65)  # More centered positioning
        
        self.cat_preview = Cat(
            position=cat_pos,
            initial_stats=data,
            scale=0.7  # Larger scale for better visibility when trying on clothes
        )
        
        # Set current indices based on cat's current accessories
        current_accessories = data.get("accessories", {})
        for category in self.wardrobe_items.keys():
            current_item = current_accessories.get(category)
            if current_item and current_item in self.category_options[category]:
                self.current_indices[category] = self.category_options[category].index(current_item)
            else:
                self.current_indices[category] = 0  # "None"
        
        # Apply current accessories to preview immediately
        self._apply_current_accessories()

    def handle_event(self, event):
        """Handle user input events."""
        if event.type == pygame.VIDEORESIZE:
            self._recalculate_layout()
            if self.cat_preview:
                current_width, current_height = self.game.screen.get_size()
                self.cat_preview.set_position(current_width * 0.7, current_height * 0.65)
        
        # Handle all button events
        for btn in self.category_buttons:
            btn.handle_event(event)
        
        self.prev_button.handle_event(event)
        self.next_button.handle_event(event)
        self.remove_button.handle_event(event)
        self.save_exit_button.handle_event(event)
        self.cancel_button.handle_event(event)
        
        # Keyboard shortcuts
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._cancel_changes()
            elif event.key == pygame.K_RETURN:
                self._save_and_exit()
            elif event.key == pygame.K_LEFT:
                self._previous_item()
            elif event.key == pygame.K_RIGHT:
                self._next_item()

    def update(self, dt):
        """Update the cat preview."""
        if self.cat_preview:
            self.cat_preview.update(dt)

    def draw(self, screen):
        """Render the wardrobe scene."""
        # Semi-transparent background overlay
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((20, 30, 50, 200))  # Dark blue overlay
        screen.blit(overlay, (0, 0))
        
        # Title
        screen.blit(self.title_surf, self.title_rect)
        
        # Category buttons
        for btn in self.category_buttons:
            btn.draw(screen)
        
        # Current category label
        category_label = self.category_font.render(f"Category: {self.current_category.title()}", True, WHITE)
        screen.blit(category_label, (250, 130))
        
        # Current item display
        current_items = self.category_options[self.current_category]
        if current_items:
            current_index = self.current_indices[self.current_category]
            current_item = current_items[current_index]
            
            item_text = f"Item: {current_item}" if current_item != "None" else "Item: None"
            item_label = self.item_font.render(item_text, True, WHITE)
            screen.blit(item_label, (250, 180))
            
            # Item counter
            counter_text = f"{current_index + 1} / {len(current_items)}"
            counter_label = self.item_font.render(counter_text, True, (200, 200, 200))
            screen.blit(counter_label, (250, 210))
        
        # Navigation buttons
        self.prev_button.draw(screen)
        self.next_button.draw(screen)
        
        # Action button
        self.remove_button.draw(screen)
        
        # Exit buttons
        self.save_exit_button.draw(screen)
        self.cancel_button.draw(screen)
        
        # Cat preview
        if self.cat_preview:
            self.cat_preview.draw(screen)
        
        # Instructions
        instructions = [
            "Arrow Keys: Navigate items",
            "Enter: Save & Exit", 
            "ESC: Cancel"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_surf = pygame.font.SysFont(DEFAULT_FONT_NAME, 18).render(instruction, True, (180, 180, 180))
            screen.blit(inst_surf, (50, screen.get_height() - 120 + i * 20))

        return [screen.get_rect()]

    def _select_category(self, category):
        """Switch to a different accessory category."""
        self.current_category = category
        self._recalculate_layout()  # Refresh button highlighting

    def _previous_item(self):
        """Navigate to the previous item in current category."""
        current_items = self.category_options[self.current_category]
        if current_items:
            self.current_indices[self.current_category] = (
                self.current_indices[self.current_category] - 1
            ) % len(current_items)
            self._apply_current_item()  # Auto-apply when navigating

    def _next_item(self):
        """Navigate to the next item in current category."""
        current_items = self.category_options[self.current_category]
        if current_items:
            self.current_indices[self.current_category] = (
                self.current_indices[self.current_category] + 1
            ) % len(current_items)
            self._apply_current_item()  # Auto-apply when navigating

    def _apply_current_item(self):
        """Apply the currently selected item to the cat preview."""
        if not self.cat_preview:
            return
        
        current_items = self.category_options[self.current_category]
        if current_items:
            current_index = self.current_indices[self.current_category]
            selected_item = current_items[current_index]
            
            # --- FIX: Access accessories through the 'data' component ---
            if selected_item == "None":
                if self.current_category in self.cat_preview.data.accessories:
                    del self.cat_preview.data.accessories[self.current_category]
            else:
                self.cat_preview.data.accessories[self.current_category] = selected_item

    def _apply_current_accessories(self):
        """Apply all current accessories to the cat preview based on current indices."""
        if not self.cat_preview:
            return
        
        # --- FIX: Access accessories through the 'data' component ---
        self.cat_preview.data.accessories.clear()
        
        for category in self.wardrobe_items.keys():
            current_items = self.category_options[category]
            if current_items:
                current_index = self.current_indices[category]
                selected_item = current_items[current_index]
                
                if selected_item != "None":
                    self.cat_preview.data.accessories[category] = selected_item

    def _try_on_current_item(self):
        """Apply the currently selected item to the cat preview."""
        if not self.cat_preview:
            return
        
        current_items = self.category_options[self.current_category]
        if current_items:
            current_index = self.current_indices[self.current_category]
            selected_item = current_items[current_index]
            
            if selected_item == "None":
                # Remove the accessory
                if self.current_category in self.cat_preview.accessories:
                    del self.cat_preview.accessories[self.current_category]
            else:
                # Equip the accessory
                self.cat_preview.accessories[self.current_category] = selected_item
            
            print(f"Trying on: {selected_item} in category {self.current_category}")

    def _remove_current_item(self):
        """Remove the current category's accessory."""
        if not self.cat_preview:
            return
        
        # --- FIX: Access accessories through the 'data' component ---
        if self.current_category in self.cat_preview.data.accessories:
            del self.cat_preview.data.accessories[self.current_category]
        
        self.current_indices[self.current_category] = 0
        print(f"Removed accessory from category: {self.current_category}")

    def _save_and_exit(self):
        """Save changes and return to cat home."""
        if self.cat_preview:
            # Update the game's cat data with new accessories
            self.game.cat_data = self.cat_preview.to_dict()
            print("Wardrobe changes saved!")
        
        self.scene_manager.pop()

    def _cancel_changes(self):
        """Cancel changes and return to cat home without saving."""
        if self.original_cat_data:
            self.game.cat_data = self.original_cat_data
            
            if self.cat_preview:
                # --- FIX: Access accessories through the 'data' component ---
                original_accessories = self.original_cat_data.get("accessories", {})
                self.cat_preview.data.accessories.clear()
                self.cat_preview.data.accessories.update(original_accessories)
                
                for category in self.wardrobe_items.keys():
                    current_item = original_accessories.get(category)
                    if current_item and current_item in self.category_options[category]:
                        self.current_indices[category] = self.category_options[category].index(current_item)
                    else:
                        self.current_indices[category] = 0
        
        print("Wardrobe changes cancelled.")
        self.scene_manager.pop()