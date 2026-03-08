"""
    Character build
"""
import pygame
from pygame.locals import *
from settings import *

class Character:
    def __init__(self, loader):
        #keyboard control
        self._keys = {
            "jump": K_SPACE,
            "left": K_a,
            "right": K_d,
            "up": K_w,
            "down": K_s,
            "dash": K_q
        }

        #stats
        self._pos = PLAYER_INIT_POS
        self._hurtbox = pygame.Vector2(PLAYER_HURTBOX_WIDTH, PLAYER_HURTBOX_HEIGHT)
        self._vel = pygame.Vector2(0, 0)
        self._moveSpeed = PLAYER_SPEED
        self._jumpforce = PLAYER_JUMPSTRENGTH
        self._doublejumpForce = PLAYER_DOUBLEJUMPSTRENGTH
        self._jumpPressedLastFrame = False
        self._jumpholdDuration = PLAYER_JUMPHOLDTIME
        self._doublejumpholdDuration = PLAYER_DOUBLEJUMPHOLDTIME

        self._jumpBufferTime = 0.12     # seconds allowed to buffer
        self._jumpBufferTimer = 0

        # state
        self._jumpTimes = 0
        self._grounded = True
        self._curJumpHold = 0.0
        self._jumpHolding = False
        self._jumpMaxHold = self._jumpholdDuration
        self._wasMoving = False
        self._crouching = False

        # sprite
        self.animations = {
            "idle": loader.get_animation("player_idle"),
            "jump": loader.get_animation("player_jump"),
            "fall": loader.get_animation("player_fall"),
            "double_jump": loader.get_animation("player_2ndjump"),
            "glide": loader.get_animation("player_gliding"),
            "run": loader.get_animation("player_run"),
            "run_start": loader.get_animation("player_run_start"),
            "run_stop": loader.get_animation("player_run_stop"),
            "run_back": loader.get_animation("player_run_back"),
            "crouch": loader.get_animation("player_down")
        }

        self.current_anim = "idle"
        self.frames = self.animations[self.current_anim]

        self.frame_index = 0
        self.frame_timer = 0
        self.frame_speed = 0.07

        self._image = self.frames[0]

        # collision box
        self._rect = pygame.Rect(0, 0, PLAYER_COLLISION_WIDTH, PLAYER_COLLISION_HEIGHT)
        self._rect.midtop = (int(self._pos.x), int(self._pos.y))

        # facing
        self._facingRight = True

        # gliding
        self._gliding = False
        self._glideGravity = gGRAVITY * 0.25
        self._maxGlideFallSpeed = 120
        self._jumpHeld = False          

    # -----------------------
    # INPUT
    # -----------------------

    def handleInput(self, keys):

        # crouch input (only allowed on ground)
        self._crouching = keys[K_s] and self._grounded

        # horizontal input
        self._inputDir = (keys[K_d] - keys[K_a])

        # prevent movement while crouching
        if self._crouching:
            self._vel.x = 0
        else:
            self._vel.x = self._inputDir * self._moveSpeed

        jumpPressed = keys[K_SPACE]
        jumpJustPressed = jumpPressed and not self._jumpPressedLastFrame
        self._jumpHeld = jumpPressed

        # store jump request
        if jumpJustPressed:
            self._jumpBufferTimer = self._jumpBufferTime

        # release jump
        if not jumpPressed:
            self._jumpHolding = False
            self._curJumpHold = 0

        self._jumpPressedLastFrame = jumpPressed

    # -----------------------
    # ANIMATION SWITCHING
    # -----------------------

    def set_animation(self, name):

        if self.current_anim != name:

            self.current_anim = name
            self.frames = self.animations[name]

            self.frame_index = 0
            self.frame_timer = 0

            # immediately update the sprite
            self._image = self.frames[self.frame_index]

    # -----------------------
    # UPDATE
    # -----------------------

    def update(self, dt):
        was_grounded = self._grounded

        # update jump buffer timer
        if self._jumpBufferTimer > 0:
            self._jumpBufferTimer -= dt

        # execute buffered jump if possible
        if self._jumpBufferTimer > 0 and not self._crouching: # Remove later when couch+jump allows sliding

        self._dashCD = 0.0
        self._dashCDStat = PLAYER_DASHCOOLDOWN
        self._dash = False
        self._dashSpeed = PLAYER_DASHSPEED

        #placeholder for char image
        self._image = pygame.Surface((PLAYER_HURTBOX_WIDTH, PLAYER_HURTBOX_HEIGHT))
        self._image.fill(COLOR_GREEN)
    
    def handleInput(self, keys):
        if keys[self._keys["left"]]:
            self._vel.x = -self._moveSpeed
        if keys[self._keys["right"]]:
            self._vel.x = self._moveSpeed
        if keys[self._keys["jump"]]:
            if self._grounded:

                self._vel.y = -self._jumpforce
                self._jumpMaxHold = self._jumpholdDuration

                self._jumpHolding = True
                self._grounded = False
                self._jumpTimes = 1

                self._jumpBufferTimer = 0


            elif self._jumpTimes < 2:

                self._vel.y = -self._doublejumpForce
                self._jumpMaxHold = self._doublejumpholdDuration

                self._curJumpHold = 0
                self._jumpTimes = 2
                self._jumpHolding = True

                self._jumpBufferTimer = 0

        self.frame_timer += dt

        # glide detection
        self._gliding = False

        if not self._grounded and self._vel.y > 0 and self._jumpHeld:
            self._gliding = True

        # gravity
        if self._gliding:
            self._vel.y += self._glideGravity * dt

            # optional fall speed cap
            if self._vel.y > self._maxGlideFallSpeed:
                self._vel.y = self._maxGlideFallSpeed
        else:
            self._vel.y += gGRAVITY * dt
            else:
                if not self._jumpHolding:
                    if (self._jumpTimes != 2):
                        self._vel.y = -self._doublejumpForce
                        self._jumpMaxHold = self._doublejumpholdDuration
                        self._curJumpHold = 0.0
                        self._jumpTimes = 2
                        self._jumpHolding = True
        if keys[self._keys["dash"]]:
            if self._dashCD <= 0.0:
                self._dashCD = self._dashCDStat
                self._dash = True

        #key release
        if ((not keys[self._keys["left"]] and self._vel.x == -self._moveSpeed) 
            or (not keys[self._keys["right"]] and self._vel.x == self._moveSpeed)): 
            self._vel.x = 0

        if self._curJumpHold >= self._jumpMaxHold:
            self._vel.y = self._gravity
        if not keys[self._keys["jump"]]:
            self._jumpHolding = False
            self._curJumpHold = 0.0
            self._vel.y = self._gravity

    def update(self, deltaTime):
        if self._dash:
            self._pos.x += self._dashSpeed * deltaTime * (self._vel.x / abs(self._vel.x))
            self._dash = False
        else:
            self._pos.x += self._vel.x * deltaTime
        self._pos.y += self._vel.y * deltaTime

        # variable jump height
        if not self._jumpHolding and self._vel.y < 0:
            self._vel.y = 0

        # jump hold
        if self._jumpHolding:
            self._curJumpHold += dt
            if self._curJumpHold >= self._jumpMaxHold:
                self._jumpHolding = False

        # move
        self._pos += self._vel * dt
        isMoving = abs(self._vel.x) > 0
        turning = False

        if isMoving:
            if self._vel.x > 0 and not self._facingRight:
                turning = True
            elif self._vel.x < 0 and self._facingRight:
                turning = True

        # sync rect BEFORE collision
        self._rect.topleft = (int(self._pos.x), int(self._pos.y))

        # collision
        self.check_collision()

        just_landed = not was_grounded and self._grounded

        if not self._grounded:
            if self._inputDir > 0:
                self._facingRight = True
            elif self._inputDir < 0:
                self._facingRight = False

        # state change
        if just_landed:
            if self._vel.x != 0:
                self.set_animation("run")
            else:
                self.set_animation("idle")

        elif self._gliding:
            self.set_animation("glide")

        elif self._crouching:
            self.set_animation("crouch")

        elif self._grounded:

            isMoving = abs(self._vel.x) > 0

            turning = False
            if isMoving:
                if self._inputDir > 0 and not self._facingRight:
                    turning = True
                elif self._inputDir < 0 and self._facingRight:
                    turning = True

            if turning:
                self.set_animation("run_back")

            elif not self._wasMoving and isMoving:
                self.set_animation("run_start")

            elif self._wasMoving and not isMoving:
                self.set_animation("run_stop")

            elif isMoving:
                if self.current_anim not in ("run_start", "run_stop", "run_back"):
                    self.set_animation("run")

            else:
                if self.current_anim not in ("run_stop",):
                    self.set_animation("idle")

            self._wasMoving = isMoving

        else:
            if self._vel.y < 0:
                if self._jumpTimes == 2:
                    self.set_animation("double_jump")
                else:
                    self.set_animation("jump")
            else:
                self.set_animation("fall")

        # update animation frames
        if self.frame_timer >= self.frame_speed:
            self.frame_timer = 0

            if self.current_anim == "fall":
            self._curJumpHold += deltaTime
        if self._dashCD > 0.0:
            self._dashCD -= deltaTime

                # loop last 2 frames
                if self.frame_index < len(self.frames) - 2:
                    self.frame_index += 1
                else:
                    if self.frame_index == len(self.frames) - 1:
                        self.frame_index = len(self.frames) - 2
                    else:
                        self.frame_index = len(self.frames) - 1

            elif self.current_anim == "glide":
                # loop last 3 frames
                if self.frame_index < len(self.frames) - 3:
                    self.frame_index += 1
                else:
                    if self.frame_index == len(self.frames) - 1:
                        self.frame_index = len(self.frames) - 3
                    else:
                        self.frame_index += 1

            elif self.current_anim == "run_start":
                if self.frame_index < len(self.frames) - 1:
                    self.frame_index += 1
                else:
                    self.set_animation("run")

            elif self.current_anim == "run_stop":
                if self.frame_index < len(self.frames) - 1:
                    self.frame_index += 1
                else:
                    self.set_animation("idle")

            elif self.current_anim == "run_back":

                if self.frame_index < len(self.frames) - 1:
                    self.frame_index += 1
                else:

                    if self._inputDir > 0:
                        self._facingRight = True
                    elif self._inputDir < 0:
                        self._facingRight = False

                    self.set_animation("run")

            else:
                # normal looping animation
                self.frame_index = (self.frame_index + 1) % len(self.frames)

            self._image = self.frames[self.frame_index]

        # sync rect AGAIN after collision fix
        self._rect.midtop = (int(self._pos.x), int(self._pos.y))

    # -----------------------
    # COLLISION
    # -----------------------

    def check_collision(self):

        self._grounded = False

        self._rect.x = int(self._pos.x)
        self._rect.y = int(self._pos.y)

        if self._pos.x <= MAP_LEFT:
            self._pos.x = MAP_LEFT

        if self._pos.x + self._rect.width >= MAP_RIGHT:
            self._pos.x = MAP_RIGHT - self._rect.width

        if self._pos.y + self._rect.height >= MAP_BOTTOM:

            self._pos.y = MAP_BOTTOM - self._rect.height
            self._vel.y = 0

            self._grounded = True
            self._jumpTimes = 0

    # -----------------------
    # DRAW
    # -----------------------
    def load(self):
        """Load character stats from saved progress"""
        pass

    def save(self):
        """save current character stats"""
        pass

    def draw(self, screen):

        image = self._image

        if not self._facingRight:
            image = pygame.transform.flip(self._image, True, False)

        draw_rect = image.get_rect(midtop=self._rect.midtop)

        screen.blit(image, draw_rect)