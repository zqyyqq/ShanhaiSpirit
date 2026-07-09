import cv2
import numpy as np
import os
from config import CREATURES_DIR

def restore_white_background(input_path, output_path):
    img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
    
    if img is None:
        print(f"无法读取图片: {input_path}")
        return False
    
    print(f"  原图片形状: {img.shape}")
    
    if len(img.shape) == 2:
        result = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    elif img.shape[2] == 4:
        bgr = img[:, :, :3]
        alpha = img[:, :, 3]
        
        white_bg = np.ones_like(bgr) * 255
        
        alpha_float = alpha / 255.0
        alpha_float = alpha_float[:, :, np.newaxis]
        
        result = (bgr * alpha_float + white_bg * (1 - alpha_float)).astype(np.uint8)
    else:
        result = img
    
    print(f"  处理后形状: {result.shape}")
    
    success = cv2.imwrite(output_path, result)
    if success:
        print(f"  ✓ 处理成功")
    else:
        print(f"  ✗ 保存失败")
    
    return success

def process_all_creatures():
    creatures = ['fenghuang', 'yinglong', 'qilin', 'baize']
    
    for creature in creatures:
        creature_dir = os.path.join(CREATURES_DIR, creature)
        if not os.path.exists(creature_dir):
            print(f"目录不存在: {creature_dir}")
            continue
        
        main_image_path = os.path.join(creature_dir, f"{creature}.png")
        if os.path.exists(main_image_path):
            print(f"\n处理 {creature}:")
            restore_white_background(main_image_path, main_image_path)

if __name__ == "__main__":
    process_all_creatures()
    print("\n所有图片处理完成！")