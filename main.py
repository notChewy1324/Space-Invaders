import pygame
import os
import time
import random
pygame.font.init()

# Window Config Settings
WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

# Load Images
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

# Player ship
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

# Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# Background Image
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))

class Ship():
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img,(self.x, self.y))

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()
class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health=health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health


def main():
    run = True
    FPS = 60
    level = 1
    lives = 5
    main_font = pygame.font.SysFont("Helvetica Neue Light", 50)
    player_vel = 3
    player = Player(300, 650)

    clock = pygame.time.Clock()

    def redraw_window():
        WIN.blit(BG, (0,0))
        # Draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))

        WIN.blit(lives_label, (10,10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        player.draw(WIN)

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] or keys[pygame.K_LEFT] and player.x - player_vel > 0: # Left
            player.x -= player_vel
        if keys[pygame.K_d] or keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH: # Right
            player.x += player_vel
        if keys[pygame.K_w] or keys[pygame.K_UP] and player.y - player_vel  > 0: # Up
            player.y -= player_vel
        if keys[pygame.K_s] or keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() < HEIGHT: # Down
            player.y += player_vel

            

main()