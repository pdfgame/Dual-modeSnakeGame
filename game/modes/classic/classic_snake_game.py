import pygame
import random
import math
import numpy as np
import time


try:
    import moderngl as mgl
    MODERNGL_AVAILABLE = True
except ImportError:
    MODERNGL_AVAILABLE = False

from core.game_ui import emit_particle_burst, draw_and_update_effects

class ClassicSnakeGame:
    def __init__(self, snake_color=(255, 182, 193), width=1280, height=720, gradient_colors_data=None): # 增加gradient_colors_data参数
        self.WHITE, self.BLACK = (255,255,255), (0,0,0)
        self.snake_color = snake_color
        self.FOOD_COLORS = [((255,105,180),(255,200,220)), ((135,206,250),(200,230,255)), ((255,255,0),(255,255,200))]
        self.width, self.height, self.grid_size = width, height, 30

        self.grid_width = max(1, (self.width - 20) // self.grid_size)
        self.grid_height = max(1, (self.height - 20) // self.grid_size)
        
        from game.utils.improved_chinese_text import get_font_path
        font_path = get_font_path()
        if font_path:
            try:
                self.font_large = pygame.font.Font(font_path, 80)
                self.font_small = pygame.font.Font(font_path, 40)
            except Exception:
                self.font_large, self.font_small = pygame.font.Font(None, 80), pygame.font.Font(None, 40)
        else:
            self.font_large, self.font_small = pygame.font.Font(None, 80), pygame.font.Font(None, 40)
        
        self.high_score, self.score = 0, 0
        self.gradient_colors_data = gradient_colors_data if gradient_colors_data is not None else {} 

        self.last_countdown_update = 0  
        self.current_freeze_display = 0  
        self.boom_sound = None
        self.fail_sound = None
        self.reset()

    def reset(self):
        self.snake, self.direction = [(self.grid_width//2, self.grid_height//2)], (1,0)
        if self.score > self.high_score: self.high_score = self.score
        self.score, self.game_over, self.game_started = 0, False, False

        self.has_started = False

        self.game_over_reason = None

        self.base_move_interval = 0.2  
        self.move_interval = self.base_move_interval
        self.min_move_interval = 0.08  
        self.acceleration_time = 0  
        self.acceleration_duration = 0.5  
        self.last_move_time = 0

        self.food_blink_timer = 0
        self.food_blink_interval = 1.0  
        self.food_visible = True
        

        self.fake_foods = []
        self.fake_foods_colors = []
        self.fake_foods_age = []
        self.fake_foods_properties = []  
        

        self.effects = {
            'speed_up': 0,      
            'speed_down': 0,    
            'freeze': 0,        
            'color_change': False  
        }
        

        self.effect_display = None  
        

        self.obstacles = []
        self._generate_obstacles()
        


        self.foods = []  
        self.food_colors = []  
        self.is_double_score_foods = []  
        

        for _ in range(random.randint(2, 3)):
            pos, color = self._place_food()
            self.foods.append(pos)
            self.food_colors.append(color)
            self.is_double_score_foods.append(random.random() < 0.2)  
        

        self._generate_fake_foods()
        

        self.restart_button_rect = None
        self.menu_button_rect = None
        

        self.food_refresh_interval = 10.0  
        self.last_food_refresh_time = pygame.time.get_ticks() / 1000.0  
        

        self.last_countdown_update = 0  
        self.current_freeze_display = 0  
    
    def _generate_fake_foods(self):
        """生成多个假食物，增加游戏难度和多样性"""
        # 清除旧的假食物
        self.fake_foods = []
        self.fake_foods_colors = []
        self.fake_foods_age = []
        self.fake_foods_properties = []  # 存储每个假食物的属性
        
        # 增加假食物数量：生成20-28个假食物，提高游戏难度
        num_fake_foods = random.randint(20, 28)
        bomb_count = 0
        
        # 假食物属性列表和概率分布
        # 属性包括：炸弹、变色、加速、减速、冻结
        properties = ['bomb', 'color_change', 'speed_up', 'speed_down', 'freeze', 'none']
        # 概率分布：降低炸弹概率到10%，普通假食物占40%
        weights = [0.1, 0.15, 0.15, 0.15, 0.15, 0.3]
        
        for i in range(num_fake_foods):
            pos = self._place_fake_food()
            self.fake_foods.append(pos)
            
            # 随机选择假食物属性
            prop = random.choices(properties, weights=weights)[0]
            
            # 限制炸弹数量，每轮最多生成6个炸弹
            if prop == 'bomb' and bomb_count >= 6:
                prop = random.choice(['color_change', 'speed_up', 'speed_down', 'freeze', 'none'])
            elif prop == 'bomb':
                bomb_count += 1
            
            # 所有假食物都使用随机颜色，不根据属性区分
            # 创建一个包含多种颜色对的列表，用于随机选择
            all_colors = [
                ((255, 105, 180), (255, 200, 220)),  # 粉色
                ((135, 206, 250), (200, 230, 255)),  # 蓝色
                ((255, 255, 0), (255, 255, 200)),    # 黄色
                ((255, 69, 0), (255, 150, 100)),     # 橙色
                ((144, 238, 144), (200, 255, 200)),  # 浅绿色
                ((255, 182, 193), (255, 200, 210)),  # 浅粉色
                ((176, 224, 230), (200, 235, 240)),  # 浅蓝色
                ((221, 160, 221), (230, 180, 230)),  # 浅紫色
            ]
            
            # 随机选择一个颜色对
            food_color = random.choice(all_colors)
            self.fake_foods_colors.append(food_color)
            self.fake_foods_age.append(0)
            self.fake_foods_properties.append(prop)
    
    def _place_fake_food(self):
        """放置假食物"""
        while True:
            pos = (random.randint(0, self.grid_width-1), random.randint(0, self.grid_height-1))
            if pos not in self.snake and pos not in self.foods:
                return pos

    def _place_food(self):
        while True:
            pos = (random.randint(0, self.grid_width-1), random.randint(0, self.grid_height-1))

            if pos not in self.snake and pos not in self.obstacles and pos not in self.foods:
                return pos, random.choice(self.FOOD_COLORS)
    
    def _generate_obstacles(self):
        """生成随机障碍物，增加游戏难度"""
        # 清除旧的障碍物
        self.obstacles = []
        
        # 生成3-5个障碍物
        num_obstacles = random.randint(3, 5)
        for _ in range(num_obstacles):
            while True:
                # 随机生成障碍物位置
                obstacle_pos = (random.randint(0, self.grid_width-1), random.randint(0, self.grid_height-1))
                # 确保障碍物不会出现在蛇的初始位置
                if obstacle_pos != self.snake[0]:
                    self.obstacles.append(obstacle_pos)
                    break

    def handle_input(self, event):
        if not self.game_over:
            if event.type == pygame.KEYDOWN:
                if not self.game_started: 
                    self.game_started = True
                    self.has_started = True
                else:
                    # 检查是否处于冻结状态
                    if self.effects['freeze'] > 0:
                        # 冻结状态下不处理方向键输入，确保蛇纹丝不动
                        return
                
                # 保存当前方向
                old_direction = self.direction
                
                # 处理方向键输入
                if event.key in (pygame.K_UP, pygame.K_w):
                    if self.direction != (0, 1):
                        # 直接转向，允许掉头
                        self.direction = (0, -1)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    if self.direction != (0, -1):
                        # 直接转向，允许掉头
                        self.direction = (0, 1)
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    if self.direction != (1, 0):
                        # 直接转向，允许掉头
                        self.direction = (-1, 0)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    if self.direction != (-1, 0):
                        # 直接转向，允许掉头
                        self.direction = (1, 0)
        else:
            # 游戏结束时处理鼠标点击，不响应键盘事件
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = event.pos
                # 检查是否点击了重新开始按钮
                if self.restart_button_rect and self.restart_button_rect.collidepoint(mouse_x, mouse_y):
                    # 重新开始游戏
                    self.reset()
                # 检查是否点击了返回菜单按钮
                elif self.menu_button_rect and self.menu_button_rect.collidepoint(mouse_x, mouse_y):
                    # 设置游戏结束和未开始状态，由GameController处理返回菜单
                    self.game_over = False
                    self.game_started = False
                # 检查是否点击了退出游戏按钮
                elif hasattr(self, 'exit_button_rect') and self.exit_button_rect and self.exit_button_rect.collidepoint(mouse_x, mouse_y):
                    # 退出游戏
                    import sys
                    sys.exit()

    def update(self):
        if self.game_over or not self.game_started: return
        
        current_time = pygame.time.get_ticks()
        time_since_last_move = current_time - self.last_move_time
        delta_time = time_since_last_move / 1000.0  # 转换为秒
        
        # 更新各种效果的剩余时间
        for effect in self.effects:
            if effect != 'color_change' and self.effects[effect] > 0:
                self.effects[effect] -= delta_time
                # 确保效果时间不会为负数
                if self.effects[effect] < 0:
                    self.effects[effect] = 0
        
        # 根据蛇的长度动态调整速度
        # 蛇长度越长，速度越快，但有合理上限
        snake_length = len(self.snake)
        
        # 基础速度计算：初始速度0.2秒，每增加1段长度减少0.005秒
        # 初始长度为1，所以长度差为snake_length - 1
        length_based_speed = 0.2 - (snake_length - 1) * 0.005
        
        # 确保速度不超过合理上限（最小移动间隔）
        self.base_move_interval = max(self.min_move_interval, length_based_speed)
        
        # 应用效果
        current_move_interval = self.base_move_interval
        
        # 检查冻结效果
        freeze_effect = self.effects['freeze'] > 0
        if freeze_effect:
            # 如果处于冻结状态，不移动
            # 更新真食物闪烁
            blink_time = 0.3  # 固定闪烁时间（秒）
            self.food_visible = (current_time % (int(blink_time * 1000) * 2)) < int(blink_time * 1000)
        
        # 更新假食物年龄
        for i in range(len(self.fake_foods_age)):
            self.fake_foods_age[i] += delta_time * 0.01
        
        # 更新效果提示时间
        if self.effect_display:
            # 检查冻结效果是否已经结束
            if '冻结效果' in self.effect_display['text']:
                if self.effects['freeze'] <= 0:
                    self.effect_display = None
            else:
                # 其他效果提示按原逻辑更新
                self.effect_display['time'] -= 1
                if self.effect_display['time'] <= 0:
                    self.effect_display = None
        
        # 检查食物是否需要自动刷新
        current_time_sec = current_time / 1000.0
        if current_time_sec - self.last_food_refresh_time >= self.food_refresh_interval:
            # 重新生成真食物，支持多个真食物
            self.foods = []  # 清空现有真食物
            self.food_colors = []
            self.is_double_score_foods = []
            
            # 生成2-3个新的真食物
            for _ in range(random.randint(2, 3)):
                pos, color = self._place_food()
                self.foods.append(pos)
                self.food_colors.append(color)
                self.is_double_score_foods.append(random.random() < 0.2)  # 20%概率生成特殊食物
            
            # 重新生成假食物
            self._generate_fake_foods()
            # 更新上次刷新时间
            self.last_food_refresh_time = current_time_sec
        
        # 应用加速和减速效果
        if self.effects['speed_up'] > 0:
            # 加速效果：移动间隔减半
            current_move_interval = max(self.min_move_interval, self.base_move_interval * 0.5)
        elif self.effects['speed_down'] > 0:
            # 减速效果：移动间隔变为原来的25倍，更明显的减速
            current_move_interval = self.base_move_interval * 25
        elif self.acceleration_time > 0:
            # 同方向按键加速
            current_move_interval = max(self.min_move_interval, self.base_move_interval * 0.5)
            self.acceleration_time -= delta_time
            if self.acceleration_time <= 0:
                self.acceleration_time = 0
        
        # 独立的真食物闪烁更新，确保一直稳定闪烁
        blink_time = 0.3  # 固定闪烁时间（秒）
        # 使用当前时间的毫秒值取模，确保闪烁稳定
        self.food_visible = (current_time % (int(blink_time * 1000) * 2)) < int(blink_time * 1000)
        
        # 检查是否需要移动
        # 使用计算好的current_move_interval，确保加速和减速效果生效
        # 冻结状态下不移动
        # 重新计算当前时间，确保时间准确
        current_time_now = pygame.time.get_ticks()
        time_since_last_move_now = current_time_now - self.last_move_time
        
        if time_since_last_move_now >= current_move_interval * 1000 and not freeze_effect:
            self.last_move_time = current_time_now
            
            hx, hy = self.snake[0]; dx, dy = self.direction; nh = (hx+dx, hy+dy)
            
            # 修复碰撞检测，确保蛇不会移出屏幕边界或撞到障碍物
            if not (0 <= nh[0] < self.grid_width and 0 <= nh[1] < self.grid_height):
                # 碰到屏幕边缘
                self.game_over_reason = "碰到屏幕边缘"
                self.game_over = True
                # 播放游戏结束音效
                if self.fail_sound:
                    try:
                        self.fail_sound.play()
                    except Exception as e:
                        print(f"播放游戏结束音效失败: {e}")
            elif nh in self.snake:
                # 碰到自己身体
                self.game_over_reason = "碰到自己身体"
                self.game_over = True
                # 播放游戏结束音效
                if self.fail_sound:
                    try:
                        self.fail_sound.play()
                    except Exception as e:
                        print(f"播放游戏结束音效失败: {e}")
            elif nh in self.obstacles:
                # 碰到障碍物
                self.game_over_reason = "碰到障碍物"
                self.game_over = True
                # 播放游戏结束音效
                if self.fail_sound:
                    try:
                        self.fail_sound.play()
                    except Exception as e:
                        print(f"播放游戏结束音效失败: {e}")
            elif self._check_fake_foods():
                # 检查是否吃到炸弹
                # 播放游戏结束音效
                if self.fail_sound:
                    try:
                        self.fail_sound.play()
                    except Exception as e:
                        print(f"播放游戏结束音效失败: {e}")
            
            if self.game_over:
                # 实时更新最高分
                if self.score > self.high_score:
                    self.high_score = self.score
                return
            
            self.snake.insert(0, nh)
            
            # 检查是否吃到真食物
            food_eaten = False
            eaten_index = -1
            
            # 遍历所有真食物，检查是否吃到
            for i in range(len(self.foods)):
                if self.snake[0] == self.foods[i]:
                    food_eaten = True
                    eaten_index = i
                    break
            
            if food_eaten:
                # 吃到了真食物
                pos_px = (self.foods[eaten_index][0]*self.grid_size+self.grid_size//2+10, self.foods[eaten_index][1]*self.grid_size+self.grid_size//2+10)
                emit_particle_burst(30, pos_px, [self.food_colors[eaten_index]])
                
                # 播放吃到食物音效
                if self.boom_sound:
                    try:
                        self.boom_sound.play()
                    except Exception as e:
                        print(f"播放吃到食物音效失败: {e}")
                
                # 检查是否是分数翻倍食物
                if self.is_double_score_foods[eaten_index]:
                    if self.score == 0:  # 第一次吃食物
                        self.score += 1  # 先加1分
                        self.score *= 2
                    else:
                        self.score *= 2   # 然后分数翻倍
                    # 显示分数翻倍效果提示
                    self.effect_display = {'text': '分数翻倍！', 'time': 60, 'color': (255, 215, 0)}
                    # 在屏幕正上方添加粒子特效
                    screen_top_center = (self.width // 2, 50)
                    emit_particle_burst(30, screen_top_center, [((255, 215, 0), (255, 235, 150))])
                else:
                    # 普通食物：加1分
                    self.score += 1
                
                # 实时更新最高分
                if self.score > self.high_score:
                    self.high_score = self.score
                
                # 吃到真食物后，移除被吃掉的食物，并生成一个新的真食物
                self.foods.pop(eaten_index)
                self.food_colors.pop(eaten_index)
                self.is_double_score_foods.pop(eaten_index)
                
                # 生成新的真食物
                new_pos, new_color = self._place_food()
                self.foods.append(new_pos)
                self.food_colors.append(new_color)
                self.is_double_score_foods.append(random.random() < 0.2)  # 20%概率生成特殊食物
            
            # 检查是否吃到假食物或炸弹
            else:
                self._check_fake_foods()
                self.snake.pop()
        
        # 更新假食物年龄
        for i in range(len(self.fake_foods_age)):
            self.fake_foods_age[i] += delta_time * 0.01
    
    def _check_fake_foods(self):
        """检查假食物和炸弹，处理各种属性效果"""
        snake_head = self.snake[0]
        to_remove = []
        
        for i, fake_food in enumerate(self.fake_foods):
            if snake_head == fake_food:
                prop = self.fake_foods_properties[i]
                pos_px = (fake_food[0]*self.grid_size+self.grid_size//2+10, fake_food[1]*self.grid_size+self.grid_size//2+10)
                
                emit_particle_burst(20, pos_px, [self.fake_foods_colors[i]])
                
                # 播放吃到食物音效（炸弹除外）
                if prop != 'bomb' and self.boom_sound:
                    try:
                        self.boom_sound.play()
                    except Exception as e:
                        print(f"播放吃到食物音效失败: {e}")
                
                if prop == 'bomb':
                    self.game_over = True
                    self.game_over_reason = 'bomb'
                    # 播放游戏结束音效
                    if self.fail_sound:
                        try:
                            self.fail_sound.play()
                        except Exception as e:
                            print(f"播放游戏结束音效失败: {e}")
                    return True  # 吃到炸弹，返回True
                elif prop == 'color_change':
                    self.effects['color_change'] = True
                    from core.game_ui import gradient_colors_data
                    if random.random() < 0.5:
                        self.snake_color = random.choice([
                            (255, 182, 193), (144, 238, 144), (173, 216, 230), (255, 255, 0),
                            (255, 165, 0), (128, 0, 128), (255, 255, 255), (128, 128, 128),
                            (255, 0, 0), (0, 255, 255), (255, 0, 255), (50, 205, 50),
                            (0, 128, 128), (0, 0, 128), (255, 215, 0), (192, 192, 192)
                        ])
                    else:
                        self.snake_color = random.choice(list(gradient_colors_data.keys()))
                    self.effect_display = {'text': '变色效果', 'time': 60, 'color': (255, 0, 255)}
                    screen_top_center = (self.width // 2, 50)
                    emit_particle_burst(30, screen_top_center, [((255, 0, 255), (255, 150, 255))])
                elif prop == 'speed_up':
                    self.effects['speed_up'] = 5.0
                    self.score += 1
                    self.effect_display = {'text': '加速效果', 'time': 60, 'color': (0, 255, 0)}
                    screen_top_center = (self.width // 2, 50)
                    emit_particle_burst(30, screen_top_center, [((0, 255, 0), (150, 255, 150))])
                elif prop == 'speed_down':
                    self.effects['speed_down'] = 12.0
                    self.score = max(0, self.score - 1)  
                    self.effect_display = {'text': '减速效果！', 'time': 90, 'color': (0, 0, 255)}
                    screen_top_center = (self.width // 2, 50)
                    emit_particle_burst(30, screen_top_center, [((0, 0, 255), (150, 150, 255))])
                elif prop == 'freeze':
                    self.effects['freeze'] = 30.0
                    self.effect_display = {'text': '冻结效果', 'time': float('inf'), 'color': (0, 0, 255)}
                    screen_top_center = (self.width // 2, 50)
                    emit_particle_burst(30, screen_top_center, [((255, 255, 255), (200, 200, 200))])
                
                to_remove.append(i)
        
        for i in sorted(to_remove, reverse=True):
            self.fake_foods.pop(i)
            self.fake_foods_colors.pop(i)
            self.fake_foods_age.pop(i)
            self.fake_foods_properties.pop(i)
            
            pos = self._place_fake_food()
            self.fake_foods.append(pos)
            
            properties = ['bomb', 'color_change', 'speed_up', 'speed_down', 'freeze', 'none']
            weights = [0.1, 0.15, 0.15, 0.15, 0.15, 0.3]  
            prop = random.choices(properties, weights=weights)[0]
            
            bomb_count = sum(1 for p in self.fake_foods_properties if p == 'bomb')
            if prop == 'bomb' and bomb_count >= 12:
                prop = random.choice(['color_change', 'speed_up', 'speed_down', 'freeze', 'none'])
            
            all_colors = [
                ((255, 105, 180), (255, 200, 220)),  
                ((135, 206, 250), (200, 230, 255)),  
                ((255, 255, 0), (255, 255, 200)),    
                ((255, 69, 0), (255, 150, 100)),     
                ((144, 238, 144), (200, 255, 200)),  
                ((255, 182, 193), (255, 200, 210)),  
                ((176, 224, 230), (200, 235, 240)),  
                ((221, 160, 221), (230, 180, 230)),  
            ]
            food_color = random.choice(all_colors)
            self.fake_foods_colors.append(food_color)
            self.fake_foods_age.append(0)
            self.fake_foods_properties.append(prop)
        
        if len(self.fake_foods) < 4:
            needed = 4 - len(self.fake_foods)
            for _ in range(needed):
                pos = self._place_fake_food()
                self.fake_foods.append(pos)
                
                properties = ['bomb', 'color_change', 'speed_up', 'speed_down', 'freeze', 'none']
                weights = [0.1, 0.15, 0.15, 0.15, 0.15, 0.3]  
                prop = random.choices(properties, weights=weights)[0]
                
                bomb_count = sum(1 for p in self.fake_foods_properties if p == 'bomb')
                if prop == 'bomb' and bomb_count >= 12:
                    prop = random.choice(['color_change', 'speed_up', 'speed_down', 'freeze', 'none'])
                
                all_colors = [
                    ((255, 105, 180), (255, 200, 220)),  
                    ((135, 206, 250), (200, 230, 255)),  
                    ((255, 255, 0), (255, 255, 200)),    
                    ((255, 69, 0), (255, 150, 100)),     
                    ((144, 238, 144), (200, 255, 200)),  
                    ((255, 182, 193), (255, 200, 210)),  
                    ((176, 224, 230), (200, 235, 240)),  
                    ((221, 160, 221), (230, 180, 230)),  
                ]
                food_color = random.choice(all_colors)
                self.fake_foods_colors.append(food_color)
                self.fake_foods_age.append(0)
                self.fake_foods_properties.append(prop)
        
        return False  # 未吃到炸弹，返回False

    def _get_segment_color(self, segment_index, total_segments):
        """
        根据蛇的颜色类型（纯色或渐变名称）和蛇身段的位置计算颜色。
        """
        if isinstance(self.snake_color, (tuple, list)):
            return tuple(self.snake_color)

        grad_name = self.snake_color
        
        if grad_name == "彩虹":

            rainbow_colors = [
                (255,0,0), (255,127,0), (255,255,0), (0,255,0),
                (0,0,255), (75,0,130), (143,0,255)
            ]

            color_index = (segment_index * len(rainbow_colors)) // total_segments
            return rainbow_colors[color_index % len(rainbow_colors)]
        

        grad_data = self.gradient_colors_data.get(grad_name)
        if grad_data and isinstance(grad_data, tuple) and len(grad_data) == 2:
            start_color, end_color = grad_data

            t = segment_index / max(1, total_segments - 1)
            r = int(start_color[0] * (1 - t) + end_color[0] * t)
            g = int(start_color[1] * (1 - t) + end_color[1] * t)
            b = int(start_color[2] * (1 - t) + end_color[2] * t)
            return (r, g, b)
            
        return (255, 182, 193) 

    def draw(self, screen):

        screen.fill((240, 240, 240)) 
        grid_color = (220, 220, 220) 
        for x in range(10, self.width-10, self.grid_size):
            pygame.draw.line(screen, grid_color, (x, 10), (x, self.height-10))
        for y in range(10, self.height-10, self.grid_size):
            pygame.draw.line(screen, grid_color, (10, y), (self.width-10, y)) 


        border_color = (40, 40, 40) 
        pygame.draw.rect(screen, border_color, (0, 0, self.width, self.height), 10)


        if not self.game_over:
            obstacle_color = (100, 100, 100)  
            for obstacle_pos in self.obstacles:
                obstacle_rect = pygame.Rect(
                    obstacle_pos[0]*self.grid_size + 10,
                    obstacle_pos[1]*self.grid_size + 10,
                    self.grid_size,
                    self.grid_size
                )
                pygame.draw.rect(screen, obstacle_color, obstacle_rect, border_radius=8)

                cross_color = (70, 70, 70)  
                pygame.draw.line(screen, cross_color, 
                               (obstacle_rect.left + 5, obstacle_rect.top + 5), 
                               (obstacle_rect.right - 5, obstacle_rect.bottom - 5), 3)
                pygame.draw.line(screen, cross_color, 
                               (obstacle_rect.right - 5, obstacle_rect.top + 5), 
                               (obstacle_rect.left + 5, obstacle_rect.bottom - 5), 3)



        if not self.game_over:

            for i in range(len(self.foods)):
                food_pos = (self.foods[i][0]*self.grid_size+self.grid_size//2+10, self.foods[i][1]*self.grid_size+self.grid_size//2+10)
                
                if self.is_double_score_foods[i]:

                    gold_color = (255, 215, 0)

                    pygame.draw.circle(screen, gold_color, food_pos, self.grid_size//2, width=3)

                    if self.food_visible:
                        pygame.draw.circle(screen, gold_color, food_pos, self.grid_size//3)
                    else:
                        pygame.draw.circle(screen, gold_color, food_pos, self.grid_size//3, width=2)
                else:

                    if self.food_visible:
                        pygame.draw.circle(screen, self.food_colors[i][0], food_pos, self.grid_size//3)
                    else:
                        pygame.draw.circle(screen, self.food_colors[i][0], food_pos, self.grid_size//3, width=2)
            

            for i, fake_food in enumerate(self.fake_foods):

                fake_color = self.fake_foods_colors[i][0]
                pygame.draw.circle(screen, fake_color, (fake_food[0]*self.grid_size+self.grid_size//2+10, fake_food[1]*self.grid_size+self.grid_size//2+10), self.grid_size//3)
            
            total_segments = len(self.snake)

            is_frozen = self.effects['freeze'] > 0
            current_time_ms = pygame.time.get_ticks()
            
            for i, seg in enumerate(self.snake):
                snake_fill_color = self._get_segment_color(i, total_segments) 
                

                border_rect = pygame.Rect(seg[0]*self.grid_size+10, seg[1]*self.grid_size+10, self.grid_size, self.grid_size)
                

                inner_rect = pygame.Rect(seg[0]*self.grid_size + 2+10, seg[1]*self.grid_size + 2+10, self.grid_size - 4, self.grid_size - 4)
                
                if is_frozen:

                    

                    ice_color = (150, 200, 255, 180)  
                    ice_surface = pygame.Surface((border_rect.width, border_rect.height), pygame.SRCALPHA)
                    

                    pygame.draw.rect(ice_surface, (200, 230, 255, 220), pygame.Rect(0, 0, border_rect.width, border_rect.height), border_radius=8, width=2)
                    

                    if isinstance(snake_fill_color, tuple):

                        frozen_color = (max(0, min(255, snake_fill_color[0] // 3 + 80)), 
                                      max(0, min(255, snake_fill_color[1] // 3 + 100)), 
                                      max(0, min(255, snake_fill_color[2] + 120)))
                    else:

                        frozen_color = (80, 150, 255)
                    

                    inner_ice_rect = pygame.Rect(2, 2, border_rect.width - 4, border_rect.height - 4)
                    pygame.draw.rect(ice_surface, frozen_color, inner_ice_rect, border_radius=6)
                    


                    sparkle_color = (255, 255, 255, 200)
                    for _ in range(3):
                        sparkle_x = random.randint(1, border_rect.width - 2)
                        sparkle_y = random.randint(1, border_rect.height - 2)
                        pygame.draw.circle(ice_surface, sparkle_color, (sparkle_x, sparkle_y), 1)
                    

                    crack_color = (220, 240, 255, 200)

                    pygame.draw.line(ice_surface, crack_color, 
                                   (5, 5), (border_rect.width - 5, border_rect.height - 5), 1)
                    pygame.draw.line(ice_surface, crack_color, 
                                   (border_rect.width - 5, 5), (5, border_rect.height - 5), 1)

                    pygame.draw.line(ice_surface, crack_color, 
                                   (border_rect.width // 2, 2), (border_rect.width // 2, border_rect.height - 2), 1)
                    pygame.draw.line(ice_surface, crack_color, 
                                   (2, border_rect.height // 2), (border_rect.width - 2, border_rect.height // 2), 1)
                    

                    screen.blit(ice_surface, border_rect.topleft)
                    

                    if (current_time_ms % 500) < 250:
                        flash_surface = pygame.Surface((border_rect.width + 4, border_rect.height + 4), pygame.SRCALPHA)
                        pygame.draw.rect(flash_surface, (255, 255, 255, 80), pygame.Rect(0, 0, border_rect.width + 4, border_rect.height + 4), border_radius=10, width=1)
                        screen.blit(flash_surface, (border_rect.left - 2, border_rect.top - 2))
                else:

                    pygame.draw.rect(screen, self.BLACK, border_rect, border_radius=8) 
                    pygame.draw.rect(screen, snake_fill_color, inner_rect, border_radius=6) 

                if i==0: 
                    for eye_pos in self._get_eye_pos(border_rect):
                        if is_frozen:


                            frozen_eye_color = (0, 80, 200)  
                            pygame.draw.circle(screen, frozen_eye_color, eye_pos, 3)
                        else:

                            pygame.draw.circle(screen, self.BLACK, eye_pos, 3)
        

        score_txt = self.font_small.render(f"分数: {self.score}", True, self.BLACK)
        hs_txt = self.font_small.render(f"最高分: {self.high_score}", True, self.BLACK)
        screen.blit(score_txt, (15,15)); screen.blit(hs_txt, (15,55))
        

        if self.effect_display:

            effect_txt = self.font_large.render(self.effect_display['text'], True, self.effect_display['color'])

            txt_rect = effect_txt.get_rect(center=(self.width//2, 80))
            

            if '冻结效果' in self.effect_display['text']:

                bg_rect = pygame.Rect(txt_rect.x - 30, txt_rect.y - 20, txt_rect.width + 60, txt_rect.height + 40)
                pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect, border_radius=15)
                

                shadow_colors = [(0, 0, 0), (100, 100, 255), (0, 0, 150)]
                shadow_offsets = [(5, 5), (3, 3), (1, 1)]
                for color, offset in zip(shadow_colors, shadow_offsets):
                    shadow_txt = self.font_large.render(self.effect_display['text'], True, color)
                    screen.blit(shadow_txt, (txt_rect.x + offset[0], txt_rect.y + offset[1]))
                

                current_time = pygame.time.get_ticks()
                if current_time % 200 < 100:
                    dynamic_border_rect = pygame.Rect(bg_rect.x - 5, bg_rect.y - 5, bg_rect.width + 10, bg_rect.height + 10)
                    pygame.draw.rect(screen, (100, 150, 255, 200), dynamic_border_rect, border_radius=20, width=3)
            

            screen.blit(effect_txt, txt_rect)
        if self.game_over:
            overlay = pygame.Surface((self.width,self.height), pygame.SRCALPHA); overlay.fill((255,255,255,180)); screen.blit(overlay,(0,0))
            

            if self.game_over_reason == 'bomb':
                over_txt=self.font_large.render("你被炸弹炸死了！",True,self.BLACK)
            elif self.game_over_reason:
                over_txt=self.font_large.render(self.game_over_reason,True,self.BLACK)
            else:
                over_txt=self.font_large.render("游戏结束",True,self.BLACK)
                

            screen.blit(over_txt, over_txt.get_rect(center=(self.width/2,self.height/2-120)))
            

            score_txt=self.font_small.render(f"最终分数: {self.score}",True,self.BLACK)
            screen.blit(score_txt, score_txt.get_rect(center=(self.width/2,self.height/2-60)))
            

            button_width = 180
            button_height = 50
            button_spacing = 30
            button_y = self.height/2 + 20
            button_color = (0, 150, 0)
            button_hover_color = (0, 200, 0)
            exit_button_color = (200, 50, 50)
            exit_button_hover_color = (255, 50, 50)
            text_color = (255, 255, 255)
            

            total_buttons_width = button_width * 3 + button_spacing * 2
            start_x = self.width//2 - total_buttons_width//2
            restart_rect = pygame.Rect(start_x, button_y, button_width, button_height)
            menu_rect = pygame.Rect(start_x + button_width + button_spacing, button_y, button_width, button_height)
            exit_rect = pygame.Rect(start_x + button_width * 2 + button_spacing * 2, button_y, button_width, button_height)
            

            self.restart_button_rect = restart_rect
            self.menu_button_rect = menu_rect
            self.exit_button_rect = exit_rect
            

            pygame.draw.rect(screen, button_color, restart_rect, border_radius=5)
            restart_txt = self.font_small.render("重新开始", True, text_color)
            screen.blit(restart_txt, restart_txt.get_rect(center=restart_rect.center))
            

            pygame.draw.rect(screen, button_color, menu_rect, border_radius=5)
            menu_txt = self.font_small.render("返回菜单", True, text_color)
            screen.blit(menu_txt, menu_txt.get_rect(center=menu_rect.center))
            

            pygame.draw.rect(screen, exit_button_color, exit_rect, border_radius=5)
            exit_txt = self.font_small.render("退出游戏", True, text_color)
            screen.blit(exit_txt, exit_txt.get_rect(center=exit_rect.center))
        elif not self.game_started:

            start_txt = self.font_small.render("按任意方向键开始游戏",True,self.BLACK)
            screen.blit(start_txt, start_txt.get_rect(center=(self.width/2,self.height/3)))
        return screen

    def _get_eye_pos(self, rect):
        ox,oy=self.grid_size//4,self.grid_size//4
        if self.direction==(1,0): return [(rect.centerx+ox,rect.centery-oy),(rect.centerx+ox,rect.centery+oy)]
        elif self.direction==(-1,0): return [(rect.centerx-ox,rect.centery-oy),(rect.centerx-ox,rect.centery+oy)]
        elif self.direction==(0,1): return [(rect.centerx-ox,rect.centery+oy),(rect.centerx+ox,rect.centery+oy)]
        else: return [(rect.centerx-ox,rect.centery-oy),(rect.centerx+ox,rect.centery-oy)]