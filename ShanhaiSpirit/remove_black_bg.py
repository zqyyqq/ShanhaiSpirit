import cv2
import numpy as np
import os
from config import CREATURES_DIR

def remove_black_background(input_path, output_path):
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
    
    black_mask = (img_bgr[:, :, 0] < 50) & (img_bgr[:, :, 1] < 50) & (img_bgr[:, :, 2] < 50)
    print(f"  黑色像素数: {np.sum(black_mask)}")
    
    near_black_mask = (img_bgr[:, :, 0] < 80) & (img_bgr[:, :, 1] < 80) & (img_bgr[:, :, 2] < 80)
    print(f"  接近黑色像素数: {np.sum(near_black_mask)}")
    
    alpha[black_mask] = 0
    
    smooth_mask = cv2.GaussianBlur((near_black_mask & ~black_mask).astype(np.float32), (15, 15), 0)
    smooth_alpha = alpha.astype(np.float32)
    smooth_alpha[near_black_mask] = smooth_alpha[near_black_mask] * (1 - smooth_mask[near_black_mask])
    
    result = np.dstack((img_bgr, smooth_alpha.astype(np.uint8)))
    
    print(f"  处理后形状: {result.shape}")
    print(f"  处理后黑色像素数: {np.sum((result[:,:,0]<50)&(result[:,:,1]<50)&(result[:,:,2]<50)&(result[:,:,3]>0))}")
    
    success = cv2.imwrite(output_path, result)
    if success:
        print(f"  ✓ 处理成功")
    else:
        print(f"  ✗ 保存失败")
    
    return success

if __name__ == "__main__":
    baize_path = os.path.join(CREATURES_DIR, "baize", "baize.png")
    print(f"处理白泽图片:")
    remove_black_background(baize_path, baize_path)
    print("\n处理完成！")