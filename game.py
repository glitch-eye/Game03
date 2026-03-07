from settings import *
from character import *

class Game:
    def __init__(self):
        self._screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self._font = pygame.font.SysFont(None, FONT_SIZE)
        self._clock = pygame.time.Clock()

        pygame.display.set_caption(GAME_NAME)
        
        self.player = Character()

    def handleInput(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        keypressed = pygame.key.get_pressed()
        #call entites to handle key events
        self.player.handleInput(keypressed)

    def load_assets(self):
        pass

    def update(self, deltaTime):
        self.player.update(deltaTime)

    def draw(self):
        self._screen.fill(COLOR_WHITE)
        self.player.draw(self._screen)

    def check_collision(self):
        self.player.check_collision()

    def play(self):
        """Game loop"""
        while True:
            self.handleInput()
            deltaTime = self._clock.tick(FPS) / 1000.0
            self.update(deltaTime)
            self.check_collision()
            self.draw()
            pygame.display.flip()