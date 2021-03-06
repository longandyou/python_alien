class GameStats:
    """跟踪游戏的统计信息"""

    def __init__(self, ai_game):
        """初始化统计信息"""
        self.settings = ai_game.settings
        self.reset_stats()
        # 让游戏刚启动时处于非活动状态
        self.game_active = False
        self.leftbullet = False
        self.rightbullet = False
        # 任何情况下都不应该重置最高得分
        # 读取文件中的最高得分
        with open('highest_score.txt', encoding='utf-8') as file:
            maxscore = file.read()
        self.high_score = int(maxscore)

    def reset_stats(self):
        """初始化在游戏期间可能发生变化的统计信息"""
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1
