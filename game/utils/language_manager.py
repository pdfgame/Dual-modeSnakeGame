# -*- coding: utf-8 -*-
"""
语言管理器
负责处理游戏中的文本翻译和语言切换
"""

# 支持的语言列表
supported_languages = {
    'zh_cn': '中文',
    'en_us': 'English'
}

# 翻译文本字典
_translations = {
    # 主菜单
    'menu_title': {
        'zh_cn': '双模式贪吃蛇游戏',
        'en_us': 'Dual-mode Snake Game'
    },
    'menu_classic_mode': {
        'zh_cn': '经典模式',
        'en_us': 'Classic Mode'
    },
    'menu_gesture_mode': {
        'zh_cn': '手势控制模式',
        'en_us': 'Gesture Control Mode'
    },
    'menu_settings': {
        'zh_cn': '设置',
        'en_us': 'Settings'
    },
    'menu_exit': {
        'zh_cn': '退出游戏',
        'en_us': 'Exit Game'
    },
    
    # 游戏中
    'game_score': {
        'zh_cn': '分数: {0}',
        'en_us': 'Score: {0}'
    },
    'game_high_score': {
        'zh_cn': '最高分: {0}',
        'en_us': 'High Score: {0}'
    },
    'game_game_over': {
        'zh_cn': '游戏结束',
        'en_us': 'Game Over'
    },
    'game_final_score': {
        'zh_cn': '最终分数: {0}',
        'en_us': 'Final Score: {0}'
    },
    'game_restart': {
        'zh_cn': '重新开始',
        'en_us': 'Restart'
    },
    'game_return_menu': {
        'zh_cn': '返回菜单',
        'en_us': 'Return to Menu'
    },
    'game_exit_game': {
        'zh_cn': '退出游戏',
        'en_us': 'Exit Game'
    },
    'game_obstacle_refreshed': {
        'zh_cn': '障碍物已刷新',
        'en_us': 'Obstacles refreshed'
    },
    
    # 经典模式
    'classic_start_prompt': {
        'zh_cn': '按任意方向键开始游戏',
        'en_us': 'Press any arrow key to start'
    },
    'classic_bomb_death': {
        'zh_cn': '你被炸弹炸死了！',
        'en_us': 'You were killed by a bomb!'
    },
    'classic_edge_death': {
        'zh_cn': '碰到屏幕边缘',
        'en_us': 'Hit screen edge'
    },
    'classic_self_death': {
        'zh_cn': '碰到自己身体',
        'en_us': 'Hit your own body'
    },
    'classic_obstacle_death': {
        'zh_cn': '碰到障碍物',
        'en_us': 'Hit an obstacle'
    },
    
    # 特效提示
    'effect_double_score': {
        'zh_cn': '分数翻倍！',
        'en_us': 'Double Score!'
    },
    'effect_speed_up': {
        'zh_cn': '加速效果',
        'en_us': 'Speed Up!'
    },
    'effect_speed_down': {
        'zh_cn': '减速效果！',
        'en_us': 'Slow Down!'
    },
    'effect_freeze': {
        'zh_cn': '冻结效果',
        'en_us': 'Freeze Effect!'
    },
    'effect_color_change': {
        'zh_cn': '变色效果',
        'en_us': 'Color Change!'
    },
    
    # 设置
    'settings_title': {
        'zh_cn': '游戏设置',
        'en_us': 'Game Settings'
    },
    'settings_color': {
        'zh_cn': '自定义蛇颜色',
        'en_us': 'Custom Snake Color'
    },
    'settings_language': {
        'zh_cn': '语言设置',
        'en_us': 'Language Settings'
    },
    'settings_camera': {
        'zh_cn': '摄像头设置',
        'en_us': 'Camera Settings'
    },
    'settings_hide_camera': {
        'zh_cn': '隐藏摄像头画面',
        'en_us': 'Hide Camera Feed'
    },
    'settings_save': {
        'zh_cn': '保存设置',
        'en_us': 'Save Settings'
    },
    'settings_return': {
        'zh_cn': '返回',
        'en_us': 'Return'
    },
    
    # 颜色名称
    'color_solid': {
        'zh_cn': '纯色',
        'en_us': 'Solid Colors'
    },
    'color_gradient': {
        'zh_cn': '渐变颜色',
        'en_us': 'Gradient Colors'
    },
    'color_pink': {
        'zh_cn': '粉色',
        'en_us': 'Pink'
    },
    'color_light_green': {
        'zh_cn': '浅绿',
        'en_us': 'Light Green'
    },
    'color_light_blue': {
        'zh_cn': '浅蓝',
        'en_us': 'Light Blue'
    },
    'color_yellow': {
        'zh_cn': '黄色',
        'en_us': 'Yellow'
    },
    'color_orange': {
        'zh_cn': '橙色',
        'en_us': 'Orange'
    },
    'color_purple': {
        'zh_cn': '紫色',
        'en_us': 'Purple'
    },
    'color_white': {
        'zh_cn': '白色',
        'en_us': 'White'
    },
    'color_gray': {
        'zh_cn': '灰色',
        'en_us': 'Gray'
    },
    'color_red': {
        'zh_cn': '红色',
        'en_us': 'Red'
    },
    'color_cyan': {
        'zh_cn': '青色',
        'en_us': 'Cyan'
    },
    'color_magenta': {
        'zh_cn': '品红',
        'en_us': 'Magenta'
    },
    'color_lime': {
        'zh_cn': '翠绿',
        'en_us': 'Lime'
    },
    'color_teal': {
        'zh_cn': '青色',
        'en_us': 'Teal'
    },
    'color_navy': {
        'zh_cn': '海军蓝',
        'en_us': 'Navy'
    },
    'color_gold': {
        'zh_cn': '金色',
        'en_us': 'Gold'
    },
    'color_silver': {
        'zh_cn': '银色',
        'en_us': 'Silver'
    },
    
    # 渐变名称
    'gradient_rainbow': {
        'zh_cn': '彩虹',
        'en_us': 'Rainbow'
    },
    'gradient_blue_green': {
        'zh_cn': '蓝绿渐变',
        'en_us': 'Blue-Green Gradient'
    },
    'gradient_fire': {
        'zh_cn': '火热渐变',
        'en_us': 'Fire Gradient'
    },
    'gradient_cosmic': {
        'zh_cn': '宇宙渐变',
        'en_us': 'Cosmic Gradient'
    },
    
    # 加载界面
    'loading': {
        'zh_cn': '加载中...',
        'en_us': 'Loading...'
    },
    'loading_gesture_mode': {
        'zh_cn': '正在加载手势控制模式...',
        'en_us': 'Loading Gesture Control Mode...'
    },
    'loading_contact': {
        'zh_cn': '有建议请联系我',
        'en_us': 'Contact me with suggestions'
    },
    'loading_releasing_resources': {
        'zh_cn': '正在释放旧资源...',
        'en_us': 'Releasing old resources...'
    },
    'loading_initializing_camera': {
        'zh_cn': '正在初始化摄像头...',
        'en_us': 'Initializing camera...'
    },
    'loading_gesture_model': {
        'zh_cn': '正在加载手势检测模型...',
        'en_us': 'Loading gesture detection model...'
    },
    'loading_game_state': {
        'zh_cn': '正在初始化游戏状态...',
        'en_us': 'Initializing game state...'
    },
    'loading_completed': {
        'zh_cn': '加载完成，准备开始游戏...',
        'en_us': 'Loading completed, ready to start...'
    },
    
    # 手势模式
    'gesture_instructions': {
        'zh_cn': '使用食指控制蛇的移动',
        'en_us': 'Use index finger to control snake'
    },
    'gesture_return_menu': {
        'zh_cn': '按 M 返回菜单',
        'en_us': 'Press M to return to menu'
    },
    'gesture_loading_camera': {
        'zh_cn': '正在加载摄像头...',
        'en_us': 'Loading camera...'
    },
    'gesture_mode': {
        'zh_cn': '手势追踪模式',
        'en_us': 'Gesture Tracking Mode'
    },
    'gesture_no_hand': {
        'zh_cn': '未检测到手部',
        'en_us': 'No hand detected'
    },
    
    # 游戏状态
    'game_paused': {
        'zh_cn': '游戏暂停',
        'en_us': 'Game Paused'
    },
    'game_resume': {
        'zh_cn': '返回游戏',
        'en_us': 'Resume Game'
    },
    'game_return_menu': {
        'zh_cn': '返回主菜单',
        'en_us': 'Return to Menu'
    },
    'game_end': {
        'zh_cn': '游戏结束',
        'en_us': 'Game Over'
    },
    
    # 其他
    'creator_text': {
        'zh_cn': '有建议请联系我',
        'en_us': 'Contact me with suggestions'
    },
    'menu_hide': {
        'zh_cn': '隐藏',
        'en_us': 'Hidden'
    },
    'menu_show': {
        'zh_cn': '显示',
        'en_us': 'Visible'
    },
    'language_switch_to_english': {
        'zh_cn': '切换到英文',
        'en_us': 'Switch to Chinese'
    },
    'chinese': {
        'zh_cn': '中文',
        'en_us': 'Chinese'
    },
}


class LanguageManager:
    """
    语言管理器类
    """
    
    def __init__(self, language='zh_cn'):
        """
        初始化语言管理器
        
        参数:
            language: 初始语言代码，默认为中文
        """
        self.current_language = language
        
    def set_language(self, language):
        """
        设置当前语言
        
        参数:
            language: 语言代码，必须是supported_languages中的键
        """
        if language in supported_languages:
            self.current_language = language
            return True
        return False
    
    def get_language(self):
        """
        获取当前语言代码
        """
        return self.current_language
    
    def get_language_name(self):
        """
        获取当前语言的名称
        """
        return supported_languages.get(self.current_language, '中文')
    
    def translate(self, key, *args):
        """
        翻译文本
        
        参数:
            key: 文本键
            args: 格式化参数
        
        返回:
            翻译后的文本，如果找不到键则返回键本身
        """
        text = _translations.get(key, {}).get(self.current_language, key)
        if args:
            return text.format(*args)
        return text
    
    def get_supported_languages(self):
        """
        获取支持的语言列表
        
        返回:
            支持的语言代码和名称的字典
        """
        return supported_languages


# 创建全局语言管理器实例
global_language_manager = LanguageManager()


def get_translation(key, *args):
    """
    便捷函数：获取翻译文本
    
    参数:
        key: 文本键
        args: 格式化参数
    
    返回:
        翻译后的文本
    """
    return global_language_manager.translate(key, *args)


def set_language(language):
    """
    便捷函数：设置当前语言
    
    参数:
        language: 语言代码
    """
    return global_language_manager.set_language(language)


def get_current_language():
    """
    便捷函数：获取当前语言代码
    """
    return global_language_manager.get_language()


def get_current_language_name():
    """
    便捷函数：获取当前语言名称
    """
    return global_language_manager.get_language_name()
