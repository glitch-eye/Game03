"""
    Stores Game settings + hardcode stuffs + magic numbers
"""
import pygame
import sys, json
from pygame.locals import *

#Game settings
GAME_NAME = "Peak Platformer"
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 360
FPS = 60
GAME_SCALE = 2

FONT_SIZE = 36

#Colors
COLOR_WHITE = (255, 255, 255)
COLOR_GREEN = (0, 255, 0)
COLOR_BLACK = (0, 0, 0)

#Game physics settings
GAME_GRAVITY = 1200.0

##place holder for map collision
MAP_BOTTOM = 650
MAP_LEFT = 0
MAP_RIGHT = 640

#player
PLAYER_COLLISION_WIDTH = 32
PLAYER_COLLISION_HEIGHT = 64

# Player base stats
PLAYER_SPEED = 150.0
PLAYER_DASHCOOLDOWN = 1.0
PLAYER_DASHSPEED = 3000.0
PLAYER_JUMPSTRENGTH = 450.0
PLAYER_JUMPHOLDTIME = 0.4                          # in secs
PLAYER_DOUBLEJUMPHOLDTIME = 0.4                    # in secs
PLAYER_DOUBLEJUMPSTRENGTH = 480.0
PLAYER_INIT_POS = pygame.Vector2(132, 100)
PLAYER_HURTBOX_WIDTH = 18
PLAYER_HURTBOX_HEIGHT = 48
