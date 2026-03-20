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
                # Load ảnh (không dùng convert_alpha vì display chưa khởi tạo)
                img = pygame.image.load(full_path)
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
    Camera theo dõi vị trí nhân vật ở giữa màn hình.
    """
    if index_map is None or not map_tiles:
        return

    # Tính vị trí camera trong thế giới (world coordinates)
    camera_x = min(max(position.x - SCREEN_WIDTH // 2, 0), MAP_NUMS[0]*TILE_SIZE - SCREEN_WIDTH)
    camera_y = min(max(position.y - SCREEN_HEIGHT // 2, 0), MAP_NUMS[1]*TILE_SIZE - SCREEN_HEIGHT)
    
    for row_idx, row in enumerate(index_map):
        for col_idx, tile_idx in enumerate(row):
            # Vị trí tile trong world
            world_x = col_idx * TILE_SIZE
            world_y = row_idx * TILE_SIZE
            
            # Vị trí trên screen (trừ camera offset)
            screen_x = world_x - camera_x
            screen_y = world_y - camera_y
            
            # Bỏ qua tiles ngoài màn hình
            if screen_x + TILE_SIZE < 0 or screen_x >= SCREEN_WIDTH or screen_y + TILE_SIZE < 0 or screen_y >= SCREEN_HEIGHT:
                continue
            
            if isinstance(tile_idx, list):
                for idx in tile_idx:
                    if idx < 0 or idx >= len(map_tiles):
                        continue
                    if idx != 0:
                        screen.blit(map_tiles[idx], (screen_x, screen_y))
            else:
                if tile_idx < 0 or tile_idx >= len(map_tiles):
                    continue
                if tile_idx != 0:
                    screen.blit(map_tiles[tile_idx], (screen_x, screen_y))

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
    return pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

def resolve_yinyang():
    pass

def get_collison(idx):
    if idx is None or (isinstance(idx, list) and len(idx) == 0):
        return 0
    
    square = [1,2,3,10,33,34] + [i for i in range (40,46)] + [50]
    square = square + [i for i in range (59,65)] + [i for i in range (67,69)] 
    square = square + [72, 80, 85, 90, 92, 105, 112] + [i for i in range (121,129)] 
    square = square + [130, 132, 146] + [i for i in range (151 ,154)] 
    square = square + [i for i in range (161,166)] + [i for i in range (167,174)] 
    square = square + [i for i in range (181,187)] + [i for i in range (203,210)]
    square = square + [i for i in range (460,475)] + [487, 685, 686]
    square = square + [i for i in range (779, 782)] + [i for i in range (789, 792)]
    square = square + [i for i in range (798,803)] + [804, 806, 808, 812, 813]
    square = square + [i for i in range (815,820)] + [822, 824, 827, 829, 832, 833, 835, 837, 839]

    left_square_tri = [69, 70, 138, 139, 142, 145, 795, 820]
    right_square_tri = [65, 66, 106, 136, 137, 144, 453]
    lleft_2x1_tri = [97, 810, 23, 48]
    rleft_2x1_tri = [98, 811, 24, 49]
    lright_2x1_tri = [95, 107, 451, 21, 46]
    rright_2x1_tri = [96, 108, 452, 22, 47]
    half_top = [i for i in range (792,795)] + [830, 831]
    half_bot = [71, 73, 81, 82, 83, 84, 420, 421, 422, 454, 810]
    half_right = [803]
    half_left = [828]
    if isinstance(idx, list):
        return get_collison(idx[0])+ get_collison(idx[1:])
    if idx in square and idx != 59:
        return 1
    elif idx in lleft_2x1_tri:
        return 2
    elif idx in rleft_2x1_tri:
        return 3
    elif idx in lright_2x1_tri:
        return 4
    elif idx in rright_2x1_tri:
        return 5
    elif idx in left_square_tri:
        return 6
    elif idx in right_square_tri:
        return 7
    elif idx in half_bot:
        return 16
    elif idx in half_top:
        return 18
    elif idx in half_right:
        return 25
    elif idx in half_left:
        return 26
    return 0


class Collide_direct:
    def __init__(self):
        self.left = False
        self.right = False
        self.top = False
        self.bot = False
        self.overlap = 0
        self.overlap_rect = None  # Rect của vùng overlap

class Map:
    def __init__(self):
        self.black = True
        self.collision_map = [[ 0 for _ in range (MAP_NUMS[0])] for _ in range (MAP_NUMS[1])]
        self.collision_tiles = []
    def check_collision(self, position, rect : pygame.Rect):
        collide = Collide_direct()
        object_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        object_surface.fill((255, 255, 255))
        object_mask = pygame.mask.from_surface(object_surface)

        least_rect = pygame.Rect(
            (position.x // TILE_SIZE) * TILE_SIZE,
            (position.y // TILE_SIZE) * TILE_SIZE,
            ((position.x + rect.width) // TILE_SIZE + 1) * TILE_SIZE,
            ((position.y + rect.height) // TILE_SIZE + 1) * TILE_SIZE
        )

        min_col = least_rect.left // TILE_SIZE
        max_col = least_rect.right // TILE_SIZE
        min_row = least_rect.top // TILE_SIZE
        max_row = least_rect.bottom // TILE_SIZE

        for row in range(min_row, max_row):
            for col in range(min_col, max_col):
                if row < 0 or row >= len(self.collision_map) or col < 0 or col >= len(self.collision_map[0]):
                    continue

                index = self.collision_map[row][col]
                if index == 0:
                    continue

                collisions_tile_mask = pygame.mask.from_surface(self.collision_tiles[index])
                offset = (col * TILE_SIZE - position.x, row * TILE_SIZE - position.y)
                overlap = object_mask.overlap_area(collisions_tile_mask, offset)
                
                if overlap:
                    if overlap > collide.overlap:
                        collide.overlap = overlap
                        
                        # Simple direction detection: which side of rect is closest to collision
                        offset_x = offset[0]
                        offset_y = offset[1]
                        
                        # Calculate penetration depth on each side
                        left_pen = offset_x + TILE_SIZE
                        right_pen = rect.width - offset_x
                        top_pen = offset_y + TILE_SIZE
                        bottom_pen = rect.height - offset_y
                        
                        # Only set if penetration is positive (actual collision)
                        collide.left = left_pen > 0 and left_pen < right_pen and left_pen < top_pen and left_pen < bottom_pen
                        collide.right = right_pen > 0 and right_pen < left_pen and right_pen < top_pen and right_pen < bottom_pen
                        collide.top = top_pen > 0 and top_pen < left_pen and top_pen < right_pen and top_pen < bottom_pen
                        collide.bot = bottom_pen > 0 and bottom_pen < left_pen and bottom_pen < right_pen and bottom_pen < top_pen

        return collide
    def update_position(self, position, rect : pygame.Rect, vel):
        collide = self.check_collision(position, rect)
        is_ground = False
        
        # Step 1: Block velocity on collision
        if collide.bot:
            vel.y = 0
            is_ground = True
            # Push up out of collision
            position.y -= 2
        if collide.top:
            vel.y = 0
            position.y += 2
        if collide.right:
            vel.x = 0
            position.x -= 2
        if collide.left:
            vel.x = 0
            position.x += 2
        
        # Step 2: Detect slope surface and climb it
        rect_center_x = position.x + rect.width // 2
        
        # Scan downward from current position to find nearest slope
        max_scan_dist = TILE_SIZE * 2  # Look up to 2 tiles down
        best_surface_y = None
        
        scan_col_start = int((position.x - TILE_SIZE) // TILE_SIZE)
        scan_col_end = int((position.x + rect.width + TILE_SIZE) // TILE_SIZE)
        scan_row = int((position.y + rect.height) // TILE_SIZE)
        
        slope_types = [2, 3, 4, 5, 6, 7]
        
        # Scan tiles below character
        for scan_offset in range(max_scan_dist // TILE_SIZE + 1):
            check_row = scan_row + scan_offset
            if check_row < 0 or check_row >= len(self.collision_map):
                continue
            
            for check_col in range(scan_col_start, scan_col_end + 1):
                if check_col < 0 or check_col >= len(self.collision_map[0]):
                    continue
                
                index = self.collision_map[check_row][check_col]
                if index not in slope_types:
                    continue
                
                # Found a slope - get its mask
                collisions_tile_mask = pygame.mask.from_surface(self.collision_tiles[index])
                
                # Local position on this tile
                local_x = int(rect_center_x) - (check_col * TILE_SIZE)
                
                if not (0 <= local_x < TILE_SIZE):
                    continue
                
                # Find topmost non-empty pixel at this x
                for py in range(TILE_SIZE):
                    try:
                        if collisions_tile_mask.get_at((local_x, py)):
                            world_surface_y = check_row * TILE_SIZE + py
                            
                            # Only consider if it's close enough and below character
                            if world_surface_y > position.y and world_surface_y - (position.y + rect.height) < max_scan_dist:
                                if best_surface_y is None or world_surface_y < best_surface_y:
                                    best_surface_y = world_surface_y
                            break
                    except:
                        pass
        
        # Step 3: Place character on slope surface
        if best_surface_y is not None:
            position.y = best_surface_y - rect.height
            is_ground = True
        
        return is_ground
        
            



    
    def build_collision(self, index_map):
        for i, row in enumerate(index_map):
            for j, cell in enumerate(row):
                self.collision_map[i][j] = get_collison(cell)
    
    def load_collision_map(self, screen, index_map, collision_tiles, position):
        self.build_collision(index_map)
        self.collision_tiles = collision_tiles
        # load_map(screen, self.collision_map, collision_tiles, position)

    
        
        
    