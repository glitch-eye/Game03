"""
    Knife projectile
"""
import pygame
from pygame.locals import *
from settings import *
from utils import *
import random

class Knife:
    def __init__(self, pos, direction, loader, attack_type = "normal", y_offset=0, forward_offset=0):
        self.pos = pygame.Vector2(pos)

        self.direction = direction
        self.vel = pygame.Vector2(300 * direction, 0)
        speed = 600

        if attack_type == "under_attack":
            # 45° downward
            self.vel = pygame.Vector2(direction * speed, speed).normalize() * speed

        elif attack_type in ("up_shot", "up_shot2", "up_shot_air", "up_shot_run"):
            # straight up
            self.vel = pygame.Vector2(0, -speed)
        elif attack_type == "down_shot":
            # straight down
            self.vel = pygame.Vector2(0, speed)

        else:
            # normal horizontal
            self.vel = pygame.Vector2(direction * speed, 0)

        forward = self.vel.normalize()

        # perpendicular (rotated 90°)
        perp = pygame.Vector2(-forward.y, forward.x)

        # fix flipping when facing left
        if self.direction < 0:
            perp *= -1

        self.pos += forward * forward_offset
        self.pos += perp * y_offset

        # animations
        self.animations = {
            "flying": loader.get_animation("flying_knife"),
            "trail_1": loader.get_animation("bullet_effect_sprite2"),
            "trail_2": loader.get_animation("bullet_effect_sprite3")
        }

        self.frames = self.animations["flying"]

        self.frame_index = 0
        self.frame_timer = 0
        self.frame_speed = 0.08

        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=self.pos)

        # lifetime
        self.life_time = 2
        self.timer = 0

        # trail system
        self.trails = []
        self.trail_timer = 0
        self.trail_interval = 0.2

        self.alive = True

    def spawn_trail(self):
        frames = random.choice([
            self.animations["trail_1"],
            self.animations["trail_2"]
        ])

        trail = {
            "frames": frames,
            "frame": 0,
            "timer": 0,
            "speed": 0.03,
            # spawn behind knife (based on velocity direction)
            "pos": self.pos - self.vel.normalize() * 15,
            "scale": random.uniform(0.9, 1.1),
            "vel": self.vel * 0.7  # slower follow
        }

        self.trails.append(trail)

    def update(self, dt):
        # movement
        self.pos += self.vel * dt

        # animation
        self.frame_timer += dt
        if self.frame_timer >= self.frame_speed:
            self.frame_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]

        self.rect.center = self.pos

        # spawn trails
        self.trail_timer += dt
        if self.trail_timer >= self.trail_interval:
            self.trail_timer = 0
            self.spawn_trail()

        # update trails
        for trail in self.trails[:]:
            trail["timer"] += dt

            trail["pos"] += trail["vel"] * dt

            if trail["timer"] >= trail["speed"]:
                trail["timer"] = 0
                trail["frame"] += 1

            if trail["frame"] >= len(trail["frames"]):
                self.trails.remove(trail)

        # lifetime
        self.timer += dt
        if self.timer >= self.life_time:
            self.alive = False

    def draw(self, screen, camera_x, camera_y):
        # draw trails FIRST
        for trail in self.trails:
            frame = trail["frames"][trail["frame"]]

            scale = trail["scale"]
            size = (int(frame.get_width()*scale), int(frame.get_height()*scale))
            frame = pygame.transform.scale(frame, size)

            angle = self.vel.angle_to(pygame.Vector2(1, 0))
            frame = pygame.transform.rotate(frame, angle)

            rect = frame.get_rect(center=(trail["pos"].x - camera_x, trail["pos"].y - camera_y))
            screen.blit(frame, rect)

        # draw knife
        angle = self.vel.angle_to(pygame.Vector2(1, 0))

        # rotate sprite
        img = pygame.transform.rotate(self.image, angle)

        rect = img.get_rect(center=(int(self.pos.x - camera_x), int(self.pos.y - camera_y)))
        screen.blit(img, rect)