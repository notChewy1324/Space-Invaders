import pygame
import os
import time
import random
pygame.init()
pygame.font.init()
enemy_count = 0

# Window Config Settings
WIDTH, HEIGHT = 1080, 750
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

# Game sounds
def reward_sound():
    sound = pygame.mixer.Sound("sounds/reward_sound.wav")
    pygame.mixer.Sound.play(sound)

def damage_sound():
    sound = pygame.mixer.Sound("sounds/damage_sound.wav")
    pygame.mixer.Sound.play(sound)

def player_laser_sound():
    sound = pygame.mixer.Sound("sounds/player_laser_sound.wav")
    pygame.mixer.Sound.play(sound)

def enemy_laser_sound():
    sound = pygame.mixer.Sound("sounds/enemy_laser_sound.wav")
    pygame.mixer.Sound.play(sound)

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

class Ship():
    COOLDOWN = 20

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
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10 # Damage
                self.lasers.remove(laser)
                damage_sound()

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            player_laser_sound()
            self.cool_down_counter = 1

    def fastshoot(self):
        COOLDOWN = 10
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            player_laser_sound()
            self.cool_down_counter = 1

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

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.lasers.remove(laser)
                        global enemy_count
                        enemy_count += 1
                        damage_sound()

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))

class Enemy(Ship):
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP, RED_LASER),
                "green": (GREEN_SPACE_SHIP, GREEN_LASER),
                "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
                }

    def __init__(self, x, y, color, health=100): 
        super().__init__(x, y, health=health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-15, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
        

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("Helvetica Neue Light", 50)
    lost_font = pygame.font.SysFont("Helvetica Neue Light", 80)

    enemies = []
    wave_lenth = 5 # Min number of enemies
    enemy_vel = 1 # Enemy speed
    global enemy_count

    player_vel = 7 # Player speed
    laser_vel = 10 # Laser speed

    player = Player(300, 630)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        WIN.blit(BG, (0,0))
        # Draw text
        # Lives text color
        if lives >= 6:
            lives_label = main_font.render(f"Lives: {lives}", 1, (0,255,0))
        elif lives <= 3:
            lives_label = main_font.render(f"Lives: {lives}", 1, (255,0,0))
        else:
            lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))

        # Enemy count text
        enemy_count_label = main_font.render(f"{enemy_count}/{wave_lenth}", 1, (255,255,255))

        # Level text color
        if level <= 4:
            level_label = main_font.render(f"Level: {level}", 1, (255,255,255))
        elif level >= 5 and level <= 9:
            level_label = main_font.render(f"Level: {level}", 1, (17,255,0))
        elif level >= 10 and level <= 14:
            level_label = main_font.render(f"Level: {level}", 1, (255,255,0))
        elif level >= 15 and level <= 19:
            level_label = main_font.render(f"Level: {level}", 1, (255,0,255))
        elif level >= 20 and level <= 24:
            level_label = main_font.render(f"Level: {level}", 1, (175,0,0))
        elif level >= 25:
            level_label = main_font.render(f"Level: {level}", 1, (255,0,0))

        WIN.blit(lives_label, (10,10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        WIN.blit(enemy_count_label, (WIDTH - enemy_count_label.get_width() - (WIDTH/2), 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost == True:
            lost_label =  lost_font.render("You Lost!", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            # Update speed and enemies with new levels
            if level <= 4:
                enemy_count = 0
                enemy_vel = 1
                wave_lenth = 5
            if level >= 5 and level <= 9:
                enemy_count = 0
                enemy_vel = 2
                wave_lenth = 10
                reward_sound()
            if level >= 10 and level <= 14:
                enemy_count = 0
                enemy_vel = 3
                lives += 3
                if player.health < 20:
                    player.health += 40
                wave_lenth = 15
                reward_sound()
            if level >= 15 and level <= 19:
                enemy_count = 0
                enemy_vel = 4
                lives += 5
                if player.health < 70:
                    player.health += 30
                player_vel = 10
                laser_vel = 13
                wave_lenth = 25
                reward_sound()
            if level >= 20 and level <= 24:
                enemy_count = 0
                enemy_vel = 5
                lives += 20
                if player.health < 100:
                    player.health = 100
                player_vel = 15
                laser_vel = 18
                wave_lenth = 45
                reward_sound()
            if level >= 25:
                enemy_count = 0
                enemy_vel = 6
                lives += 50
                if player.health < 100:
                    player.health = 150
                player_vel = 17
                laser_vel = 20
                wave_lenth = 65
                reward_sound()
            for i in range(wave_lenth):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0 or keys[pygame.K_LEFT] and player.x - player_vel > 0: # Left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH or keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH: # Right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel  > 0 or keys[pygame.K_UP] and player.y - player_vel  > 0: # Up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 20 < HEIGHT or keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() + 20 < HEIGHT: # Down
            player.y += player_vel
        if keys[pygame.K_SPACE] or keys[pygame.K_e]:
            if level >= 16:
                player.fastshoot()
            else:
                player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 6*FPS) == 1 and enemy.y - enemy_vel > 0:
                enemy_laser_sound()
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 15 # Damage
                enemies.remove(enemy)
                enemy_count += 1
                damage_sound()
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)
                enemy_count += 1
                damage_sound()

        player.move_lasers(-laser_vel, enemies)

def main_menu():
    title_font = pygame.font.SysFont("Helvetica Neue Light", 80)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label = title_font.render("Press the mouse to begin...", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()

main_menu()