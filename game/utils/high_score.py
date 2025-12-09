import json
import os


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
GAME_DATA_FILE = os.path.join(CURRENT_DIR, "..", "data", "game_data.json") 

def load_game_data():
    """
    从文件中加载游戏数据（最高分和蛇颜色）
    如果文件不存在或损坏，则返回默认值
    """
    default_data = {
        'high_score': 0,
        'snake_color': (255, 182, 193) 
    }
    try:
        if os.path.exists(GAME_DATA_FILE):
            with open(GAME_DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)

                for key, default_value in default_data.items():
                    if key not in data:
                        data[key] = default_value

                if 'snake_color' in data and isinstance(data['snake_color'], list):
                    data['snake_color'] = tuple(data['snake_color'])
                return data
        else:
            return default_data
    except (json.JSONDecodeError, IOError, Exception):

        return default_data

def save_game_data(data):
    """
    保存游戏数据到文件
    """
    try:

        if 'snake_color' in data and isinstance(data['snake_color'], tuple):
            data['snake_color'] = list(data['snake_color'])
        with open(GAME_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except (IOError, Exception):

        return False