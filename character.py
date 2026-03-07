"""
    Character build
"""
from settings import *
class Character:
    def __init__(self):
        #stats
        self._pos = pINIT_POS
        self._vel = pygame.Vector2(0, -gGRAVITY)
        self._moveSpeed = pSPEED
        self._rect = pygame.Rect(self._pos.x, self._pos.y, pHURTBOX_WIDTH, pHURTBOX_HEIGHT)
        self._jumpforce = pJUMPSTRENGTH
        self._doublejumpForce = pDOUBLEJUMPSTRENGTH
        self._jumpholdDuration = pJUMPHOLDTIME
        self._doublejumpholdDuration = pDOUBLEJUMPHOLDTIME

        #state
        self._jumpTimes = 0
        self._grounded = True
        self._curJumpHold = 0.0
        self._jumpHolding = False
        self._jumpMaxHold = self._jumpholdDuration

        #placeholder for char image
        self._image = pygame.Surface((pHURTBOX_WIDTH, pHURTBOX_HEIGHT))
        self._image.fill(COLOR_GREEN)
    
    def handleInput(self, keys):
        if keys[K_a]:
            self._vel.x = -self._moveSpeed
        if keys[K_d]:
            self._vel.x = self._moveSpeed
        if keys[K_SPACE]:
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

        #key release
        if (not keys[K_a] and self._vel.x == -self._moveSpeed) or (not keys[K_d] and self._vel.x == self._moveSpeed):
            self._vel.x = 0

        if self._curJumpHold >= self._jumpMaxHold:
            self._vel.y = gGRAVITY
        if not keys[K_SPACE]:
            self._jumpHolding = False
            self._curJumpHold = 0.0
            self._vel.y = gGRAVITY
        

    def update(self, deltaTime):
        self._pos.x += self._vel.x * deltaTime
        self._pos.y += self._vel.y * deltaTime

        if self._jumpHolding:
            self._curJumpHold += deltaTime

        self._rect.left = self._pos.x
        self._rect.top = self._pos.y

    def check_collision(self):
        if self._pos.x <= mLEFT:
            self._pos.x = mLEFT
        if self._pos.x + pHURTBOX_WIDTH >= mRIGHT:
            self._pos.x = mRIGHT - pHURTBOX_WIDTH
        if self._pos.y + pHURTBOX_HEIGHT >= mBOTTOM:
            self._pos.y = mBOTTOM - pHURTBOX_HEIGHT
            self._grounded = True
            self._jumpTimes = 0

    def draw(self, screen):
        screen.blit(self._image, self._rect)