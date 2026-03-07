"""
    Stores Game settings + hardcode stuffs + magic numbers
"""
import pygame
import sys, json
from pygame.locals import *

#Game settings
GAME_NAME = "Peak Platformer"
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

FONT_SIZE = 36

#Colors
COLOR_WHITE = (255, 255, 255)
COLOR_GREEN = (0, 255, 0)

#Game physics settings
GAME_GRAVITY = 900.0

##place holder for map collision
MAP_BOTTOM = 650
MAP_LEFT = 30
MAP_RIGHT = 1250

# Player base stats
PLAYER_SPEED = 500.0
PLAYER_DASHCOOLDOWN = 1.0
PLAYER_DASHSPEED = 3000.0
PLAYER_JUMPSTRENGTH = 600.0
PLAYER_JUMPHOLDTIME = 0.5                          # in secs
PLAYER_DOUBLEJUMPHOLDTIME = 0.3                    # in secs
PLAYER_DOUBLEJUMPSTRENGTH = 400.0
PLAYER_INIT_POS = pygame.Vector2(100, 100)
PLAYER_HURTBOX_WIDTH = 32
PLAYER_HURTBOX_HEIGHT = 32