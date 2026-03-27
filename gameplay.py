"""
Main game logic module - contains all game classes and functions.
"""

import pygame
import random
import json
import os
import math
from constants import *


# ---- GAME OBJECT CLASSES ----

class GameObject(pygame.sprite.Sprite):
    """Base class for all game objects."""
    
    def __init__(self, x, y, width, height, color, speed=0):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.color = color
        self.speed = speed
    
    def draw(self, surface):
        """Draw the object to the given surface."""
        surface.blit(self.image, self.rect)


class Player(GameObject):
    """Player character that can move left and right."""
    
    def __init__(self, x=None, y=None, lives=PLAYER_LIVES):
        if x is None:
            x = (WIDTH - PLAYER_WIDTH) // 2
        if y is None:
            y = HEIGHT - PLAYER_HEIGHT - 50
        
        super().__init__(x, y, PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_COLOR)
        self.lives = lives
    
    def move_left(self):
        """Move player left by PLAYER_SPEED pixels."""
        self.rect.x = max(0, self.rect.x - PLAYER_SPEED)
    
    def move_right(self):
        """Move player right by PLAYER_SPEED pixels."""
        self.rect.x = min(WIDTH - self.rect.width, self.rect.x + PLAYER_SPEED)
    
    def take_damage(self):
        """Reduce lives by 1. Returns True if player still has lives."""
        self.lives -= 1
        return self.lives > 0
    
    def reset(self):
        """Reset player to starting position and lives."""
        self.rect.topleft = ((WIDTH - PLAYER_WIDTH) // 2, HEIGHT - PLAYER_HEIGHT - 50)
        self.lives = PLAYER_LIVES


class Enemy(GameObject):
    """Falling enemy that can be normal or missile type."""
    
    def __init__(self, x, y, enemy_type='normal'):
        self.enemy_type = enemy_type
        
        if enemy_type == 'missile':
            width = MISSILE_WIDTH
            height = MISSILE_HEIGHT
            color = MISSILE_COLOR
            speed = MISSILE_SPEED
        else:  # 'normal'
            width = NORMAL_ENEMY_WIDTH
            height = NORMAL_ENEMY_HEIGHT
            color = ENEMY_COLOR
            speed = NORMAL_ENEMY_SPEED
        
        super().__init__(x, y, width, height, color, speed)
    
    def update(self):
        """Move enemy down by its speed."""
        self.rect.y += self.speed
    
    def is_off_screen(self):
        """Check if enemy has fallen off the bottom of the screen."""
        return self.rect.y > HEIGHT


class ZigZagTriangle(GameObject):
    """Purple triangle that moves down and zig-zags."""
    def __init__(self, x, y):
        super().__init__(x, y, TRIANGLE_WIDTH, TRIANGLE_HEIGHT, PURPLE, TRIANGLE_SPEED)
        self.initial_x = x
        self.color = PURPLE

    def update(self):
        """Move triangle down and zig-zag."""
        self.rect.y += self.speed
        # Zig-zag movement
        self.rect.x = self.initial_x + math.sin(self.rect.y / 20) * 20

    def is_off_screen(self):
        """Check if triangle has fallen off the bottom of the screen."""
        return self.rect.y > HEIGHT

    def draw(self, surface):
        """Draw the triangle."""
        # Calculate points for a triangle: top-middle, bottom-left, bottom-right
        points = [
            (self.rect.centerx, self.rect.top),
            (self.rect.left, self.rect.bottom),
            (self.rect.right, self.rect.bottom)
        ]
        pygame.draw.polygon(surface, self.color, points)


# ---- GAME STATE CLASS ----

class GameState:
    """Centralized game state management."""
    
    def __init__(self, player):
        self.player = player
        self.falling_objects = pygame.sprite.Group()
        self.paused = False
        
        # Timing variables
        self.start_ticks = pygame.time.get_ticks()
        self.pause_start_ticks = 0
        self.spawn_timer = pygame.time.get_ticks()
        self.triangle_spawn_timer = pygame.time.get_ticks() # Added
        
        # Calculate zones for spawning
        self.zone_width = WIDTH // ZONE_DIVISIONS
        self.zones = [
            (0, self.zone_width),
            (self.zone_width, self.zone_width * 2),
            (self.zone_width * 2, WIDTH)
        ]
    
    def reset(self):
        """Reset all game state for a new game."""
        self.falling_objects = pygame.sprite.Group()
        self.paused = False
        self.start_ticks = pygame.time.get_ticks()
        self.pause_start_ticks = 0
        self.spawn_timer = pygame.time.get_ticks()
        self.triangle_spawn_timer = pygame.time.get_ticks() # Added
        self.player.reset()
    
    def pause(self):
        """Pause the game."""
        self.paused = True
        self.pause_start_ticks = pygame.time.get_ticks()
    
    def resume(self):
        """Resume the game and adjust timers."""
        if self.paused:
            pause_duration = pygame.time.get_ticks() - self.pause_start_ticks
            self.start_ticks += pause_duration
            self.paused = False
    
    def toggle_pause(self):
        """Toggle pause state."""
        if self.paused:
            self.resume()
        else:
            self.pause()
    
    def spawn_enemy(self, enemy_type='normal'):
        """Spawn an enemy of the given type in a random zone."""
        zone = random.choice(self.zones)
        x = random.randint(zone[0], zone[1] - (MISSILE_WIDTH if enemy_type == 'missile' else NORMAL_ENEMY_WIDTH))
        enemy = Enemy(x, -45 if enemy_type == 'missile' else -15, enemy_type)
        self.falling_objects.add(enemy)
        
    def spawn_triangle(self):
        """Spawn a triangle."""
        x = random.randint(0, WIDTH - TRIANGLE_WIDTH)
        triangle = ZigZagTriangle(x, -TRIANGLE_HEIGHT)
        self.falling_objects.add(triangle)
    
    def spawn_random_enemy(self):
        """Spawn a random enemy based on spawn chances."""
        if random.random() < MISSILE_SPAWN_CHANCE:
            self.spawn_enemy('missile')
        else:
            self.spawn_enemy('normal')
    
    def update_enemies(self):
        """Update all falling enemies and remove off-screen ones."""
        self.falling_objects.update()
        for enemy in self.falling_objects:
            if enemy.is_off_screen():
                enemy.kill()
    
    def get_elapsed_seconds(self):
        """Get elapsed game time in seconds (excluding paused time)."""
        current_ticks = pygame.time.get_ticks()
        return (current_ticks - self.start_ticks) // 1000
    
    def should_spawn(self):
        """Check if it's time to spawn a new enemy."""
        current_ticks = pygame.time.get_ticks()
        return (current_ticks - self.spawn_timer) > SPAWN_INTERVAL

    def should_spawn_triangle(self):
        """Check if it's time to spawn a new triangle."""
        current_ticks = pygame.time.get_ticks()
        return (current_ticks - self.triangle_spawn_timer) > 8000 # 8 seconds

    def update_spawn_timer(self):
        """Reset the spawn timer."""
        self.spawn_timer = pygame.time.get_ticks()
        
    def update_triangle_spawn_timer(self):
        """Reset the triangle spawn timer."""
        self.triangle_spawn_timer = pygame.time.get_ticks()


# ---- HIGH SCORE MANAGEMENT ----

class HighScoreManager:
    """Manages game high scores - loading, saving, and tracking."""
    
    def __init__(self, filename='high_scores.json'):
        self.filename = filename
        self.scores = []
        self.load_scores()
    
    def load_scores(self):
        """Load high scores from file. If file doesn't exist, create empty list."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    self.scores = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.scores = []
        else:
            self.scores = []
    
    def save_scores(self):
        """Save high scores to file."""
        with open(self.filename, 'w') as f:
            json.dump(self.scores, f, indent=2)
    
    def add_score(self, score):
        """
        Add a new score. Returns True if score is in top 10, False otherwise.
        """
        self.scores.append(score)
        self.scores.sort(reverse=True)
        # Keep only top 10 scores
        self.scores = self.scores[:10]
        self.save_scores()
        return True
    
    def get_top_scores(self, count=3):
        """Get top N scores. Default is top 3."""
        return self.scores[:count]
    
    def is_high_score(self, score):
        """Check if a score would be in the high score list."""
        if len(self.scores) < 10:
            return True
        return score > self.scores[-1]


# ---- UI/RENDERING ----

class GameUI:
    """Handles all UI rendering including fonts, text, and screens."""
    
    def __init__(self, window):
        self.window = window
        self.text_cache = {}
        self._init_fonts()
    
    def _init_fonts(self):
        """Initialize all fonts."""
        self.title_font = pygame.font.Font(None, 48)
        self.game_option_font = pygame.font.Font(None, 36)
        self.game_over_font = pygame.font.Font(None, 72)
        self.button_font = pygame.font.Font(None, 48)
        self.stats_font = pygame.font.Font(None, 36)
        self.timer_font = pygame.font.Font(None, 24)
        self.pause_font = pygame.font.Font(None, 72)
        self.score_font = pygame.font.Font(None, 32)

    def draw_button(self, text, center_pos):
        """Helper to draw a standardized button."""
        # Use cache for buttons if needed, but text is dynamic, so maybe not worth it
        button_text = self.button_font.render(text, True, TEXT_COLOR)
        button_rect_text = button_text.get_rect(center=center_pos)
        button_padding = 10
        button_rect = pygame.Rect(
            button_rect_text.left - button_padding,
            button_rect_text.top - button_padding,
            button_rect_text.width + 2 * button_padding,
            button_rect_text.height + 2 * button_padding
        )
        pygame.draw.rect(self.window, BUTTON_COLOR, button_rect)
        self.window.blit(button_text, button_rect_text.topleft)
        return button_rect
    
    def draw_game_selection_screen(self):
        """Draw the game selection menu with game and high scores buttons."""
        self.window.fill(BG_COLOR)
        
        # Draw title
        title_text = self.title_font.render("What game do you want to play?", True, TEXT_COLOR)
        title_x = WIDTH // 2 - title_text.get_width() // 2
        self.window.blit(title_text, (title_x, 30))
        
        # Draw buttons
        play_button_rect = self.draw_button("Evan's Falling Game", (WIDTH // 2, 140))
        high_scores_button_rect = self.draw_button("High Scores", (WIDTH // 2, 250))
        
        pygame.display.flip()
        
        return play_button_rect, high_scores_button_rect
    
    def draw_game_screen(self, game_state):
        """Draw the main game screen."""
        self.window.fill(BG_COLOR)
        
        # Draw player
        game_state.player.draw(self.window)
        
        # Draw falling objects
        for enemy in game_state.falling_objects:
            enemy.draw(self.window)
        
        # Draw title
        game_title = self.stats_font.render("Evan's Falling Object Game", True, TEXT_COLOR)
        title_x = WIDTH // 2 - game_title.get_width() // 2
        title_y = HEIGHT - game_title.get_height() - 10
        self.window.blit(game_title, (title_x, title_y))
        
        # Draw lives
        lives_key = f"lives_{game_state.player.lives}"
        if lives_key not in self.text_cache:
            self.text_cache[lives_key] = self.stats_font.render(f"Lives: {game_state.player.lives}", True, TEXT_COLOR)
        self.window.blit(self.text_cache[lives_key], (10, 10))
        
        # Draw timer
        elapsed_seconds = game_state.get_elapsed_seconds()
        timer_key = f"timer_{elapsed_seconds}"
        if timer_key not in self.text_cache:
            self.text_cache[timer_key] = self.timer_font.render(f"Sec: {elapsed_seconds:05}", True, TEXT_COLOR)
        timer_surface = self.text_cache[timer_key]
        timer_x = WIDTH - timer_surface.get_width() - 10
        timer_y = HEIGHT - timer_surface.get_height() - 10
        self.window.blit(timer_surface, (timer_x, timer_y))
        
        pygame.display.flip()
    
    def draw_pause_screen(self):
        """Draw the pause screen overlay."""
        paused_text = self.pause_font.render("Paused", True, PAUSED_TEXT_COLOR)
        paused_rect = paused_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.window.blit(paused_text, paused_rect.topleft)
        pygame.display.flip()
    
    def draw_game_over_screen(self):
        """Draw the game over screen and return play again and main menu button rects."""
        self.window.fill(BG_COLOR)
        
        game_over_text = self.game_over_font.render("Game Over", True, ENEMY_COLOR)
        game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
        self.window.blit(game_over_text, game_over_rect.topleft)
        
        # Buttons
        play_again_button = self.draw_button("Play Again", (WIDTH // 2, HEIGHT // 2 + 20))
        menu_button = self.draw_button("Main Menu", (WIDTH // 2, HEIGHT // 2 + 80))
        
        pygame.display.flip()
        
        return play_again_button, menu_button
    
    def draw_high_scores_screen(self, top_scores):
        """Draw the high scores screen and return the back button rect."""
        self.window.fill(BG_COLOR)
        
        # Draw title
        title_text = self.title_font.render("High Scores", True, TEXT_COLOR)
        title_rect = title_text.get_rect(center=(WIDTH // 2, 30))
        self.window.blit(title_text, title_rect.topleft)
        
        # Draw top 3 scores
        if top_scores:
            y_offset = 100
            for i, score in enumerate(top_scores, 1):
                rank_text = self.score_font.render(f"{i}. {score} seconds", True, TEXT_COLOR)
                rank_rect = rank_text.get_rect(center=(WIDTH // 2, y_offset))
                self.window.blit(rank_text, rank_rect.topleft)
                y_offset += 60
        else:
            no_scores_text = self.score_font.render("No scores yet!", True, TEXT_COLOR)
            no_scores_rect = no_scores_text.get_rect(center=(WIDTH // 2, 150))
            self.window.blit(no_scores_text, no_scores_rect.topleft)
        
        # Draw back button
        back_button = self.draw_button("Back", (WIDTH // 2, HEIGHT - 50))
        
        pygame.display.flip()
        
        return back_button


# ---- GAME LOOP ----

class GameLoop:
    """Main game loop orchestration."""
    
    def __init__(self, window):
        self.window = window
        self.ui = GameUI(window)
        self.clock = pygame.time.Clock()
        self.high_score_manager = HighScoreManager()
    
    def game_selection_screen(self):
        """
        Display game selection menu.
        Returns 'falling_game' if user clicks play, None if user quits.
        """
        selection = None
        running = True
        
        while running:
            # Draw screen and get button rects
            play_button_rect, high_scores_button_rect = self.ui.draw_game_selection_screen()
            
            # Handle input (fixed - get events here, not in separate handler)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_button_rect.collidepoint(event.pos):
                        selection = 'falling_game'
                        running = False
                    elif high_scores_button_rect.collidepoint(event.pos):
                        self.high_scores_screen()
            
            self.clock.tick(FPS)
        
        return selection
    
    def high_scores_screen(self):
        """Display the high scores screen."""
        viewing_scores = True
        
        while viewing_scores:
            # Get top 3 scores
            top_scores = self.high_score_manager.get_top_scores(3)
            
            # Draw high scores screen
            back_button = self.ui.draw_high_scores_screen(top_scores)
            
            # Handle input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if back_button.collidepoint(event.pos):
                        viewing_scores = False
            
            self.clock.tick(FPS)
        
        return True
    
    def game_over_screen(self):
        """
        Display game over screen.
        Returns 'play_again' if user wants to play again, 'main_menu' if user wants to go back to menu, False if quit.
        """
        game_over = True
        
        while game_over:
            play_again_button, menu_button = self.ui.draw_game_over_screen()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_again_button.collidepoint(event.pos):
                        return 'play_again'
                    elif menu_button.collidepoint(event.pos):
                        return 'main_menu'
            
            self.clock.tick(FPS)
    
    def evans_falling_game(self):
        """
        Main game loop.
        Returns True if user wants to play again, False if quit.
        """
        # Initialize game state
        player = Player()
        game_state = GameState(player)
        
        running = True
        
        while running:
            # Handle input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        game_state.toggle_pause()
            
            # Update game only if not paused
            if not game_state.paused:
                # Continuous movement
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    player.move_left()
                if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    player.move_right()
                
                # Spawn new enemies
                if game_state.should_spawn():
                    game_state.spawn_random_enemy()
                    game_state.update_spawn_timer()
                
                if game_state.should_spawn_triangle():
                    game_state.spawn_triangle()
                    game_state.update_triangle_spawn_timer()
                
                # Update all enemies
                game_state.update_enemies()
                
                # Check collisions
                hits = pygame.sprite.spritecollide(player, game_state.falling_objects, True)
                for enemy in hits:
                    # Handle collision
                    if not player.take_damage():
                        # Player is out of lives
                        running = False
                    
                    # Spawn replacement
                    if running:  # Only spawn if game continues
                        game_state.spawn_random_enemy()
            
            # Draw game
            if game_state.paused:
                self.ui.draw_game_screen(game_state)
                self.ui.draw_pause_screen()
            else:
                self.ui.draw_game_screen(game_state)
            
            self.clock.tick(FPS)
        
        # Game over - save score and show game over screen
        score = game_state.get_elapsed_seconds()
        self.high_score_manager.add_score(score)
        result = self.game_over_screen()
        return result
    
    def run(self):
        """Main entry point - runs the game loop."""
        running = True
        
        while running:
            # Show game selection
            game_choice = self.game_selection_screen()
            
            if game_choice is None:  # User quit from menu
                running = False
            elif game_choice == 'falling_game':
                # Play the game - loop until user quits or goes to main menu
                while True:
                    result = self.evans_falling_game()
                    if result == 'play_again':
                        # Play another game
                        continue
                    elif result == 'main_menu':
                        # Go back to main menu
                        break
                    else:
                        # User quit (False returned)
                        running = False
                        break
