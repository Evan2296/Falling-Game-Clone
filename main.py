"""
Evan's Falling Game - Main Entry Point

A simple pygame-based falling object dodging game.
The player controls a character at the bottom of the screen and must avoid falling objects.

Controls:
  - LEFT ARROW: Move player left
  - RIGHT ARROW: Move player right
  - P: Pause/Resume game
  - MOUSE CLICK: Select menu options
"""

import pygame
import sys
from constants import WIDTH, HEIGHT, FPS
from gameplay import GameLoop


def main():
    """Initialize pygame and run the game."""
    # Initialize Pygame
    pygame.init()
    pygame.font.init()
    
    # Create window
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Evan's Falling Object Pygame")
    
    # Create and run game loop
    game_loop = GameLoop(window)
    game_loop.run()
    
    # Clean up
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
