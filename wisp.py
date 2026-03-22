import pygame
import math
import random
from pygame.locals import *
from settings import *
import threading

thread_knife_lock = threading.Lock() # lock mechanism for shared mem

def update_entity_pos(camera_pos, entity_rect):
    """
    Scale entity position from world coordinates to camera coordinates.
    Updates entity._pos so it can be drawn correctly on screen. 
    returning pos will be topleft
    """
    # Tính vị trí camera trong thế giới (world coordinates)
    camera_x = min(max(camera_pos.x - SCREEN_WIDTH // 2, 0), MAP_NUMS[0]*TILE_SIZE - SCREEN_WIDTH)
    camera_y = min(max(camera_pos.y - SCREEN_HEIGHT // 2, 0), MAP_NUMS[1]*TILE_SIZE - SCREEN_HEIGHT)

    cur_pos = entity_rect.topleft

    # check if it appears in camera (using rect overlapping check)
    overlap = False
    draw_pos = None
    if (entity_rect.left <= camera_x + SCREEN_WIDTH and entity_rect.right >= camera_x
        and entity_rect.top <= camera_y + SCREEN_HEIGHT and entity_rect.bottom >= camera_y):
        overlap = True
        # calculate position relative to camera
        draw_pos = (cur_pos[0] - camera_x, cur_pos[1] - camera_y)

    return overlap, draw_pos
class Wisp:

    def __init__(self, data, loader):

        # position
        self._pos = pygame.Vector2(data[0], data[1])
        self._speed = 50

        # animation
        self._normal_frames = loader.get_animation("wisp")
        self._frames = self._normal_frames
        self._ded_frames = loader.get_animation("big_bomb_effect")
        self._frame_index = 0
        self._anim_speed = 8
        self._anim_timer = 0

        self._image = self._frames[0]
        self._rect = self._image.get_rect(center=self._pos)

        # floating drift
        self._float_timer = random.uniform(0, 10)

        self._died = False
        self._alive = True
        self._radius = SCREEN_WIDTH * GAME_SCALE

    # -----------------------
    # UPDATE
    # -----------------------

    def update(self, dt, player, knives):
        
        if self._alive:
            if self.is_hit(knives):
                self._frames = self._ded_frames
                self._frame_index = 0
                self._anim_timer = 0
                self._image = self._frames[0]
                self._alive = False

        if self._alive:
            # direction to player
            direction = pygame.Vector2(player._pos) - self._pos + (16,32)
            distance = direction.length()

            if distance > 0:
                direction = direction.normalize()

            if distance > self._radius:
                # out of range
                return
            
            #check attacking
            if self.did_hit(player):
                player.apply_damage(WISP_DAMAGE, self._pos.x)

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

    def draw(self, screen, camera_pos):
        is_draw, draw_pos = update_entity_pos(camera_pos, self._rect)
        if not self._died and is_draw:
            rect = self._image.get_rect(center=draw_pos)
            screen.blit(self._image, rect)

    # -----------------------
    # COLLISION (for later)
    # -----------------------

    def get_rect(self):
        return self._rect
    
    #------------------------------
    #    ENEMY ATTACK
    #------------------------------
    def did_hit(self, player):
        player_hurtbox = pygame.Rect(0, 0, PLAYER_HURTBOX_WIDTH, PLAYER_HURTBOX_HEIGHT)
        player_hurtbox.midbottom = player._rect.midbottom
        if player.current_anim == "crouch" or player.current_anim == "slide":
            player_hurtbox.height //= 2
        if self._rect.colliderect(player_hurtbox):
            return True
        return False
    
    #------------------------------
    #    ENEMY HIT DETECTION
    #------------------------------
    def is_hit(self, knives):
        # accumulate the hitbox of every 3 knives to one
        with thread_knife_lock:
            for i in range(0, len(knives), 3):
                if not knives[i].alive:
                    continue
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
    def __init__(self, loader, data):
        self._animations = {
            "idle": loader.get_animation("goblin_idle"),
            "attack": loader.get_animation("goblin_attack"),
            "run": loader.get_animation("goblin_run"),
            "die": loader.get_animation("big_bomb_effect")
        }

        # position
        self._pos = pygame.Vector2(data[0], data[2])
        self._vel = pygame.Vector2(0, 0)

        # animation
        self._frames = self._animations["run"]
        self._frame_index = 0
        self._anim_speed = 8
        self._anim_timer = 0
        self._attack = False
        self._dir = "right"

        self._image = self._frames[0]
        self._rect = pygame.Rect(0, 0, GOB_WIDTH, GOB_HEIGHT)
        self._rect.topleft = self._pos

        # seeing + hitting logic
        self._hit_range = GOB_HIT_RANGE
        self._hit_height = GOB_HIT_HEIGHT
        self._sight_range = GOB_SIGHT_RADIUS
        self._sight_angle = GOB_SIGHT_ANGLE #in degree
        self._health = GOB_HEALTH
        self._died = False
        self._show_hitbox = True
        self.hitbox = pygame.Rect(0, 0, 0, self._hit_height)

        # take damage logic
        self._shake_timer = 0
        self._shake_strength = 4 
        self._shake_duration = 8
        self._hit = False

        #moving range
        self.start = min(data[0], data[1])
        self.end = max(data[0], data[1])
        if self.start == self._pos.x:
            self._dir = "right"
        else:
            self._dir = "left"

    #----------------------
    #    UPDATE     !!!! KNIFE DAMAGE MAGIC NUMBER !!!!!
    #----------------------
    def update(self, dt, player, knives):
        """Update animation, position based on dt, attack if player_pos in range"""
        player_rect = player._rect
        # check hit player if attacking (hit box increase from frame 15 - 21 and then reduce)
        if self._attack:
            if self.did_hit(player):
                player.apply_damage(GOB_DAMAGE, self._pos.x)

        #hit check
        if self._health > 0:
            if self.is_hit(knives):
                self._hit = True
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
                        # done attack and no more in range then follow
                        self._vel.x = (direction.x / abs(direction.x)) * 30
                        self._dir = "right" if self._vel.x > 0 else "left"
                        self._attack = False
                        self._vel.x = 30 if self._dir == "right" else -30
                        self._frame_index = 0
                        self._frames = self._animations["run"]
                        self._anim_timer = 0
                        self._anim_speed = 8
                        self._image = self._frames[0]
                    elif not self._attack:
                        # move
                        self._vel.x = (direction.x / abs(direction.x)) * 30
                        self._vel.x = 30 if self._dir == "right" else -30
                        if self._frame_index != 0: # continue the movement if not idling
                            self._frame_index = 0
                            self._frames = self._animations["run"]
                            self._anim_timer = 0
                            self._anim_speed = 8
                            self._image = self._frames[0]
            else:
                # no seeing then return to normal once the attack animation is done
                if self._attack and self._frame_index == len(self._frames) - 1:
                    self.hitbox.width = 0
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
    #    DRAW FUNCTION
    #----------------------
    def draw(self, screen, camera_pos):
        is_draw, draw_pos = update_entity_pos(camera_pos, self._rect)
        if self._died or not is_draw:
            return
        offset_x = 0
        _, hitbox_draw = update_entity_pos(camera_pos, self.hitbox)
        draw_image = self._image
        if self._hit:
            offset_x = int(math.sin(self._shake_timer * 20) * self._shake_strength)
            draw_image = self.apply_flash()
        drawpos = (draw_pos[0] + offset_x, draw_pos[1])
        if self._show_hitbox and self._attack and hitbox_draw is not None:
            screen_hitbox = self.hitbox.copy()
            screen_hitbox.topleft = hitbox_draw
            pygame.draw.rect(screen, rect=screen_hitbox, color=COLOR_GREEN)
        if self._dir == "left":
            if not self._attack:
                screen.blit(draw_image, drawpos)
            else:
                #trimming
                drawpos = (drawpos[0] - GOB_TRIM_ATTACK_LEFT, drawpos[1])
                screen.blit(draw_image, drawpos)
        else:
            image = pygame.transform.flip(draw_image, True, False)

            if self._attack:
                drawpos = (drawpos[0] - GOB_TRIM_ATTACK_RIGHT, drawpos[1])
                screen.blit(image, drawpos)
            else:
                screen.blit(image, drawpos)

    #----------------------
    #    COLLISION
    #----------------------
    def check_collision(self):
        if self._pos.x >= self.end:
            self._pos.x = self.end
            self._vel.x = -self._vel.x
            self._dir = "left"
        elif self._pos.x <= self.start:
            self._pos.x = self.start
            self._vel.x = -self._vel.x
            self._dir = "right"

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
    #    ENEMY HIT PLAYER
    #------------------------------
    def did_hit(self, player):
        player_hurtbox = pygame.Rect(0, 0, PLAYER_HURTBOX_WIDTH, PLAYER_HURTBOX_HEIGHT)
        player_hurtbox.midbottom = player._rect.midbottom
        if player.current_anim == "crouch" or player.current_anim == "slide":
            player_hurtbox.height //= 2
        if 15 <= self._frame_index <= 21:
            # hitbox size increasing horizontaly
            progress = (self._frame_index - 15) / (21 - 15)
            hitbox_length = self._hit_range * progress
            hitbox_left = self._rect.centerx if self._dir == "right" else self._rect.centerx- hitbox_length
            hitbox_top = self._rect.centery - self._hit_height // 2
            self.hitbox.topleft = (hitbox_left, hitbox_top)
            self.hitbox.width = hitbox_length
            
            if self.hitbox.colliderect(player_hurtbox):
                return True
        elif 22 <= self._frame_index <= 25:
            # hibox size decreasing
            progress = (self._frame_index - 25) / (22 - 25)
            hitbox_length = self._hit_range * progress
            hitbox_left = self._rect.centerx if self._dir == "right" else self._rect.centerx - hitbox_length
            hitbox_top = self._rect.centery - self._hit_height // 2
            self.hitbox.topleft = (hitbox_left, hitbox_top)
            self.hitbox.width = hitbox_length
            
            if self.hitbox.colliderect(player_hurtbox):
                return True
        else:
            return False
        
    #--------------------------------
    #    HURT FLASHING EFFECT HELPER
    #--------------------------------
    def apply_flash(self, color=(255, 0, 0), alpha=120):
        # Copy the sprite
        flash_img = self._image.copy()

        # Create a surface filled with the flash color
        tint = pygame.Surface(self._image.get_size(), pygame.SRCALPHA)
        tint.fill((*color, alpha))  # RGBA

        # Blend onto the copy
        flash_img.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        return flash_img
    
    #------------------------------
    #    ENEMY HIT DETECTION
    #------------------------------
    def is_hit(self, knives):
        # accumulate the hitbox of every 3 knives to one
        ret = False
        with thread_knife_lock:
            for i in range(0, len(knives), 3):
                if not knives[i].alive:
                    continue
                if self._health <= 0:
                    break
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
                    self._health -= 1
                    ret = True

        return ret

class Item:
    def __init__(self, loader, name, pos):
        self._pop = False
        self._shown = False
        self._pop_duration = 0.8
        self._pop_height = 40
        self._pop_timer = 0
        self._image = loader.get_image(name)
        self._rect = self._image.get_rect(midbottom=pos)
        self._pos = pygame.Vector2(pos)
        self.name = name

    def update(self, dt, player):
        if self._pop:
            self._pop_timer += dt

            if self._pop_timer >= self._pop_duration:
                self._pop_timer = self._pop_duration
        
        if self._shown:
            distance = (player._pos - self._rect.midtop).length()
            if distance <= ITEM_COLLECT_RANGE:
                self._shown = False
                if self.name == "hp_item":
                    player.hp = player.hp_max
                else:
                    player.mp = player.mp_max

    def draw(self, screen, camera_pos):
        is_draw, draw_pos = update_entity_pos(camera_pos, self._rect)
        if is_draw:
            offset_y = 0
            if self._pop:
                progress = self._pop_timer / self._pop_duration
                offset_y = -self._pop_height * math.sin(progress * math.pi)

            draw_pos = (draw_pos[0], draw_pos[1] + offset_y)
            if self._shown:
                item_rect = self._image.get_rect(topleft=draw_pos)
                screen.blit(self._image, item_rect)

class Crystal:
    """
    crystal 4: hp
    crystal 0: mp
    """
    def __init__(self, loader, data):
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
        index = data[2] % len(frames)
        self._frame = [frames[index]]
        
        self._health = 3

        self._image = self._frame[0]
        self._pos = pygame.Vector2(data[0], data[1])
        self._rect = self._image.get_rect(midbottom=self._pos)
        self._died = False

        match index:
            case 0:
                self._item = Item(loader, "mp_item", self._pos)
            case 1:
                self._item = Item(loader, "hp_item", self._pos)
            case _:
                item_type = random.choice(["hp_item", "mp_item"])
                self._item = Item(loader, item_type, self._pos)

    def update(self, dt, player, knives):
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
        self._item.update(dt, player)

    # helper function to apply flash effect when hit
    def apply_flash(self, color=(255, 0, 0), alpha=120):
        # Copy the sprite
        flash_img = self._image.copy()

        # Create a surface filled with the flash color
        tint = pygame.Surface(self._image.get_size(), pygame.SRCALPHA)
        tint.fill((*color, alpha))  # RGBA

        # Blend onto the copy
        flash_img.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        return flash_img

    def draw(self, screen, camera_pos):
        is_draw, draw_pos = update_entity_pos(camera_pos, self._rect)
        if is_draw:
            if not self._died:
                offset_x = 0
                draw_image = self._image
                if self._hit and self._alive:
                    offset_x = int(math.sin(self._shake_timer * 20) * self._shake_strength)
                    draw_image = self.apply_flash()

                draw_pos = (draw_pos[0] + offset_x, draw_pos[1])
                if self._alive:
                    rect = draw_image.get_rect(topleft=draw_pos)
                else:
                    rect = draw_image.get_rect(midtop=draw_pos)
                screen.blit(draw_image, rect)
            self._item.draw(screen, camera_pos)

    def is_hit(self, knives):
        # accumulate the hitbox of every 3 knives to one
        ret = False
        with thread_knife_lock:
            for i in range(0, len(knives), 3):
                if not knives[i].alive:
                    continue
                if self._health <= 0:
                    break
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
                    self._health -= 1
                    ret = True

        return ret