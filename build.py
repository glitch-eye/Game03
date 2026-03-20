import threading
import os, re, csv
import pygame
from settings import *

def build_map():
    # 1. Định nghĩa đường dẫn
    path_map = "assets/map_tiles"
    path_coll = "assets/collision_tiles"
    
    # Hàm phụ để lấy số từ tên file (giúp sắp xếp đúng: 0, 1, 2... thay vì 0, 1, 10)
    def get_num(filename):
        nums = re.findall(r'\d+', filename)
        return int(nums[0]) if nums else 0

    def load_from_dir(directory):
        tiles = []
        # Lấy danh sách file .png và sắp xếp theo số trong tên
        if not os.path.exists(directory):
            print(f"Cảnh báo: Thư mục {directory} không tồn tại!")
            return []
            
        files = [f for f in os.listdir(directory) if f.endswith('.png')]
        files.sort(key=get_num) # Sắp xếp theo số 0, 1, 2...
        
        for f in files:
            full_path = os.path.join(directory, f)
            try:
                # Load và tối ưu hóa ảnh
                img = pygame.image.load(full_path).convert_alpha()
                tiles.append(img)
            except pygame.error as e:
                print(f"Lỗi khi load {f}: {e}")
        return tiles

    # Tải cả 2 danh sách độc lập
    map_tiles = load_from_dir(path_map)
    collision_tiles = load_from_dir(path_coll)
    return map_tiles, collision_tiles

def load_map(screen, index_map, map_tiles, position):
    """
    Vẽ phần bản đồ nằm trong cửa sổ.

    position = (offset_x, offset_y) là tọa độ pixel của góc trên trái
    bản đồ so với màn hình.
    """
    if index_map is None or not map_tiles:
        return

    offset_x, offset_y = position

    for row_idx, row in enumerate(index_map):
        for col_idx, tile_idx in enumerate(row):
            if isinstance(tile_idx, list):
                for idx in tile_idx:
                    if idx < 0 or idx >= len(map_tiles):
                        continue
                    x = col_idx * TILE_SIZE + offset_x
                    y = row_idx * TILE_SIZE + offset_y
                    if x + TILE_SIZE < 0 or x > WIDTH or y + TILE_SIZE < 0 or y > HEIGHT:
                        break
                    if idx != 0:
                        screen.blit(map_tiles[idx], (x, y))
                continue
            if tile_idx < 0 or tile_idx >= len(map_tiles):
                continue
            x = col_idx * TILE_SIZE + offset_x
            y = row_idx * TILE_SIZE + offset_y
            if x + TILE_SIZE < 0 or x > WIDTH or y + TILE_SIZE < 0 or y > HEIGHT:
                continue
            if tile_idx != 0:
                screen.blit(map_tiles[tile_idx], (x, y))

def load_map_from_excel(file_path = "map.csv"):
    game_map = []
    
    if not os.path.exists(file_path):
        print(f"Lỗi: Không tìm thấy file {file_path}. Đang tạo mảng trống 40x120.")
        return [[0 for _ in range(MAP_NUMS[0])] for _ in range(MAP_NUMS[1])]

    try:
        with open(file_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.reader(f, delimiter=';')
            for row in reader:
                # Chuyển từng ô từ chữ thành số nguyên (int)
                # lọc bỏ các dòng trống nếu có
                if row:
                    numeric_row = [handle_value(cell) for cell in row]
                    game_map.append(numeric_row)
        
        print(f"Đã tải bản đồ: {len(game_map)} hàng x {len(game_map[0])} cột")
        game_map = game_map[1:]
        return game_map

    except Exception as e:
        print(f"Lỗi khi đọc file: {e}")
        return None
def handle_value(cell : str):
    if cell == '':
        return 0 
    elif len(cell.split(',')) > 1:
        ds = cell.split(',')
        return list(int(x) for x in ds)
    elif not cell.isnumeric():
        return 0
    return int(cell)
def build_background():
    bg = pygame.image.load("assets/background/background_sprite_0.png")
    return pygame.transform.scale(bg, (WIDTH, HEIGHT))

def resolve_yinyang():
    pass

class Map:
    def __init__(self):
        black = True
        collision_map = [[ 0 for _ in range (MAP_NUMS[0])] for _ in range (MAP_NUMS[1])]

    def check_collision(self, position):
        pass
    
    def build_collision(self, index_map):
        pass
    