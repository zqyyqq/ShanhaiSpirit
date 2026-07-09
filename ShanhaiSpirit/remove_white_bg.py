import cv2
import numpy as np
import os
from config import CREATURES_DIR

def remove_white_background(input_path, output_path):
    img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
    
    if img is None:
        print(f"无法读取图片: {input_path}")
        return False
    
    print(f"  原图片形状: {img.shape}")
    
    if len(img.shape) == 2:
        img_bgr = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        alpha = np.ones((img.shape[0], img.shape[1]), dtype=np.uint8) * 255
    elif img.shape[2] == 4:
        img_bgr = img[:, :, :3]
        alpha = img[:, :, 3]
    else:
        img_bgr = img
        alpha = np.ones((img.shape[0], img.shape[1]), dtype=np.uint8) * 255
    
    white_mask = (img_bgr[:, :, 0] > 230) & (img_bgr[:, :, 1] > 230) & (img_bgr[:, :, 2] > 230)
    print(f"  白色像素数: {np.sum(white_mask)}")
    
    near_white_mask = (img_bgr[:, :, 0] > 200) & (img_bgr[:, :, 1] > 200) & (img_bgr[:, :, 2] > 200)
    print(f"  接近白色像素数: {np.sum(near_white_mask)}")
    
    alpha[white_mask] = 0
    
    smooth_mask = cv2.GaussianBlur((near_white_mask & ~white_mask).astype(np.float32), (15, 15), 0)
    smooth_alpha = alpha.astype(np.float32)
    smooth_alpha[near_white_mask] = smooth_alpha[near_white_mask] * (1 - smooth_mask[near_white_mask])
    
    result = np.dstack((img_bgr, smooth_alpha.astype(np.uint8)))
    
    print(f"  处理后形状: {result.shape}")
    print(f"  处理后白色像素数: {np.sum((result[:,:,0]>240)&(result[:,:,1]>240)&(result[:,:,2]>240)&(result[:,:,3]>0))}")
    
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
            remove_white_background(main_image_path, main_image_path)

if __name__ == "__main__":
    process_all_creatures()
    print("\n所有图片处理完成！")