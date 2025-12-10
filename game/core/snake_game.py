import math
import random
import os
import cvzone
import cv2
import numpy as np

from game.utils.improved_chinese_text import put_chinese_text_with_background, put_chinese_text_pil
from game.utils.language_manager import get_translation

class SnakeGame:
    def __init__(self, food_path, width=1280, height=720, snake_color=(200,0,200), gradient_colors_data=None):
        self.width, self.height = width, height
        self.points = []            
        self.lengths = []           
        self.currentLength = 0      
        self.base_allowed_length = 150    
        self.allowedLength = self.base_allowed_length    
        self.previousHead = 0, 0    
        self.snake_color = snake_color  
        self.gradient_colors_data = gradient_colors_data if gradient_colors_data is not None else {}  


        self.imgFood = cv2.imread(food_path, cv2.IMREAD_UNCHANGED)
        if self.imgFood is None:

            self.imgFood = np.zeros((50, 50, 4), dtype=np.uint8)
            cv2.circle(self.imgFood, (25, 25), 25, (0, 255, 255, 255), cv2.FILLED)
        self.hFood, self.wFood, _ = self.imgFood.shape
        self.foodPoint = 0, 0
        self.randomFoodLocation()


        self.obstacles = []
        

        obstacle_files = ['780.png', 'R-C.png', '780.png', 'R-C.png', '780.png', 'R-C.png']
        

        fixed_obstacle_size = (80, 80)  
        
        for file in obstacle_files:
            img_path = os.path.join(os.path.dirname(__file__), '..', 'assets', file)
            img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
            if img is not None:

                img_resized = cv2.resize(img, fixed_obstacle_size)
                

                if len(img_resized.shape) == 3 and img_resized.shape[2] == 3:

                    img_resized = cv2.cvtColor(img_resized, cv2.COLOR_RGB2RGBA)
                
                self.obstacles.append({
                    'image': img_resized,
                    'x': random.randint(100, self.width - fixed_obstacle_size[0] - 100),
                    'y': random.randint(100, self.height - fixed_obstacle_size[1] - 100),
                    'width': fixed_obstacle_size[0],
                    'height': fixed_obstacle_size[1]
                })

        self.score = 0
        self.gameOver = False
        self.return_to_menu = False  
        

        self.obstacle_refresh_timer = 0  
        self.obstacle_refresh_interval = 600  

    def randomFoodLocation(self):

        screen_margin = 50
        self.foodPoint = random.randint(screen_margin + 50, self.width - screen_margin - 50), \
                         random.randint(screen_margin + 50, self.height - screen_margin - 50)
    
    def create_particle_border(self, imgMain):
        """创建静态边框"""
        screen_margin = 50
        
        # 绘制静态边框，提醒玩家边缘地带
        border_color = (255, 0, 255)  # 紫色边框
        border_thickness = 3  # 边框厚度
        
        # 绘制主边框
        cv2.rectangle(imgMain, (screen_margin, screen_margin), 
                     (self.width - screen_margin, self.height - screen_margin), 
                     border_color, border_thickness, cv2.LINE_AA)
        
        # 在边框角落添加装饰点
        corner_size = 5
        corner_color = (0, 255, 0)  # 绿色角落
        cv2.circle(imgMain, (screen_margin, screen_margin), corner_size, corner_color, cv2.FILLED)
        cv2.circle(imgMain, (self.width - screen_margin, screen_margin), corner_size, corner_color, cv2.FILLED)
        cv2.circle(imgMain, (screen_margin, self.height - screen_margin), corner_size, corner_color, cv2.FILLED)
        cv2.circle(imgMain, (self.width - screen_margin, self.height - screen_margin), corner_size, corner_color, cv2.FILLED)
        
        # 添加文字提示
        border_text = "边缘地带"
        try:
            from game.utils.improved_chinese_text import put_chinese_text_pil
            imgMain = put_chinese_text_pil(imgMain, border_text, (screen_margin + 10, screen_margin + 10), 20, border_color)
        except Exception as e:
            # 如果中文文字渲染失败，使用英文或不显示
            pass

    def reset(self):
        self.points = []
        self.lengths = []
        self.currentLength = 0
        self.allowedLength = self.base_allowed_length
        self.previousHead = 0, 0
        self.score = 0
        self.gameOver = False
        self.return_to_menu = False  # 重置返回主菜单标志
        self.randomFoodLocation()
        
        # 重置障碍物位置
        for obstacle in self.obstacles:
            obstacle['x'] = random.randint(100, self.width - obstacle['width'] - 100)
            obstacle['y'] = random.randint(100, self.height - obstacle['height'] - 100)

    def update(self, imgMain, currentHead, mouse_pos=None, mouse_clicked=False, high_score=0):
        if self.gameOver:
            # 获取屏幕尺寸
            screen_height, screen_width, _ = imgMain.shape
            center_x = screen_width // 2
            center_y = screen_height // 2
            
            # 绘制游戏结束画面，所有文字居中显示
            
            # 绘制"游戏结束"文字，位置居中
            game_over_text = get_translation('game_end')
            game_over_font_size = 80
            # 使用put_chinese_text_with_background函数的自动居中特性，文字不会超出框外
            imgMain = put_chinese_text_with_background(imgMain, game_over_text, 
                                                     (center_x - 220, center_y - 150), 
                                                     game_over_font_size, (255, 255, 255), (0, 0, 0))
            
            # 绘制得分文字，位置居中
            score_text = get_translation('game_final_score').format(self.score)
            score_font_size = 60
            # 使用put_chinese_text_with_background函数的自动居中特性，文字不会超出框外
            imgMain = put_chinese_text_with_background(imgMain, score_text, 
                                                     (center_x - 200, center_y - 50), 
                                                     score_font_size, (255, 255, 255), (0, 0, 0))
            
            # 按钮配置
            button_width = 180  # 减小按钮宽度，适应三个按钮
            button_height = 80
            button_spacing = 30  # 调整按钮间距
            button_y = center_y + 50  # 调整按钮垂直位置
            
            # 计算三个按钮的位置，并排居中显示
            total_buttons_width = button_width * 3 + button_spacing * 2
            start_x = center_x - total_buttons_width // 2
            
            # 重新开始按钮
            restart_button_x = start_x
            
            # 返回主菜单按钮
            menu_button_x = start_x + button_width + button_spacing
            
            # 退出游戏按钮
            exit_button_x = start_x + button_width * 2 + button_spacing * 2
            
            # 检测按钮点击
            if mouse_clicked and mouse_pos:
                # 检测重新开始按钮点击
                if restart_button_x <= mouse_pos[0] <= restart_button_x + button_width and button_y <= mouse_pos[1] <= button_y + button_height:
                    self.reset()
                # 检测返回主菜单按钮点击
                elif menu_button_x <= mouse_pos[0] <= menu_button_x + button_width and button_y <= mouse_pos[1] <= button_y + button_height:
                    self.return_to_menu = True
                # 检测退出游戏按钮点击
                elif exit_button_x <= mouse_pos[0] <= exit_button_x + button_width and button_y <= mouse_pos[1] <= button_y + button_height:
                    # 退出游戏，通过抛出SystemExit异常
                    import sys
                    sys.exit()
            
            # 从game_ui导入get_text_size函数用于精确计算文字尺寸
            from game.core.game_ui import get_text_size
            
            # 绘制重新开始按钮
            cv2.rectangle(imgMain, (restart_button_x, button_y), (restart_button_x + button_width, button_y + button_height), (0, 150, 0), cv2.FILLED)
            cv2.rectangle(imgMain, (restart_button_x, button_y), (restart_button_x + button_width, button_y + button_height), (255, 255, 255), 3)
            # 精确计算文字位置
            text = "重新开始"
            font_size = 35
            text_width, text_height = get_text_size(text, font_size)
            restart_text_x = restart_button_x + (button_width - text_width) // 2  # 精确水平居中
            restart_text_y = button_y + (button_height + text_height) // 2 - 30 # 精确垂直居中
            imgMain = put_chinese_text_pil(imgMain, text, 
                                         (restart_text_x, restart_text_y), 
                                         font_size, (255, 255, 255))
            
            # 绘制返回主菜单按钮
            cv2.rectangle(imgMain, (menu_button_x, button_y), (menu_button_x + button_width, button_y + button_height), (50, 100, 200), cv2.FILLED)
            cv2.rectangle(imgMain, (menu_button_x, button_y), (menu_button_x + button_width, button_y + button_height), (255, 255, 255), 3)
            # 精确计算文字位置
            text = "返回主菜单"
            font_size = 32
            text_width, text_height = get_text_size(text, font_size)
            menu_text_x = menu_button_x + (button_width - text_width) // 2  # 精确水平居中
            menu_text_y = button_y + (button_height + text_height) // 2 - 30  # 精确垂直居中
            imgMain = put_chinese_text_pil(imgMain, text, 
                                         (menu_text_x, menu_text_y), 
                                         font_size, (255, 255, 255))
            
            # 绘制退出游戏按钮
            cv2.rectangle(imgMain, (exit_button_x, button_y), (exit_button_x + button_width, button_y + button_height), (200, 50, 50), cv2.FILLED)
            cv2.rectangle(imgMain, (exit_button_x, button_y), (exit_button_x + button_width, button_y + button_height), (255, 255, 255), 3)
            # 精确计算文字位置
            text = "退出游戏"
            font_size = 35
            text_width, text_height = get_text_size(text, font_size)
            exit_text_x = exit_button_x + (button_width - text_width) // 2  # 精确水平居中
            exit_text_y = button_y + (button_height + text_height) // 2 - 30  # 精确垂直居中
            imgMain = put_chinese_text_pil(imgMain, text, 
                                         (exit_text_x, exit_text_y), 
                                         font_size, (255, 255, 255))
        else:
            # 障碍物刷新逻辑 - 放在外层，确保计时器持续更新
            self.obstacle_refresh_timer += 1
            if self.obstacle_refresh_timer >= self.obstacle_refresh_interval:
                print("刷新障碍物位置")
                
                # 刷新所有障碍物位置，确保不重叠
                for obstacle in self.obstacles:
                    # 生成随机位置，确保不重叠且不与食物重叠
                    max_attempts = 100
                    for _ in range(max_attempts):
                        new_x = random.randint(100, self.width - obstacle['width'] - 100)
                        new_y = random.randint(100, self.height - obstacle['height'] - 100)
                        
                        # 检查是否与其他障碍物重叠
                        overlap = False
                        for other_obstacle in self.obstacles:
                            # 使用id()函数比较，避免比较包含numpy数组的字典
                            if id(other_obstacle) != id(obstacle):
                                if (new_x < other_obstacle['x'] + other_obstacle['width'] and
                                    new_x + obstacle['width'] > other_obstacle['x'] and
                                    new_y < other_obstacle['y'] + other_obstacle['height'] and
                                    new_y + obstacle['height'] > other_obstacle['y']):
                                    overlap = True
                                    break
                        
                        # 检查是否与食物重叠
                        rx, ry = self.foodPoint
                        if (new_x < rx + self.wFood // 2 and
                            new_x + obstacle['width'] > rx - self.wFood // 2 and
                            new_y < ry + self.hFood // 2 and
                            new_y + obstacle['height'] > ry - self.hFood // 2):
                            overlap = True
                        
                        if not overlap:
                            obstacle['x'] = new_x
                            obstacle['y'] = new_y
                            break
                
                # 重置计时器
                self.obstacle_refresh_timer = 0
            
            if currentHead:
                px, py = self.previousHead
                cx, cy = currentHead

                self.points.append([cx, cy])  
                
                # 只有当points列表有两个或以上点时才计算距离，避免初始距离过大
                if len(self.points) > 1:
                    distance = math.hypot(cx - px, cy - py)  # 两点之间的距离
                    self.lengths.append(distance)            # 添加蛇的距离列表内容
                    self.currentLength += distance
                    
                    # Length Reduction 收缩长度
                    if self.currentLength > self.allowedLength:
                        for i, length in enumerate(self.lengths):
                            self.currentLength -= length
                            self.lengths.pop(i)
                            self.points.pop(i)
                            if self.currentLength < self.allowedLength:
                                break
                
                self.previousHead = cx, cy

                # Check if snake ate the food 是否吃了食物
                rx, ry = self.foodPoint
                if rx - self.wFood // 2 < cx < rx + self.wFood // 2 and \
                        ry - self.hFood // 2 < cy < ry + self.hFood // 2:
                    self.randomFoodLocation()
                    self.allowedLength += 50
                    self.score += 1
                    print(self.score)

                # Draw Snake 画蛇
                if self.points:
                    # 确定蛇的颜色
                    snake_color = self.snake_color
                    if isinstance(snake_color, str):
                        # 如果是渐变颜色名称，使用默认颜色
                        snake_color = (200, 0, 200)
                    
                    for i, point in enumerate(self.points):
                         if i != 0:
                            self.points[i-1] = tuple(self.points[i-1])
                            self.points[i] = tuple(self.points[i])
                            cv2.line(imgMain, self.points[i - 1], self.points[i], snake_color, 20)
                    # 对列表最后一个点也就是蛇头使用相同颜色
                    self.points[-1] = tuple(self.points[-1])
                    cv2.circle(imgMain, self.points[-1], 20, snake_color, cv2.FILLED)

                # Draw Food 画食物
                imgMain = cvzone.overlayPNG(imgMain, self.imgFood, (rx - self.wFood // 2, ry - self.hFood // 2))

                # Draw Obstacles 画障碍物
                for obstacle in self.obstacles:
                    imgMain = cvzone.overlayPNG(imgMain, obstacle['image'], (obstacle['x'], obstacle['y']))

                # 显示中文得分
                imgMain = put_chinese_text_with_background(imgMain, get_translation('game_score').format(self.score), (50, 80), 40, (50, 130, 246), (0, 0, 0))

                # 获取实际图像尺寸，确保边框适应实际屏幕大小
                actual_height, actual_width, _ = imgMain.shape
                
                # 绘制屏幕边缘边框，提醒玩家，使用实际图像尺寸
                border_thickness = 4
                border_color = (255, 255, 0)  # 黄色边框
                cv2.rectangle(imgMain, (0, 0), (actual_width, actual_height), border_color, border_thickness)
                
                # Check for Collision - 修改后的碰撞检测：只有碰到障碍物和边框才死亡
                if not self.gameOver:  # 只在游戏未结束时检测
                    snake_radius = 20  # 蛇头半径
                    
                    # 1. 检查是否碰到障碍物
                    obstacle_collision = False
                    for obstacle in self.obstacles:
                        if obstacle['x'] - snake_radius < cx < obstacle['x'] + obstacle['width'] + snake_radius and \
                           obstacle['y'] - snake_radius < cy < obstacle['y'] + obstacle['height'] + snake_radius:
                            print("撞到障碍物")
                            obstacle_collision = True
                            break
                    
                    if obstacle_collision:
                        self.gameOver = True
                    # 2. 检查是否碰到屏幕边缘 - 优化：考虑蛇的大小，使用实际图像尺寸
                    elif (cx - snake_radius < 0 or 
                          cx + snake_radius > actual_width or 
                          cy - snake_radius < 0 or 
                          cy + snake_radius > actual_height):
                        print("撞到屏幕边缘")
                        self.gameOver = True
                    # 移除碰到自己死亡的判定，只有碰到障碍物和边框才死亡
        
            # 创建动态粒子边框
            self.create_particle_border(imgMain)
            
            # 在左上角显示历史最高分数和本次分数累计进度
            imgMain = put_chinese_text_with_background(imgMain, get_translation('game_high_score').format(high_score), (50, 150), 30, (50, 130, 246), (0, 0, 0))
            imgMain = put_chinese_text_with_background(imgMain, get_translation('game_score').format(self.score), (50, 200), 30, (50, 130, 246), (0, 0, 0))
        
        return imgMain
