import pygame
import sys
from settings import *
from pygame.locals import *

class Menu:
    def __init__(self, loader, font=None, pos=(100, 100), spacing=40):
        self.options = ["New Game", "Load Game", "Settings", "About", "Exit"]
        self.scales = [1, 1.5, 2]
        self.scale_index = 0
        self.setting_options = {
            "GAME SCALE": self.scales[0],
            "VOLUME": GAME_VOLUME
        }
        self.setting_chosen = False
        self.setting_index = 0
        self.font = {
            "taohao": loader.get_animation("taohao_font"),
            "status": loader.get_animation("status_font")
        }
        self.digits = [loader.get_image(f"time_number_sprite_{i}") for i in range(10)]
        self.pause_screen = loader.get_animation("pause_screen")
        self.start_screen = loader.get_animation("start_screen")
        self.game_start = False
        self.game_paused = False
        self.start_type = 0 # 0: start, 1: settings, 2: about
        self.pos = pos
        self.spacing = spacing
        self.selected_index = 0

    def draw(self, screen):
        if not self.game_start:
            match self.start_type:
                case 0:
                    self.draw_start_screen(screen)
                case 1:
                    self.draw_settings(screen)
                case 2:
                    self.draw_about(screen)
                case _:
                    self.draw_start_screen()
        elif self.game_paused:
            bg = pygame.transform.scale(self.pause_screen[0], (SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(bg, (0, 0))

    def draw_start_screen(self, screen):
        # Scale and blit background
        bg = pygame.transform.scale(self.start_screen[0], (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(bg, (0, 0))

        # Draw title
        title = GAME_NAME.upper()
        letter_sprites = self.font["status"]

        start_x = SCREEN_WIDTH // 2 - (len(title) * MENU_FONT[0]) // 2
        start_y = 50
        x = start_x
        for ch in title:
            if 'A' <= ch <= 'Z':
                index = 26 + (ord(ch) - ord('A'))
                letter_surface = pygame.transform.scale(letter_sprites[index], MENU_FONT)
                screen.blit(letter_surface, (x, start_y))
                x += letter_surface.get_width() + 2
            elif ch == ' ':
                x += 20

        # Draw menu options as buttons
        option_y = 150
        for i, option in enumerate(self.options):
            x = SCREEN_WIDTH // 2 - (len(option) * MENU_FONT[0] // 2) // 2
            for ch in option.upper():
                if 'A' <= ch <= 'Z':
                    index = 26 + (ord(ch) - ord('A'))
                    letter_surface = pygame.transform.scale(letter_sprites[index], (MENU_FONT[0] // 2, MENU_FONT[1] // 2))
                    # Highlight selected option in yellow tint
                    if i == self.selected_index:
                        # apply a tint by filling with color
                        tinted = letter_surface.copy()
                        tinted.fill((255, 255, 0), special_flags=pygame.BLEND_RGB_MULT)
                        screen.blit(tinted, (x, option_y))
                    else:
                        screen.blit(letter_surface, (x, option_y))
                    x += letter_surface.get_width() + 2
                elif ch == ' ':
                    x += 20
            option_y += self.spacing

    def draw_settings(self, screen):
        # Background
        bg = pygame.transform.scale(self.start_screen[0], (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(bg, (0, 0))

        # Title
        title = "SETTINGS"
        letter_sprites = self.font["status"]
        start_x = SCREEN_WIDTH // 2 - (len(title) * MENU_FONT[0]) // 2
        start_y = 50
        x = start_x
        for ch in title:
            if 'A' <= ch <= 'Z':
                index = 26 + (ord(ch) - ord('A'))
                letter_surface = pygame.transform.scale(letter_sprites[index], MENU_FONT)
                screen.blit(letter_surface, (x, start_y))
                x += letter_surface.get_width() + 2

        # Draw each setting option with its value
        option_y = 150
        for i, (option, value) in enumerate(self.setting_options.items()):
            line = f"{option}: {value}"
            x = SCREEN_WIDTH // 2 - (len(line) * MENU_FONT[0] // 2) // 2

            for ch in line.upper():
                if 'A' <= ch <= 'Z':
                    index = 26 + (ord(ch) - ord('A'))
                    letter_surface = pygame.transform.scale(
                        letter_sprites[index],
                        (MENU_FONT[0] // 2, MENU_FONT[1] // 2)
                    )
                elif ch.isdigit():
                    digit_surface = self.digits[int(ch)]
                    letter_surface = pygame.transform.scale(
                        digit_surface,
                        (MENU_FONT[0] // 2, MENU_FONT[1] // 2)
                    )
                elif ch == ' ' or ch == ':':
                    x += 20
                    continue
                else:
                    continue

                # Apply tint depending on state
                if i == self.setting_index:
                    if self.setting_chosen:
                        # Different tint when chosen (cyan here)
                        tinted = letter_surface.copy()
                        tinted.fill((0, 255, 255), special_flags=pygame.BLEND_RGB_MULT)
                        screen.blit(tinted, (x, option_y))
                    else:
                        # Normal selection tint (yellow)
                        tinted = letter_surface.copy()
                        tinted.fill((255, 255, 0), special_flags=pygame.BLEND_RGB_MULT)
                        screen.blit(tinted, (x, option_y))
                else:
                    screen.blit(letter_surface, (x, option_y))

                x += letter_surface.get_width() + 2

            option_y += self.spacing

    def draw_about(self, screen):
        # Background
        bg = pygame.transform.scale(self.start_screen[0], (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(bg, (0, 0))

        # Title
        title = "ABOUT"
        letter_sprites = self.font["status"]
        start_x = SCREEN_WIDTH // 2 - (len(title) * MENU_FONT[0]) // 2
        start_y = 50
        x = start_x
        for ch in title:
            if 'A' <= ch <= 'Z':
                index = 26 + (ord(ch) - ord('A'))
                letter_surface = pygame.transform.scale(letter_sprites[index], MENU_FONT)
                screen.blit(letter_surface, (x, start_y))
                x += letter_surface.get_width() + 2

        # About text
        about_lines = [
            "THIS GAME WAS HARDLY VIBE CODED",
            "USING PYGAME AND CUSTOM SPRITES",
            "THANK YOU FOR PLAYING!"
        ]
        option_y = 150
        for line in about_lines:
            x = SCREEN_WIDTH // 2 - (len(line) * MENU_FONT[0] // 2) // 2
            for ch in line.upper():
                if 'A' <= ch <= 'Z':
                    index = 26 + (ord(ch) - ord('A'))
                    letter_surface = pygame.transform.scale(letter_sprites[index], (MENU_FONT[0] // 2, MENU_FONT[1] // 2))
                    screen.blit(letter_surface, (x, option_y))
                    x += letter_surface.get_width() + 2
                elif ch == ' ':
                    x += 20
            option_y += self.spacing

    def handle_event(self, event):
        """Handle keyboard input for navigation."""
        if event.type == pygame.KEYDOWN and not self.game_start:
            if event.key == pygame.K_UP:
                if self.start_type == 0:
                    self.selected_index = (self.selected_index - 1) % len(self.options) 
                else:
                    if not self.setting_chosen:
                        self.setting_index = (self.setting_index - 1) % len(self.setting_options.keys())
                    else:
                        self.update_setting(True)
            elif event.key == pygame.K_DOWN:
                if self.start_type == 0:
                    self.selected_index = (self.selected_index + 1) % len(self.options) 
                else:
                    if not self.setting_chosen:
                        self.setting_index = (self.setting_index + 1) % len(self.setting_options.keys())
                    else:
                        self.update_setting(False)
            elif event.key == pygame.K_RETURN:
                if self.start_type == 0:
                    match self.selected_index:
                        case 0:
                            self.game_start = True
                            return True
                        case 1:
                            pass
                        case 2:
                            self.start_type = 1
                        case 3:
                            self.start_type = 2
                        case 4:
                            pygame.quit()
                            sys.exit()
                else:
                    self.setting_chosen = True
            elif event.key == pygame.K_ESCAPE:
                if self.start_type == 1 and self.setting_chosen:
                    self.setting_chosen = False
                elif self.start_type != 0:
                    self.start_type = 0
        elif event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif self.game_start and self.game_paused:
            if event.type == pygame.MOUSEBUTTONDOWN:
                _, mouse_y = event.pos
                if mouse_y in range(PAUSE_RESUME[0] * self.setting_options["GAME SCALE"], PAUSE_RESUME[1] * self.setting_options["GAME SCALE"]):
                    self.game_paused = False
                    return True
                elif mouse_y in range(PAUSE_EXIT[0] * self.setting_options["GAME SCALE"], PAUSE_EXIT[1] * self.setting_options["GAME SCALE"]):
                    self.game_start = False
                    self.game_paused = False
                    return False
        return False

    def update_setting(self, up):
        if self.setting_index == 0:
            #edit game scale
            if up:
                self.scale_index = (self.scale_index + 1) % len(self.scales)
            else:
                self.scale_index = (self.scale_index - 1) % len(self.scales)
            
            self.setting_options["GAME SCALE"] = self.scales[self.scale_index]
        else:
            #edit game volume
            if up:
                self.setting_options["VOLUME"] = (self.setting_options["VOLUME"] + 1) % 100
            else:
                self.setting_options["VOLUME"] = (self.setting_options["VOLUME"] - 1) % 100
            