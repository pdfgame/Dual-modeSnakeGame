import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

def get_font_path():
    """
    获取中文字体路径。
    首先尝试从fonts目录获取，如果不存在则尝试从系统字体目录获取。
    """

    font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
    

    chinese_fonts = [
        "simhei.ttf",  
        "msyh.ttc",    
        "simsun.ttc",  
        "simkai.ttf",  
        "Deng.ttf",    
        "方正粗黑宋简体.ttf",  
    ]
    

    for font_name in chinese_fonts:
        font_path = os.path.join(font_dir, font_name)
        if os.path.exists(font_path):


            return font_path
    

    import platform
    system = platform.system()
    
    if system == "Windows":

        system_font_dirs = [
            "C:\\Windows\\Fonts",
            "C:\\WINNT\\Fonts"
        ]
    elif system == "Darwin":

        system_font_dirs = [
            "/Library/Fonts",
            "/System/Library/Fonts",
            os.path.expanduser("~/.fonts")
        ]
    else:

        system_font_dirs = [
            "/usr/share/fonts/truetype",
            "/usr/share/fonts/opentype",
            os.path.expanduser("~/.fonts")
        ]
    

    system_chinese_fonts = [
        "simhei.ttf",    
        "simhei.ttc",    
        "msyh.ttc",      
        "msyhbd.ttc",    
        "simsun.ttc",    
        "simsun.ttf",    
        "simkai.ttf",    
        "kaiu.ttf",      
        "Deng.ttf",      
        "STHeiti Light.ttc",  
        "STHeiti Medium.ttc", 
        "STSong.ttf",    
        "STKaiti.ttf",   
        "STXingkai.ttf", 
        "STXinwei.ttf",  
        "STZhongsong.ttf", 
        "STFangsong.ttf", 
        "YuGothB.ttc",   
        "YuGothM.ttc",   
        "YuGothR.ttc",   
        "方正粗黑宋简体.ttf", 
    ]
    

    for font_dir in system_font_dirs:
        if os.path.exists(font_dir):
            for font_name in system_chinese_fonts:
                font_path = os.path.join(font_dir, font_name)
                if os.path.exists(font_path):


                    return font_path
    


    return None

def _get_font(font_size):
    """
    加载指定大小的字体，如果失败则返回Pillow的默认字体。
    """

    font_path = get_font_path()
    if font_path:
        try:
            return ImageFont.truetype(font_path, font_size)
        except Exception:
            pass
    

    system_fonts = [
        "SimHei",          
        "Microsoft YaHei", 
        "SimSun",          
        "KaiTi",           
        "DengXian",        
        "Arial",           
        "Helvetica",       
    ]
    
    for font_name in system_fonts:
        try:
            return ImageFont.truetype(font_name, font_size)
        except Exception:
            continue
    

    return ImageFont.load_default()

def put_chinese_text_pil(img, text, position, font_size, color):
    """
    使用PIL在图像上绘制中文文本。
    """
    try:

        img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil)
        

        font = _get_font(font_size)
        

        rgb_color = (color[2], color[1], color[0])

        draw.text(position, text, font=font, fill=rgb_color)
        

        return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    except Exception as e:
        print(f"绘制文本错误: {e}")

        try:

            cv2.putText(img, text, position, cv2.FONT_HERSHEY_SIMPLEX, font_size / 20, color, 2)
        except Exception as e2:
            print(f"备用绘制方法也失败: {e2}")
        return img

def put_chinese_text_with_background(img, text, position, font_size, text_color, bg_color, bg_opacity=0.6):
    """
    在带背景的图像上绘制中文文本。
    """

    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)).convert('RGBA')
    

    txt_layer = Image.new('RGBA', img_pil.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)
    

    font = _get_font(font_size)
    

    try:
        bbox = draw.textbbox(position, text, font=font)
    except AttributeError: 
        text_width, text_height = draw.textsize(text, font=font)
        bbox = (position[0], position[1], position[0] + text_width, position[1] + text_height)


    bg_position = (bbox[0] - 5, bbox[1] - 5, bbox[2] + 5, bbox[3] + 5)

    rgb_bg_color = (bg_color[2], bg_color[1], bg_color[0])
    bg_color_rgba = rgb_bg_color + (int(255 * bg_opacity),)
    draw.rectangle(bg_position, fill=bg_color_rgba)
    


    rgb_text_color = (text_color[2], text_color[1], text_color[0])
    draw.text(position, text, font=font, fill=rgb_text_color)
    

    out = Image.alpha_composite(img_pil, txt_layer)
    

    return cv2.cvtColor(np.array(out.convert('RGB')), cv2.COLOR_RGB2BGR)

def put_rainbow_text_pil(img, text, position, font_size):
    """
    使用PIL在图像上绘制彩虹色中文文本。
    """
    try:

        img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil)
        

        font = _get_font(font_size)
        

        rainbow_colors = [(255, 0, 0), (255, 165, 0), (255, 255, 0), 
                          (0, 255, 0), (0, 0, 255), (75, 0, 130), (238, 130, 238)]
        

        x, y = position
        try:

            for i, char in enumerate(text):
                char_color = rainbow_colors[i % len(rainbow_colors)]

                char_bbox = draw.textbbox((0, 0), char, font=font)
                char_width = char_bbox[2] - char_bbox[0]
                draw.text((x, y), char, font=font, fill=char_color)
                x += char_width
        except Exception:

            char_width = font_size 
            for i, char in enumerate(text):
                char_color = rainbow_colors[i % len(rainbow_colors)]
                char_position = (position[0] + i * char_width, position[1])
                draw.text(char_position, char, font=font, fill=char_color)


        return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    except Exception as e:
        print(f"绘制彩虹文本错误: {e}")

        try:

            cv2.putText(img, text, position, cv2.FONT_HERSHEY_SIMPLEX, font_size / 20, (255, 255, 255), 2)
        except Exception as e2:
            print(f"备用绘制方法也失败: {e2}")
        return img
