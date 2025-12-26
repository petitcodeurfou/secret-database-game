import pygame

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 40
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 300
        self.jump_power = 650
        self.gravity = 1500
        self.on_ground = False
        self.color = (200, 200, 255)  # Light blue like the Knight

    def update(self, dt, platforms):
        # Get keyboard input
        keys = pygame.key.get_pressed()

        # Horizontal movement
        self.vel_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = self.speed

        # Jump
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vel_y = -self.jump_power
            self.on_ground = False

        # Apply gravity
        self.vel_y += self.gravity * dt

        # Update horizontal position and check collisions
        self.x += self.vel_x * dt
        player_rect = self.get_rect()

        for platform in platforms:
            if player_rect.colliderect(platform):
                # Horizontal collision
                if self.vel_x > 0:  # Moving right
                    self.x = platform.left - self.width
                elif self.vel_x < 0:  # Moving left
                    self.x = platform.right
                player_rect = self.get_rect()

        # Update vertical position and check collisions
        self.y += self.vel_y * dt
        player_rect = self.get_rect()
        self.on_ground = False

        for platform in platforms:
            if player_rect.colliderect(platform):
                # Vertical collision
                if self.vel_y > 0:  # Falling down
                    self.y = platform.top - self.height
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:  # Jumping up
                    self.y = platform.bottom
                    self.vel_y = 0
                player_rect = self.get_rect()

        # Keep player on screen (left bound only, allow right for secret passage)
        if self.x < 0:
            self.x = 0
        # Allow player to go beyond right edge for secret passage (up to 1300)
        if self.x > 1300:
            self.x = 1300

        # Fall detection (respawn if fall too far)
        if self.y > 800:
            self.x = 100
            self.y = 500
            self.vel_y = 0

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.get_rect())
        # Draw a simple eye
        eye_x = int(self.x + self.width * 0.5)
        eye_y = int(self.y + self.height * 0.3)
        pygame.draw.circle(screen, (50, 50, 50), (eye_x, eye_y), 4)
