"""
Web version of the game using Pygbag
This is the entry point for the web build
"""
import asyncio
import pygame
import sys
import random
import string
import json
from player import Player
from level import Level

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Secret Passage - Hollow Knight Style")
        self.clock = pygame.time.Clock()
        self.running = True

        # Game state
        self.current_room = "level1"
        self.show_victory = False
        self.database_opened = False
        self.secret_code = None
        self.show_code_screen = False
        self.code_display_time = 0

        # Create player
        self.player = Player(100, 500)

        # Create rooms
        self.level1 = Level(self.player)

    def generate_secret_code(self):
        """Generate a random 6-character code"""
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        # Save code to localStorage (web version)
        # For now, just store in memory
        return code

    async def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds

            self.handle_events()
            self.update(dt)
            self.draw()

            # Yield control to browser
            await asyncio.sleep(0)

        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE and self.show_code_screen:
                    # Close code screen and return to game
                    self.show_code_screen = False
                elif event.key == pygame.K_r and self.show_victory:
                    # Restart the game
                    self.show_victory = False
                    self.current_room = "level1"
                    self.player.x = 100
                    self.player.y = 500
                    self.player.vel_x = 0
                    self.player.vel_y = 0

    def update(self, dt):
        # Update code display timer
        if self.show_code_screen:
            self.code_display_time += dt
            # Auto-close after 3 seconds
            if self.code_display_time >= 3.0:
                self.show_code_screen = False

        if self.current_room == "level1" and not self.show_code_screen:
            self.level1.update(dt)

            # Check if player reached the flag
            if self.level1.player_reached_flag():
                self.show_victory = True

            # Check if player entered secret passage
            if self.level1.player_in_secret_passage() and not self.database_opened:
                self.database_opened = True
                # Generate secret code
                self.secret_code = self.generate_secret_code()
                self.show_code_screen = True
                self.code_display_time = 0
                # Store code and open website (web version only)
                try:
                    # Pygbag uses platform module for web APIs
                    import platform
                    # Store code in localStorage
                    platform.window.localStorage.setItem("access_code", self.secret_code)

                    # Get current origin (domain)
                    origin = platform.window.location.origin
                    url = f"{origin}/"

                    # Open login page in new tab
                    platform.window.open(url, "_blank")
                except:
                    # Desktop version - do nothing
                    pass

    def draw(self):
        self.screen.fill((20, 20, 30))  # Dark background like Hollow Knight

        if self.current_room == "level1":
            self.level1.draw(self.screen)

        # Draw code screen if showing code
        if self.show_code_screen:
            self.draw_code_screen()
        # Draw victory screen if player reached flag
        elif self.show_victory:
            self.draw_victory_screen()

        pygame.display.flip()

    def draw_code_screen(self):
        """Draw secret code screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((1280, 720))
        overlay.set_alpha(240)
        overlay.fill((10, 10, 20))
        self.screen.blit(overlay, (0, 0))

        # Code box
        code_box = pygame.Rect(290, 180, 700, 360)
        pygame.draw.rect(self.screen, (30, 30, 50), code_box, border_radius=15)
        pygame.draw.rect(self.screen, (100, 255, 150), code_box, 4, border_radius=15)

        # Title
        font_title = pygame.font.Font(None, 64)
        title_text = font_title.render("BIENVENUE MAX", True, (100, 255, 150))
        title_rect = title_text.get_rect(center=(640, 240))
        self.screen.blit(title_text, title_rect)

        # Code label
        font_label = pygame.font.Font(None, 36)
        label_text = font_label.render("Your Access Code:", True, (180, 180, 200))
        label_rect = label_text.get_rect(center=(640, 310))
        self.screen.blit(label_text, label_rect)

        # The CODE (big and flashy)
        font_code = pygame.font.Font(None, 96)
        code_text = font_code.render(self.secret_code, True, (255, 255, 100))
        code_rect = code_text.get_rect(center=(640, 380))
        self.screen.blit(code_text, code_rect)

        # Instructions for web version
        font_small = pygame.font.Font(None, 24)
        inst1 = font_small.render("Opening secret page...", True, (150, 255, 150))
        inst1_rect = inst1.get_rect(center=(640, 460))
        self.screen.blit(inst1, inst1_rect)

        remaining = max(0, int(3.0 - self.code_display_time))
        hint_text = font_small.render(f"Returning to game in {remaining}... (or press SPACE)", True, (150, 150, 170))
        hint_rect = hint_text.get_rect(center=(640, 495))
        self.screen.blit(hint_text, hint_rect)

    def draw_victory_screen(self):
        """Draw victory screen overlay"""
        # Semi-transparent overlay
        overlay = pygame.Surface((1280, 720))
        overlay.set_alpha(230)
        overlay.fill((20, 20, 30))
        self.screen.blit(overlay, (0, 0))

        # Victory box
        victory_box = pygame.Rect(340, 200, 600, 320)
        pygame.draw.rect(self.screen, (40, 40, 60), victory_box, border_radius=15)
        pygame.draw.rect(self.screen, (220, 50, 50), victory_box, 3, border_radius=15)

        # Title
        font_title = pygame.font.Font(None, 72)
        title_text = font_title.render("LEVEL COMPLETE!", True, (220, 220, 255))
        title_rect = title_text.get_rect(center=(640, 270))
        self.screen.blit(title_text, title_rect)

        # Message
        font_msg = pygame.font.Font(None, 32)
        msg_text = font_msg.render("You reached the flag!", True, (180, 180, 200))
        msg_rect = msg_text.get_rect(center=(640, 340))
        self.screen.blit(msg_text, msg_rect)

        # Next level hint
        font_hint = pygame.font.Font(None, 28)
        hint_text = font_hint.render("Level 2 is coming soon...", True, (150, 150, 170))
        hint_rect = hint_text.get_rect(center=(640, 390))
        self.screen.blit(hint_text, hint_rect)

        # Instructions
        font_small = pygame.font.Font(None, 22)
        restart_text = font_small.render("Press R to restart  |  Press ESC to quit", True, (150, 150, 150))
        restart_rect = restart_text.get_rect(center=(640, 460))
        self.screen.blit(restart_text, restart_rect)

# Async main entry point for Pygbag
async def main():
    game = Game()
    await game.run()

# Run the game
asyncio.run(main())
