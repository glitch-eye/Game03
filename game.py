from settings import *
from character import *
from asset_loader import AssetLoader
import pygame
import sys

class Game:

    def __init__(self):

        self._display = pygame.display.set_mode(
            (SCREEN_WIDTH * GAME_SCALE, SCREEN_HEIGHT * GAME_SCALE)
        )

        self._screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(GAME_NAME)

        self._clock = pygame.time.Clock()
        self._font = pygame.font.SysFont(None, FONT_SIZE)

        self.loader = AssetLoader()

        self.player = None
        self.wisp_frames = None   # store animation frames

    # -----------------------
    # ASSET LOADING
    # -----------------------

    def load_assets(self):

        # player
        self.loader.load_animation("player_idle", "assets/sprite/player_stop")
        self.loader.load_animation("player_jump", "assets/sprite/player_jump")
        self.loader.load_animation("player_fall", "assets/sprite/player_falling")
        self.loader.load_animation("player_2ndjump", "assets/sprite/player_2ndjump")
        self.loader.load_animation("player_gliding", "assets/sprite/player_gliding")
        self.loader.load_animation("player_run", "assets/sprite/player_run")
        self.loader.load_animation("player_run_start", "assets/sprite/player_run_start")
        self.loader.load_animation("player_run_stop", "assets/sprite/player_run_stop")
        self.loader.load_animation("player_run_back", "assets/sprite/player_run_back")
        self.loader.load_animation("player_down", "assets/sprite/player_down")

        # sounds

        # wisp
        self.loader.load_animation(
            "wisp",
            "assets/sprite/will_o_wisp_sprite"
        )

        # music

        # loading screen loop
        while not self.loader.done():

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self._screen.fill((0,0,0))

            text = self._font.render("Loading...", True, (255,255,255))
            rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self._screen.blit(text, rect)

            pygame.display.flip()

        # finalize assets
        self.loader.finalize()

        # retrieve animation frames
        self.wisp_frames = self.loader.get_animation("wisp")

        # create entities AFTER assets exist
        self.player = Character(self.loader)

    # -----------------------
    # INPUT
    # -----------------------

    def handleInput(self):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keypressed = pygame.key.get_pressed()

        self.player.handleInput(keypressed)

    # -----------------------
    # UPDATE
    # -----------------------

    def update(self, dt):

        self.player.update(dt)

    # -----------------------
    # COLLISION
    # -----------------------

    def check_collision(self):

        self.player.check_collision()

    # -----------------------
    # DRAW
    # -----------------------

    def draw(self):

        self._screen.fill(COLOR_BLACK)

        self.player.draw(self._screen)

        scaled = pygame.transform.scale(
            self._screen,
            (SCREEN_WIDTH * GAME_SCALE, SCREEN_HEIGHT * GAME_SCALE)
        )

        self._display.blit(scaled, (0,0))
        pygame.display.flip()
    
    def save(self, savename=None):
        """Save current game progress to new save / override current save"""
        pass

    def load(self, savename):
        """Load saved progress"""
        pass

    # -----------------------
    # GAME LOOP
    # -----------------------

    def play(self):

        while True:

            dt = self._clock.tick(FPS) / 1000.0

            self.handleInput()
            self.update(dt)
            self.check_collision()
            self.draw()