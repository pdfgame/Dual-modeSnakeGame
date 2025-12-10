import json
import os


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
GAME_DATA_FILE = os.path.join(os.path.dirname(CURRENT_DIR), "resources", "data", "game_data.json")


def ensure_data_dir_exists():
    """
    确保游戏数据文件目录存在，如果不存在则创建
    """
    data_dir = os.path.dirname(GAME_DATA_FILE)
    if not os.path.exists(data_dir):
        try:
            os.makedirs(data_dir, exist_ok=True)
            print(f"创建游戏数据目录: {data_dir}")
        except Exception as e:
            print(f"创建游戏数据目录失败: {e}")

def load_game_data():
    """
    从文件中加载游戏数据（最高分和蛇颜色）
    如果文件不存在或损坏，则返回默认值
    """
    default_data = {
        'high_score_classic': 0,       
        'high_score_gesture': 0,       
        'snake_color': (255, 182, 193),  
        'hide_camera_feed': True,      
        'language': 'zh_cn'            
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

            ensure_data_dir_exists()

            save_game_data(default_data)
            return default_data
    except (json.JSONDecodeError, IOError, Exception) as e:

        print(f"加载游戏数据失败: {e}")
        return default_data

def save_game_data(data):
    """
    保存游戏数据到文件
    """
    try:

        ensure_data_dir_exists()
        

        if 'snake_color' in data and isinstance(data['snake_color'], tuple):
            data['snake_color'] = list(data['snake_color'])
        

        with open(GAME_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except (IOError, Exception) as e:

        print(f"保存游戏数据失败: {e}")
        return False