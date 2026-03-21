from PIL import Image
import os

# --- CẤU HÌNH ---
INPUT_FILE = "stage05_map.png"
OUTPUT_DIR = "assets/map_tiles"  # Thư mục lưu các ô đã cắt
NEW_SIZE = (288, 288)             # Kích thước sau khi scale
TILE_SIZE = 36                   # Kích thước mỗi ô Grid để cắt

def scale_and_slice_collision():
    # 1. Kiểm tra và nạp ảnh gốc
    if not os.path.exists(INPUT_FILE):
        print(f"Lỗi: Không tìm thấy file {INPUT_FILE}")
        return
    
    img = Image.open(INPUT_FILE)
    print(f"Ảnh gốc: {img.size[0]}x{img.size[1]}px")
    
    # 2. Scale (Phóng to) lên 288x288
    # Dùng Image.NEAREST để giữ nguyên nét pixel cứng của collision, không bị mờ
    # scaled_img = img.resize(NEW_SIZE, Image.NEAREST)
    print(f"Đã scale lên: {img.size[0]}x{img.size[1]}px")
    
    # Tùy chọn: Lưu lại ảnh đã scale để kiểm tra
    # scaled_img.save("collision_288x288.png")

    # 3. Tạo thư mục đầu ra
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    # 4. Cắt thành các ô Grid 36x36
    width, height = img.size
    count = 0
    
    for y in range(0, height, TILE_SIZE):
        for x in range(0, width, TILE_SIZE):
            # Định nghĩa vùng cắt: (left, top, right, bottom)
            box = (x, y, x + TILE_SIZE, y + TILE_SIZE)
            
            # Cắt và lưu
            tile = img.crop(box)
            tile_name = f"{OUTPUT_DIR}/collision_{count}.png"
            tile.save(tile_name)
            count += 1
            
    print(f"Thành công! Đã cắt thành {count} file 36x36px trong thư mục '{OUTPUT_DIR}'")

# Chạy hàm
scale_and_slice_collision()