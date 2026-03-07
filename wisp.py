import pygame
import math
import random

class Wisp:

    def __init__(self, x, y, frames):

        # position
        self._pos = pygame.Vector2(x, y)
        self._speed = 35

        # animation
        self._frames = frames
        self._frame_index = 0
        self._anim_speed = 8
        self._anim_timer = 0

        self._image = self._frames[0]
        self._rect = self._image.get_rect(center=self._pos)

        # floating drift
        self._float_timer = random.uniform(0, 10)

    # -----------------------
    # UPDATE
    # -----------------------

    def update(self, dt, player_pos):

        # direction to player
        direction = pygame.Vector2(player_pos) - self._pos
        distance = direction.length()

        if distance > 0:
            direction = direction.normalize()

        # move toward player
        self._pos += direction * self._speed * dt

        # floating movement (ghost drift)
        self._float_timer += dt
        self._pos.y += math.sin(self._float_timer * 3) * 0.5

        # update rect
        self._rect.center = (int(self._pos.x), int(self._pos.y))

        # animate
        self._anim_timer += dt
        if self._anim_timer > 1 / self._anim_speed:

            self._anim_timer = 0
            self._frame_index = (self._frame_index + 1) % len(self._frames)
            self._image = self._frames[self._frame_index]

    # -----------------------
    # DRAW
    # -----------------------

    def draw(self, screen):

        screen.blit(self._image, self._rect)

    # -----------------------
    # COLLISION (for later)
    # -----------------------

    def get_rect(self):
        return self._rect