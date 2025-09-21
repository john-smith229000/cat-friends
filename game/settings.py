import pygame

# Screen and Display Settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
WINDOW_TITLE = "Cat Friends"

# Color Palette (can be expanded later)
BLACK = pygame.Color(0, 0, 0)
WHITE = pygame.Color(255, 255, 255)
BACKGROUND_COLOR = pygame.Color(230, 240, 255) # A light pastel blue

# Font Settings (placeholders)
DEFAULT_FONT_NAME = "Arial"
DEFAULT_FONT_SIZE = 32

MAX_STAT_VALUE = 100.0

# Values are in points-per-second
HUNGER_DECAY_RATE = 0.2
HAPPINESS_DECAY_RATE = 0.2
HAPPINESS_INCREASE_RATE = 15.0 # While being petted

# Values are in points-per-action
FOOD_HUNGER_REPLENISH = 25.0