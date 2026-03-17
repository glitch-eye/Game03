from settings import *
from character import *
from wisp import *
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
        self.wisp = None   # store animation frames
        self.goblin = None

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
        self.loader.load_animation("arrow_ring_sprite", "assets/sprite/arrow_ring_sprite")
        self.loader.load_animation("player_jump_effect", "assets/sprite/player_jump_effect")
        self.loader.load_animation("bullet_effect_sprite2", "assets/sprite/bullet_effect_sprite2")
        self.loader.load_animation("bullet_effect_sprite3", "assets/sprite/bullet_effect_sprite3")
        self.loader.load_animation("player_action1", "assets/sprite/player_action")
        self.loader.load_animation("player_action2", "assets/sprite/player_action2")
        self.loader.load_animation("player_action3", "assets/sprite/player_action3")
        self.loader.load_animation("player_action4", "assets/sprite/player_action4")
        self.loader.load_animation("player_run_attack1", "assets/sprite/player_run_attack2")
        self.loader.load_animation("player_run_attack2", "assets/sprite/player_run_attack")
        self.loader.load_animation("player_run_attack3", "assets/sprite/player_run_attack3")
        self.loader.load_animation("player_run_attack4", "assets/sprite/player_run_attack4")
        self.loader.load_animation("player_jump_attack", "assets/sprite/player_jump_attack")
        self.loader.load_animation("player_up_shot","assets/sprite/player_up_shot")
        self.loader.load_animation("player_up_shot2","assets/sprite/player_up_shot2")
        self.loader.load_animation("player_up_shot_run","assets/sprite/player_up_shot_run")
        self.loader.load_animation("player_up_shot_air","assets/sprite/player_up_shot_air")
        self.loader.load_animation("player_under_attack","assets/sprite/player_under_attack")
        self.loader.load_animation("player_sliding","assets/sprite/player_sliding")
        self.loader.load_animation("player_time_stop", "assets/sprite/player_time_stop")
        self.loader.load_animation("player_time_stop_air", "assets/sprite/player_time_stop_air")

        self.loader.load_animation("crystal", "assets/sprite/crystal_sprite")
        self.loader.load_animation("big_bomb_effect", "assets/sprite/big_bomb_effect")
        self.loader.load_animation("mp_item", "assets/sprite/mpup_sprite")
        self.loader.load_animation("hp_item", "assets/sprite/hpup_sprite")

        # sounds

        # enemies
        self.loader.load_animation(
            "wisp",
            "assets/sprite/will_o_wisp_sprite"
        )

        self.loader.load_animation("goblin_attack", "assets/sprite/goblin_attack_sprite")
        self.loader.load_animation("goblin_run", "assets/sprite/goblin_run_sprite")
        self.loader.load_animation("goblin_idle", "assets/sprite/goblin_sprite")

        # music
        # self.loader.load_music("Luna_Dial", "assets/music/Lunar Clock Lunar Dial.ogg")
        # music_path = self.loader.get_music("Luna_Dial")
        # pygame.mixer.music.load(music_path)

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

        # start music
        # pygame.mixer.music.play(-1)   # -1 = loop forever

        # retrieve animation frames
        self.wisp = Wisp(0, 0, self.loader.get_animation("wisp"))
        self.goblin = Goblin(0, 0, self.loader)

        self.crystal = Crystal(self.loader, 1)

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
        self.wisp.update(dt, self.player._pos)
        self.goblin.update(dt, self.player._rect)
        self.crystal.update(dt)

    # -----------------------
    # COLLISION
    # -----------------------

    def check_collision(self):

        self.player.check_collision()
        self.goblin.check_collision()

    # -----------------------
    # DRAW
    # -----------------------

    def draw(self):

        self._screen.fill(COLOR_BLACK)

        self.player.draw(self._screen)
        self.wisp.draw(self._screen)
        self.goblin.draw(self._screen)
        self.crystal.draw(self._screen)

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