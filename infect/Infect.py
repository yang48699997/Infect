import math
import sys
from pathlib import Path
import pygame
import random

SCREEN_WEIGHT = 1500
SCREEN_HEIGHT = 770
BG_COLOR = pygame.Color(0, 0, 0)
TEXT_COLOR = pygame.Color(255, 255, 255)
current_dir = Path(__file__).resolve().parent
picture_path = [
    str(current_dir) + "\\..\\static\\empty.png",
    str(current_dir) + "\\..\\static\\treeBall.png",
    str(current_dir) + "\\..\\static\\fireBall.png",
    str(current_dir) + "\\..\\static\\waterBall.png",
    str(current_dir) + "\\..\\static\\treeBallSelected.png",
    str(current_dir) + "\\..\\static\\fireBallSelected.png",
    str(current_dir) + "\\..\\static\\waterBallSelected.png",
]
PLAYER_CLASS = 'WaterBall'


class MainGame:
    def __init__(self):
        self.window = None
        self.game_name = "Infect"
        self.version = "V1.1"
        self.my_ball = None
        self.mouse_x = 0
        self.mouse_y = 0
        self.water_balls_list = []
        self.fire_balls_list = []
        self.tree_balls_list = []
        self.all_balls_list = []
        self.water_group: pygame.sprite.Group = pygame.sprite.Group()
        self.fire_group: pygame.sprite.Group = pygame.sprite.Group()
        self.tree_group: pygame.sprite.Group = pygame.sprite.Group()

    @staticmethod
    def printt():
        print('=================================================================')

    def start_game(self):
        self.init_game()
        while True:
            self.window.fill(BG_COLOR)
            self.window. \
                blit(pygame.font.SysFont("kaiti", 18).render("时间", True, TEXT_COLOR), (SCREEN_WEIGHT / 2 - 50, 10))
            for water_ball in self.water_balls_list:
                water_ball.move()
            # 对发生碰撞的Ball重新分配其list
            self.redistribute_collision_balls(self.water_group, self.fire_group)
            # 改变发生碰撞的无敌害作用的Ball碰撞状态
            self.change_collision_state(self.water_group, self.water_group)
            self.change_collision_state(self.tree_group, self.tree_group)
            self.change_collision_state(self.fire_group, self.fire_group)
            self.change_collision_state(self.water_group, self.tree_group)
            # 绘制Ball
            for ball in self.all_balls_list:
                ball.display_ball(self)
            # 循环获取事件，监听事件状态
            for event in pygame.event.get():
                self.mouse_x = pygame.mouse.get_pos()[0]
                self.mouse_y = pygame.mouse.get_pos()[1]
                # 判断用户是否点了"X"关闭按钮,并执行if代码段
                if event.type == pygame.QUIT:
                    # 卸载所有模块
                    pygame.quit()
                    # 终止程序，确保退出程序
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONUP:
                    # Ball的位置范围
                    # 判断鼠标位置是否在Ball内
                    for water_ball in self.water_balls_list:
                        ball_position_range = water_ball.ball_position_range()
                        if self.position_in_range(ball_position_range):
                            if water_ball.state == 'unselected':
                                water_ball.state = 'selected'
                            elif water_ball.state == 'selected':
                                water_ball.state = 'unselected'
                self.move_ball()
            self.move_ball()
            pygame.display.flip()

    def init_game(self):
        # 使用pygame之前必须初始化
        pygame.init()
        # 设置主屏窗口
        self.window = pygame.display.set_mode([SCREEN_WEIGHT, SCREEN_HEIGHT])
        # 初始化water_ball
        self.my_ball = WaterBall(SCREEN_WEIGHT / 2, SCREEN_HEIGHT / 2)
        self.water_balls_list.append(self.my_ball)
        # 生成fire_ball
        self.fire_balls_list = self.fire_balls_generate()
        # 生成tree_ball
        self.tree_balls_list = self.tree_balls_generate()
        # 将所有Ball添加到all_balls_list
        self.ball_lists_gather()
        # 将所有Ball添加到各自的精灵group
        self.add_ball_to_group()
        # 设置窗口的标题，即游戏名称
        pygame.display.set_caption(self.game_name + "   " + self.version)

    def position_in_range(self, ball_position_range):
        return ball_position_range[0] <= self.mouse_x <= ball_position_range[2] and \
            ball_position_range[1] <= self.mouse_y <= ball_position_range[3]

    def move_ball(self):
        self.mouse_x = pygame.mouse.get_pos()[0]
        self.mouse_y = pygame.mouse.get_pos()[1]
        for water_ball in self.water_balls_list:
            ball_position_range = water_ball.ball_position_range()
            if self.position_in_range(ball_position_range):
                water_ball.moving = False
            else:
                water_ball.moving = True
                dist = [self.mouse_x - ball_position_range[4], self.mouse_y - ball_position_range[5]]
                result = math.sqrt(dist[0] ** 2 + dist[1] ** 2)
                water_ball.x_speed_ratio = dist[0] / result
                water_ball.y_speed_ratio = dist[1] / result

    # 该函数应用于相同的group1 和 group2相同,后续进行修改使其具有普遍性
    def change_collision_state(self, ball_group1, balls_group2):
        list1 = self.not_vanish_collision(ball_group1, balls_group2)
        collision_dirt = list1[0]
        key_list = list1[1]
        if collision_dirt:
            if ball_group1 == balls_group2:
                for ball in key_list:
                    if len(collision_dirt.get(ball)) > 1:
                        ball.collision_state = True
            else:
                for ball in key_list:
                    if len(collision_dirt.get(ball)) > 0:
                        ball.collision_state = True

    def redistribute_collision_balls(self, group1, group2):
        # 获取发生碰撞的所有water_ball fire_ball
        collisions_balls_list = self.vanish_collision(group1, group2)
        ball_collision_list = collisions_balls_list[2]
        if len(ball_collision_list) != 0:
            # 改变与water_ball发生碰撞的所有fire_ball的property
            self.property_change(ball_collision_list)
            # 将改变后的fire_ball添加到 water_ball_group 与 water_balls_list中
            self.water_group.add(*ball_collision_list)
            self.water_balls_list.extend(ball_collision_list)
            # 删除该改变property的元素
            self.fire_balls_list = self.delete_balls_from_ball_list(self.fire_balls_list, ball_collision_list)

    @staticmethod
    def fire_balls_generate():
        fire_balls_list = []
        for i in range(3):
            fire_ball = FireBall(random.randrange(SCREEN_WEIGHT + 40), random.randrange(SCREEN_HEIGHT - 50))
            fire_balls_list.append(fire_ball)
        return fire_balls_list
        # self.all_balls_list.append(fire_ball)

    @staticmethod
    def tree_balls_generate():
        tree_balls_list = []
        for i in range(3):
            tree_ball = TreeBall(random.randrange(SCREEN_WEIGHT + 40), random.randrange(SCREEN_HEIGHT - 50))
            tree_balls_list.append(tree_ball)
        return tree_balls_list

    @staticmethod
    def vanish_collision(water_group, fire_group):
        collisions = pygame.sprite.groupcollide(water_group, fire_group, False, True)
        sprites_from_group1 = list(collisions.keys())
        sprites_from_group2 = [sprite for sprites in collisions.values() for sprite in sprites]
        return [collisions, sprites_from_group1, sprites_from_group2]

    @staticmethod
    def not_vanish_collision(group1, group2):
        collision_dict = pygame.sprite.groupcollide(group1, group2, False, False)
        sprites_from_group1 = list(collision_dict.keys())
        sprites_from_group2 = [sprite for sprites in collision_dict.values() for sprite in sprites]
        # [字典, group1中发生碰撞的精灵(所有的key), group2中发生碰撞的精灵(所有的value)]
        return [collision_dict, sprites_from_group1, sprites_from_group2]

    @staticmethod
    def property_change(ball_collision_list):
        tmp_ball = ball_collision_list[0]
        if isinstance(tmp_ball, FireBall):
            for ball in ball_collision_list:
                ball.property = 'waterBall'
        elif isinstance(tmp_ball, WaterBall):
            for ball in ball_collision_list:
                ball.property = 'treeBall'
        else:
            for ball in ball_collision_list:
                ball.property = 'fireBall'

    def ball_lists_gather(self):
        self.all_balls_list.extend(self.water_balls_list)
        self.all_balls_list.extend(self.fire_balls_list)
        self.all_balls_list.extend(self.tree_balls_list)

    def add_ball_to_group(self):
        self.water_group.add(*self.water_balls_list)
        self.fire_group.add(*self.fire_balls_list)
        self.tree_group.add(*self.tree_balls_list)

    @staticmethod
    def delete_balls_from_ball_list(original_list, removal_list):
        final_list = original_list
        if len(removal_list) != 0:
            removal_set = set(removal_list)
            new_list = [x for x in original_list if x not in removal_set]
            final_list = new_list
        return final_list


class Ball(pygame.sprite.Sprite):
    # 位置初始化
    def __init__(self, left, top):
        super().__init__()
        self.property_images = {
            'empty': pygame.image.load(picture_path[0]),
            'treeBall': pygame.image.load(picture_path[1]),
            'fireBall': pygame.image.load(picture_path[2]),
            'waterBall': pygame.image.load(picture_path[3])
        }
        self.state_images = {
            'waterBallSelected': pygame.image.load(picture_path[6]),
            'fireBallSelected': pygame.image.load(picture_path[5]),
            'treeBallSelected': pygame.image.load(picture_path[4]),
            # 'selected': pygame.image.load(picture_path[0]),
            # 'unselected': pygame.image.load(picture_path[1]),
        }
        # 选中状态
        self.state = "selected"
        self.property = 'empty'
        # 根据选中属性加载图片
        self.image = self.property_images[self.property]
        # 根据图片获取区域
        self.rect = self.image.get_rect()
        # 获取图片的尺寸
        self.size = self.image.get_size()
        # 初始化位置
        self.left = left
        self.top = top
        self.rect.left = left
        self.rect.top = top
        # 移动状态
        self.moving = False
        self.speed = 1
        self.x_speed_ratio = float(0)
        self.y_speed_ratio = float(0)
        # 碰撞状态
        self.collision_state = False
        self.previous_position_list = [self.rect.left, self.rect.top]
        self.previous_position_list = [self.rect.left, self.rect.top]

    def move(self):
        if self.collision_state is True:
            self.rect.left = self.previous_position_list[0] - self.x_speed_ratio * 2
            self.rect.top = self.previous_position_list[1] - self.y_speed_ratio * 2
            self.collision_state = False
        elif PLAYER_CLASS == 'WaterBall' and self.moving is True and self.state == 'selected':
            self.previous_position_list = self.previous_position()
            self.rect.top += self.speed * self.y_speed_ratio
            self.rect.left += self.speed * self.x_speed_ratio
            self.rect.top = max(0, self.rect.top)
            self.rect.top = min(SCREEN_HEIGHT - self.size[0], self.rect.top)
            self.rect.left = max(0, self.rect.left)
            self.rect.left = min(SCREEN_WEIGHT - self.size[1], self.rect.left)

    def display_ball(self, main_game):
        # 获取展示的对象
        # self.image = self.property_images[self.property]
        self.image = self.image_change()
        self.size = self.image.get_size()
        # 调用blit方法展示
        main_game.window.blit(self.image, self.rect)

    def previous_position(self):
        previous_rect_left = self.rect.left
        previous_rect_top = self.rect.top
        return [previous_rect_left, previous_rect_top]

    def image_change(self):
        if self.state == 'selected':
            image = self.state_images[str(self.property) + 'Selected']
        else:
            image = self.property_images[str(self.property)]
        return image

    def ball_position_range(self):
        #  [最左方，最上方，最右方，最下方，中心点x，中心点y]
        position_range = [
            self.rect.left,
            self.rect.top,
            self.rect.left + self.size[0],
            self.rect.top + self.size[1],
            self.rect.left + self.size[0] // 2,
            self.rect.top + self.size[1] // 2
        ]
        return position_range

    def collisions(self, group1, group2):
        pass


class FireBall(Ball, pygame.sprite.Sprite):
    def __init__(self, left, top):
        super().__init__(left, top)
        self.property = 'fireBall'
        self.state = 'selected'


class WaterBall(Ball, pygame.sprite.Sprite):
    def __init__(self, left, top):
        super().__init__(left, top)
        self.property = 'waterBall'


class TreeBall(Ball, pygame.sprite.Sprite):
    def __init__(self, left, top):
        super().__init__(left, top)
        self.property = 'treeBall'
        self.state = 'selected'


if __name__ == '__main__':
    game = MainGame()
    game.start_game()
