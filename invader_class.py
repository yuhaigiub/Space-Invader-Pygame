import pygame
import os

pygame.font.init()

# CONSTANTS

WIN_WIDTH = 750
WIN_HEIGHT = 750 

FPS = 60

SCALE_SIZE = (50, 50)

MAX_ENEMY_VEL = 8
MAX_ENEMIES_PER_WAVE = 20

COOL_DOWN = 30
PLAYER_LASER_VEL = 20
ENEMY_LASER_VEL = 10

PLAYER_VEL = 5

# LOAD IMAGES

# enemy ships
RED_SPACESHIP = pygame.transform.scale(pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png")), SCALE_SIZE)
GREEN_SPACESHIP = pygame.transform.scale(pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png")), SCALE_SIZE)
BLUE_SPACESHIP = pygame.transform.scale(pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png")), SCALE_SIZE)

# player ship
YELLOW_SPACESHIP = pygame.transform.scale(pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png")), SCALE_SIZE)

# lasers
RED_LASER = pygame.transform.scale(pygame.image.load(os.path.join("assets", "pixel_laser_red.png")), SCALE_SIZE)
GREEN_LASER = pygame.transform.scale(pygame.image.load(os.path.join("assets", "pixel_laser_green.png")), SCALE_SIZE)
BLUE_LASER = pygame.transform.scale(pygame.image.load(os.path.join("assets", "pixel_laser_blue.png")), SCALE_SIZE)
YELLOW_LASER = pygame.transform.scale(pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png")), SCALE_SIZE)

# background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIN_WIDTH, WIN_HEIGHT))

# FONT
MAIN_FONT = pygame.font.SysFont("comicsans", 30)

# DICTIONARIES

COLOR_MAP = {
    "red" : (RED_SPACESHIP, RED_LASER),
    "green" : (GREEN_SPACESHIP, GREEN_LASER),
    "blue" : (BLUE_SPACESHIP, BLUE_LASER)
}

# CLASS

class Ship:
    def __init__(self, x, y, vel, hp=100):
        self.x = x
        self.y = y
        self.hp = hp
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cooldown_counter = 0
        self.vel = vel
        
    def draw(self, win):
        win.blit(self.ship_img, (self.x, self.y))
    
    def move(self, hor, ver):
        if (hor == 1 and self.x < WIN_WIDTH - self.ship_img.get_width()) or (hor == -1 and self.x > 0):
            self.x += hor * self.vel
        if (ver == 1 and self.y < WIN_HEIGHT - self.ship_img.get_height()) or (ver == -1 and self.y > 0):
            self.y += ver * self.vel
        
        self.cooldown()
    
    def cooldown(self):
        if self.cooldown_counter > 0:
            self.cooldown_counter -= 1
    
    def shoot(self, vel):
        if self.cooldown_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img, vel)
            self.lasers.append(laser)
            self.cooldown_counter = COOL_DOWN
    
    
class Player(Ship):
    MAX_HEALTH = 100
    
    def __init__(self, x, y, vel, health=100):
        super().__init__(x, y, vel, health)
        self.ship_img = YELLOW_SPACESHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)

class Enemy(Ship):
    
    def __init__(self, x, y, vel, color, health=100):
        super().__init__(x, y, vel, health)
        self.ship_img, self.laser_img = COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
            
    def move(self):
        self.y += self.vel   
    
    def is_off_screen(self):
        if self.y > WIN_WIDTH + self.ship_img.get_width():
            return True
        return False     
    
    def is_laser(self):
        return False
    
class Laser():
    def __init__(self, x, y, img, vel):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)
        self.vel = vel
        
    def draw(self, win):
        win.blit(self.img, (self.x, self.y))
        
    def move(self, dir):
        self.y += self.vel * dir
        
    def is_off_screen(self):
        if self.y > WIN_WIDTH + self.img.get_width():
            return True
        return False
    
    def is_laser(self):
        return True   

class Background():
    
    def __init__(self):
        self.img = BG
        self.y1 = 0
        self.y2 = 0 - self.img.get_height()
        self.vel = PLAYER_VEL // 2
    
    def move(self):
        self.y1 += self.vel 
        self.y2 += self.vel
        
        if self.y1 > WIN_HEIGHT:
            self.y1 = self.y2 - WIN_HEIGHT
        if self.y2 > WIN_HEIGHT:
            self.y2 = self.y1 - WIN_HEIGHT
    
    def draw(self, win):
        win.blit(self.img, (0, self.y1))
        win.blit(self.img, (0, self.y2))
        

        
def collide(obj1, obj2):
    offset = (obj2.x - obj1.x, obj2.y - obj1.y)
    point = obj1.mask.overlap(obj2.mask, offset)
    
    return point != None

def sqr_distance(obj1, obj2):
    return (obj1.x - obj2.x)**2 + (obj1.y - obj2.y)**2
