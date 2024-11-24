import math
import sys
from pathlib import Path
import pygame

SCREEN_WEIGHT = 1500
SCREEN_HEIGHT = 770
BG_COLOR = pygame.Color(0, 0, 0)
TEXT_COLOR = pygame.Color(255, 255, 255)
current_dir = Path(__file__).resolve().parent
picture_path = [
    str(current_dir) + "\\..\\static\\greenBall.png",
    str(current_dir) + "\\..\\static\\greyBall.png"
]


class MainGame:
    def __init__(self):
        self.window = None
        self.game_name = "Infect"
        self.version = "V1.1"
        self.my_ball = None
        self.mouse_x = 0
        self.mouse_y = 0

    def start_game(self):

        self.init_game()

        while True:
            self.window.fill(BG_COLOR)
            self.window.\
                blit(pygame.font.SysFont("kaiti", 18).render("时间", True, TEXT_COLOR), (SCREEN_WEIGHT / 2 - 50, 10))
            self.my_ball.move()
            self.my_ball.display_ball(self)

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
                    ball_position_range = self.my_ball.ball_position_range()
                    if self.position_in_range(ball_position_range):
                        if self.my_ball.state == 'unselected':
                            self.my_ball.state = 'selected'
                        elif self.my_ball.state == 'selected':
                            self.my_ball.state = 'unselected'
                self.move_ball()
            self.move_ball()
            pygame.display.flip()

    def init_game(self):
        # 使用pygame之前必须初始化
        pygame.init()
        # 设置主屏窗口
        self.window = pygame.display.set_mode([SCREEN_WEIGHT, SCREEN_HEIGHT])
        # 初始化Ball
        self.my_ball = Ball(SCREEN_WEIGHT / 2, SCREEN_HEIGHT / 2)
        # 设置窗口的标题，即游戏名称
        pygame.display.set_caption(self.game_name + "   " + self.version)

    def position_in_range(self, ball_position_range):
        return ball_position_range[0] <= self.mouse_x <= ball_position_range[2] and\
                ball_position_range[1] <= self.mouse_y <= ball_position_range[3]

    def move_ball(self):
        self.mouse_x = pygame.mouse.get_pos()[0]
        self.mouse_y = pygame.mouse.get_pos()[1]
        ball_position_range = self.my_ball.ball_position_range()
        if self.position_in_range(ball_position_range):
            self.my_ball.moving = False
        else:
            self.my_ball.moving = True
            dist = [self.mouse_x - ball_position_range[4], self.mouse_y - ball_position_range[5]]
            result = math.sqrt(dist[0] ** 2 + dist[1] ** 2)
            self.my_ball.x_speed_ratio = dist[0] / result
            self.my_ball.y_speed_ratio = dist[1] / result


class Ball:
    # 位置初始化
    def __init__(self, left, top):
        self.images = {
            'selected': pygame.image.load(picture_path[0]),
            'unselected': pygame.image.load(picture_path[1])
        }
        # 选中状态
        self.state = "unselected"
        # 根据选中状态加载图片
        self.image = self.images[self.state]
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
        self.moveDirection_Up = False
        self.moveDirection_Left = False
        self.speed = 1
        self.x_speed_ratio = float(0)
        self.y_speed_ratio = float(0)

    def move(self):

        if self.moving is True:
            self.rect.top += self.speed * self.y_speed_ratio
            self.rect.left += self.speed * self.x_speed_ratio
            self.rect.top = max(0, self.rect.top)
            self.rect.top = min(SCREEN_HEIGHT - self.size[0], self.rect.top)
            self.rect.left = max(0, self.rect.left)
            self.rect.left = min(SCREEN_WEIGHT - self.size[1], self.rect.left)

    def display_ball(self, main_game):
        # 获取展示的对象
        self.image = self.images[self.state]
        self.size = self.image.get_size()
        # 调用blit方法展示
        main_game.window.blit(self.image, self.rect)

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


if __name__ == '__main__':
    game = MainGame()
    game.start_game()
