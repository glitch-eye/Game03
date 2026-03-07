"""
    Character build
"""
from settings import *
class Character:
    def __init__(self):
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
        self._vel = pygame.Vector2(0, -GAME_GRAVITY)
        self._moveSpeed = PLAYER_SPEED
        self._gravity = GAME_GRAVITY
        self._rect = pygame.Rect(self._pos.x, self._pos.y, PLAYER_HURTBOX_WIDTH, PLAYER_HURTBOX_HEIGHT)
        self._jumpforce = PLAYER_JUMPSTRENGTH
        self._doublejumpForce = PLAYER_DOUBLEJUMPSTRENGTH
        self._jumpholdDuration = PLAYER_JUMPHOLDTIME
        self._doublejumpholdDuration = PLAYER_DOUBLEJUMPHOLDTIME

        #state
        self._jumpTimes = 0
        self._grounded = True
        self._curJumpHold = 0.0
        self._jumpHolding = False
        self._jumpMaxHold = self._jumpholdDuration

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

        if self._jumpHolding:
            self._curJumpHold += deltaTime
        if self._dashCD > 0.0:
            self._dashCD -= deltaTime

        self._rect.left = self._pos.x
        self._rect.top = self._pos.y

    def check_collision(self):
        if self._pos.x <= MAP_LEFT:
            self._pos.x = MAP_LEFT
        if self._pos.x + self._hurtbox.x >= MAP_RIGHT:
            self._pos.x = MAP_RIGHT - self._hurtbox.x
        if self._pos.y + self._hurtbox.y >= MAP_BOTTOM:
            self._pos.y = MAP_BOTTOM - self._hurtbox.y
            self._grounded = True
            self._jumpTimes = 0

    def load(self):
        """Load character stats from saved progress"""
        pass

    def save(self):
        """save current character stats"""
        pass

    def draw(self, screen):
        screen.blit(self._image, self._rect)