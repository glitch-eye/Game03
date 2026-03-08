"""
    Stores Game settings + hardcode stuffs + magic numbers
"""
import pygame
import sys
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
gGRAVITY = 1200.0

##place holder for map collision
mBOTTOM = 360
mLEFT = 0
mRIGHT = 640
# player
PLAYER_COLLISION_WIDTH = 32
PLAYER_COLLISION_HEIGHT = 64
pSPEED = 150.0
pJUMPSTRENGTH = 450.0
pJUMPHOLDTIME = 0.4                          # in secs
pDOUBLEJUMPHOLDTIME = 0.4                    # in secs
pDOUBLEJUMPSTRENGTH = 480.0
pINIT_POS = pygame.Vector2(132, 100)
PLAYER_HURTBOX_WIDTH = 18
PLAYER_HURTBOX_HEIGHT = 48