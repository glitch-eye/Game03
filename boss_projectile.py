import pygame
from settings import *
from utils import *
import random
import math

class DashTrail:
    def __init__(self, pos, frames, facing_right):
        self.frames = frames
        self.frame_index = 0
        self.frame_timer = 0
        self.frame_speed = 0.05

        self.image = frames[0]
        self.pos = pygame.Vector2(pos)
        self.facing_right = facing_right

        self.rect = self.image.get_rect(center=self.pos)
        self.alive = True

    def update(self, dt, player=None):
        self.frame_timer += dt
        if self.frame_timer >= self.frame_speed:
            self.frame_timer = 0
            self.frame_index += 1
            if self.frame_index >= len(self.frames):
                self.alive = False
                return
            self.image = self.frames[self.frame_index]

        self.rect.center = self.pos

    def draw(self, screen, camera_x, camera_y):
        img = self.image
        if not self.facing_right:
            img = pygame.transform.flip(img, True, False)
        screen.blit(img, self.rect.move(int(-camera_x), int(-camera_y)))

class ZangaiTrail:
    def __init__(self, pos, frames):
        self.frames = frames
        self.frame_index = 0
        self.frame_timer = 0
        self.frame_speed = 0.04

        self.image = frames[0]
        self.pos = pygame.Vector2(pos)
        self.rect = self.image.get_rect(center=self.pos)

        self.life = 0.22  # short lived
        self.alive = True

    def update(self, dt, player=None):
        self.life -= dt
        if self.life <= 0:
            self.alive = False
            return

        self.frame_timer += dt
        if self.frame_timer >= self.frame_speed:
            self.frame_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]

    def draw(self, screen, camera_x, camera_y):
        img = self.image.copy()
        img.set_alpha(int(255 * (self.life / 0.22)))
        rect = img.get_rect(center=self.pos)
        screen.blit(img, rect.move(-camera_x, -camera_y))

class SmokeColumn:
    def __init__(self, pos, frames):
        self.frames = [tint_surface_red(f) for f in frames]
        self.frame_index = 0
        self.frame_timer = 0
        self.frame_speed = 0.11

        self.base_pos = pygame.Vector2(pos)

        # how tall the column is (number of stacked sprites)
        self.layers = random.randint(4, 4)
        frame = frames[0]
        width = frame.get_width()
        h = frame.get_height()

        overlap = h * 0.45
        height = int(h + (self.layers - 1) * overlap)
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.midbottom = self.base_pos

        self.alive = True
        self.life_timer = 0
        self.life_duration = 2.0
        self.hitbox = None

    def update(self, dt, player):
        self.rect.y -= 20 * dt

        self.life_timer += dt
        if self.life_timer >= self.life_duration:
            self.alive = False
            return

        # animate
        self.frame_timer += dt
        if self.frame_timer >= self.frame_speed:
            self.frame_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)

        self.hitbox = self.rect.copy()

        if self.hitbox and self.hitbox.colliderect(player.get_hurtbox_rect()):
            player.time_energy -= 50 * dt
            player._inSmoke = True

    def timestop_update(self, dt, player):
        self.hitbox = self.rect.copy()

        if self.hitbox and self.hitbox.colliderect(player.get_hurtbox_rect()):
            player.time_energy -= 50 * dt
            player._inSmoke = True
    
    def draw(self, screen, camera_x, camera_y):
        frame = self.frames[self.frame_index]
        w = frame.get_width()
        h = frame.get_height()

        base_x = self.rect.centerx
        base_y = self.rect.bottom

        overlap = h * 0.45  # strong blending

        for i in range(self.layers):
            # Fade higher layers slightly
            alpha = int(255 * (1 - i * 0.18))
            frame.set_alpha(alpha)

            x = base_x - w // 2
            y = base_y - h - i * overlap

            screen.blit(frame, (x - camera_x, y - camera_y))
        
        if self.hitbox:
            pygame.draw.rect(
            screen, (0,0,255),
            self.hitbox.move(int(-camera_x), int(-camera_y)),
            2
            )

class TimeShotProjectile:
    def __init__(self, pos, facing_right, loader):
        self.facing_right = facing_right

        self.smoke = loader.get_animation("smoke")

        self.anim = loader.get_animation("marisa_timeshot")
        self.frame_index = 0
        self.frame_timer = 0
        self.frame_speed = 0.08

        self.image = self.anim[0]

        offset = -40 if facing_right else 40
        self.pos = pygame.Vector2(pos.x + offset, pos.y + 40)

        self.fall_speed = 350

        self.rect = self.image.get_rect(center=self.pos)
        self.hitbox = None

        # STANDARDIZED LIFETIME
        self.alive = True

    def update(self, dt, player, particle_list):
        # Fall
        self.pos.y += self.fall_speed * dt

        # Remove when offscreen
        ground_y = BOSS_ARENA.bottom
        if self.pos.y >= ground_y + 50:
            self.alive = False

            explosion_pos = pygame.Vector2(self.rect.midbottom)

            particle_list.append(
                SmokeColumn(explosion_pos, self.smoke)
            )
            return

        # Animate
        self.frame_timer += dt
        if self.frame_timer >= self.frame_speed:
            self.frame_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.anim)
            self.image = self.anim[self.frame_index]

        self.rect.center = self.pos

    def draw(self, screen, camera_x, camera_y):
        img = self.image
        if not self.facing_right:
            img = pygame.transform.flip(img, True, False)
        screen.blit(img, self.rect.move(int(-camera_x), int(-camera_y)))


class UndershotProjectile:
    def __init__(self, x, y, proj_frames, laser_frames, zangai_frames):
        self.proj_frames = proj_frames
        self.laser_frames = laser_frames
        self.frames = proj_frames

        self.frame_index = 0
        self.frame_timer = 0
        self.frame_speed = 0.08

        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.hitbox = None

        self.vel = pygame.Vector2(0, 480)

        self.state = "projectile"
        self.alive = True

        self.zangai_frames = zangai_frames
        self.zangai_timer = 0
        self.zangai_duration = 0.18
        self.zangai_interval = 0.02

        # TRUE physics ground
        self.ground_y = BOSS_ARENA.bottom + 70

    def update(self, dt, player=None, particle_list=None):

        # -----------------------
        # PROJECTILE FALL
        # -----------------------
        if self.state == "projectile":
            self.rect.centery += self.vel.y * dt

            # Wait until it ACTUALLY touches ground
            if self.rect.bottom >= self.ground_y:
                self.rect.bottom = self.ground_y
                particle_list.append(
                        ZangaiTrail(
                            (self.rect.centerx, self.ground_y),
                            self.zangai_frames
                        )
                    )
                self._become_laser()

        self.zangai_timer += dt

        if self.zangai_timer <= self.zangai_duration:
            self.zangai_interval -= dt
            if self.zangai_interval <= 0:
                self.zangai_interval = 0.02
                particle_list.append(
                    ZangaiTrail(self.rect.center, self.zangai_frames)
                )

        # -----------------------
        # ANIMATION
        # -----------------------
        self.frame_timer += dt
        if self.frame_timer >= self.frame_speed:
            self.frame_timer = 0
            self.frame_index += 1

            if self.frame_index >= len(self.frames):
                if self.state == "laser":
                    self.alive = False
                    return
                else:
                    self.frame_index = 0

            self.image = self.frames[self.frame_index]
                
        if self.state == "laser":
            self.hitbox = get_tight_hitbox(self.image, self.rect, "midbottom")
            if self.hitbox.colliderect(player.get_hurtbox_rect()):
                player.apply_damage(10, self.hitbox.centerx)
        else:
            self.hitbox = get_tight_hitbox(self.image, self.rect, "center")
            if self.hitbox.colliderect(player.get_hurtbox_rect()):
                player.apply_damage(20, self.hitbox.centerx)


    def _become_laser(self):
        self.state = "laser"
        self.frames = self.laser_frames
        self.frame_index = 0
        self.frame_timer = 0
        self.vel = pygame.Vector2(0, 0)

        # Scale every laser frame to screen height
        scaled_frames = []
        for frame in self.frames:
            w = frame.get_width()
            scaled = pygame.transform.scale(frame, (w, SCREEN_HEIGHT))
            scaled_frames.append(scaled)

        self.frames = scaled_frames
        self.image = self.frames[0]

        # Anchor to bottom center of screen
        self.rect = self.image.get_rect(
            midbottom=(self.rect.centerx, BOSS_ARENA.bottom + 70)
        )
        self.hitbox = get_tight_hitbox(self.image, self.rect, "midbottom")

    def timestop_update(self, dt, player):
        if self.state == "laser":
            self.hitbox = get_tight_hitbox(self.image, self.rect, "midbottom")
            if self.hitbox.colliderect(player.get_hurtbox_rect()):
                player.apply_damage(20, self.hitbox.centerx)
        else:
            self.hitbox = get_tight_hitbox(self.image, self.rect, "center")
            if self.hitbox.colliderect(player.get_hurtbox_rect()):
                player.apply_damage(10, self.hitbox.centerx)

    def draw(self, screen, camera_x, camera_y):
        screen.blit(self.image, self.rect.move(int(-camera_x), int(-camera_y)))
        pygame.draw.rect(screen, (0,0,255),
                 self.hitbox.move(int(-camera_x), int(-camera_y)), 2)

class ShotProjectile:
    def __init__(self, start, first_target, frames, facing_right, trail_big, trail_small, zangai_frames):
        self.frames = frames
        self.frame_index = 0
        self.frame_timer = 0
        self.frame_speed = 0.08

        self.image = self.frames[0]
        self.pos = pygame.Vector2(start)
        self.rect = self.image.get_rect(center=self.pos)
        self.hitbox = None

        # Direction
        self.facing_right = facing_right

        # Trail visuals
        self.trail_big = trail_big
        self.trail_small = trail_small
        self.trail_timer = 0

        self.zangai_frames = zangai_frames
        self.zangai_timer = 0
        self.zangai_duration = 0.18
        self.zangai_interval = 0.02

        # --- Homing phases ---
        self.phase = 1
        self.phase_timer = 0

        self.target = pygame.Vector2(first_target)

        self.speed_phase1 = 200
        self.speed_phase2 = 500

        self.fly_time = 0
        self.max_fly_time = 10.0

        direction = (self.target - self.pos)
        if direction.length() != 0:
            direction = direction.normalize()
        self.velocity = direction * self.speed_phase1

        self.alive = True

    def update(self, dt, player, particle_list):
        self.phase_timer += dt

        # -----------------------
        # PHASE 1 — Slow tracking
        # -----------------------
        if self.phase == 1:
            self.pos += self.velocity * dt

            if self.phase_timer >= 0.3:
                self.phase = 2
                self.phase_timer = 0
                self.velocity = pygame.Vector2(0, 0)
                self.target = pygame.Vector2(player._rect.center)

        self.zangai_timer += dt

        if self.zangai_timer <= self.zangai_duration:
            self.zangai_interval -= dt
            if self.zangai_interval <= 0:
                self.zangai_interval = 0.02
                particle_list.append(
                    ZangaiTrail(self.pos, self.zangai_frames)
                )

        # -----------------------
        # PHASE 2 — Aggressive dash
        # -----------------------
        elif self.phase == 2:
            to_target = self.target - self.pos
            distance = to_target.length()

            if distance > 8:
                direction = to_target.normalize()
                self.velocity = direction * self.speed_phase2
                self.pos += self.velocity * dt
            else:
                self.phase = 3
                self.fly_time = 0

                # keep strong forward motion
                if self.velocity.length() != 0:
                    self.velocity = self.velocity.normalize() * self.speed_phase2

        # -----------------------
        # PHASE 3 — Fly-through
        # -----------------------
        elif self.phase == 3:
            self.fly_time += dt
            self.pos += self.velocity * dt

            # Hit ground
            ground_y = BOSS_ARENA.bottom
            if self.pos.y >= ground_y + 50:
                self.alive = False
                particle_list.append(
                    ZangaiTrail(self.pos, self.zangai_frames)
                )
                return

            # Timeout
            if self.fly_time >= self.max_fly_time:
                self.alive = False
                particle_list.append(
                    ZangaiTrail(self.pos, self.zangai_frames)
                )
                return

        # -----------------------
        # DUAL TRAIL EFFECTS
        # -----------------------
        self.trail_timer += dt

        # SMALL trail — frequent
        if self.trail_timer >= 0.035:
            x_jitter = random.randint(-10, 10)
            y_jitter = random.randint(-6, 14)
            back_offset = -12 if self.facing_right else 12

            spawn_pos = pygame.Vector2(
                self.pos.x + back_offset + x_jitter,
                self.pos.y + y_jitter
            )

            particle_list.append(
                DashTrail(spawn_pos, self.trail_small, self.facing_right)
            )

        # BIG trail — less frequent
        if self.trail_timer >= 0.09:
            self.trail_timer = 0  # reset only after big trail

            x_jitter = random.randint(-6, 6)
            y_jitter = random.randint(-4, 10)
            back_offset = -10 if self.facing_right else 10

            spawn_pos = pygame.Vector2(
                self.pos.x + back_offset + x_jitter,
                self.pos.y + y_jitter
            )

            particle_list.append(
                DashTrail(spawn_pos, self.trail_big, self.facing_right)
            )

        self.rect.center = self.pos

        # -----------------------
        # ANIMATION
        # -----------------------
        self.frame_timer += dt
        if self.frame_timer >= self.frame_speed:
            self.frame_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]

        self.hitbox = get_tight_hitbox(self.image, self.rect, "center")
        if self.hitbox.colliderect(player.get_hurtbox_rect()):
            player.apply_damage(15, self.hitbox.centerx)
            self.alive = False

    def timestop_update(self, dt, player):
        if self.hitbox.colliderect(player.get_hurtbox_rect()):
            player.apply_damage(15, self.hitbox.centerx)
            self.alive = False

    def draw(self, screen, camera_x, camera_y):
        screen.blit(self.image, self.rect.move(int(-camera_x), int(-camera_y)))
        pygame.draw.rect(screen, (0,0,255),
                 self.hitbox.move(int(-camera_x), int(-camera_y)), 2)
        
class MasterSparkProjectile:
    def __init__(self, boss, anims, ground_y):
        self.boss = boss
        self.anims = anims
        self.ground_y = ground_y
        self.alive = True

        self.frame = 0
        self.timer = 0
        self.frame_speed = 0.05

        # convenience
        self.anim_a = anims["a"]
        self.anim_b = anims["b"]
        self.anim_c = anims["c"]
        self.anim_d = anims["d"]

        self.hitboxes = []
        self.segment_size = 102

    def update(self, dt, player, particle_list):
        # Die when boss stops firing
        if self.boss.attack_state != "master_spark":
            self.alive = False
            return
        
        for hb in self.hitboxes:
            if hb.colliderect(player.get_hurtbox_rect()):
                player.apply_damage(40, self.boss.rect.centerx)
                break
        
        self.timer += dt
        if self.timer >= self.frame_speed:
            self.timer = 0
            self.frame += 1

        # loop animation
        self.frame %= len(self.anim_a)

    def draw(self, screen, camera_x, camera_y):
        boss = self.boss

        # --- ORIGIN POSITION ---
        boss_mid_x = boss.rect.centerx
        start_y = boss.rect.centery + 20  # slightly below center

        # total beam height
        total_height = self.ground_y - start_y
        segment_count = max(1, total_height // self.segment_size)

        # ======================
        # A — ORIGIN
        # ======================
        frame_a = self.anim_a[self.frame % len(self.anim_a)]
        rect_a = frame_a.get_rect(midtop=(boss_mid_x, start_y))
        screen.blit(frame_a, rect_a.move(-camera_x, -camera_y))

        # --- MUZZLE HITBOX ---
        bbox = frame_a.get_bounding_rect()
        hitbox = pygame.Rect(
            rect_a.left + bbox.left,
            rect_a.top  + bbox.top,
            bbox.width,
            bbox.height
        )
        self.hitboxes.append(hitbox)

        # ======================
        # B + C — BODY (CROP ONLY OVERFLOW)
        # ======================
        current_y = start_y + frame_a.get_height() - 24 
        max_bottom = self.ground_y

        i = 0
        while True:
            # choose alternating segment
            if i % 2 == 0:
                frame = self.anim_b[self.frame % len(self.anim_b)]
            else:
                frame = self.anim_c[self.frame % len(self.anim_c)]

            seg_top = current_y
            seg_bottom = current_y + frame.get_height()

            # If fully visible → draw normally
            if seg_bottom <= max_bottom:
                rect = frame.get_rect(midtop=(boss_mid_x, seg_top))
                screen.blit(frame, rect.move(-camera_x, -camera_y))

                bbox = frame.get_bounding_rect()
                hitbox = pygame.Rect(
                    rect.left + bbox.left,
                    rect.top  + bbox.top,
                    bbox.width,
                    bbox.height
                )
                self.hitboxes.append(hitbox)

            else:
                # Partially visible → crop only overflow
                visible_height = max_bottom - seg_top
                if visible_height > 0:
                    cropped = frame.subsurface((0, 0, frame.get_width(), visible_height))
                    rect = cropped.get_rect(midtop=(boss_mid_x, seg_top))
                    screen.blit(cropped, rect.move(-camera_x, -camera_y))

                    bbox = cropped.get_bounding_rect()
                    hitbox = pygame.Rect(
                        rect.left + bbox.left,
                        rect.top  + bbox.top,
                        bbox.width,
                        bbox.height
                    )
                    self.hitboxes.append(hitbox)
                break

            current_y += frame.get_height()
            i += 1

        # ======================
        # D — IMPACT
        # ======================
        ground_y = self.ground_y

        frame_d = self.anim_d[self.frame % len(self.anim_d)]
        rect_d = frame_d.get_rect(midbottom=(boss_mid_x, ground_y))
        screen.blit(frame_d, rect_d.move(-camera_x, -camera_y))

        for hb in self.hitboxes:
            pygame.draw.rect(screen, (0,0,255), hb.move(-camera_x,-camera_y), 2)

    def timestop_update(self, dt, player):
                
        for hb in self.hitboxes:
            if hb.colliderect(player.get_hurtbox_rect()):
                player.apply_damage(40, self.boss.rect.centerx)
                break