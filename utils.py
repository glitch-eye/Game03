import pygame
from pygame.locals import *

# ------------------------
# HELPER
# ------------------------
    
def trim_right(frames, pixels):

    trimmed = []

    for frame in frames:

        w = frame.get_width()
        h = frame.get_height()

        new_rect = pygame.Rect(0, 0, w - pixels, h)

        trimmed_frame = frame.subsurface(new_rect).copy()

        trimmed.append(trimmed_frame)

    return trimmed

def trim_top(frames):

    trimmed = []

    for frame in frames:

        w, h = frame.get_size()
        trim_y = 0

        # find first row that contains a visible pixel
        for y in range(h):
            for x in range(w):
                if frame.get_at((x, y)).a != 0:
                    trim_y = y
                    break
            if trim_y != 0 or frame.get_at((0, y)).a != 0:
                break

        new_rect = pygame.Rect(0, trim_y, w, h - trim_y)
        trimmed_frame = frame.subsurface(new_rect).copy()

        trimmed.append(trimmed_frame)

    return trimmed