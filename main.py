import sys
import os

# 获取当前脚本的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))

# 将当前目录添加到Python路径，以便导入game模块
sys.path.insert(0, current_dir)

# 导入game.core.game_controller
from game.core.game_controller import GameController

if __name__ == "__main__":
    # 创建游戏控制器并运行游戏
    controller = GameController()
    controller.run()