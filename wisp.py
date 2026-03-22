import pygame
import math
import random
from pygame.locals import *
from settings import *

class Wisp:

    def __init__(self, x, y, loader):

        # position
        self._pos = pygame.Vector2(x, y)
        self._speed = 50

        # animation
        self._normal_frames = loader.get_animation("wisp")
        self._frames = self._normal_frames
        self._ded_frames = loader.get_animation("big_bomb_effect")
        self._frame_index = 0
        self._anim_speed = 8
        self._anim_timer = 0
        self.spawn_freeze_timer = 10.0 # freeze for 10 seconds after spawn

        self._image = self._frames[0]
        self._rect = self._image.get_rect(center=self._pos)

        # floating drift
        self._float_timer = random.uniform(0, 10)

        self._died = False
        self._alive = True

    # -----------------------
    # UPDATE
    # -----------------------

    def update(self, dt, player_pos, knives):
        if self.spawn_freeze_timer > 0:
            self.spawn_freeze_timer -= dt
            return
        
        if self._alive:
            if self.is_hit(knives):
                self._frames = self._ded_frames
                self._frame_index = 0
                self._anim_timer = 0
                self._image = self._frames[0]
                self._alive = False

        if self._alive:
            # direction to player
            direction = pygame.Vector2(player_pos) - self._pos + (16,32)
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
            self._frame_index += 1
            if self._frame_index >= len(self._frames):
                if self._alive:
                    self._frame_index = (self._frame_index) % len(self._frames)
                    self._image = self._frames[self._frame_index]
                else:
                    self._died = True
            else:
                self._image = self._frames[self._frame_index]


    # -----------------------
    # DRAW
    # -----------------------

    def draw(self, screen):
        if not self._died:
            screen.blit(self._image, self._rect)

    # -----------------------
    # COLLISION (for later)
    # -----------------------

    def get_rect(self):
        return self._rect
    
    #------------------------------
    #    ENEMY HIT DETECTION
    #------------------------------
    def is_hit(self, knives):
        # accumulate the hitbox of every 3 knives to one
        for i in range(0, len(knives), 3):
            group = knives[i:i+3]
            rect_left = min(x.rect.left for x in group)
            rect_top = min(x.rect.top for x in group)
            rect_right = max(x.rect.right for x in group)
            rect_bottom = max(x.rect.bottom for x in group)

            if (rect_left <= self._rect.right and rect_right >= self._rect.left
                and rect_top <= self._rect.bottom and rect_bottom >= self._rect.top):
                #hit detected, gotta mark this batch of knives as ded
                for x in group:
                    x.alive = False
                return True

        return False
    
class Goblin:
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

        self._hit_range = GOB_HIT_RANGE
        self._sight_range = GOB_SIGHT_RADIUS
        self._sight_angle = GOB_SIGHT_ANGLE #in degree
        self._health = GOB_HEALTH
        self._died = False

        self._shake_timer = 0
        self._shake_strength = 4 
        self._shake_duration = 8
        self._hit = False

    #----------------------
    #    UPDATE     !!!! KNIFE DAMAGE MAGIC NUMBER !!!!!
    #----------------------
    def update(self, dt, player_rect, knives):
        """Update animation, position based on dt, attack if player_pos in range"""
        #hit check
        if self._health > 0:
            if self.is_hit(knives):
                self._hit = True
                self._health -= 20
                if self._health <= 0:
                    self._health = 0
                    self._frames = self._animations["die"]
                    self._frame_index = 0
                    self._image = self._frames[0]

        if self._health > 0:
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
            if self._frame_index >= len(self._frames):
                if self._health > 0:
                    self._frame_index %= len(self._frames)
                else:
                    self._frame_index
                    self._died = True

        if self._hit:
            self._shake_timer += dt
            if self._shake_timer >= 1 / self._shake_duration:
                self._shake_timer = 0
                self._hit = False

        if not self._died:
            self._image = self._frames[self._frame_index]

        self._rect.topleft = self._pos


    #----------------------
    #    DRAW !!!! TRIMMING USING MAGIC NUMBER !!!!!!
    #----------------------
    def draw(self, screen):
        if self._died:
            return
        offset_x = 0
        if self._hit:
            offset_x = int(math.sin(self._shake_timer * 20) * self._shake_strength)
        drawpos = (self._rect.topleft[0] + offset_x, self._rect.topleft[1])
        if self._dir == "left":
            if not self._attack:
                screen.blit(self._image, drawpos)
            else:
                #trimming
                drawpos = (drawpos[0] - 90, drawpos[1])
                screen.blit(self._image, drawpos)
        else:
            image = pygame.transform.flip(self._image, True, False)

            if self._attack:
                drawpos = (drawpos[0] - 20, drawpos[1])
                screen.blit(image, drawpos)
            else:
                screen.blit(image, drawpos)

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
    
    #------------------------------
    #    ENEMY HIT DETECTION
    #------------------------------
    def is_hit(self, knives):
        # accumulate the hitbox of every 3 knives to one
        for i in range(0, len(knives), 3):
            group = knives[i:i+3]
            rect_left = min(x.rect.left for x in group)
            rect_top = min(x.rect.top for x in group)
            rect_right = max(x.rect.right for x in group)
            rect_bottom = max(x.rect.bottom for x in group)

            if (rect_left <= self._rect.right and rect_right >= self._rect.left
                and rect_top <= self._rect.bottom and rect_bottom >= self._rect.top):
                #hit detected, gotta mark this batch of knives as ded
                for x in group:
                    x.alive = False
                return True

        return False

class Item:
    def __init__(self, loader, name, pos):
        self._pop = False
        self._shown = False
        self._pop_duration = 0.8
        self._pop_height = 40
        self._pop_timer = 0
        self._image = loader.get_animation(name)[0]
        self._rect = self._image.get_rect(center=pos)
        self._pos = pygame.Vector2(pos)

    def update(self, dt, player_pos):
        if self._pop:
            self._pop_timer += dt

            if self._pop_timer >= self._pop_duration:
                self._pop_timer = self._pop_duration
        
        if self._shown:
            distance = (player_pos - self._pos).length()
            if distance <= ITEM_COLLECT_RANGE:
                self._shown = False
                print("Item collected")

    def draw(self, screen):
        offset_y = 0
        if self._pop:
            progress = self._pop_timer / self._pop_duration
            offset_y = -self._pop_height * math.sin(progress * math.pi)

        draw_pos = (self._rect.centerx, self._rect.centery + offset_y)
        if self._shown:
            item_rect = self._image.get_rect(center=draw_pos)
            screen.blit(self._image, item_rect)

class Crystal:
    """
    crystal 4: hp
    crystal 0: mp
    """
    def __init__(self, loader, c_type=0):
        frames = loader.get_animation("crystal")
        self._death_frames = loader.get_animation("big_bomb_effect")
        self._alive = True
        self._image_index = 0
        self._frame_speed = 8
        self._frame_timer = 0
        self._shake_timer = 0
        self._shake_strength = 4 
        self._shake_duration = 8
        self._hit = False
        index = c_type % len(frames)
        self._frame = [frames[index]]
        
        self._health = 100

        self._image = self._frame[0]
        self._pos = pygame.Vector2(150, 150)
        self._rect = self._image.get_rect(center=self._pos)
        self._died = False

        if index == 0:
            self._item = Item(loader, "mp_item", self._pos)
        else:
            self._item = Item(loader, "hp_item", self._pos)

    def update(self, dt, player_pos, knives):
        if not self._died:
            if self._alive and self.is_hit(knives):
                self._hit = True
                self._shake_timer = 0
                self._health -= 20

            if self._health <= 0 and self._alive:
                self._alive = False
                self._frame_timer = 0
                self._image_index = 0
                self._image = self._death_frames[0]
                self._item._pop = True
                self._item._shown = True

            self._frame_timer += dt
            if self._frame_timer > 1 / self._frame_speed:
                self._frame_timer = 0
                self._image_index += 1
                if self._alive:
                    self._image_index = 0
                elif self._image_index < len(self._death_frames):
                    self._image = self._death_frames[self._image_index]
                else:
                    self._died = True

            if self._hit and self._alive:
                self._shake_timer += dt

                if self._shake_timer > 1 / self._shake_duration:
                    self._shake_timer = 0
                    self._hit = False
        self._item.update(dt, player_pos)

    def draw(self, screen):
        if not self._died:
            offset_x = 0
            if self._hit and self._alive:

                offset_x = int(math.sin(self._shake_timer * 20) * self._shake_strength)
                overlay = pygame.Surface(self._image.get_size(), pygame.SRCALPHA)
                overlay.fill((255, 255, 255, 120)) 
                self._image.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

            draw_pos = (self._rect.centerx + offset_x, self._rect.centery)
            rect = self._image.get_rect(center=draw_pos)
            screen.blit(self._image, rect)
        self._item.draw(screen)

    def is_hit(self, knives):
        # accumulate the hitbox of every 3 knives to one
        for i in range(0, len(knives), 3):
            group = knives[i:i+3]
            rect_left = min(x.rect.left for x in group)
            rect_top = min(x.rect.top for x in group)
            rect_right = max(x.rect.right for x in group)
            rect_bottom = max(x.rect.bottom for x in group)

            if (rect_left <= self._rect.right and rect_right >= self._rect.left
                and rect_top <= self._rect.bottom and rect_bottom >= self._rect.top):
                #hit detected, gotta mark this batch of knives as ded
                for x in group:
                    x.alive = False
                return True

        return False