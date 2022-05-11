import sys
from time import sleep

import pygame
from Scripts.activate_this import path

from settings import Settings

from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from leftbullet import LeftBullet
from rightbullet import RightBullet
from alien import Alien

class AlienInvasion:
    """管理游戏资源和行为的类"""
    def __init__(self):
        """初始化游戏并创建游戏资源"""
        pygame.init()
        self.settings = Settings()

        # 全屏显示
        # self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        # self.settings.screen_width = self.screen.get_rect().width
        # self.settings.screen_height = self.screen.get_rect().height
        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("Alien Invasion")

        # 创建一个用于存储游戏统计信息的实例
        #   并且创建记分牌
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.leftbullets = pygame.sprite.Group()
        self.rightbullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()
        # 创建Play按钮
        self.play_button = Button(self, "Play")
        # 设置背景颜色
        self.bg_color = (230, 230, 230)

    def _create_fleet(self):
        """创建外星人群"""
        # 创建一个外星人
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)

        # 计算屏幕可容纳多少行外星人
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height -
                             (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)

        # 创建外星人群
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_number):
        """创建一个外星人并且将其加入当前行"""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

    def _check_fleet_edges(self):
        """有外星人到达边缘时采取相应的措施"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """将整群外星人下移，并且改变他们的方向"""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def run_game(self):
        """开始游戏的主循环"""
        while True:
            self._check_events()

            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_leftbullets()
                self._update_rightbullets()
                self._update_aliens()

            self._update_screen()
            # 每次循环都重绘屏幕

    def _check_events(self):
        """监视键盘和鼠标事件。"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_play_button(self, mouse_pos):
        """玩家点击开始按钮之后开始游戏"""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            # 重置游戏设置
            self.settings.initialize_dynamic_settings()
            # 重置游戏统计信息
            self.stats.reset_stats()
            self.stats.game_active = True
            self.sb.prep_score()
            self.sb.prep_level()

            # 清空余下的外星人和子弹
            self.aliens.empty()
            self.bullets.empty()
            if self.stats.leftbullet:
                self.leftbullets.empty()
            if self.stats.rightbullet:
                self.rightbullets.empty()

            # 创建一群新的外星人并且让飞船居中
            self._create_fleet()
            self.ship.center_ship()

            # 隐藏鼠标光标
            pygame.mouse.set_visible(False)

    def _check_keydown_events(self, event):
        """响应按下按键"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
            if self.stats.leftbullet:
                self._fire_leftbullet()
            if self.stats.rightbullet:
                self._fire_rightbullet()

    def _check_keyup_events(self, event):
        """响应松开按键"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _fire_bullet(self):
        """创建一颗子弹，并将其加入编组bullets中。"""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        """更新子弹的位置并删除消失的子弹。"""
        # 删除消失的子弹
        self.bullets.update()

        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()

    def _fire_leftbullet(self):
        """创建一颗子弹，并将其加入编组bullets中。"""
        if len(self.leftbullets) < self.settings.bullets_allowed:
            new_leftbullet = LeftBullet(self)
            self.leftbullets.add(new_leftbullet)

    def _update_leftbullets(self):
        """更新子弹的位置并删除消失的子弹。"""
        # 删除消失的子弹
        self.leftbullets.update()

        for leftbullet in self.leftbullets.copy():
            if leftbullet.rect.bottom <= 0:
                self.leftbullets.remove(leftbullet)

        self._check_bullet_alien_collisions()

    def _fire_rightbullet(self):
        """创建一颗子弹，并将其加入编组bullets中。"""
        if len(self.rightbullets) < self.settings.bullets_allowed:
            new_rightbullet = RightBullet(self)
            self.rightbullets.add(new_rightbullet)

    def _update_rightbullets(self):
        """更新子弹的位置并删除消失的子弹。"""
        # 删除消失的子弹
        self.rightbullets.update()

        for rightbullet in self.rightbullets.copy():
            if rightbullet.rect.bottom <= 0:
                self.rightbullets.remove(rightbullet)

        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """响应子弹与外星人碰撞"""
        # 检查是否有子弹击中了外星人
        # 如果是，就删除相应的子弹和外星人
        flag1 = True
        flag2 = True
        flag3 = True
        if self.stats.level >= 4:
            flag1 = False
        if self.stats.level >= 5:
            flag2 = False
        if self.stats.level >= 6:
            flag3 = False
        collisions = pygame.sprite.groupcollide(
                self.bullets, self.aliens, flag1, True
            )
        if self.stats.leftbullet:
            collisions2 = pygame.sprite.groupcollide(
                self.leftbullets, self.aliens, flag2, True
            )
        if self.stats.rightbullet:
            collisions3 = pygame.sprite.groupcollide(
                self.rightbullets, self.aliens, flag3, True
            )
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()
        if self.stats.leftbullet:
            if collisions2:
                for aliens in collisions2.values():
                    self.stats.score += self.settings.alien_points * len(aliens)
                self.sb.prep_score()
                self.sb.check_high_score()
        if self.stats.rightbullet:
            if collisions3:
                for aliens in collisions3.values():
                    self.stats.score += self.settings.alien_points * len(aliens)
                self.sb.prep_score()
                self.sb.check_high_score()

        if not self.aliens:
            # 删除所有的子弹并且新建一群外星人
            self.bullets.empty()
            if self.stats.leftbullet:
                self.leftbullets.empty()
            if self.stats.rightbullet:
                self.rightbullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            # 提升等级
            self.stats.level += 1
            if self.stats.level >= 2:
                self.stats.leftbullet = True
            if self.stats.level >= 3:
                self.stats.rightbullet = True
            self.sb.prep_level()

    def _update_aliens(self):
        """检查是否有外星人位于屏幕边缘，更新外星人群所有外星人的位置"""
        self._check_fleet_edges()
        self.aliens.update()

        # 检测外星人和飞船之间的碰撞
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        # 检查是否有外星人到达了屏幕底部
        self._check_aliens_bottom()

    def _check_aliens_bottom(self):
        """检查是否有外星人到达了屏幕底端"""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # 像撞到飞船一样处理
                self._ship_hit()
                break

    def _ship_hit(self):
        """响应飞船被外星人撞到"""
        if self.stats.ships_left > 0:
            # 将ship_left 减1并且更新记分牌
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            # 清空余下的外星人和子弹
            self.aliens.empty()
            self.bullets.empty()
            if self.stats.leftbullet:
                self.leftbullets.empty()
            if self.stats.rightbullet:
                self.rightbullets.empty()

            # 创建一群新的外星人
            self._create_fleet()
            self.ship.center_ship()

            # 暂停
            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def _update_screen(self):
        self.screen.fill(self.settings.bg_color)
        self.ship.blitime()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        if self.stats.leftbullet:
            for leftbullet in self.leftbullets.sprites():
                leftbullet.draw_bullet()
        if self.stats.rightbullet:
            for rightbullet in self.rightbullets.sprites():
                rightbullet.draw_bullet()
        self.aliens.draw(self.screen)
        # 显示得分
        self.sb.show_score()

        # 如果游戏处于非活动状态就绘制按钮
        if not self.stats.game_active:
            self.play_button.draw_button()

        # 让最近绘制的屏幕可见
        pygame.display.flip()


if __name__ == '__main__':
    # 创建游戏实例并运行游戏
    ai = AlienInvasion()
    ai.run_game()
