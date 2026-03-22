"""
    Fire gate object
"""
import pygame
from pygame.locals import *
from settings import *
from utils import *
from build import *
import math

class FireGate:
    def __init__(self, pos, loader):
        self.pos = pygame.Vector2(pos)
        self.loader = loader

        self.frames = loader.get_animation("huda_fire")
        self.frame_index = 0
        self.anim_speed = 10

        self.image = self.frames[0]

        # Gate size
        self.width = 32
        self.height = 72

        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.midbottom = self.pos

        # sine wave animation
        self.time = 0

        # damage cooldown (prevents instant melt)
        self.damage_cooldown = 0

    # -----------------------
    # UPDATE
    # -----------------------
    def update(self, dt, player):

        # Animate flame sprite
        self.frame_index += self.anim_speed * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

        self.time += dt

        # Damage cooldown timer
        if self.damage_cooldown > 0:
            self.damage_cooldown -= dt

        # -----------------------
        # COLLISION CHECK
        # -----------------------
        if self.rect.colliderect(player.get_hurtbox_rect()):

            # Player immune to fire?
            if not player.get_fire():

                # damage player (x position used for knockback direction)
                player.apply_damage(25, self.rect.centerx)

    # -----------------------
    # DRAW
    # -----------------------
    def draw(self, screen, camera_x, camera_y):

        tile_h = self.image.get_height()
        tiles = 5

        base_x = self.rect.centerx
        base_y = self.rect.bottom

        for i in range(tiles):
            # sine wave horizontal sway
            offset_x = math.sin(self.time * 7 + i * 0.4) * 3

            x = base_x - self.image.get_width() // 2 + offset_x
            overlap = tile_h * 0.65
            y = base_y - overlap * (i + 1)

            screen.blit(
                self.image,
                (x - camera_x, y - camera_y)
            )

class Magatama:
    def __init__(self, pos, loader):
        self.image = loader.get_image("magatama")
        self.pos = pygame.Vector2(pos)
        self.rect = self.image.get_rect(center=self.pos)

        self.alive = True
        self.float_time = 0

    def update(self, dt, player):
        # Floating animation
        self.float_time += dt
        self.pos.y += math.sin(self.float_time * 3) * 20 * dt
        self.rect.center = self.pos

        # Pickup check
        dx = abs(player._pos.x - self.pos.x)
        dy = abs(player._pos.y - self.pos.y)

        if dx < 20 and dy < 20:
            player.fire_upgrade()
            self.alive = False

    def draw(self, screen, camera_x, camera_y):
        screen.blit(self.image, self.rect.move(-camera_x, -camera_y))