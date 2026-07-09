import cv2
import numpy as np
import os
from config import CREATURES_DIR

def remove_background(input_path, output_path):
    img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
    
    if img is None:
        print(f"无法读取图片: {input_path}")
        return False
    
    print(f"  原图片形状: {img.shape}")
    
    if len(img.shape) == 2:
        img_bgr = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    elif img.shape[2] == 4:
        img_bgr = img[:, :, :3]
    else:
        img_bgr = img
    
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    
    corners = [
        gray[0, 0], gray[0, -1],
        gray[-1, 0], gray[-1, -1]
    ]
    bg_mean = np.mean(corners)
    bg_std = np.std(corners)
    print(f"  角落颜色均值: {bg_mean:.1f}, 标准差: {bg_std:.1f}")
    
    threshold = bg_mean + 50
    print(f"  背景阈值: {threshold:.1f}")
    
    _, mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)
    
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=3)
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        mask = np.zeros_like(mask)
        cv2.drawContours(mask, [largest_contour], 0, 255, -1)
    
    mask = cv2.GaussianBlur(mask, (9, 9), 0)
    
    result = np.dstack((img_bgr, mask))
    
    print(f"  处理后形状: {result.shape}")
    
    success = cv2.imwrite(output_path, result)
    if success:
        print(f"  ✓ 处理成功")
    else:
        print(f"  ✗ 保存失败")
    
    return success

if __name__ == "__main__":
    baize_path = os.path.join(CREATURES_DIR, "baize", "baize.png")
    print(f"处理白泽图片:")
    remove_background(baize_path, baize_path)
    print("\n处理完成！")