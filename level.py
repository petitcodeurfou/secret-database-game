import pygame

class Level:
    def __init__(self, player):
        self.player = player
        self.platforms = []
        self.secret_passage_rect = None
        self.hint_shown = False

        # Create platforms for level 1
        # Ground
        self.platforms.append(pygame.Rect(0, 650, 1280, 70))

        # Main path platforms (left side going up)
        self.platforms.append(pygame.Rect(100, 570, 150, 20))
        self.platforms.append(pygame.Rect(280, 500, 150, 20))
        self.platforms.append(pygame.Rect(460, 430, 150, 20))
        self.platforms.append(pygame.Rect(640, 360, 150, 20))
        self.platforms.append(pygame.Rect(460, 290, 150, 20))
        self.platforms.append(pygame.Rect(280, 220, 150, 20))
        self.platforms.append(pygame.Rect(100, 150, 150, 20))

        # Flag platform (destination - top left)
        self.flag_platform = pygame.Rect(50, 80, 100, 20)
        self.platforms.append(self.flag_platform)
        self.flag_pos = (90, 30)  # Flag position

        # Middle area platforms
        self.platforms.append(pygame.Rect(800, 500, 120, 20))
        self.platforms.append(pygame.Rect(950, 430, 120, 20))
        self.platforms.append(pygame.Rect(800, 360, 120, 20))

        # Secret area platform (upper right - hidden)
        self.platforms.append(pygame.Rect(1100, 250, 180, 20))

        # Fake wall hiding the secret passage (very discrete - looks like normal wall)
        self.fake_wall = pygame.Rect(1240, 200, 40, 70)

        # Secret passage trigger area (behind the fake wall)
        self.secret_passage_rect = pygame.Rect(1250, 200, 50, 70)

        # Visual decorations
        self.decorative_platforms = [
            pygame.Rect(350, 600, 80, 15),
            pygame.Rect(600, 550, 100, 15),
            pygame.Rect(900, 620, 70, 15),
        ]

    def update(self, dt):
        self.player.update(dt, self.platforms)

    def player_in_secret_passage(self):
        """Check if player has entered the secret passage"""
        player_rect = self.player.get_rect()
        return player_rect.colliderect(self.secret_passage_rect)

    def player_reached_flag(self):
        """Check if player has reached the flag"""
        player_rect = self.player.get_rect()
        flag_area = pygame.Rect(self.flag_pos[0] - 30, self.flag_pos[1] - 20, 80, 80)
        return player_rect.colliderect(flag_area)

    def draw(self, screen):
        # Draw platforms
        for platform in self.platforms:
            pygame.draw.rect(screen, (100, 100, 120), platform)
            pygame.draw.rect(screen, (150, 150, 170), platform, 2)  # Border

        # Draw decorative platforms
        for platform in self.decorative_platforms:
            pygame.draw.rect(screen, (80, 80, 100), platform)

        # Draw fake wall (discrete - looks like a normal dark area)
        # Very subtle, blends with background
        fake_wall_surface = pygame.Surface((self.fake_wall.width, self.fake_wall.height))
        fake_wall_surface.set_alpha(150)
        fake_wall_surface.fill((30, 30, 40))
        screen.blit(fake_wall_surface, (self.fake_wall.x, self.fake_wall.y))

        # Draw flag (destination indicator)
        flag_x, flag_y = self.flag_pos
        # Flag pole
        pygame.draw.line(screen, (180, 180, 180), (flag_x, flag_y), (flag_x, flag_y + 50), 3)
        # Flag cloth (red)
        flag_points = [
            (flag_x, flag_y),
            (flag_x + 40, flag_y + 10),
            (flag_x + 40, flag_y + 25),
            (flag_x, flag_y + 15)
        ]
        pygame.draw.polygon(screen, (220, 50, 50), flag_points)
        pygame.draw.polygon(screen, (180, 30, 30), flag_points, 2)

        # Flag text
        font_flag = pygame.font.Font(None, 20)
        flag_text = font_flag.render("Level 2", True, (220, 220, 220))
        screen.blit(flag_text, (flag_x - 15, flag_y - 25))

        # Draw some atmospheric particles (like Hollow Knight)
        for i in range(20):
            x = (i * 73) % 1280
            y = (i * 97) % 720
            size = (i % 3) + 1
            alpha = 30 + (i % 50)
            particle_surface = pygame.Surface((size, size))
            particle_surface.set_alpha(alpha)
            particle_surface.fill((150, 180, 200))
            screen.blit(particle_surface, (x, y))

        # Draw player
        self.player.draw(screen)

        # Draw level indicator
        font = pygame.font.Font(None, 36)
        level_text = font.render("Level 1 - The Beginning", True, (150, 150, 200))
        screen.blit(level_text, (20, 20))
