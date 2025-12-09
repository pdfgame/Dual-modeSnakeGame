import cv2
import numpy as np
from game.utils.chinese_text import put_chinese_text, put_rainbow_text
import random
from PIL import ImageFont
import pygame
import os
from game.utils.improved_chinese_text import put_chinese_text_pil, put_rainbow_text_pil


gradient_colors_data = {
    "彩虹": [((255,0,0),(255,165,0)), ((255,165,0),(255,255,0)), ((255,255,0),(0,128,0)), ((0,128,0),(0,0,255)), ((0,0,255),(75,0,130)), ((75,0,130),(238,130,238))],
    "蓝绿渐变": ((0, 0, 255), (0, 255, 0)), 
    "火热渐变": ((255, 0, 0), (255, 255, 0)), 
    "宇宙渐变": ((128, 0, 128), (0, 0, 128))  
}


global_particles = []
shockwaves = []

def get_text_size(text, size):
    """使用Pillow计算中文文本的渲染尺寸"""
    font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "utils", "fonts", "simhei.ttf")
    try:
        font = ImageFont.truetype(font_path, size)
    except IOError:
        try:
            font = ImageFont.truetype("msyh.ttc", size)
        except IOError:
            try:
                font = ImageFont.truetype("simsun.ttc", size)
            except IOError:
                # 使用系统默认字体并确保能正确显示中文
                try:
                    font = ImageFont.truetype("arial.ttf", size)
                except:
                    font = ImageFont.load_default()
    
    # getbbox返回(left, top, right, bottom)
    if hasattr(font, 'getbbox'):
        bbox = font.getbbox(text)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]
    else:
        # 兼容旧版本Pillow
        text_width, text_height = font.getsize(text)
        return text_width, text_height

class EnhancedParticle:
    """增强版粒子类，支持颜色渐变"""
    def __init__(self, x, y, start_color, end_color, velocity_range=(-3, 3), lifespan_range=(15, 30), size_range=(2, 6), gravity=0.05):

        self.x, self.y = float(x), float(y)
        self.vx, self.vy = random.uniform(velocity_range[0], velocity_range[1]), random.uniform(velocity_range[0], velocity_range[1])
        self.lifespan = self.initial_lifespan = random.randint(lifespan_range[0], lifespan_range[1])
        self.start_color, self.end_color = np.array(start_color), np.array(end_color)
        self.color = self.start_color
        self.size = random.uniform(size_range[0], size_range[1])
        self.gravity = gravity

    def update(self):
        self.x += self.vx; self.y += self.vy; self.vy += self.gravity; self.lifespan -= 1
        life_ratio = max(0, self.lifespan / self.initial_lifespan)
        self.color = self.end_color + (self.start_color - self.end_color) * life_ratio
        self.size = max(0, self.size * life_ratio)

    def draw(self, surface):
        if self.lifespan > 0 and self.size > 0:
            draw_color = tuple(self.color.astype(int))
            if isinstance(surface, np.ndarray): cv2.circle(surface, (int(self.x), int(self.y)), int(self.size), [int(x) for x in draw_color], cv2.FILLED)
            elif isinstance(surface, pygame.Surface): pygame.draw.circle(surface, draw_color, (int(self.x), int(self.y)), int(self.size))

class Shockwave:
    """冲击波效果类"""
    def __init__(self, x, y, end_radius=250, lifespan=30, color=(255, 255, 255), thickness=8):
        self.x, self.y, self.lifespan, self.initial_lifespan = x, y, lifespan, lifespan
        self.end_radius, self.color, self.initial_thickness = end_radius, color, thickness

    def update(self): self.lifespan -= 1

    def draw(self, surface):
        if self.lifespan > 0:
            life_ratio = 1.0 - (self.lifespan / self.initial_lifespan)
            current_radius = int(self.end_radius * life_ratio)
            current_alpha = 1.0 - life_ratio
            current_thickness = int(self.initial_thickness * current_alpha)
            if current_thickness > 0 and isinstance(surface, np.ndarray):
                overlay = surface.copy()
                cv2.circle(overlay, (self.x, self.y), current_radius, self.color, current_thickness, cv2.LINE_AA)
                cv2.addWeighted(overlay, current_alpha, surface, 1 - current_alpha, 0, surface)

def emit_particle_burst(count, pos, colors, vel_range=(-4, 4), life_range=(30, 60), size_range=(3, 8), grav=0.02):
    for _ in range(count):
        # 生成径向速度，使粒子从中心均匀向外扩散
        angle = random.uniform(0, 2 * np.pi)
        speed = random.uniform(vel_range[0], vel_range[1])
        # 确保vx和vy是标量值，不是numpy数组
        vx = float(speed * np.cos(angle))
        vy = float(speed * np.sin(angle))
        # 创建粒子
        particle = EnhancedParticle(pos[0], pos[1], *random.choice(colors), (-4, 4), life_range, size_range, grav)
        # 覆盖速度，使用径向速度
        particle.vx = vx
        particle.vy = vy
        global_particles.append(particle)
def emit_particle_trail(count, pos, colors, vel_range=(-2, 2), life_range=(20, 40), size_range=(2, 5), grav=0.02):
    for _ in range(count): global_particles.append(EnhancedParticle(pos[0], pos[1], *random.choice(colors), vel_range, life_range, size_range, grav))
def create_shockwave(position): shockwaves.append(Shockwave(position[0], position[1]))

def draw_and_update_effects(surface):
    global global_particles, shockwaves
    
    # 优化：限制最大粒子数量，避免过多粒子导致卡顿
    max_particles = 100  # 设置最大粒子数量
    if len(global_particles) > max_particles:
        # 只保留最新的max_particles个粒子
        global_particles = global_particles[-max_particles:]
    
    # 更新和绘制粒子
    active_particles = []
    for p in global_particles:
        if p.lifespan > 0:
            p.update()
            active_particles.append(p)
            p.draw(surface)
    
    global_particles = active_particles
    
    # 更新和绘制冲击波
    active_shockwaves = []
    for sw in shockwaves:
        if sw.lifespan > 0:
            sw.update()
            active_shockwaves.append(sw)
            sw.draw(surface)
    
    shockwaves = active_shockwaves
    return surface

background_stars = []
def initialize_stars(w, h, n=250):
    global background_stars; background_stars = [{'x': random.randint(0, w), 'y': random.randint(0, h), 'b': random.uniform(0.4, 1.0), 'c': random.choice([(255,200,150),(200,255,150),(150,200,255),(255,150,255)]), 'ts': random.uniform(0.05,0.2), 'tp': random.uniform(0,6.28)} for _ in range(n)]
def draw_starry_background(img):
    if not background_stars or len(background_stars) != 250: initialize_stars(img.shape[1], img.shape[0])
    for i in range(img.shape[0]): cv2.line(img, (0, i), (img.shape[1], i), (int(60+40*(i/img.shape[0])), int(50-30*(i/img.shape[0])), int(20+40*(i/img.shape[0]))), 1)
    for s in background_stars:
        s['tp'] += s['ts']; t = (np.sin(s['tp'])+1)/2; c = tuple(int(c*s['b']*t) for c in s['c']); cv2.circle(img, (s['x'],s['y']), random.choice([1,2]), c, -1)
    return img

def draw_pulsing_sphere(surface, frame, cx, cy):
    r = 50 + 20 * np.sin(frame * 0.1)
    for i in range(200):
        a = (i/200)*6.28; R = r+random.uniform(-10,10); x,y=cx+R*np.cos(a),cy+R*np.sin(a); s=max(1,int(3*(R/70))); i=0.6+0.4*(R/70); c=(int(255*i),int(200*i),int(255*i)); cv2.circle(surface,(int(x),int(y)),s,c,-1)

def draw_startup_animation(img, frame):
    h, w, _ = img.shape
    cx, cy = w // 2, h // 2
    img = draw_starry_background(img)
    PULSE_END, S_START = 50, 70  # 减少脉冲动画和S形开始的帧数
    if frame < PULSE_END: draw_pulsing_sphere(img, frame, cx, cy)
    elif frame == PULSE_END:
            colors=[((255,255,220),(255,100,0)),((255,255,255),(255,50,0)),((255,200,100),(180,0,0))]
            # 将爆炸特效增大一倍，更加壮观
            emit_particle_burst(1000, (cx,cy), colors, vel_range=(-20,20), life_range=(100,150), size_range=(5,15), grav=0.01)
    if frame >= S_START:
        sf=frame-S_START; prog=min(sf/80.0,1.0); sl=int(400*prog); pts=[(int(cx+100*np.sin(i*0.02)),int(cy-200+i)) for i in range(sl)]
        if len(pts)>1:
            for i in range(1,len(pts)): cv2.line(img,pts[i-1],pts[i],(int(255*(1-i/400)),255,int(255*i/400)),int(15*(1-i/400)+5))
        if pts: head=pts[-1]; emit_particle_trail(2,head,[((255,255,255),(200,200,200))],vel_range=(-2,2),life_range=(20,40),size_range=(2,5),grav=0.02); cv2.circle(img,head,20,(255,255,255),-1); cv2.circle(img,head,30,(255,255,255),2)
    draw_and_update_effects(img)
    
    # 主加载文字
    text = "正在加载中..."
    font_size = 40
    # 使用改进的中文文本渲染函数
    try:
        img = put_chinese_text_pil(img, text, ((w - 150) // 2, cy + h // 3), font_size, tuple(int(255*min(frame/(PULSE_END+30),1.0)) for _ in range(3)))
    except Exception as e:
        print(f"加载动画文本渲染错误: {e}")
        # 备用方案
        cv2.putText(img, "Loading...", ((w - 150) // 2, cy + h // 3), cv2.FONT_HERSHEY_SIMPLEX, 1, tuple(int(255*min(frame/(PULSE_END+30),1.0)) for _ in range(3)), 2)
    
    # 在加载页面右下角添加按钮
    creator_text = "有建议请联系我"
    button_width = 180
    button_height = 40
    margin = 20
    # 按钮位置：右下角
    button_x = w - button_width - margin
    button_y = h - button_height - margin
    
    # 绘制按钮背景
    button_color = (100, 100, 100)  # 深灰色背景
    hover_color = (120, 120, 120)    # 悬停时颜色
    # 使用圆角矩形绘制按钮
    draw_rounded_rectangle(img, (button_x, button_y), (button_x + button_width, button_y + button_height), button_color, 8)
    
    # 在按钮上绘制文字
    creator_font_size = 20
    try:
        # 保持使用put_chinese_text_pil函数，但改进居中计算
        # 首先获取文字大小
        text_width, text_height = get_text_size(creator_text, creator_font_size)
        
        # 计算水平居中位置
        text_x = button_x + (button_width - text_width) // 2
        
        # 计算垂直居中位置，使用经验值确保中文正确显示且居中
        text_y = button_y + (button_height + text_height) // 2 - 18
        
        # 使用put_chinese_text_pil函数绘制文字，确保中文正确显示
        img = put_chinese_text_pil(img, creator_text, (text_x, text_y), creator_font_size, (255, 255, 255))
    except Exception as e:
        print(f"按钮文字渲染错误: {e}")
        # 备用方案，确保文字居中
        cv2.putText(img, creator_text, (button_x + (button_width - 80) // 2, button_y + button_height // 2 + 8), 
                    cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 255, 255), 2)
    return img

def draw_rounded_rectangle(img, top_left, bottom_right, color, radius, thickness=cv2.FILLED, line_type=cv2.LINE_AA):
    x1, y1 = top_left
    x2, y2 = bottom_right
    
    # 绘制矩形主体
    cv2.rectangle(img, (x1 + radius, y1), (x2 - radius, y2), color, thickness, line_type)
    cv2.rectangle(img, (x1, y1 + radius), (x2, y2 - radius), color, thickness, line_type)
    
    # 绘制圆角
    cv2.circle(img, (x1 + radius, y1 + radius), radius, color, thickness, line_type)
    cv2.circle(img, (x2 - radius, y1 + radius), radius, color, thickness, line_type)
    cv2.circle(img, (x1 + radius, y2 - radius), radius, color, thickness, line_type)
    cv2.circle(img, (x2 - radius, y2 - radius), radius, color, thickness, line_type)

def draw_mode_selection_screen(img, hovered_button=None, clicked_button=None):
    """绘制游戏模式选择界面，包括自定义中文按钮"""
    h,w,_=img.shape
    bg=draw_starry_background(np.zeros_like(img))
    

    title_text = "选择游戏模式"
    title_fs = 100  

    try:

        text_width, title_height = get_text_size(title_text, title_fs)
        title_x = (w - text_width) // 2
        title_y = h // 4  

        bg = put_chinese_text_pil(bg, title_text, (title_x, title_y), title_fs, (255, 255, 255))  
    except Exception as e:
        print(f"模式选择标题渲染错误: {e}")

        try:

            font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "utils", "fonts", "simhei.ttf")
            if os.path.exists(font_path):

                cv2.putText(bg, title_text, (title_x, title_y), cv2.FONT_HERSHEY_TRIPLEX, 3, (255, 255, 255), 8)  
            else:

                cv2.putText(bg, "Select Mode", (title_x, title_y), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255), 8)  
        except Exception as e2:
            print(f"备用方案也失败: {e2}")

            cv2.putText(bg, "Mode", (title_x, title_y), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255), 8)  
    

    button_width = 600  
    button_height = 120  
    button_spacing = 40
    start_y = h // 2 - 60  
    

    buttons = [
        {"id": "classic", "text": "经典模式", "color": (0, 128, 0), "hover_color": (0, 160, 0), "pos": (w // 2 - button_width - button_spacing // 2, start_y)},
        {"id": "hand_tracking", "text": "手势控制模式", "color": (50, 100, 200), "hover_color": (66, 116, 216), "pos": (w // 2 + button_spacing // 2, start_y)}
    ]
    
    for button in buttons:
        x, y = button["pos"]
        

        if button["id"] == clicked_button:

            button_color = (255, 215, 0)  
        elif button["id"] == hovered_button:

            button_color = button["hover_color"]
        else:

            button_color = button["color"]
        

        draw_rounded_rectangle(bg, (x, y), (x + button_width, y + button_height), button_color, 15)  
        

        try:
                text_size = 48  
                text_width, text_height = get_text_size(button["text"], text_size)

                text_x = x + (button_width - text_width) // 2

                text_y = y + (button_height + text_height) // 2 - 36  

                bg = put_chinese_text_pil(bg, button["text"], (text_x, text_y), text_size, (255, 255, 255))
        except Exception as e:
                print(f"按钮文字渲染错误: {e}")

                try:

                    text_width = len(button["text"]) * 30  
                    text_x = x + (button_width - text_width) // 2
                    cv2.putText(bg, button["text"], (text_x, y + button_height // 2 + 16), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1.6, (255, 255, 255), 4)  
                except Exception as e2:
                    print(f"按钮文字备用方案也失败: {e2}")

                    simple_text = button["id"]  
                    cv2.putText(bg, simple_text, (x + 20, y + 80), cv2.FONT_HERSHEY_SIMPLEX, 1.6, (255, 255, 255), 4)  
    

    bg = draw_and_update_effects(bg)

    return bg

def draw_settings_screen(img, current_color, mouse_pos=None, hovered_color=None):
    """绘制游戏设置界面，直接展示颜色块，不使用边框"""
    h, w, _ = img.shape
    bg = draw_starry_background(np.zeros_like(img))
    
    title_text = "自定义蛇颜色"
    title_fs = 60
    # 使用改进的中文文本渲染函数
    try:
        # 计算中文标题的准确位置
        title_width, title_height = get_text_size(title_text, title_fs)
        title_x = (w - title_width) // 2
        title_y = h // 10 
        # 确保中文标题能正确显示
        bg = put_chinese_text_pil(bg, title_text, (title_x, title_y), title_fs, (255, 255, 255))
    except Exception as e:
        print(f"设置标题渲染错误: {e}")
        # 备用方案：使用系统默认中文字体
        try:
            # 使用cv2.putText的中文支持
            cv2.putText(bg, title_text, ((w - 300) // 2, h // 6), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
        except Exception as e2:
            print(f"设置标题备用方案也失败: {e2}")
            # 最后尝试使用英文标题
            cv2.putText(bg, "Customize Snake Color", ((w - 350) // 2, h // 6), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)

    solid_colors = [
        (255, 182, 193), (144, 238, 144), (173, 216, 230), (255, 255, 0),  # 粉色, 浅绿, 浅蓝, 黄色
        (255, 165, 0), (128, 0, 128), (255, 255, 255), (128, 128, 128),  # 橙色, 紫色, 白色, 灰色
        (255, 0, 0), (0, 255, 255), (255, 0, 255), (50, 205, 50),      # 红色, 青色, 品红, 翠绿
        (0, 128, 128), (0, 0, 128), (255, 215, 0), (192, 192, 192)      # 青色, 海军蓝, 金色, 银色
    ]
    solid_color_names = [
        "粉色", "浅绿", "浅蓝", "黄色",
        "橙色", "紫色", "白色", "灰色",
        "红色", "青色", "品红", "翠绿",
        "青色", "海军蓝", "金色", "银色"
    ]

    block_size = 80
    spacing = 20 # 减小间距
    text_height_offset = 25 # 文本下方偏移
    name_fs = 20

    # --- 纯色 ---
    solid_grid_cols = 8
    solid_grid_rows = len(solid_colors) // solid_grid_cols
    solid_grid_width = solid_grid_cols * block_size + (solid_grid_cols - 1) * spacing
    solid_start_x = (w - solid_grid_width) // 2
    solid_start_y = 200  # 增大这个值，将颜色块下移，不覆盖标题文字

    # 存储颜色块位置，用于鼠标点击检测
    color_blocks = []

    for i, color in enumerate(solid_colors):
        row = i // solid_grid_cols
        col = i % solid_grid_cols
        x = solid_start_x + (col * (block_size + spacing))
        y = solid_start_y + (row * (block_size + text_height_offset + spacing))

        bgr_color = (color[2], color[1], color[0])
        # 直接绘制颜色块，不使用边框
        cv2.rectangle(bg, (x, y), (x + block_size, y + block_size), bgr_color, -1)
        
        # 如果是当前选中的颜色，添加一个淡色边框
        if color == current_color:
            cv2.rectangle(bg, (x, y), (x + block_size, y + block_size), (255, 255, 255), 3)
        
        # 如果鼠标悬停在当前颜色块上，添加一个白色边框
        if mouse_pos and x <= mouse_pos[0] <= x + block_size and y <= mouse_pos[1] <= y + block_size:
            cv2.rectangle(bg, (x, y), (x + block_size, y + block_size), (255, 255, 255), 3)
        
        # 添加颜色块位置和颜色信息
        color_blocks.append((x, y, x + block_size, y + block_size, color, "solid", solid_color_names[i]))
        
        name = solid_color_names[i]
        # 使用改进的中文文本渲染函数
        try:
            bg = put_chinese_text_pil(bg, name, (x + (block_size - 50)//2, y + block_size + 5), name_fs, (255, 255, 255))
        except Exception as e:
            print(f"颜色名称渲染错误: {e}")
            # 备用方案
            cv2.putText(bg, name, (x + (block_size - 50)//2, y + block_size + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    # --- 渐变色 ---
    gradient_grid_cols = 4 # 渐变色保持4列
    gradient_display_height = block_size
    gradient_start_y = solid_start_y + solid_grid_rows * (block_size + text_height_offset + spacing) + 50

    grad_title_text = "渐变颜色"
    grad_title_fs = 40
    # 使用改进的中文文本渲染函数
    try:
        # 计算中文标题的准确位置
        grad_title_width, grad_title_height = get_text_size(grad_title_text, grad_title_fs)
        grad_title_x = (w - grad_title_width) // 2
        grad_title_y = gradient_start_y - 40
        # 确保渐变颜色标题能正确显示
        bg = put_chinese_text_pil(bg, grad_title_text, (grad_title_x, grad_title_y), grad_title_fs, (255, 255, 255))
    except Exception as e:
        print(f"渐变颜色标题渲染错误: {e}")
        # 备用方案：使用系统默认中文字体
        try:
            # 使用cv2.putText的中文支持
            cv2.putText(bg, grad_title_text, ((w - 150) // 2, gradient_start_y - 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        except Exception as e2:
            print(f"渐变颜色标题备用方案也失败: {e2}")
            # 最后尝试使用英文标题
            cv2.putText(bg, "Gradient Colors", ((w - 200) // 2, gradient_start_y - 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    gradient_grid_width = gradient_grid_cols * block_size + (gradient_grid_cols - 1) * spacing
    gradient_actual_start_x = (w - gradient_grid_width) // 2

    # 使用中文渐变颜色名称，与gradient_colors_data的键对应
    gradient_color_names = ["彩虹", "蓝绿渐变", "火热渐变", "宇宙渐变"]

    for i, (grad_name, grad_value) in enumerate(gradient_colors_data.items()):
        col = i % gradient_grid_cols
        row = i // gradient_grid_cols
        x = gradient_actual_start_x + (col * (block_size + spacing))
        y = gradient_start_y + (row * (gradient_display_height + text_height_offset + spacing))

        # 绘制渐变颜色块
        if grad_name == "彩虹":
            # 对于彩虹色，绘制一个彩色渐变条
            for j in range(block_size):
                # 创建彩虹渐变效果，确保hue值在0-255范围内
                hue = int(359 * j / block_size)  # 使用359代替360，确保最大值为359
                r, g, b = cv2.cvtColor(np.array([[[hue, 255, 255]]], dtype=np.uint8), cv2.COLOR_HSV2RGB)[0][0]
                # 将RGB值转换为整数
                r, g, b = int(r), int(g), int(b)
                cv2.line(bg, (x + j, y), (x + j, y + gradient_display_height), (b, g, r), 1)
        else:
            # 对于双色渐变，绘制两半
            color1_bgr = (grad_value[0][2], grad_value[0][1], grad_value[0][0])
            color2_bgr = (grad_value[1][2], grad_value[1][1], grad_value[1][0])
            cv2.rectangle(bg, (x + block_size // 2, y), (x + block_size, y + gradient_display_height), color2_bgr, -1)
            cv2.rectangle(bg, (x, y), (x + block_size // 2, y + gradient_display_height), color1_bgr, -1)

        # 如果是当前选中的渐变颜色，添加一个淡色边框
        if isinstance(current_color, str) and current_color == grad_name:
            cv2.rectangle(bg, (x, y), (x + block_size, y + gradient_display_height), (255, 255, 255), 3)
        
        # 如果鼠标悬停在当前渐变颜色块上，添加一个白色边框
        if mouse_pos and x <= mouse_pos[0] <= x + block_size and y <= mouse_pos[1] <= y + gradient_display_height:
            cv2.rectangle(bg, (x, y), (x + block_size, y + gradient_display_height), (255, 255, 255), 3)
        
        # 添加渐变颜色块位置和颜色信息
        color_blocks.append((x, y, x + block_size, y + gradient_display_height, grad_name, "gradient", gradient_color_names[i]))
        
        # 使用改进的中文文本渲染函数
        try:
            bg = put_chinese_text_pil(bg, gradient_color_names[i], (x + (block_size - 70)//2, y + gradient_display_height + 5), name_fs, (255, 255, 255))
        except Exception as e:
            print(f"渐变名称渲染错误: {e}")
            # 备用方案
            cv2.putText(bg, gradient_color_names[i], (x + (block_size - 70)//2, y + gradient_display_height + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    # 按钮配置
    button_width = 200
    button_height = 50
    button_spacing = 40
    button_y = h - 120
    
    # 计算两个按钮的位置，并排居中显示
    total_buttons_width = button_width * 2 + button_spacing
    start_x = (w - total_buttons_width) // 2
    
    # 确定按钮
    confirm_button_rect = pygame.Rect(start_x, button_y, button_width, button_height)
    cv2.rectangle(bg, (confirm_button_rect.x, confirm_button_rect.y), (confirm_button_rect.x + confirm_button_rect.width, confirm_button_rect.y + confirm_button_rect.height), (0, 128, 0), -1)
    # 检查鼠标是否悬停在确定按钮上
    if mouse_pos and confirm_button_rect.collidepoint(mouse_pos):
        cv2.rectangle(bg, (confirm_button_rect.x, confirm_button_rect.y), (confirm_button_rect.x + confirm_button_rect.width, confirm_button_rect.y + confirm_button_rect.height), (0, 160, 0), -1)
    # 绘制确定按钮文字
    try:
        # 计算确定按钮文字的居中位置
        text_width, text_height = get_text_size("确定", 24)
        text_x = confirm_button_rect.x + (button_width - text_width) // 2
        # 调整Y坐标计算，确保文字在按钮内居中显示
        text_y = confirm_button_rect.y + button_height // 9 + text_height // 4
        bg = put_chinese_text_pil(bg, "确定", (text_x, text_y), 24, (255, 255, 255))
    except Exception as e:
        print(f"确定按钮文字渲染错误: {e}")
        # 确保文字居中
        cv2.putText(bg, "确定", (confirm_button_rect.x + (button_width - 30) // 2, confirm_button_rect.y + button_height // 2 + 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    # 添加确定按钮到颜色块列表
    color_blocks.append((confirm_button_rect.x, confirm_button_rect.y, confirm_button_rect.x + confirm_button_rect.width, confirm_button_rect.y + confirm_button_rect.height, "confirm", "button", "确定"))
    
    # 返回主菜单按钮
    menu_button_rect = pygame.Rect(start_x + button_width + button_spacing, button_y, button_width, button_height)
    cv2.rectangle(bg, (menu_button_rect.x, menu_button_rect.y), (menu_button_rect.x + menu_button_rect.width, menu_button_rect.y + menu_button_rect.height), (100, 100, 100), -1)
    # 检查鼠标是否悬停在返回主菜单按钮上
    if mouse_pos and menu_button_rect.collidepoint(mouse_pos):
        cv2.rectangle(bg, (menu_button_rect.x, menu_button_rect.y), (menu_button_rect.x + menu_button_rect.width, menu_button_rect.y + menu_button_rect.height), (120, 120, 120), -1)
    # 绘制返回主菜单按钮文字
    try:
        # 计算返回主菜单按钮文字的居中位置
        text_width, text_height = get_text_size("返回主菜单", 24)
        text_x = menu_button_rect.x + (button_width - text_width) // 2
        # 调整Y坐标计算，确保文字在按钮内居中显示
        text_y = menu_button_rect.y + button_height // 9 + text_height // 4
        bg = put_chinese_text_pil(bg, "返回主菜单", (text_x, text_y), 24, (255, 255, 255))
    except Exception as e:
        print(f"返回主菜单按钮文字渲染错误: {e}")
        # 确保文字居中
        cv2.putText(bg, "返回主菜单", (menu_button_rect.x + (button_width - 100) // 2, menu_button_rect.y + button_height // 2 + 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    # 添加返回主菜单按钮到颜色块列表
    color_blocks.append((menu_button_rect.x, menu_button_rect.y, menu_button_rect.x + menu_button_rect.width, menu_button_rect.y + menu_button_rect.height, "menu", "button", "返回主菜单"))

    return bg, color_blocks

def draw_game_over_screen(img,score):
    h,w,_=img.shape
    bg=draw_starry_background(np.zeros_like(img))

    try:
        # 使用改进的中文文本渲染函数
        bg = put_rainbow_text_pil(bg, "游戏结束", ((w - 200) // 2, h // 3), 80)
        bg = put_chinese_text_pil(bg, f"得分: {score}", ((w - 150) // 2, h // 2), 60, (0, 255, 255))

    except Exception as e:
        # 如果中文文本失败，则使用英文文本作为后备
        cv2.putText(bg, "Game Over", ((w - 200) // 2, h // 3), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255), 3)
        cv2.putText(bg, f"Score: {score}", ((w - 150) // 2, h // 2), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 255), 2)
        cv2.putText(bg, "Press 'R' to Restart", ((w - 250) // 2, h // 2 + 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    return bg
    
def draw_score(img,score): 
    try:
        # 使用改进的中文文本渲染函数
        return put_chinese_text_pil(img, f"得分: {score}", (50, 50), 40, (255, 255, 255))
    except Exception as e:
        # 如果中文文本失败，则使用英文文本作为后备
        img_copy = img.copy()
        cv2.putText(img_copy, f"Score: {score}", (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
        return img_copy