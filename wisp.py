import pygame
import math
import random
from pygame.locals import *
from settings import *

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
    
class Goblin():
    def __init__(self, x, y, loader):
        self._animations = {
            "idle": loader.get_animation("goblin_idle"),
            "attack": loader.get_animation("goblin_attack"),
            "run": loader.get_animation("goblin_run"),
            "die": loader.get_animation("big_bomb_effect")
        }

        # position
        self._pos = pygame.Vector2(x, y)
        self._vel = pygame.Vector2(0, GAME_GRAVITY)

        # animation
        self._frames = self._animations["run"]
        self._frame_index = 0
        self._anim_speed = 8
        self._anim_timer = 0
        self._attack = False
        self._dir = "left"

        self._image = self._frames[0]
        self._rect = pygame.Rect(0, 0, GOB_WIDTH, GOB_HEIGHT)
        self._rect.topleft = self._pos

        self._hit_range = 100
        self._sight_range = 90
        self._sight_angle = 30 #in degree

    #----------------------
    #    UPDATE
    #----------------------
    def update(self, dt, player_rect):
        """Update animation, position based on dt, attack if player_pos in range"""
        # sight seeing
        seeing = self.ray_casting(player_rect)
        if seeing:
            direction = pygame.Vector2(player_rect.center) - pygame.Vector2(self._rect.center)
            dist = direction.length()
            if dist <= self._hit_range and not self._attack:
                self._attack = True
                self._vel.x = 0
                self._frame_index = 0
                self._frames = self._animations["attack"]
                self._anim_timer = 0
                self._anim_speed = 15
                self._image = self._frames[0]
            else:
                # if not in range then tryna follow la
                if self._attack and self._frame_index == len(self._frames) - 1:
                    self._vel.x = (direction.x / abs(direction.x)) * 30
                    self._dir = "right" if self._vel.x > 0 else "left"
                    self._attack = False
                    self._vel.x = 30 if self._dir == "right" else -30
                    self._frame_index = 0
                    self._frames = self._animations["run"]
                    self._anim_timer = 0
                    self._anim_speed = 8
                    self._image = self._frames[0]
        else:
            # no seeing then return to normal once the attack animation is done
            if self._attack and self._frame_index == len(self._frames) - 1:
                self._attack = False
                self._vel.x = 30 if self._dir == "right" else -30
                self._frame_index = 0
                self._frames = self._animations["run"]
                self._anim_timer = 0
                self._anim_speed = 8
                self._image = self._frames[0]

        # moving logic + animation
        self._pos += self._vel * dt
        if self._attack:
            self._vel.x = 0
        self._anim_timer += dt
        if self._anim_timer >= 1 / self._anim_speed:
            self._anim_timer = 0
            self._frame_index += 1
            self._frame_index %= len(self._frames)
            self._image = self._frames[self._frame_index]

        self._rect.topleft = self._pos

    #----------------------
    #    DRAW !!!! TRIMMING USING MAGIC NUMBER !!!!!!
    #----------------------
    def draw(self, screen):
        drawpos = self._rect.topleft
        if self._dir == "left":
            if not self._attack:
                screen.blit(self._image, self._rect)
            else:
                #trimming
                drawpos = (drawpos[0] - 90, drawpos[1])
                screen.blit(self._image, drawpos)
        else:
            image = pygame.transform.flip(self._image, True, False)

            # Align flipped image so its right edge matches the rect’s right edge
            if self._attack:
                drawpos = (drawpos[0] - 20, drawpos[1])
                screen.blit(image, drawpos)
            else:
                screen.blit(image, self._rect)

    #----------------------
    #    COLLISION
    #----------------------
    def check_collision(self):
        if self._pos.x <= MAP_LEFT:
            self._pos.x = MAP_LEFT
            self._vel.x = 30
            self._dir = "right"

        if self._pos.x + self._rect.width >= MAP_RIGHT:
            self._pos.x = MAP_RIGHT - self._rect.width
            self._vel.x = -30
            self._dir = "left"

        if self._pos.y + self._rect.height >= MAP_BOTTOM:
            self._pos.y = MAP_BOTTOM - self._rect.height
            self._vel.y = 0
        else:
            self._vel.y = GAME_GRAVITY

    #------------------------------
    #    ENEMY EYE SIGHT LOGIC
    #------------------------------
    def ray_casting(self, player_rect):
        origin = pygame.Vector2(self._rect.midtop)

        # Facing axis
        axis = pygame.Vector2(1, 0) if self._dir == "right" else pygame.Vector2(-1, 0)

        # End point of the ray
        ray_end = origin + axis * self._sight_range

        ray_vec = ray_end - origin
        bottom_ray = ray_vec.rotate(-self._sight_angle / 2)
        # cast rays 
        see = False
        delta = self._sight_angle / 15.0
        for i in range(15):
            ray = bottom_ray.rotate(delta * i)
            new_end = origin + ray
            ray_line = (origin, new_end)
            see = see or player_rect.clipline(ray_line)
        
        return see
    
import math

class Crystal:
    """
    crystal 4: hp
    crystal 0: mp
    """
    def __init__(self, loader, c_type=0):
        frames = loader.get_animation("crystal")
        self._death_frames = loader.get_animation("big_bomb_effect")
        self._alive = True
        self._item_pop = False
        self._item_pop_duration = 8
        self._item_pop_height = 10
        self._pop_timer = 0
        self._image_index = 0
        self._frame_speed = 8
        self._frame_timer = 0
        self._shake_timer = 0
        self._shake_strength = 4 
        self._shake_duration = 8
        self._hit = False
        index = c_type % len(frames)
        self._frame = [frames[index]]
        if index == 0:
            self._item = loader.get_animation("mp_item")
        elif index == 1:
            self._item = loader.get_animation("hp_item")
        
        self._health = 100

        self._image = self._frame[0]
        self._pos = (150, 150)
        self._rect = self._image.get_rect(center=self._pos)

    def update(self, dt):
        if self._alive and self.is_hit():
            self._hit = True
            self._shake_timer = 0
            self._health -= 20

        if self._health <= 0 and self._alive:
            self._alive = False
            self._frame_timer = 0
            self._image_index = 0
            self._image = self._death_frames[0]

        self._frame_timer += dt
        if self._frame_timer > 1 / self._frame_speed:
            self._frame_timer = 0
            self._image_index += 1
            if self._alive:
                self._image_index = 0
            elif self._image_index < len(self._death_frames):
                self._image = self._death_frames[self._image_index]
            else:
                # pop the item out
                self._item_pop = True
                self._image = self._item[0]

        # update shake timer if alive
        if self._hit and self._alive:
            self._shake_timer += dt

            if self._shake_timer > 1 / self._shake_duration:
                self._shake_timer = 0
                self._hit = False
        
        if self._item_pop:
            self._pop_timer += dt

            if self._pop_timer >= 1 / self._item_pop_duration:
                self._pop_timer = 1 / self._item_pop_duration
                self._item_pop = False

    def draw(self, screen):
        offset_x = 0
        offset_y = 0
        if self._hit and self._alive:
            # sine wave jiggle
            offset_x = int(math.sin(self._shake_timer * 20) * self._shake_strength)
        
        if self._item_pop:
            progress = self._pop_timer * self._item_pop_duration
            offset_y = - self._item_pop_height * (1 - progress)

        draw_pos = (self._rect.centerx + offset_x, self._rect.centery + offset_y)
        rect = self._image.get_rect(center=draw_pos)
        screen.blit(self._image, rect)

    def is_hit(self):
        """simple random hit"""
        if random.randint(1, 100) in [11, 28]:
            return True
        return False