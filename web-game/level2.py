import pygame
import base64

class Level2:
    def __init__(self, player):
        self.player = player
        self.platforms = []
        self.moving_platforms = []
        self.secret_passage_rect = None
        self.hint_shown = False

        # Obfuscated secret coordinates for level 2 (different location)
        self._sc = base64.b64decode(b'MzUwLDEyMCw0MCw2MA==').decode().split(',')
        # Obfuscated secret platform
        self._sp = base64.b64decode(b'MzIwLDE1MCwxMDAsMjA=').decode().split(',')

        # Create platforms for level 2 - DIFFICULT!
        # Ground (smaller sections - gaps to fall)
        self.platforms.append(pygame.Rect(0, 650, 400, 70))
        self.platforms.append(pygame.Rect(600, 650, 680, 70))

        # Starting area - Jump challenge
        self.platforms.append(pygame.Rect(100, 570, 80, 20))
        self.platforms.append(pygame.Rect(220, 500, 80, 20))
        self.platforms.append(pygame.Rect(340, 430, 80, 20))

        # Difficult jump section (big gaps)
        self.platforms.append(pygame.Rect(500, 360, 90, 20))
        self.platforms.append(pygame.Rect(680, 290, 90, 20))
        self.platforms.append(pygame.Rect(860, 220, 90, 20))

        # Upper difficult section
        self.platforms.append(pygame.Rect(1050, 150, 100, 20))
        self.platforms.append(pygame.Rect(900, 150, 100, 20))

        # Right side vertical climb
        self.platforms.append(pygame.Rect(1100, 550, 80, 20))
        self.platforms.append(pygame.Rect(1020, 480, 80, 20))
        self.platforms.append(pygame.Rect(1140, 410, 80, 20))
        self.platforms.append(pygame.Rect(1060, 340, 80, 20))
        self.platforms.append(pygame.Rect(1180, 270, 80, 20))

        # Flag platform (top right - hard to reach)
        self.flag_platform = pygame.Rect(1150, 80, 100, 20)
        self.platforms.append(self.flag_platform)
        self.flag_pos = (1185, 30)  # Flag position

        # Middle dangerous area (small platforms)
        self.platforms.append(pygame.Rect(450, 570, 60, 15))
        self.platforms.append(pygame.Rect(750, 500, 60, 15))
        self.platforms.append(pygame.Rect(600, 420, 60, 15))

        # Secret area platform (hidden in upper left)
        self.platforms.append(pygame.Rect(int(self._sp[0]), int(self._sp[1]), int(self._sp[2]), int(self._sp[3])))

        # Fake wall hiding the secret passage
        _fw_x = int(self._sc[0]) - 10
        _fw_y = int(self._sc[1])
        self.fake_wall = pygame.Rect(_fw_x, _fw_y, 40, 60)

        # Secret passage trigger area
        self.secret_passage_rect = pygame.Rect(int(self._sc[0]), int(self._sc[1]), int(self._sc[2]), int(self._sc[3]))

        # Moving platform setup
        self.moving_platform1 = {
            'rect': pygame.Rect(200, 200, 100, 15),
            'start_x': 200,
            'end_x': 500,
            'speed': 80,
            'direction': 1
        }
        self.moving_platform2 = {
            'rect': pygame.Rect(700, 350, 80, 15),
            'start_x': 500,
            'end_x': 800,
            'speed': 100,
            'direction': 1
        }
        self.moving_platforms = [self.moving_platform1, self.moving_platform2]

        # Add moving platforms to collision platforms
        for mp in self.moving_platforms:
            self.platforms.append(mp['rect'])

        # Decorative platforms (tricky - look like real platforms but smaller)
        self.decorative_platforms = [
            pygame.Rect(400, 250, 40, 10),
            pygame.Rect(550, 180, 40, 10),
            pygame.Rect(150, 400, 50, 10),
        ]

    def update(self, dt):
        # Update moving platforms
        for mp in self.moving_platforms:
            mp['rect'].x += mp['speed'] * mp['direction'] * dt

            # Reverse direction at boundaries
            if mp['rect'].x <= mp['start_x']:
                mp['rect'].x = mp['start_x']
                mp['direction'] = 1
            elif mp['rect'].x >= mp['end_x']:
                mp['rect'].x = mp['end_x']
                mp['direction'] = -1

        # Update player
        self.player.update(dt, self.platforms)

    def player_in_secret_passage(self):
        """Check if player is in the secret passage"""
        player_rect = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
        return self.secret_passage_rect.colliderect(player_rect)

    def player_reached_flag(self):
        """Check if player reached the flag"""
        player_rect = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
        return self.flag_platform.colliderect(player_rect)

    def draw(self, screen):
        # Draw platforms
        for platform in self.platforms:
            if platform in [mp['rect'] for mp in self.moving_platforms]:
                # Moving platforms - different color
                pygame.draw.rect(screen, (80, 200, 120), platform)
            elif platform == self.flag_platform:
                # Flag platform - highlight color
                pygame.draw.rect(screen, (200, 100, 100), platform)
            else:
                # Normal platforms - darker color for level 2
                pygame.draw.rect(screen, (60, 60, 80), platform)

        # Draw decorative platforms (lighter, to show they're different)
        for platform in self.decorative_platforms:
            pygame.draw.rect(screen, (50, 50, 70), platform)

        # Draw fake wall (very subtle - same color as background)
        pygame.draw.rect(screen, (25, 25, 35), self.fake_wall)

        # Draw flag
        flag_x, flag_y = self.flag_pos
        # Flag pole
        pygame.draw.line(screen, (200, 200, 220), (flag_x, flag_y), (flag_x, flag_y + 40), 3)
        # Flag
        flag_points = [(flag_x, flag_y), (flag_x + 30, flag_y + 10), (flag_x, flag_y + 20)]
        pygame.draw.polygon(screen, (220, 50, 50), flag_points)

        # Draw player
        self.player.draw(screen)

        # Level indicator
        font = pygame.font.Font(None, 36)
        level_text = font.render("LEVEL 2", True, (100, 100, 120))
        screen.blit(level_text, (10, 10))
