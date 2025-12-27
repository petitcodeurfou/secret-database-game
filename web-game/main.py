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
from level2 import Level2

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
        self.show_app_menu = False
        self.selected_app = None

        # Create player
        self.player = Player(100, 500)

        # Create rooms
        self.level1 = Level(self.player)
        self.level2 = Level2(self.player)

    def generate_secret_code(self):
        """Generate a random 6-character code"""
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        # Save code to localStorage (web version)
        # For now, just store in memory
        return code

    def open_cloud_app(self):
        """Open the Cloud app - generate code and open website"""
        # Close app menu
        self.show_app_menu = False

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
                    if self.show_app_menu:
                        # Close app menu and return to game
                        self.show_app_menu = False
                    else:
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
                elif event.key == pygame.K_1 and self.show_app_menu:
                    # Select Cloud app (number 1)
                    self.open_cloud_app()
            elif event.type == pygame.MOUSEBUTTONDOWN and self.show_app_menu:
                # Check if clicked on Cloud app
                mouse_x, mouse_y = pygame.mouse.get_pos()
                cloud_rect = pygame.Rect(440, 280, 400, 180)
                if cloud_rect.collidepoint(mouse_x, mouse_y):
                    self.open_cloud_app()

    def update(self, dt):
        # Update code display timer
        if self.show_code_screen:
            self.code_display_time += dt
            # Auto-close after 3 seconds
            if self.code_display_time >= 3.0:
                self.show_code_screen = False

        if self.show_victory:
            # Don't update game when victory screen is showing
            return

        if self.current_room == "level1" and not self.show_code_screen and not self.show_app_menu:
            self.level1.update(dt)

            # Check if player reached the flag - Go to level 2
            if self.level1.player_reached_flag():
                self.current_room = "level2"
                # Reset player position for level 2
                self.player.x = 100
                self.player.y = 500
                self.player.vel_x = 0
                self.player.vel_y = 0

            # Check if player entered secret passage
            if self.level1.player_in_secret_passage() and not self.database_opened:
                self.database_opened = True
                # Show app selection menu
                self.show_app_menu = True

        elif self.current_room == "level2" and not self.show_code_screen and not self.show_app_menu:
            self.level2.update(dt)

            # Check if player reached the flag - Victory!
            if self.level2.player_reached_flag():
                self.show_victory = True
                print("[DEBUG] Victory triggered!")  # Debug

            # Check if player entered secret passage in level 2
            if self.level2.player_in_secret_passage() and not self.database_opened:
                self.database_opened = True
                # Show app selection menu
                self.show_app_menu = True

    def draw(self):
        self.screen.fill((20, 20, 30))  # Dark background like Hollow Knight

        if self.current_room == "level1":
            self.level1.draw(self.screen)
        elif self.current_room == "level2":
            self.level2.draw(self.screen)

        # Draw app menu if showing
        if self.show_app_menu:
            self.draw_app_menu()
        # Draw code screen if showing code
        elif self.show_code_screen:
            self.draw_code_screen()
        # Draw victory screen if player reached flag
        elif self.show_victory:
            self.draw_victory_screen()

        pygame.display.flip()

    def draw_app_menu(self):
        """Draw app selection menu - Modern style"""
        # Gradient background overlay
        overlay = pygame.Surface((1280, 720))
        overlay.set_alpha(230)
        # Purple to blue gradient effect
        for y in range(720):
            color_r = int(102 + (118 - 102) * (y / 720))
            color_g = int(126 + (75 - 126) * (y / 720))
            color_b = int(234 + (162 - 234) * (y / 720))
            pygame.draw.line(overlay, (color_r, color_g, color_b), (0, y), (1280, y))
        self.screen.blit(overlay, (0, 0))

        # Title
        font_title = pygame.font.Font(None, 72)
        title_text = font_title.render("Selectionnez une app", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(640, 150))
        self.screen.blit(title_text, title_rect)

        # Cloud app card
        mouse_x, mouse_y = pygame.mouse.get_pos()
        cloud_rect = pygame.Rect(440, 280, 400, 180)

        # Check if mouse is hovering
        is_hovering = cloud_rect.collidepoint(mouse_x, mouse_y)

        # Shadow
        shadow_rect = pygame.Rect(445, 285, 400, 180)
        pygame.draw.rect(self.screen, (20, 20, 40), shadow_rect, border_radius=20)

        # Card background - lighter if hovering
        card_color = (255, 255, 255) if is_hovering else (245, 245, 250)
        pygame.draw.rect(self.screen, card_color, cloud_rect, border_radius=20)

        # Border - purple if hovering
        border_color = (118, 75, 162) if is_hovering else (200, 200, 210)
        pygame.draw.rect(self.screen, border_color, cloud_rect, 3, border_radius=20)

        # Cloud icon
        font_icon = pygame.font.Font(None, 96)
        icon_text = font_icon.render("☁", True, (102, 126, 234))
        icon_rect = icon_text.get_rect(center=(640, 340))
        self.screen.blit(icon_text, icon_rect)

        # App name
        font_name = pygame.font.Font(None, 48)
        name_text = font_name.render("Cloud", True, (60, 60, 80))
        name_rect = name_text.get_rect(center=(640, 410))
        self.screen.blit(name_text, name_rect)

        # Instructions
        font_small = pygame.font.Font(None, 24)
        inst_text = font_small.render("Cliquez ou appuyez sur 1  |  ESC pour retourner", True, (200, 200, 220))
        inst_rect = inst_text.get_rect(center=(640, 560))
        self.screen.blit(inst_text, inst_rect)

    def draw_code_screen(self):
        """Draw secret code screen - Modern style"""
        # Gradient background overlay
        overlay = pygame.Surface((1280, 720))
        overlay.set_alpha(230)
        # Purple to blue gradient effect
        for y in range(720):
            color_r = int(102 + (118 - 102) * (y / 720))
            color_g = int(126 + (75 - 126) * (y / 720))
            color_b = int(234 + (162 - 234) * (y / 720))
            pygame.draw.line(overlay, (color_r, color_g, color_b), (0, y), (1280, y))
        self.screen.blit(overlay, (0, 0))

        # Modern white card with shadow
        shadow_box = pygame.Rect(295, 185, 700, 360)
        pygame.draw.rect(self.screen, (20, 20, 40), shadow_box, border_radius=20)

        code_box = pygame.Rect(290, 180, 700, 360)
        pygame.draw.rect(self.screen, (255, 255, 255), code_box, border_radius=20)

        # Title - Purple gradient effect
        font_title = pygame.font.Font(None, 64)
        title_text = font_title.render("Bienvenue Max", True, (102, 126, 234))
        title_rect = title_text.get_rect(center=(640, 240))
        self.screen.blit(title_text, title_rect)

        # Code label
        font_label = pygame.font.Font(None, 36)
        label_text = font_label.render("Votre code d'acces:", True, (95, 99, 104))
        label_rect = label_text.get_rect(center=(640, 310))
        self.screen.blit(label_text, label_rect)

        # The CODE - Purple color
        font_code = pygame.font.Font(None, 96)
        code_text = font_code.render(self.secret_code, True, (118, 75, 162))
        code_rect = code_text.get_rect(center=(640, 380))
        self.screen.blit(code_text, code_rect)

        # Instructions - Modern gray
        font_small = pygame.font.Font(None, 24)
        inst1 = font_small.render("Ouverture de la page securisee...", True, (102, 126, 234))
        inst1_rect = inst1.get_rect(center=(640, 460))
        self.screen.blit(inst1, inst1_rect)

        remaining = max(0, int(3.0 - self.code_display_time))
        hint_text = font_small.render(f"Retour au jeu dans {remaining}s... (ou appuyez ESPACE)", True, (140, 140, 160))
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
        title_text = font_title.render("VICTOIRE!", True, (220, 220, 255))
        title_rect = title_text.get_rect(center=(640, 270))
        self.screen.blit(title_text, title_rect)

        # Message
        font_msg = pygame.font.Font(None, 32)
        msg_text = font_msg.render("Tu as termine tous les niveaux!", True, (180, 180, 200))
        msg_rect = msg_text.get_rect(center=(640, 340))
        self.screen.blit(msg_text, msg_rect)

        # Congrats
        font_hint = pygame.font.Font(None, 28)
        hint_text = font_hint.render("Felicitations Max! Niveau 2 complete!", True, (150, 220, 150))
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
