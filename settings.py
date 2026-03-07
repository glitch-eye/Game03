"""
    Stores Game settings + hardcode stuffs + magic numbers
"""
import pygame
import sys
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
gGRAVITY = 900.0

##place holder for map collision
mBOTTOM = 650
mLEFT = 30
mRIGHT = 1250

pSPEED = 500.0
pJUMPSTRENGTH = 600.0
pJUMPHOLDTIME = 0.5                          # in secs
pDOUBLEJUMPHOLDTIME = 0.3                    # in secs
pDOUBLEJUMPSTRENGTH = 400.0
pINIT_POS = pygame.Vector2(100, 100)
pHURTBOX_WIDTH = 32
pHURTBOX_HEIGHT = 32