import math
from math import tan

import pygame
from pygame.sprite import Sprite


class LeftBullet(Sprite):
    """管理飞船所发射左边子弹的类"""

    def __init__(self, ai_game):
        """在飞船当前位置创建一个子弹对象。"""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.color = self.settings.bullet_color

        # 在(0,0)处创建一个表示子弹的矩形,再设置正确的位置。
        self.rect = pygame.Rect(0, 0, self.settings.bullet_width,
                                self.settings.bullet_height)
        self.rect.midtop = ai_game.ship.rect.midtop

        # 存储用小数表示的子弹位置
        self.y = float(self.rect.y)
        self.x = float(self.rect.x)

    def update(self):
        """向斜上方移动子弹"""
        # 更新表示子弹位置的小数值。
        self.y -= self.settings.bullet_speed
        self.x -= tan(math.pi / 6) * self.settings.bullet_speed
        # 更新表示子弹的rect的位置
        self.rect.y = self.y
        self.rect.x = self.x

    def draw_bullet(self):
        """在屏幕上绘制子弹"""
        pygame.draw.rect(self.screen, self.color, self.rect)
