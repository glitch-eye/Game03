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

def apply_grayscale(surface):
    arr = pygame.surfarray.array3d(surface)

    # luminance formula
    gray = (0.299 * arr[:,:,0] + 0.587 * arr[:,:,1] + 0.114 * arr[:,:,2]).astype("uint8")

    arr[:,:,0] = gray
    arr[:,:,1] = gray
    arr[:,:,2] = gray

    return pygame.surfarray.make_surface(arr)

def recolor_red(surface):
    surf = surface.copy().convert_alpha()

    # Zero out green & blue, keep red channel
    tint = pygame.Surface(surf.get_size()).convert_alpha()
    tint.fill((255, 0, 0, 255))  # bright red tint

    surf.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return surf

def tint_surface_red(surface):
    tinted = surface.copy()
    tinted.fill((255, 60, 60, 180), special_flags=pygame.BLEND_RGBA_MULT)
    return tinted

def get_tight_hitbox(image, anchor_rect, anchor="center"):
    mask = pygame.mask.from_surface(image)
    rects = mask.get_bounding_rects()

    if not rects:
        return anchor_rect.copy()

    r = max(rects, key=lambda x: x.width * x.height)
    tight = pygame.Rect(0, 0, r.width, r.height)

    if anchor == "center":
        tight.center = anchor_rect.center
    elif anchor == "midbottom":
        tight.midbottom = anchor_rect.midbottom

    return tight