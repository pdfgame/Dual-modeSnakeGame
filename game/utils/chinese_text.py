import cv2
import numpy as np

def put_chinese_text(img, text, position, font_size, color):
    """
    在图像上绘制文本 - 使用OpenCV的简单实现
    虽然不能直接显示中文，但至少能显示文字占位符
    """

    if len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    elif len(img.shape) == 3 and img.shape[2] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    

    cv2.putText(img, text, position, cv2.FONT_HERSHEY_SIMPLEX, 
                font_size/30.0, color, max(1, font_size//15))
    
    return img

def put_rainbow_text(img, text, position, font_size):
    """
    在图像上绘制彩虹色文本
    """
    colors = [(0, 0, 255), (0, 165, 255), (0, 255, 255), (0, 255, 0), (255, 0, 0), (255, 0, 255)]
    
    for i, color in enumerate(colors):
        offset = i * 2
        offset_position = (position[0] + offset, position[1] + offset)
        cv2.putText(img, text, offset_position, cv2.FONT_HERSHEY_SIMPLEX, 
                    font_size/30.0, color, max(1, font_size//15))
    
    cv2.putText(img, text, position, cv2.FONT_HERSHEY_SIMPLEX, 
                font_size/30.0, (255, 255, 255), max(1, font_size//15))
    
    return img

def put_rainbow_text_with_alpha(img, text, position, font_size, alpha):
    """
    在图像上绘制带透明度的炫彩中文文本
    """
    if isinstance(text, bytes):
        text = text.decode('utf-8')
    elif not isinstance(text, str):
        text = str(text)
        
    temp_img = img.copy()
    temp_img = put_rainbow_text(temp_img, text, position, font_size)
    
    img = cv2.addWeighted(img, 1 - alpha, temp_img, alpha, 0)
    return img