import threading
import os, re, csv
import pygame
from settings import *

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
        return cell
    return int(cell)
def build_background():
    bg = pygame.image.load("assets/background/background_sprite_0.png")
    return pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

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
    square = square + [i for i in range (798,803)] + [796, 804, 806, 808, 812, 813, 814]
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
def resolve_huda(text, is_black):
    if text == "gh":
        return 5
    if text == "bh" and is_black:
        return 6
    if text == "bv" and is_black:
        return 7
    if text == "gb":
        return 4
    if text == "wh" and not is_black:
        return 2
    if text == "bb":
        return 4
    if text == "wv" and not is_black:
        return 3
    if text == "wb":
        return 0
    return None

class Map_animation_handler:
    def __init__(self):
        self.huda = []
        self.stop = []
        self.nonstop = []
        self.ora = []
        self.white_ring = []

    def display(self, tile_idx, screen, screen_x, screen_y, is_black, incoming, mode = 0):
        num = resolve_huda(tile_idx, is_black)
        if num is not None:
            image = self.huda[num]
            image = pygame.transform.scale(image, (TILE_SIZE,TILE_SIZE))
            screen.blit(image, (screen_x, screen_y))
            if is_black and tile_idx == "bb":
                image2 = self.huda[9]
                image2.set_alpha(int(255* mode /8))
                image2 = pygame.transform.scale(image2, (TILE_SIZE,TILE_SIZE))
                screen.blit(image2, (screen_x, screen_y))
            elif not is_black and tile_idx == "wb":
                image2 = self.huda[8]
                image2.set_alpha(int(255* mode /8))
                image2 = pygame.transform.scale(image2, (TILE_SIZE,TILE_SIZE))
                screen.blit(image2, (screen_x, screen_y))
            return
        if tile_idx == "r":
            image = self.stop[1] if is_black else self.stop[0]
            image = pygame.transform.scale(image, (TILE_SIZE,TILE_SIZE))
            screen.blit(image, (screen_x, screen_y))
            return
        if tile_idx == "vr":
            image0 = self.nonstop[2]
            image0 = pygame.transform.scale(image0, (TILE_SIZE,TILE_SIZE))
            screen.blit(image0, (screen_x, screen_y))
            is_black_real = is_black if not incoming else not is_black 
            image = self.nonstop[1] if is_black_real else self.stop[0]
            image = pygame.transform.scale(image, (TILE_SIZE,TILE_SIZE))
            screen.blit(image, (screen_x, screen_y))
            return
        



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
        self.stop = None
        self.nonstop = None
        self.black = True
        self.pause = False
        self.mode = 0
        self.tolerant = 5
        self.time = 0
        self.incoming_signal = False
        self.collision_map = [[ 0 for _ in range (MAP_NUMS[0])] for _ in range (MAP_NUMS[1])]
        self.collision_tiles = []
        self.prev_foot_y = None
        self.pre_pos = None
        self.puzzle = Map_animation_handler()
        self.condition_collision = {}
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
                    collide.overlap = max(overlap, collide.overlap)
                    # Determine direction by offset from center
                    tile_center_x = offset[0] + TILE_SIZE // 2
                    tile_center_y = offset[1] + TILE_SIZE // 2
                    rect_center_x = rect.width // 2
                    rect_center_y = rect.height // 2
                    
                    # Calculate how much we overlap in each direction
                    dx = tile_center_x - rect_center_x
                    dy = tile_center_y - rect_center_y
                    
                    # Set flags based on direction (accumulate, don't reset)
                    if tile_center_x < rect_center_x:
                        collide.left = True
                    if tile_center_x > rect_center_x:
                        collide.right = True
                    if tile_center_y < rect_center_y:
                        collide.top = True
                    if tile_center_y > rect_center_y:
                        collide.bot = True

        return collide
    
    def bot_collide_rel(self, position, rect, vel):
        # 2. Xác định điểm kiểm tra (giữa chân nhân vật)
        foot_x = position.x + rect.width / 2 
        foot_y = position.y + rect.height
        
        col = int(foot_x // TILE_SIZE)
        row = int(foot_y // TILE_SIZE)
        
        is_ground = False
        tolerance = 5  # Khoảng dung sai để bám vào dốc (pixels)
        current_block = None
        # Kiểm tra nếu đang đứng trong phạm vi bản đồ
        if 0 <= row < len(self.collision_map) and 0 <= col < len(self.collision_map[0]):
            tile_type = self.collision_map[row][col]
            rel_x = (foot_x % TILE_SIZE) / TILE_SIZE  # Vị trí 0.0 -> 1.0 trong 1 ô
            
            target_y = None
            
            # Logic dốc 45 độ
            if tile_type == 6: # Dốc lên /
                target_y = (row + rel_x) * TILE_SIZE
            elif tile_type == 7: # Dốc xuống \
                target_y = (row + 1 - rel_x) * TILE_SIZE
            # Logic dốc thoải 2x1 (Loại 2,3 và 4,5)
            elif tile_type == 2: # Lên (thấp)
                target_y = (row + (1 - ((1 - rel_x) + 1) / 2)) * TILE_SIZE
            elif tile_type == 3: # Lên (cao)
                target_y = (row + (0.5 + rel_x * 0.5)) * TILE_SIZE
            elif tile_type == 4: # Xuống (cao)
                target_y = (row + (1 - rel_x * 0.5)) * TILE_SIZE
            elif tile_type == 5: # Xuống (thấp)
                target_y = (row + (1 - (rel_x + 1) / 2)) * TILE_SIZE
                
            # Logic gạch vuông
            elif tile_type == 1 or tile_type == 18:
                target_y = row * TILE_SIZE
            elif tile_type == 16:
                target_y = row * TILE_SIZE + 0.5 * TILE_SIZE
            elif tile_type == 25:
                target_y = row * TILE_SIZE if rel_x >= 0.5 else (row + 1)*TILE_SIZE
            elif tile_type == 26:
                target_y = row * TILE_SIZE if rel_x <= 0.5 else (row + 1)*TILE_SIZE
            
            if tile_type == 0:
                target_y = None
            # Nếu tìm thấy sàn (dốc hoặc gạch)
            if target_y is not None:
                # Nếu chân nhân vật gần sàn (trong khoảng dung sai)
                if abs(foot_y - target_y) <= tolerance:
                    position.y = target_y - rect.height
                    vel.y = 0
                    # if 0 <= row-1 < len(self.collision_map) and self.collision_map[row-1][col] == 1:
                    #     position.y = position.y - 1
                    #     self.prev_foot_y = foot_y
                    #     self.update_position(position, rect, vel)
                    #     return is_ground
                    is_ground = True
            current_block = tile_type
        return is_ground, current_block

    def left_rel(self, position, rect, vel, current_block, is_ground, count = 0):
        modify = False
        # 2. Xác định điểm kiểm tra (giữa chân nhân vật)
        foot_x = position.x 
        foot_y = position.y + rect.height
        
        col = int(foot_x // TILE_SIZE)
        row = int(foot_y // TILE_SIZE)
        
        leastrow = int(position.y // TILE_SIZE)
        # left
        
        if 0 <= row < len(self.collision_map) and 0 <= col < len(self.collision_map[0]):
            target_x = None
            for idx in range(leastrow, row + 1):
                tile_type = self.collision_map[idx][col]
                if idx == row:
                    tile_type = self.collision_map[idx - 1][col - 1]
                    if (tile_type == 6 or tile_type == 3) and vel.x < 0 and self.collision_map[idx][col] in [1, 2 , 6] :
                        position.y = position.y - 1
                        position.x = position.x - TILE_SIZE/6 
                        return is_ground, count
                    if (tile_type == 7 or tile_type == 4) and vel.x > 0 and current_block == 1 :
                        position.y = position.y - 1
                        return self.update_position(position, rect, vel, count)

                if tile_type != 25 and tile_type != 26 and tile_type != 0 :
                    temp_x = (col + 1) * TILE_SIZE
                    vel.x = 0
                    modify = True
                    if target_x is None:
                        target_x = temp_x
                    else :
                        target_x = max(target_x, temp_x)
                elif tile_type == 25:
                    temp_x = (col + 1) * TILE_SIZE
                    if target_x is None:
                        target_x = temp_x
                    else :
                        target_x = max(target_x, temp_x)
                    vel.x = 0
                    modify = True
                elif tile_type == 26:
                    temp_x = (col + 0.5) * TILE_SIZE
                    if target_x is None:
                        target_x = temp_x
                    else :
                        target_x = max(target_x, temp_x)
                    vel.x = 0
                    modify = True
            if modify:
                position.x = max(target_x, position.x)
                rect.topleft = (int(position.x), int(position.y))
                self.prev_foot_y = foot_y
        return is_ground, count
    
    def right_rel(self, position, rect, vel, current_block, is_ground, count = 0):
        modify = False
        # 2. Xác định điểm kiểm tra (giữa chân nhân vật)
        foot_x = position.x + rect.width 
        foot_y = position.y + rect.height
        
        col = int(foot_x // TILE_SIZE)
        row = int(foot_y // TILE_SIZE)
        
        leastrow = int(position.y // TILE_SIZE)
        if 0 <= row < len(self.collision_map) and 0 <= col < len(self.collision_map[0]):
            target_x = None
            for idx in range(leastrow, row):
                
                tile_type = self.collision_map[idx][col+1]
                if idx == row - 1:
                    tile_type = self.collision_map[idx][col]
                    if (tile_type == 3 or tile_type == 6) and vel.x > 0 and current_block == 1 :
                        position.y = position.y - 1
                        return self.update_position(position, rect, vel, count)
                    if (tile_type == 7 or tile_type == 4) and vel.x > 0 and self.collision_map[idx+1][col] in [1, 4, 7]:
                        position.y = position.y - 1
                        position.x = position.x + TILE_SIZE/6 
                        return is_ground, count
                        
                if tile_type != 25 and tile_type != 26 and tile_type != 0 :
                    temp_x = col * TILE_SIZE
                    vel.x = 0
                    modify = True
                    if target_x is None:
                        target_x = temp_x
                    else :
                        target_x = min(target_x, temp_x)
                elif tile_type == 25:
                    temp_x = (col + 0.5) * TILE_SIZE
                    if target_x is None:
                        target_x = temp_x
                    else :
                        target_x = min(target_x, temp_x)
                    vel.x = 0
                    modify = True
                elif tile_type == 26:
                    temp_x = (col) * TILE_SIZE
                    if target_x is None:
                        target_x = temp_x
                    else :
                        target_x = min(target_x, temp_x)
                    vel.x = 0
                    modify = True
            if modify:
                position.x = target_x - rect.width
                rect.topleft = (int(position.x), int(position.y))
                self.prev_foot_y = foot_y
        return is_ground, count

    def top_rel(self, position, rect, vel, is_ground):
        foot_x = position.x + rect.width / 2 
        col = int(foot_x // TILE_SIZE)
        tolerance = 5
        leastrow = int((position.y) // TILE_SIZE)
        if 0 <= leastrow < len(self.collision_map) and 0 <= col < len(self.collision_map[0]):
            tile_type = self.collision_map[leastrow][col]
            rel_y = ((position.y) % TILE_SIZE) / TILE_SIZE  # Vị trí 0.0 -> 1.0 trong 1 ô
            target_y_2 = None
            if tile_type == 18:
                target_y_2 = (leastrow + 0.5) * TILE_SIZE if rel_y < 0.5 else None
            elif tile_type != 0:
                target_y_2 = (leastrow + 1) * TILE_SIZE if 1 - rel_y > 0 else None
            # Nếu tìm thấy sàn (dốc hoặc gạch)
            if target_y_2 is not None:
                # Nếu chân nhân vật gần sàn (trong khoảng dung sai)
                position.y = target_y_2
                vel.y = 0

    def update_position(self, position, rect, vel, count = 0):
        

        # 2. Xác định điểm kiểm tra (giữa chân nhân vật)
        foot_x = position.x + rect.width / 2 
        foot_y = position.y + rect.height
        
        col = int(foot_x // TILE_SIZE)
        row = int(foot_y // TILE_SIZE)
        
        is_ground = False
        if self.prev_foot_y is None:
            self.prev_foot_y =  foot_y
        # Continuous collision detection - kiểm tra tất cả rows giữa vị trí cũ và mới
        prev_row = int(self.prev_foot_y // TILE_SIZE)
        if vel.y > 0 and row > prev_row:  # Đang rơi xuống
            # Kiểm tra từng row từ prev_row đến row hiện tại
            for check_row in range(prev_row, min(row + 1, len(self.collision_map))):
                if 0 <= check_row < len(self.collision_map) and 0 <= col < len(self.collision_map[0]):
                    tile_type = self.collision_map[check_row][col]
                    if tile_type != 0:  # Tìm thấy collision
                        rel_x = (foot_x % TILE_SIZE) / TILE_SIZE
                        target_y = None
                        
                        # Tính target_y cho tile này
                        if tile_type == 6:
                            target_y = (check_row + rel_x) * TILE_SIZE
                        elif tile_type == 7:
                            target_y = (check_row + 1 - rel_x) * TILE_SIZE
                        elif tile_type == 2:
                            target_y = (check_row + (1 - ((1 - rel_x) + 1) / 2)) * TILE_SIZE
                        elif tile_type == 3:
                            target_y = (check_row + (0.5 + rel_x * 0.5)) * TILE_SIZE
                        elif tile_type == 4:
                            target_y = (check_row + (1 - rel_x * 0.5)) * TILE_SIZE
                        elif tile_type == 5:
                            target_y = (check_row + (1 - (rel_x + 1) / 2)) * TILE_SIZE
                        elif tile_type == 1 or tile_type == 18:
                            target_y = check_row * TILE_SIZE
                        elif tile_type == 16:
                            target_y = check_row * TILE_SIZE + 0.5 * TILE_SIZE
                        
                        if target_y is not None and foot_y > target_y and foot_y - target_y <= TILE_SIZE * 5:
                            position.y = target_y - rect.height
                            vel.y = 0
                            is_ground = True
                            self.prev_foot_y = target_y
                            rect.topleft = (int(position.x), int(position.y))
                            return is_ground, count + 1
        
        
        
        

        original_pos = pygame.Vector2(position.x, position.y)
        results = []

        # 12 kịch bản thứ tự ưu tiên (Trục check trước, Trục check sau, và hướng ép buộc)
        # Mỗi bộ là: (Thứ tự ưu tiên, Hướng ưu tiên cụ thể)
        strategies = [
            ('top_first', 'left'), ('top_first', 'right'),
            ('bot_first', 'left'), ('bot_first', 'right'),
            ('left_first', 'top'), ('right_first', 'top'),
            ('left_first', 'bot'), ('right_first', 'bot'),
        ]

        for strategy in strategies:
            # Tạo bản sao tạm thời để thử nghiệm
            test_pos = pygame.Vector2(original_pos.x, original_pos.y)
            test_vel = pygame.Vector2(vel.x, vel.y)
            test_rect = rect.copy()
            
            # Thực hiện kịch bản check
            is_ground = self._apply_strategy(test_pos, test_rect, test_vel, strategy)
            
            # Kiểm tra xem sau khi áp dụng, vị trí này có còn "kẹt" (overlap) không
            collision_data = self.check_collision(test_pos, test_rect)
            if collision_data.overlap <= 7:
                dist = original_pos.distance_to(test_pos)
                results.append((dist, test_pos, is_ground))

        # Nếu tìm thấy các vị trí hợp lệ, chọn vị trí có khoảng cách di chuyển nhỏ nhất
        if results:
            results.sort(key=lambda x: x[0])

        # if vel.y >= 0:
        #     is_ground, current_block = self.bot_collide_rel(position, rect, vel)
        # else:
        #     self.top_rel(position, rect, vel, is_ground)
        # if vel.x > 0:
        #     is_ground, countr = self.right_rel(position, rect, vel, current_block, is_ground, count)
        # else:
        #     is_ground, countl = self.left_rel(position, rect, vel, current_block, is_ground, count)
        if len(results) > 0:
            result = results[0]
            for res in results:
                
                if result[0] == 0 and res[0] > 0 and 0 < position.y - res[1].y < 36 and abs(res[1].x - position.x) < 36:
                    result = res
                    is_ground = True
                    
            if position.x == result[1].x and position.x == result[1].y:
                is_ground = True
            position.x, position.y = result[1].x, result[1].y
            is_ground = result[2] or is_ground
        # Cập nhật lại Rect để vẽ (Dùng int để tránh lỗi TypeError)
        rect.topleft = (int(position.x), int(position.y))
        self.prev_foot_y = foot_y
        return is_ground, count + 1


    
    def _apply_strategy(self, pos, rect, vel, strategy):
        is_ground = False
        current_block = None
        
        mode, sub = strategy
        
        if mode == 'bot_first':
            is_ground, current_block = self.bot_collide_rel(pos, rect, vel)
            if sub == 'right': self.right_rel(pos, rect, vel, current_block, is_ground)
            else: self.left_rel(pos, rect, vel, current_block, is_ground)
            
        elif mode == 'right_first':
            # Check ngang trước để chặn tường, sau đó mới tính sàn/dốc
            self.right_rel(pos, rect, vel, current_block, is_ground)
            if sub == 'top': self.top_rel(pos, rect, vel,is_ground)
            is_ground, current_block = self.bot_collide_rel(pos, rect, vel)
            
        elif mode == 'top_first':
            self.top_rel(pos, rect, vel, is_ground)
            if sub == 'left': self.left_rel(pos, rect, vel, None, is_ground)
            else: self.right_rel(pos, rect, vel, None, is_ground)
        elif mode == 'left_first':
            self.left_rel(pos, rect, vel, current_block, is_ground)
            if sub == 'top': self.top_rel(pos, rect, vel,is_ground)
            is_ground, current_block = self.bot_collide_rel(pos, rect, vel)
            
        rect.topleft = (int(pos.x), int(pos.y))
        return is_ground
    def build_collision(self, index_map, collision_tiles):
        self.collision_tiles = collision_tiles
        for i, row in enumerate(index_map):
            for j, cell in enumerate(row):
                self.collision_map[i][j] = get_collison(cell)
                if isinstance(cell, str):
                    dic = self.condition_collision.get(cell, None)
                    if dic is None:
                        self.condition_collision[cell]=[[i,j]]
                    else:
                        dic += [[i,j]]
        self.load_keys()
        self.set_collision_by_condition()

    def load_map(self, screen, index_map, map_tiles, position):
        """
        Vẽ phần bản đồ nằm trong cửa sổ.
        Camera theo dõi vị trí nhân vật ở giữa màn hình.
        """
        if index_map is None or not map_tiles:
            return
        self.time = self.time + 1
        if self.time == self.tolerant:
            self.mode +=  1
            self.time = 0
            if self.mode >= 8 :
                self.mode = 0

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
                elif isinstance(tile_idx, str):
                    self.puzzle.display(tile_idx, screen, screen_x, screen_y, self.black, self.incoming_signal, self.mode)
                else:
                    if tile_idx < 0 or tile_idx >= len(map_tiles):
                        continue
                    if tile_idx != 0:
                        screen.blit(map_tiles[tile_idx], (screen_x, screen_y))

    def load_collision_map(self, screen, collision_tiles, position):
        self.load_map(screen, self.collision_map, collision_tiles, position)
    
    def build_map(self):
        # 1. Định nghĩa đường dẫn
        path_map = "assets/map_tiles"
        path_coll = "assets/collision_tiles"
        path_huda = "assets/yin_yang/white_or_black_huda"
        path_stop = "assets/yin_yang/white_or_black"
        path_nonstop = "assets/yin_yang/white_or_black_nonstop"
        path_ora = "assets/yin_yang/white_or_black_ora"
        path_white_ring = "assets/yin_yang/white_ring_effect"
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

        self.puzzle.huda = load_from_dir(path_huda)
        self.puzzle.nonstop = load_from_dir(path_nonstop)
        self.puzzle.ora = load_from_dir(path_ora)
        self.puzzle.stop = load_from_dir(path_stop)
        self.puzzle.white_ring = load_from_dir(path_white_ring)
        return map_tiles, collision_tiles

    def set_collision_by_condition(self):
        """
        Cập nhật collision_map dựa trên key của condition_collision và trạng thái self.black.
        - Bắt đầu bằng 'g' hoặc kết thúc bằng 'b': Luôn là 1 (Vật cản cố định).
        - Nếu self.black == True: Bắt đầu bằng 'b' là 1, bắt đầu bằng 'w' là 0.
        - Nếu self.black == False: Bắt đầu bằng 'b' là 0, bắt đầu bằng 'w' là 1.
        """
        for key, coords in self.condition_collision.items():
            key_str = str(key)
            collision_value = 0

            # 1. Kiểm tra điều kiện ưu tiên (Cố định)
            # g: global/ground, b (suffix): block
            if key_str.startswith('g') or key_str.endswith('b'):
                collision_value = 1
            
            # 2. Kiểm tra điều kiện theo trạng thái Âm - Dương (Black/White)
            elif self.black:
                print("black")
                if key_str.startswith('b'):
                    collision_value = 1
                elif key_str.startswith('w'):
                    collision_value = 0
            else: # self.black == False
                print("white")
                if key_str.startswith('b'):
                    collision_value = 0
                elif key_str.startswith('w'):
                    collision_value = 1

            # 3. Áp dụng giá trị tính được vào bản đồ tại các tọa độ đã lưu
            for i, j in coords:
                if 0 <= i < len(self.collision_map) and 0 <= j < len(self.collision_map[0]):
                    self.collision_map[i][j] = collision_value
    def time_stop(self):
        self.pause = True

    def time_go(self):
        self.pause = False
        if self.incoming_signal == True:
            self.black = not self.black
            self.incoming_signal = False
            self.set_collision_by_condition()
    def load_keys(self):
        self.stop = self.condition_collision["r"]
        self.nonstop = self.condition_collision["vr"]


    def rect_collide(self, pos, rect, pos_, rect_):
        return pos.x <= pos_.x + rect_.width and pos_.x <= pos.x + rect.width and pos.y <= pos_.y + rect_.height and pos_.y <= pos.y + rect.height

    def check_pressing(self, position, rect):
        if self.pre_pos is not None and self.pre_pos.x == position.x and self.pre_pos.y == position.y:
            return
        pre_pos = pygame.Vector2(self.pre_pos.x, self.pre_pos.y) if self.pre_pos is not None else None
        if self.pre_pos is None:
            self.pre_pos = pygame.Vector2(position.x, position.y)
        for pos in self.nonstop:
            if self.rect_collide(position, rect, pygame.Vector2(pos[1]* TILE_SIZE, pos[0]* TILE_SIZE), pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)):
                if pre_pos is not None and not self.rect_collide(pre_pos, rect, pygame.Vector2(pos[1]* TILE_SIZE, pos[0]* TILE_SIZE), pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)):
                    if self.pause:
                        self.incoming_signal = not self.incoming_signal
                    else:
                        self.black = not self.black
                        print("ok")
                        self.set_collision_by_condition()
                    break
        if not self.pause: 
            for pos in self.stop:
                if self.rect_collide(position, rect, pygame.Vector2(pos[1] * TILE_SIZE, pos[0] * TILE_SIZE), pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)):
                    if pre_pos is not None and not self.rect_collide(pre_pos, rect, pygame.Vector2(pos[1]* TILE_SIZE, pos[0]* TILE_SIZE), pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)):   
                        self.black = not self.black
                        print("ok")
                        self.set_collision_by_condition()
                        break
        self.pre_pos = pygame.Vector2(position.x, position.y)
        return
            
    


            

    
        
        
    
