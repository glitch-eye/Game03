"""
    Stores Game settings + hardcode stuffs + magic numbers
"""
import pygame
import os
import re
import csv
TILE_SIZE = 36
MAP_NUMS = (120, 40)
INDEX_MAP = [[0 for _ in range(MAP_NUMS[0])] for _ in range(MAP_NUMS[1])]


WIDTH, HEIGHT = 900, 480

VELOCITY = 10
