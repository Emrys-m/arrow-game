import pygame
import sys
import math

# 初始化 Pygame
pygame.init()

# ---------- 常量设置 ----------
WIDTH, HEIGHT = 800, 600
ROWS, COLS = 5, 5
CELL_SIZE = 80
MARGIN_X = (WIDTH - COLS * CELL_SIZE) // 2
MARGIN_Y = (HEIGHT - ROWS * CELL_SIZE) // 2 + 40

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
BLUE = (70, 130, 180)
RED = (220, 20, 60)
GREEN = (34, 139, 34)

DIRS = {'U': (0, -1), 'D': (0, 1), 'L': (-1, 0), 'R': (1, 0)}
MAX_MISTAKES = 3

# ---------- 关卡数据（至少 3 关） ----------
LEVELS = [
    # 关卡 1：简单，无阻挡
    [
        [None, 'R', None, None, None],
        [None, None, None, None, None],
        [None, 'D', None, 'L', None],
        [None, None, None, None, None],
        [None, None, None, None, None]
    ],
    # 关卡 2：有阻挡，需按顺序消除
    [
        [None, 'R', 'R', None, None],
        [None, 'D', None, 'U', None],
        [None, None, None, None, None],
        [None, None, None, None, None],
        [None, None, None, None, None]
    ],
    # 关卡 3：更复杂
    [
        [None, 'R', 'R', None, None],
        [None, 'D', 'L', 'L', None],
        [None, 'D', None, None, None],
        [None, None, None, None, None],
        [None, None, None, None, None]
    ]
]

# ---------- 画箭头函数 ----------
def draw_arrow(surface, x, y, direction, color=BLUE):
    size = 25
    if direction == 'U':
        points = [(x, y - size), (x - size, y + size), (x + size, y + size)]
    elif direction == 'D':
        points = [(x, y + size), (x - size, y - size), (x + size, y - size)]
    elif direction == 'L':
        points = [(x - size, y), (x + size, y - size), (x + size, y + size)]
    elif direction == 'R':
        points = [(x + size, y), (x - size, y - size), (x - size, y + size)]
    else:
        return
    pygame.draw.polygon(surface, color, points)
    pygame.draw.polygon(surface, BLACK, points, 2)

# ---------- 飞行动画类 ----------
class FlyingArrow:
    def __init__(self, row, col, direction):
        self.direction = direction
        self.x = MARGIN_X + col * CELL_SIZE + CELL_SIZE // 2
        self.y = MARGIN_Y + row * CELL_SIZE + CELL_SIZE // 2
        self.speed = 15
        dx, dy = DIRS[direction]
        self.vx = dx * self.speed
        self.vy = dy * self.speed

    def update(self):
        self.x += self.vx
        self.y += self.vy

    def is_off_screen(self):
        return (self.x < -CELL_SIZE or self.x > WIDTH + CELL_SIZE or
                self.y < -CELL_SIZE or self.y > HEIGHT + CELL_SIZE)

    def draw(self, screen):
        draw_arrow(screen, self.x, self.y, self.direction, BLUE)

# ---------- 游戏主类 ----------
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("一箭又一箭")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("simhei", 24)
        self.big_font = pygame.font.SysFont("simhei", 48)

        self.state = "START"  # START, PLAYING, WIN, LOSE
        self.level_index = 0
        self.grid = []
        self.mistakes = 0
        self.flying_arrows = []
        self.shake_timers = {}  # 记录晃动的箭头 {(row, col): timer}
        self.load_level(0)

    def load_level(self, index):
        self.level_index = index
        # 深拷贝关卡数据，防止修改原数据
        self.grid = [row[:] for row in LEVELS[index]]
        self.mistakes = 0
        self.flying_arrows = []
        self.shake_timers = {}
        self.state = "PLAYING"

    def reset_level(self):
        self.load_level(self.level_index)

    def count_arrows(self):
        return sum(1 for row in self.grid for cell in row if cell is not None)

    def is_path_clear(self, row, col, direction):
        if direction == 'R':
            for c in range(col + 1, COLS):
                if self.grid[row][c] is not None:
                    return False
        elif direction == 'L':
            for c in range(col - 1, -1, -1):
                if self.grid[row][c] is not None:
                    return False
        elif direction == 'U':
            for r in range(row - 1, -1, -1):
                if self.grid[r][col] is not None:
                    return False
        elif direction == 'D':
            for r in range(row + 1, ROWS):
                if self.grid[r][col] is not None:
                    return False
        return True

    def handle_click(self, pos):
        if self.state != "PLAYING":
            return
        x, y = pos
        col = (x - MARGIN_X) // CELL_SIZE
        row = (y - MARGIN_Y) // CELL_SIZE
        if 0 <= row < ROWS and 0 <= col < COLS:
            direction = self.grid[row][col]
            if direction:
                if self.is_path_clear(row, col, direction):
                    # 消除箭头，添加飞行动画
                    self.grid[row][col] = None
                    self.flying_arrows.append(FlyingArrow(row, col, direction))
                    if self.count_arrows() == 0:
                        self.state = "WIN"
                else:
                    # 碰撞反馈
                    self.mistakes += 1
                    self.shake_timers[(row, col)] = 15  # 晃动 15 帧
                    if self.mistakes >= MAX_MISTAKES:
                        self.state = "LOSE"

    def update(self):
        # 更新飞行动画
        for arrow in self.flying_arrows[:]:
            arrow.update()
            if arrow.is_off_screen():
                self.flying_arrows.remove(arrow)
        # 更新晃动计时器
        for key in list(self.shake_timers.keys()):
            self.shake_timers[key] -= 1
            if self.shake_timers[key] <= 0:
                del self.shake_timers[key]

    def draw(self):
        self.screen.fill(WHITE)

        if self.state == "START":
            title = self.big_font.render("一箭又一箭", True, BLACK)
            self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 100))
            hint = self.font.render("按空格键或点击开始游戏", True, BLACK)
            self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2))
        else:
            # 画网格
            for r in range(ROWS):
                for c in range(COLS):
                    rect = pygame.Rect(MARGIN_X + c * CELL_SIZE, MARGIN_Y + r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(self.screen, GRAY, rect, 2)

            # 画箭头
            for r in range(ROWS):
                for c in range(COLS):
                    direction = self.grid[r][c]
                    if direction:
                        cx = MARGIN_X + c * CELL_SIZE + CELL_SIZE // 2
                        cy = MARGIN_Y + r * CELL_SIZE + CELL_SIZE // 2
                        # 晃动效果
                        if (r, c) in self.shake_timers:
                            offset = math.sin(self.shake_timers[(r, c)] * 0.8) * 6
                            cx += offset
                        draw_arrow(self.screen, cx, cy, direction)

            # 画飞行中的箭头
            for arrow in self.flying_arrows:
                arrow.draw(self.screen)

            # 信息栏
            info = self.font.render(f"关卡: {self.level_index + 1}  剩余箭头: {self.count_arrows()}  失误: {self.mistakes}/{MAX_MISTAKES}", True, BLACK)
            self.screen.blit(info, (20, 20))

            # 重新开始按钮
            restart_rect = pygame.Rect(WIDTH - 150, 20, 120, 40)
            pygame.draw.rect(self.screen, GRAY, restart_rect)
            restart_text = self.font.render("重新开始", True, BLACK)
            self.screen.blit(restart_text, (restart_rect.x + 10, restart_rect.y + 8))

            # 结算界面
            if self.state == "WIN":
                win_text = self.big_font.render("通关！", True, GREEN)
                self.screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2 - 50))
                hint = self.font.render("点击进入下一关", True, BLACK)
                self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 20))
            elif self.state == "LOSE":
                lose_text = self.big_font.render("失败！", True, RED)
                self.screen.blit(lose_text, (WIDTH // 2 - lose_text.get_width() // 2, HEIGHT // 2 - 50))
                hint = self.font.render("点击重新开始", True, BLACK)
                self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 20))

        pygame.display.flip()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.state == "START":
                        self.state = "PLAYING"
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = pygame.mouse.get_pos()
                    if self.state == "START":
                        self.state = "PLAYING"
                    elif self.state == "PLAYING":
                        restart_rect = pygame.Rect(WIDTH - 150, 20, 120, 40)
                        if restart_rect.collidepoint(pos):
                            self.reset_level()
                        else:
                            self.handle_click(pos)
                    elif self.state == "WIN":
                        if self.level_index + 1 < len(LEVELS):
                            self.load_level(self.level_index + 1)
                        else:
                            self.state = "START"
                    elif self.state == "LOSE":
                        self.reset_level()
            self.update()
            self.draw()
            self.clock.tick(60)

if __name__ == "__main__":
    game = Game()
    game.run()