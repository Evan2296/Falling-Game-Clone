# ---- CONSTANTS AND GLOBAL SETTINGS ----

# Display settings
WIDTH = 600
HEIGHT = 400

# Colors (RGB tuples)
LIGHT_BLUE = (173, 216, 230)
GREEN = (0, 128, 0)
RED = (255, 0, 0)
TEXT_COLOR = (128, 0, 128)  # Purple
ORANGE = (255, 165, 0)
PAUSED_TEXT_COLOR = (0, 0, 139)  # Dark Blue
DARK_GREEN = (0, 100, 0)
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
NORMAL_ENEMY_COLOR = RED

MISSILE_WIDTH = 10
MISSILE_HEIGHT = 45
MISSILE_SPEED = 8
MISSILE_COLOR = ORANGE

# Spawning settings
SPAWN_INTERVAL = 500  # Milliseconds between spawns
NORMAL_SPAWN_CHANCE = 0.75  # 75% chance to spawn normal enemy
MISSILE_SPAWN_CHANCE = 0.25  # 25% chance to spawn missile

# Zone settings
ZONE_DIVISIONS = 3  # Divide screen into 3 vertical zones

# Frame rate
FPS = 60
