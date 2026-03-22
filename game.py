from settings import *
from character import *
from utils import *
from wisp import *
from menu import *
from boss import Boss
from asset_loader import AssetLoader
import pygame
import sys
from build import *

class Position:
    def __init__(self):
        self.x = 36*36
        self.y = 360

pos = Position()
class Game:

    def __init__(self):

        self.time_stop = False

        self._display = pygame.display.set_mode(
            (SCREEN_WIDTH * GAME_SCALE, SCREEN_HEIGHT * GAME_SCALE)
        )

        self._screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(GAME_NAME)

        self._clock = pygame.time.Clock()
        self._font = pygame.font.SysFont(None, FONT_SIZE)

        self.loader = AssetLoader()
        self.in_menu = True
        self.menu = None

        self.player = None
        self.wisp = None   # store animation frames
        self.goblin = None
        self.boss = None

    # -----------------------
    # ASSET LOADING
    # -----------------------

    def load_assets(self):
        # menu
        self.loader.load_animation("start_screen", "assets/sprite/start_screen_sprite")
        self.loader.load_animation("taohao_font", "assets/sprite/toho_font_sprite")
        self.loader.load_animation("pause_screen", "assets/sprite/title_back")
        self.loader.load_animation("status_font", "assets/sprite/status_font")

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
        self.loader.load_animation("flying_knife", "assets/sprite/bullet_sprite3")
        self.loader.load_animation("player_damage", "assets/sprite/player_damage")
        self.loader.load_animation("player_fall_down", "assets/sprite/player_fall_down")
        self.loader.load_animation("player_des", "assets/sprite/player_des")
        # item and effect
        self.loader.load_animation("crystal", "assets/sprite/crystal_sprite")
        self.loader.load_animation("big_bomb_effect", "assets/sprite/big_bomb_effect")
        self.loader.load_animation("mp_item", "assets/sprite/mpup_sprite")
        self.loader.load_animation("hp_item", "assets/sprite/hpup_sprite")

        # UI
        self.loader.load_image("gauge", "assets/sprite/gauge_sprite/gauge_sprite_1.png")
        for i in range(10):
            self.loader.load_image(
                f"time_number_sprite_{i}",
                f"assets/sprite/time_number_sprite/time_number_sprite_{i}.png"
            )
        self.loader.load_image("hp_bar", "assets/sprite/hpvar_sprite/hpvar_sprite_19.png")
        self.loader.load_image("mp_bar", "assets/sprite/mpvar_sprite/mpvar_sprite_19.png")

        # Boss
        self.loader.load_animation("marisa_idle", "assets/sprite/marisa")
        self.loader.load_animation("marisa_dir_change", "assets/sprite/marisa_dir_change")
        self.loader.load_animation("marisa_up_to_down", "assets/sprite/marisa_up_to_down")
        self.loader.load_animation("marisa_down", "assets/sprite/marisa_down")
        self.loader.load_animation("marisa_down_to_up", "assets/sprite/marisa_down_to_up")
        self.loader.load_animation("marisa_dira_down_change", "assets/sprite/marisa_dira_change_down")
        self.loader.load_animation("marisa_stop", "assets/sprite/marisa_stop")
        self.loader.load_animation("marisa_dash", "assets/sprite/marisa_dash")
        self.loader.load_animation("marisa_dash_zanzou", "assets/sprite/marisa_dash_zanzou")
        self.loader.load_animation("marisa_undershot", "assets/sprite/marisa_undershot")
        self.loader.load_animation("marisa_timeshot", "assets/sprite/marisa_timeshot")
        self.loader.load_animation("marisa_shot", "assets/sprite/marisa_shot")
        self.loader.load_animation("marisa_undershot_a", "assets/sprite/marisa_undershot_a")
        self.loader.load_animation("marisa_laser", "assets/sprite/marisa_laser")
        self.loader.load_animation("marisa_after_effect", "assets/sprite/marisa_after_effect")
        self.loader.load_animation("marisa_after_effect_s", "assets/sprite/marisa_after_effect_s")
        self.loader.load_animation("marisa_shot_a", "assets/sprite/marisa_shot_a")
        self.loader.load_animation("smoke", "assets/sprite/smoke")
        # sounds

        # enemies
        self.loader.load_animation("wisp","assets/sprite/will_o_wisp_sprite")

        self.loader.load_animation("goblin_attack", "assets/sprite/goblin_attack_sprite")
        self.loader.load_animation("goblin_run", "assets/sprite/goblin_run_sprite")
        self.loader.load_animation("goblin_idle", "assets/sprite/goblin_sprite")

        self.knives = []
        self.enemy_projectiles = []
        self.enemy_particles = []
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
        self.menu = Menu(loader=self.loader)
        # retrieve animation frames
        self.wisp = Wisp(0, 0, self.loader)
        self.goblin = Goblin(300, 1000, self.loader)

        self.crystal = Crystal(self.loader, 1)

        # create entities AFTER assets exist
        self.player = Character(self.loader, self)

        # spawn boss
        self.boss = Boss(self.loader, self, self.player)

        self.BG = build_background()
        self.INDEX_MAP = load_map_from_excel()
        self.collision_map = Map()
        self.map_tiles, self.collision_tiles = self.collision_map.build_map()
        self.player.set_map(self.collision_map)
        self.collision_map.build_collision(self.INDEX_MAP, self.collision_tiles)

    # -----------------------
    # INPUT
    # -----------------------

    def handleInput(self):

        for event in pygame.event.get():
            if self.in_menu:
                option = self.menu.handle_event(event)
                if option:
                    self.in_menu = False
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and self.menu.game_start:
                    self.in_menu = not self.in_menu
                    self.menu.game_paused = not self.menu.game_paused

        keypressed = pygame.key.get_pressed()
        if self.time_stop:
            self.collision_map.time_stop()
        else:
            self.collision_map.time_go()
        

        self.player.handleInput(keypressed)
        

    # -----------------------
    # UPDATE
    # -----------------------

    def update(self, dt):
        global GAME_SCALE
        if self.menu.setting_options["GAME SCALE"] != GAME_SCALE:
            GAME_SCALE = self.menu.setting_options["GAME SCALE"]
            self._display = pygame.display.set_mode(
                (SCREEN_WIDTH * GAME_SCALE, SCREEN_HEIGHT * GAME_SCALE)
            )
        self.collision_map.update_position(pos, pygame.Rect(0,0,40,40), pygame.Vector2(10,10))
        self.player.update(dt)

        if not self.time_stop:
            self.boss.update(dt, self.player._pos, self.knives)
            self.wisp.update(dt, self.player._pos, self.knives)
            self.goblin.update(dt, self.player, self.knives)
            self.crystal.update(dt, self.player._pos, self.knives)

            for knife in self.knives:
                knife.update(dt)

            for proj in self.enemy_projectiles:
                proj.update(dt, self.player._rect, self.enemy_particles)

            # --- Update enemy particles ---
            for p in self.enemy_particles:
                p.update(dt)

            self.enemy_particles = [p for p in self.enemy_particles if p.alive]

            self.enemy_projectiles = [p for p in self.enemy_projectiles if p.alive]

            # remove dead knives
            self.knives = [k for k in self.knives if k.alive]

    # -----------------------
    # COLLISION
    # -----------------------

    def check_collision(self):

        self.player.check_collision()
        self.goblin.check_collision(self.collision_map)

    # -----------------------
    # DRAW
    # -----------------------

    def draw(self):
        self._screen.fill(COLOR_BLACK)
        self._screen.blit(self.BG, (0,0))
        
        if self.in_menu:
            self.menu.draw(self._screen)
            scaled = pygame.transform.scale(
                self._screen,
                (SCREEN_WIDTH * GAME_SCALE, SCREEN_HEIGHT * GAME_SCALE)
            )
        else:
            # Update camera position to follow player
            pos.x = self.player._pos.x
            pos.y = self.player._pos.y
            
            self.collision_map.load_map(self._screen, self.INDEX_MAP, self.map_tiles, pos)
            self.collision_map.load_collision_map(self._screen, self.collision_tiles, pos)

            # camera_x = min(max(pos.x - SCREEN_WIDTH // 2, 0), MAP_NUMS[0]*TILE_SIZE - SCREEN_WIDTH)
            # camera_y = min(max(pos.y - SCREEN_HEIGHT // 2, 0), MAP_NUMS[1]*TILE_SIZE - SCREEN_HEIGHT)
            # x,y = SCREEN_WIDTH//2 , SCREEN_HEIGHT//2
            # if camera_x == 0:
            #     x = pos.x
            # if camera_x == MAP_NUMS[0]*TILE_SIZE - SCREEN_WIDTH:
            #     x = pos.x%SCREEN_WIDTH
            # if camera_y == 0:
            #     y = pos.y
            # if camera_y == MAP_NUMS[1]*TILE_SIZE - SCREEN_HEIGHT:
            #     y = pos.y%SCREEN_HEIGHT
            
            # pygame.draw.rect(self._screen, (255, 0, 0), (x, y, 40, 40))
            # -----------------------
            # DRAW WORLD (no player)
            # -----------------------
            self.wisp.draw(self._screen)
            self.goblin.draw(self._screen, pos)
            self.crystal.draw(self._screen)
            # draw boss
            self.boss.draw(self._screen)

            for knife in self.knives:
                knife.draw(self._screen)
            for proj in self.enemy_projectiles:
                proj.draw(self._screen)
            for p in self.enemy_particles:
                p.draw(self._screen)

            # -----------------------
            # APPLY FILTER SAFELY
            # -----------------------
            if self.time_stop:
                filtered = apply_grayscale(self._screen.copy())
            else:
                # Update camera position to follow player
                pos.x = self.player._pos.x
                pos.y = self.player._pos.y
                
                self.collision_map.load_map(self._screen, self.INDEX_MAP, self.map_tiles, pos)
                self.collision_map.load_collision_map(self._screen, self.collision_tiles, pos)

                # camera_x = min(max(pos.x - SCREEN_WIDTH // 2, 0), MAP_NUMS[0]*TILE_SIZE - SCREEN_WIDTH)
                # camera_y = min(max(pos.y - SCREEN_HEIGHT // 2, 0), MAP_NUMS[1]*TILE_SIZE - SCREEN_HEIGHT)
                # x,y = SCREEN_WIDTH//2 , SCREEN_HEIGHT//2
                # if camera_x == 0:
                #     x = pos.x
                # if camera_x == MAP_NUMS[0]*TILE_SIZE - SCREEN_WIDTH:
                #     x = pos.x%SCREEN_WIDTH
                # if camera_y == 0:
                #     y = pos.y
                # if camera_y == MAP_NUMS[1]*TILE_SIZE - SCREEN_HEIGHT:
                #     y = pos.y%SCREEN_HEIGHT
                
                # pygame.draw.rect(self._screen, (255, 0, 0), (x, y, 40, 40))
                # -----------------------
                # DRAW WORLD (no player)
                # -----------------------
                self.wisp.draw(self._screen)
                self.goblin.draw(self._screen, pos)
                self.crystal.draw(self._screen)

                for knife in self.knives:
                    knife.draw(self._screen)

                # -----------------------
                # APPLY FILTER SAFELY
                # -----------------------
                if self.time_stop:
                    filtered = apply_grayscale(self._screen.copy())
                else:
                    filtered = self._screen

                # -----------------------
                # HP/MP bar
                # -----------------------
                hp_bar = self.loader.get_image("hp_bar")
                mp_bar = self.loader.get_image("mp_bar")

                # ratios
                hp_ratio = self.player.hp / self.player.hp_max
                mp_ratio = self.player.mp / self.player.mp_max

                # clamp
                hp_ratio = max(0, min(1, hp_ratio))
                mp_ratio = max(0, min(1, mp_ratio))

                # --- crop width ---
                hp_width = int(hp_bar.get_width() * hp_ratio)
                mp_width = int(mp_bar.get_width() * mp_ratio)

                # create cropped surfaces
                hp_crop = pygame.Surface((hp_width, hp_bar.get_height()), pygame.SRCALPHA)
                mp_crop = pygame.Surface((mp_width, mp_bar.get_height()), pygame.SRCALPHA)
                # --- position (under your gauge UI) ---
                base_x = SCREEN_WIDTH // 2 - 199   # tweak this
                base_y = 25                        # tweak this

                hp_crop.blit(hp_bar, (0, 0), (0, 0, hp_width, hp_bar.get_height()))
                mp_crop.blit(mp_bar, (0, 0), (0, 0, mp_width, mp_bar.get_height()))                      # tweak this

            # draw HP (top)
                filtered.blit(hp_crop, (base_x, base_y))
                value = int(self.player.time_energy)
                digits = list(str(value))

                # -----------------------
                # BOSS HP BAR
                # -----------------------
                if self.boss and self.boss.hp > 0:

                    base_bar = self.loader.get_image("hp_bar")
                    boss_bar = recolor_red(base_bar)

                    # --- Stretch horizontally ---
                    stretch_w = int(boss_bar.get_width() * 1.7)   # widen boss bar
                    stretch_h = boss_bar.get_height()

                    boss_bar = pygame.transform.scale(boss_bar, (stretch_w, stretch_h))

                    ratio = self.boss.hp / self.boss.max_hp
                    ratio = max(0, min(1, ratio))

                    width = int(stretch_w * ratio)

                    crop = pygame.Surface((width, stretch_h), pygame.SRCALPHA)
                    crop.blit(boss_bar, (0,0), (0,0,width,stretch_h))

                    # centered top
                    x = SCREEN_WIDTH//2 - stretch_w//2 + 160
                    y = 25

                    filtered.blit(crop, (x, y))
            
                # -----------------------
                # GAUGE
                # -----------------------
                gauge = self.loader.get_image("gauge")

                # draw MP (below HP)
                filtered.blit(mp_crop, (base_x, base_y + 12))

                value = int(self.player.time_energy)
                digits = list(str(value))
            
                # -----------------------
                # GAUGE
                # -----------------------
                gauge = self.loader.get_image("gauge")
                gauge_rect = gauge.get_rect(midtop=(
                SCREEN_WIDTH // 2 + OFFSET_X,
                -15  # small padding from top
            ))

                gauge_rect = gauge.get_rect(midtop=(
                    SCREEN_WIDTH // 2 + OFFSET_X,
                    -7  # small padding from top
                ))

                filtered.blit(gauge, gauge_rect)

                # -----------------------
                # TIME
                # -----------------------
                value = int(self.player.time_energy)
                value = max(0, min(999, value))  # clamp

                digits = list(str(value))

                digit_images = [
                    self.loader.get_image(f"time_number_sprite_{d}")
                    for d in digits
                ]

                spacing = 2
                # --- adjust these ---
                circle_center_x = SCREEN_WIDTH // 2 + OFFSET_X
                circle_center_y = 44
                # --------------------

                total_width = sum(img.get_width() for img in digit_images) + spacing * (len(digit_images) - 1)


                start_x = circle_center_x - total_width // 2

                x = start_x
                for img in digit_images:
                    y = circle_center_y - img.get_height() // 2
                    filtered.blit(img, (x, y))
                    x += img.get_width() + spacing

                # -----------------------
                # DRAW PLAYER ON TOP (NOT FILTERED)
                # -----------------------
            self.player.draw(filtered)
            
                # -----------------------
                # SCALE + DISPLAY
                # -----------------------
            scaled = pygame.transform.scale(
                filtered,
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
            if not self.in_menu:
                self.update(dt)
                self.check_collision()
            self.draw()