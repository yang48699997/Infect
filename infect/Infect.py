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
    str(current_dir) + "\\..\\static\\water.png",
    str(current_dir) + "\\..\\static\\treeBall.png",
    str(current_dir) + "\\..\\static\\fireBall.png",
    str(current_dir) + "\\..\\static\\waterBall.png",
    str(current_dir) + "\\..\\static\\treeBallSelected.png",
    str(current_dir) + "\\..\\static\\fireBallSelected.png",
    str(current_dir) + "\\..\\static\\waterBallSelected.png",
    str(current_dir) + "\\..\\static\\pot.png",
]
PLAYER_CLASS = 'WaterBall'

# ############################################################################################
#  ctrl + s  取消选中所有小球
#  ctrl + 鼠标左键 选中小球
#  ctrl + a  选中所有小球
#  未选中为灰色
#  只有选中的小球能移动
# 现在的两种控制移动的方式
# 单击shift 用来改变
# 方法1(默认): 鼠标方向控制
# 方法2: 鼠标右键位置控制  右键会显示鼠标标记位置
#
# ############################################################################################


class MainGame:
    def __init__(self):
        self.window = None
        self.pot = False
        self.game_name = "Infect"
        self.version = "V1.1"
        self.my_ball = None
        self.mouse_x = 0
        self.mouse_y = 0
        self.ctrl_held = False
        self.shift_held = False
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

            # ###############################################################################################################

            # 碰撞逻辑 #

            # 对发生碰撞的Ball重新分配其list
            self.redistribute_collision_balls(self.water_group, self.fire_group)
            # 改变发生碰撞的同类的Ball 或 water_group 与 tree_group碰撞中 ball的 碰撞状态
            self.change_collision_state(self.water_group, self.water_group)
            self.change_collision_state(self.water_group, self.tree_group)

            # 后面两行目前用不到
            # self.change_collision_state(self.tree_group, self.tree_group)
            # self.change_collision_state(self.fire_group, self.fire_group)

            # ###############################################################################################################

            # 绘制鼠标位置
            if self.pot is True:
                self.display_pot(self.mouse_x, self.mouse_y)

            # 绘制所有Ball
            for ball in self.all_balls_list:
                ball.display_ball(self)
                # 监听事件状态
                self.event_listen()
            # 第一种控制移动的方式
            if self.shift_held is False and self.ctrl_held is False:

                for water_ball in self.water_balls_list:
                    if water_ball.state == 'selected':
                        # 将鼠标位置 给want_x
                        water_ball.want_x = pygame.mouse.get_pos()[0]
                        water_ball.want_y = pygame.mouse.get_pos()[1]
                self.move_ball()
            else:
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

    def event_listen(self):
        for event in pygame.event.get():
            # self.mouse_x = pygame.mouse.get_pos()[0]
            # self.mouse_y = pygame.mouse.get_pos()[1]
            # 判断用户是否点了"X"关闭按钮,并执行if代码段
            if event.type == pygame.QUIT:
                # 卸载所有模块
                pygame.quit()
                # 终止程序，确保退出程序
                sys.exit()

            # 改变 ctrl 和 shift 的按下状态
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LCTRL:
                    self.ctrl_held = True
                elif event.key == 1073742049:
                    if self.shift_held is False:
                        # 将操纵移动的方式改变
                        self.shift_held = True
                    else:
                        self.shift_held = False
                        self.pot = False

            if self.ctrl_held is True:
                # 改变小球的选中状态
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for water_ball in self.water_balls_list:
                            mouse_x = pygame.mouse.get_pos()[0]
                            mouse_y = pygame.mouse.get_pos()[1]
                            ball_position_range = water_ball.ball_position_range()
                            if self.position_in_range(ball_position_range, mouse_x, mouse_y):
                                if water_ball.state == 'unselected':
                                    water_ball.state = 'selected'
                                elif water_ball.state == 'selected':
                                    water_ball.state = 'unselected'
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        for water_ball in self.water_balls_list:
                            water_ball.state = 'selected'
                    elif event.key == pygame.K_s:
                        for water_ball in self.water_balls_list:
                            water_ball.state = 'unselected'
                            water_ball.moving = False
                # 改变ctrl的状态
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_LCTRL:
                        self.ctrl_held = False

            # 第二种控制移动方式的实现
            if self.shift_held is True:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # 右键点击移动
                    if event.button == 3:
                        self.mouse_x = pygame.mouse.get_pos()[0]
                        self.mouse_y = pygame.mouse.get_pos()[1]
                        self.pot = True

                        mouse_x = self.mouse_x
                        mouse_y = self.mouse_y
                        for water_ball in self.water_balls_list:
                            if water_ball.state == 'selected':
                                water_ball.want_x = mouse_x
                                water_ball.want_y = mouse_y

            if self.shift_held is False and self.ctrl_held is False:
                mouse_x = pygame.mouse.get_pos()[0]
                mouse_y = pygame.mouse.get_pos()[1]
                for water_ball in self.water_balls_list:
                    water_ball.want_x = mouse_x
                    water_ball.want_x = mouse_y
                self.move_ball()

    @staticmethod
    def position_in_range(ball_position_range, mouse_x, mouse_y):
        return ball_position_range[0] <= mouse_x <= ball_position_range[2] and \
            ball_position_range[1] <= mouse_y <= ball_position_range[3]

    # ########################################################################################################
    #
    # move_ball
    # 每个water_ball中记录了 想要去的位置
    # 把原来的 self.mouse_x 改为 water_ball_want_x  其余不变
    #
    #############################################################################################################
    def move_ball(self):
        for water_ball in self.water_balls_list:
            ball_position_range = water_ball.ball_position_range()
            if self.position_in_range(ball_position_range, water_ball.want_x, water_ball.want_y):
                water_ball.moving = False
                self.pot = False
            else:
                water_ball.moving = True
                dist = [water_ball.want_x - ball_position_range[4], water_ball.want_y - ball_position_range[5]]
                result = math.sqrt(dist[0] ** 2 + dist[1] ** 2)
                if result != 0:
                    water_ball.x_speed_ratio = dist[0] / result
                    water_ball.y_speed_ratio = dist[1] / result
                else:
                    water_ball.x_speed_ratio = 0
                    water_ball.y_speed_ratio = 0

    def change_collision_state(self, ball_group1, balls_group2):
        list1 = self.not_vanish_collision(ball_group1, balls_group2)
        # 拿到dirt
        collision_dirt = list1[0]
        # 拿到key
        key_list = list1[1]
        # 如果发生了碰撞
        if collision_dirt:
            # 如果是同类碰撞
            if ball_group1 == balls_group2:
                for ball in key_list:
                    # 与ball 发生碰撞的group2中的小球
                    collision_list = collision_dirt.get(ball)
                    # collision_list长度为1时, value为 water_ball自己
                    # 只有长度大于1时才说明 与除自己外的其他小球发生了碰撞
                    if len(collision_list) > 1:
                        # 改变碰撞状态
                        ball.collision_state = True
                        for collided_ball in collision_list:
                            if ball != collided_ball:
                                # 调整球的位置，避免重叠
                                self.resolve_overlap(ball, collided_ball)
            else:
                # 如果是 water_group 与 tree_group中 ball的碰撞
                for ball in key_list:
                    collision_list = collision_dirt.get(ball)
                    if len(collision_list) > 0:
                        ball.collision_state = True
                        for collided_ball in collision_list:
                            # 调整球的位置，避免重叠
                            self.resolve_overlap(ball, collided_ball)

    @staticmethod
    def resolve_overlap(ball1, ball2):
        # 计算小球重叠区域
        overlap_x = ball1.rect.centerx - ball2.rect.centerx
        overlap_y = ball1.rect.centery - ball2.rect.centery
        total_overlap = abs(overlap_x) + abs(overlap_y)

        # 两小球完全重叠后重置到previous_position
        # 若无此代码 小球完全重叠后无法偏移开
        if total_overlap == 0:
            ball1.move()

        else:
            # 按比例分离两个小球
            offset_x = (overlap_x / total_overlap) * 2
            offset_y = (overlap_y / total_overlap) * 2

            # 对重叠小球进行偏移
            ball1.collision_excursion(offset_x, offset_y)
            ball2.collision_excursion(offset_x, offset_y)

    def redistribute_collision_balls(self, group1, group2):
        # 并从group2中删除发生碰撞的fire_ball 并将所有碰撞信息记录到collisions_balls_list中
        collisions_balls_list = self.vanish_collision(group1, group2)

        # 并从group2中所有发生碰撞的fire_ball
        ball_collision_list = collisions_balls_list[2]
        if len(ball_collision_list) != 0:
            # 改变与water_ball发生碰撞的所有fire_ball的property
            self.property_change(ball_collision_list)
            # 将改变后的fire_ball添加到 water_ball_group 与 water_balls_list中
            self.water_group.add(*ball_collision_list)
            self.water_balls_list.extend(ball_collision_list)
            # 从list中删除该改变property的元素
            self.fire_balls_list = self.delete_balls_from_ball_list(self.fire_balls_list, ball_collision_list)

    @staticmethod
    def fire_balls_generate():
        fire_balls_list = []
        for i in range(10):
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
    # 对group1 和 group2 中的所有小球进行碰撞检测 (water_group中的water_ball 可将 fire_group中的 fire_ball 感染)
    def vanish_collision(water_group, fire_group):
        # 发生碰撞的小球在存储在字典中   每个key分别为group1中发生的碰撞的ball,  value 为与group2中与key发生碰撞的小球
        #  后两个参数为(是否删除water_group中发生碰撞的ball, 是否删除fire_group发生碰撞的ball)
        collisions = pygame.sprite.groupcollide(water_group, fire_group, False, True)
        # 存放  所有key
        sprites_from_group1 = list(collisions.keys())
        # 存放 所有value
        sprites_from_group2 = [sprite for sprites in collisions.values() for sprite in sprites]
        # [字典, group1中发生碰撞的精灵(所有的key),  group2中发生碰撞的精灵(所有的value)]
        return [collisions, sprites_from_group1, sprites_from_group2]

    @staticmethod
    # 对group1 和 group2 中的所有小球进行碰撞检测 (group1和group2 可以为同类也可为异类)
    # 即检测 同类碰撞 与 water_group 与 tree_group 碰撞
    def not_vanish_collision(group1, group2):
        # 发生碰撞的小球在存储在字典中   每个key分别为group1中发生的碰撞的ball,  value 为与group2中与key发生碰撞的小球
        #  后两个参数为(是否删除group1中发生碰撞的ball, 是否删除group2发生碰撞的ball)
        collision_dict = pygame.sprite.groupcollide(group1, group2, False, False)
        # 存放  所有key
        sprites_from_group1 = list(collision_dict.keys())
        # 存放 所有value
        sprites_from_group2 = [sprite for sprites in collision_dict.values() for sprite in sprites]
        # [字典, group1中发生碰撞的精灵(所有的key),  group2中发生碰撞的精灵(所有的value)]
        return [collision_dict, sprites_from_group1, sprites_from_group2]

    @staticmethod
    # 改变发生碰撞的ball的property (infect)
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

    def display_pot(self, mouse_x, mouse_y):
        image = pygame.image.load(picture_path[7])
        rect = image.get_rect()
        rect.centerx = mouse_x
        rect.centery = mouse_y
        self.window.blit(image, rect)


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
        # ball属性
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
        # ball 想去的位置
        self.want_x = left
        self.want_y = top
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
            # 重置到原来的位置 防止小球完全重叠
            # 只有resolve_overlap方法调用了
            self.move_to_previous_position()
            self.collision_state = False

        elif PLAYER_CLASS == 'WaterBall' and self.moving is True and self.state == 'selected':
            # 每次移动前记录当前位置信息
            self.previous_position_list = self.previous_position()

            self.rect.top += self.speed * self.y_speed_ratio
            self.rect.left += self.speed * self.x_speed_ratio
            self.rect.top = max(0, self.rect.top)
            self.rect.top = min(SCREEN_HEIGHT - self.size[0], self.rect.top)
            self.rect.left = max(0, self.rect.left)
            self.rect.left = min(SCREEN_WEIGHT - self.size[1], self.rect.left)

    # 小球重置到原来的位置 防止小球完全重叠
    def move_to_previous_position(self):
        self.rect.left = self.previous_position_list[0] + self.x_speed_ratio
        self.rect.top = self.previous_position_list[1] + self.y_speed_ratio

    def collision_excursion(self, offset_x, offset_y):
        if self.collision_state is True and self.state == 'selected':
            # 每次移动前记录当前位置信息
            self.previous_position()
            # 对重叠小球进行偏移
            self.rect.move_ip(offset_x, offset_y)
            self.rect.top = max(0, self.rect.top)
            self.rect.top = min(SCREEN_HEIGHT - self.size[0], self.rect.top)
            self.rect.left = max(0, self.rect.left)
            self.rect.left = min(SCREEN_WEIGHT - self.size[1], self.rect.left)

            self.collision_state = False

    def display_ball(self, main_game):
        # 获取展示的对象
        # self.image = self.property_images[self.property]
        self.image = self.image_change()
        self.size = self.image.get_size()
        # 调用blit方法展示
        main_game.window.blit(self.image, self.rect)

    # 记录小球移动前位置
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
