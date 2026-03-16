# ---- CONSTANTS AND GLOBAL SETTINGS ----

# Display settings
WIDTH = 600
HEIGHT = 400

# Colors (RGB tuples)
# Dark Evergreen/Black Theme
BG_COLOR = (0, 0, 0)
EVERGREEN = (0, 80, 50)
TEXT_COLOR = (220, 220, 200)  # Off-white
PLAYER_COLOR = (50, 200, 100) # Bright green for contrast
ENEMY_COLOR = (200, 50, 50)   # Red for alerts
MISSILE_COLOR = (200, 150, 50) # Orange
PAUSED_TEXT_COLOR = (100, 150, 100) # Lighter green
BUTTON_COLOR = (0, 100, 60)
BLACK = (0, 0, 0)

# Game settings
PLAYER_LIVES = 3
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 30
PLAYER_SPEED = 30  # Pixels per movement

# Enemy settings
NORMAL_ENEMY_WIDTH = 30
NORMAL_ENEMY_HEIGHT = 15
NORMAL_ENEMY_SPEED = 5

MISSILE_WIDTH = 10
MISSILE_HEIGHT = 45
MISSILE_SPEED = 8

# Spawning settings
SPAWN_INTERVAL = 500  # Milliseconds between spawns
NORMAL_SPAWN_CHANCE = 0.75  # 75% chance to spawn normal enemy
MISSILE_SPAWN_CHANCE = 0.25  # 25% chance to spawn missile

# Zone settings
ZONE_DIVISIONS = 3  # Divide screen into 3 vertical zones

# Frame rate
FPS = 60
