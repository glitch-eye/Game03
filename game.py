import pygame
import os
from settings import *
from build import *

os.environ['SDL_VIDEO_CENTERED'] = '1'

pygame.init()
pygame.mixer.init()
pygame.font.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DIO simulator")

BG = build_background()
map_tiles, collision_tiles = build_map()
INDEX_MAP = load_map_from_excel()

# camera offset (pixel)
cam_x = 0
cam_y = 0

running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_RIGHT]:
        cam_x -= VELOCITY
    if keys[pygame.K_LEFT]:
        cam_x += VELOCITY
    if keys[pygame.K_UP]:
        cam_y += VELOCITY
    if keys[pygame.K_DOWN]:
        cam_y -= VELOCITY

    # giới hạn camera không ra khỏi bản đồ
    if INDEX_MAP:
        rows = len(INDEX_MAP)
        cols = len(INDEX_MAP[0])
        map_w = cols * TILE_SIZE
        map_h = rows * TILE_SIZE

        if map_w > WIDTH:
            cam_x = max(min(cam_x, 0), WIDTH - map_w)
        else:
            cam_x = 0
        if map_h > HEIGHT:
            cam_y = max(min(cam_y, 0), HEIGHT - map_h)
        else:
            cam_y = 0

    screen.blit(BG, (0, 0))                      # vẽ nền
    load_map(screen, INDEX_MAP, map_tiles, (cam_x, cam_y))  # vẽ map đã scroll

    pygame.draw.rect(screen, (255, 0, 0), (WIDTH//2, 280, 40, 40))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()