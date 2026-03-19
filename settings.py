"""
    Stores Game settings + hardcode stuffs + magic numbers
"""
import pygame
import os
import re
import csv
TILE_SIZE = 36
INDEX_MAP = [[0 for _ in range(100)] for _ in range(40)]

WIDTH, HEIGHT = 720, 480

VELOCITY = 10
