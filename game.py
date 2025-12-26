import pygame
import sys
import webbrowser
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

        # Create player
        self.player = Player(100, 500)

        # Create rooms
        self.level1 = Level(self.player)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds

            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r and self.show_victory:
                    # Restart the game
                    self.show_victory = False
                    self.current_room = "level1"
                    self.player.x = 100
                    self.player.y = 500
                    self.player.vel_x = 0
                    self.player.vel_y = 0

    def update(self, dt):
        if self.current_room == "level1":
            self.level1.update(dt)

            # Check if player reached the flag
            if self.level1.player_reached_flag():
                self.show_victory = True

            # Check if player entered secret passage
            if self.level1.player_in_secret_passage() and not self.database_opened:
                self.database_opened = True
                # Open React app in browser
                webbrowser.open('http://localhost:3000')
                print("Secret database opened in browser!")
                print("Make sure the React app and API are running:")
                print("  1. cd database-ui && npm start")
                print("  2. python api.py")

    def draw(self):
        self.screen.fill((20, 20, 30))  # Dark background like Hollow Knight

        if self.current_room == "level1":
            self.level1.draw(self.screen)

        # Draw victory screen if player reached flag
        if self.show_victory:
            self.draw_victory_screen()

        pygame.display.flip()

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

        # Secret message
        font_secret = pygame.font.Font(None, 24)
        secret_text = font_secret.render("But did you find the secret database?", True, (150, 255, 150))
        secret_rect = secret_text.get_rect(center=(640, 390))
        self.screen.blit(secret_text, secret_rect)

        # Instructions
        font_small = pygame.font.Font(None, 22)
        restart_text = font_small.render("Press R to restart  |  Press ESC to quit", True, (150, 150, 150))
        restart_rect = restart_text.get_rect(center=(640, 460))
        self.screen.blit(restart_text, restart_rect)

if __name__ == "__main__":
    game = Game()
    game.run()
