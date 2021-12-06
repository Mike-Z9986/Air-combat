import pygame
import os
import time
import random

# display window
WIDTH, HEIGHT = 1440, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
# caption of window
pygame.display.set_caption("Mola's Air-combat")

# load ship
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets","pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets","pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets","pixel_ship_blue_small.png"))

# player ship
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets","pixel_ship_yellow.png"))

# Lasers
RED_LASER = pygame.image.load(os.path.join("assets","pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets","pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets","pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets","pixel_laser_yellow.png"))

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets","background-black.png")),(WIDTH, HEIGHT))


# create font object
pygame.font.init()

# check two objs overlap
def collide(obj1, obj2):
    offset_x = obj2.x = obj1.x
    offset_y = obj2.y = obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self,window):
        window.blit(self.img, (self.x, self.y))

    def move(self,vel):
        self.y += vel

    def off_screen(self, height):
        return self.y <= height and self.y >= 0

    def collsion(self,obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 30
    # 1.ship position 2.color 3.default health
    def __init__(self,x,y,health = 100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    # create ship on window
    def draw(self,window):
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
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    # return ship's width and height
    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

# definite player ship
class Player(Ship):
    def __init__(self,x,y,health=100):
        super().__init__(x,y,health)
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

# definite enemy ship
class Enemy(Ship):
    COLOR_MAP = {
        "red" : (RED_LASER, RED_SPACE_SHIP),
        "green" : (GREEN_LASER, GREEN_SPACE_SHIP),
        "blue" : (BLUE_LASER, BLUE_SPACE_SHIP),
    }
    def __init__(self,x,y,color,health=100):
        super().__init__(x,y,health)
        self.ship_laser, self.ship_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self,vel):
        self.y += vel


def main():
    run = True
    FPS = 60
    level = 0
    lives = 3
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)
    playe_vel = 5  # move 5 pixel

    # set player
    player = Player(300,650)

    # set enemies
    enemies = []
    wave_length = 5
    enemy_vel = 2

    laser_vel = 4

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0


    # set window of all parameters
    def redraw_window():
        # set background
        WIN.blit(BG, (0, 0))

        # set lives and level
        level_label = main_font.render(f"level: {level}",1,(0, 0, 255))  #(,,) means RGB color setting
        lives_label = main_font.render(f"lives: {lives}", 1, (255, 255, 255))
        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10)) # set right on the edge

        # set enemies on window
        for enemy in enemies:
            enemy.draw(WIN)

        # set player ship on window
        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("You LOST!!",1,(255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2,350))

        pygame.display.update()

    # Game loop
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

        # level up
        if len(enemies) == 0:
            level += 1
            wave_length += 5
          # set enemy
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # set key
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - playe_vel > 0:
            player.x -= playe_vel
        if keys[pygame.K_d] and player.x + playe_vel + player.get_width()< WIDTH:
            player.x += playe_vel
        if keys[pygame.K_w] and player.y - playe_vel > 0:
            player.y -= playe_vel
        if keys[pygame.K_s] and player.y + playe_vel + player.get_height() < HEIGHT:
            player.y += playe_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        # enemy move and distance
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)
            # lives reduce if enemy is over off screen
            if enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(laser_vel, enemies)

main()


