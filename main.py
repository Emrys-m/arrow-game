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

# ---------- 高级感深色配色 ----------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

BG_COLOR = (10, 12, 20)          # 深色背景
GRID_COLOR = (25, 30, 45)        # 极暗网格线
CELL_BG = (22, 26, 40)           # 格子底色
CELL_BORDER = (45, 55, 75)       # 格子边框

NEON_BLUE = (0, 200, 255)        # 霓虹青色箭头（正常）
NEON_RED = (255, 80, 80)         # 霓虹红色箭头（碰撞）
NEON_GREEN = (80, 255, 120)      # 霓虹绿色文字（通关）

TITLE_COLOR = (240, 245, 255)    # 亮白
SUB_TITLE_COLOR = (140, 150, 180)
HELP_TEXT = (100, 110, 140)

BTN_COLOR = (20, 28, 45)         # 深色按钮
BTN_HOVER = (35, 50, 80)         # 按钮悬停
BTN_BORDER = (0, 200, 255)       # 青色边框

DIRS = {'U': (0, -1), 'D': (0, 1), 'L': (-1, 0), 'R': (1, 0)}
MAX_MISTAKES = 3

# ---------- 关卡数据（5 关，难度逐级递增） ----------
LEVELS = [
    [
        [None, 'R', None, None, None],
        [None, None, None, None, None],
        [None, 'D', None, 'L', None],
        [None, None, None, None, None],
        [None, None, None, 'U', None]
    ],
    [
        [None, 'R', 'R', None, None],
        [None, 'D', None, 'U', None],
        [None, None, 'L', None, None],
        [None, None, 'D', None, None],
        [None, None, None, None, None]
    ],
    [
        [None, 'R', 'R', 'R', None],
        ['D', 'D', 'L', 'U', 'R'],
        ['D', 'L', 'U', 'L', 'D'],
        ['D', 'L', 'D', 'U', 'D'],
        [None, 'R', 'R', None, None]
    ],
    [
        [None, 'R', 'R', 'R', 'R'],
        ['D', 'D', 'D', 'U', 'U'],
        ['D', 'L', 'D', 'L', 'D'],
        ['D', 'L', 'U', 'L', 'R'],
        [None, 'R', 'R', 'R', None]
    ],
    [
        ['R', 'R', 'R', 'R', 'R'],
        ['D', 'L', 'L', 'L', 'U'],
        ['D', 'L', 'D', 'L', 'U'],
        ['D', 'L', 'U', 'L', 'U'],
        ['R', 'R', 'R', 'R', 'R']
    ]
]

# ---------- 画箭头函数（支持缩放，用于残影） ----------
def draw_arrow(surface, x, y, direction, color=NEON_BLUE, outline_color=WHITE, scale=1.0):
    size = int(25 * scale)
    if size <= 0: return
    
    if direction == 'U':
        points = [(x, y - size), (x - size, y + size), (x, y + size // 2), (x + size, y + size)]
    elif direction == 'D':
        points = [(x, y + size), (x - size, y - size), (x, y - size // 2), (x + size, y - size)]
    elif direction == 'L':
        points = [(x - size, y), (x + size, y - size), (x + size // 2, y), (x + size, y + size)]
    elif direction == 'R':
        points = [(x + size, y), (x - size, y - size), (x - size // 2, y), (x - size, y + size)]
    else:
        return
    pygame.draw.polygon(surface, color, points)
    pygame.draw.polygon(surface, outline_color, points, max(1, int(2 * scale)))

# ---------- 飞行动画类（加入加速和拖尾） ----------
class FlyingArrow:
    def __init__(self, row, col, direction):
        self.direction = direction
        self.x = MARGIN_X + col * CELL_SIZE + CELL_SIZE // 2
        self.y = MARGIN_Y + row * CELL_SIZE + CELL_SIZE // 2
        
        # 新增：初始速度较慢，飞行过程中加速
        self.speed = 6 
        dx, dy = DIRS[direction]
        self.vx = dx * self.speed
        self.vy = dy * self.speed
        
        # 新增：拖尾残影集合
        self.trail = []

    def update(self):
        # 记录当前坐标进入拖尾数组
        self.trail.append((self.x, self.y))
        if len(self.trail) > 7:  # 保留最近7帧的位置
            self.trail.pop(0)

        # 加速效果：每帧速度增加，带来弹射感
        self.speed += 1.2
        dx, dy = DIRS[self.direction]
        self.vx = dx * self.speed
        self.vy = dy * self.speed

        self.x += self.vx
        self.y += self.vy

    def is_off_screen(self):
        return (self.x < -CELL_SIZE or self.x > WIDTH + CELL_SIZE or
                self.y < -CELL_SIZE or self.y > HEIGHT + CELL_SIZE)

    def draw(self, screen):
        # 1. 绘制拖尾残影
        for i, (tx, ty) in enumerate(self.trail):
            # 越靠后的残影越小、颜色越暗（逼近背景色）
            scale = (i + 1) / len(self.trail) * 0.7  # 缩放比例 0.1 ~ 0.7
            trail_color = (0, int(150 * (i / len(self.trail))), 200) # 颜色逐渐变暗
            draw_arrow(screen, tx, ty, self.direction, trail_color, NEON_BLUE, scale)
        
        # 2. 绘制本体
        draw_arrow(screen, self.x, self.y, self.direction, NEON_BLUE, WHITE)

# ---------- 碰撞弹回动画类 ----------
class BumpingArrow:
    def __init__(self, row, col, direction, max_dist):
        self.row = row
        self.col = col
        self.direction = direction
        self.start_x = MARGIN_X + col * CELL_SIZE + CELL_SIZE // 2
        self.start_y = MARGIN_Y + row * CELL_SIZE + CELL_SIZE // 2
        self.x = self.start_x
        self.y = self.start_y
        self.max_dist = max_dist

        self.speed = 12
        dx, dy = DIRS[direction]
        self.vx = dx * self.speed
        self.vy = dy * self.speed

        self.distance_traveled = 0
        self.state = "forward"
        self.finished = False

    def update(self):
        if self.state == "forward":
            self.x += self.vx
            self.y += self.vy
            self.distance_traveled += self.speed
            if self.distance_traveled >= self.max_dist:
                self.state = "backward"
                self.x -= self.vx
                self.y -= self.vy
                self.vx = -self.vx * 1.5  # 弹回时加速，显得有力量感
                self.vy = -self.vy * 1.5
        elif self.state == "backward":
            self.x += self.vx
            self.y += self.vy
            self.distance_traveled -= abs(self.speed * 1.5)
            dx = self.x - self.start_x
            dy = self.y - self.start_y
            if math.hypot(dx, dy) <= abs(self.speed * 1.5):
                self.x = self.start_x
                self.y = self.start_y
                self.finished = True

    def draw(self, screen):
        draw_arrow(screen, self.x, self.y, self.direction, NEON_RED, WHITE)

# ---------- 游戏主类 ----------
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("一箭又一箭")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("simhei", 24)
        self.big_font = pygame.font.SysFont("simhei", 48)
        self.title_font = pygame.font.SysFont("simhei", 64)

        self.state = "START"
        self.level_index = 0
        self.grid = []
        self.mistakes = 0
        self.flying_arrows = []
        self.bumping_arrows = []

        self.start_btn_rect = pygame.Rect(WIDTH // 2 - 110, HEIGHT // 2 + 20, 220, 65)

        self.load_level(0)
        self.state = "START"

    def load_level(self, index):
        self.level_index = index
        self.grid = [row[:] for row in LEVELS[index]]
        self.mistakes = 0
        self.flying_arrows = []
        self.bumping_arrows = []
        self.state = "PLAYING"

    def reset_level(self):
        self.load_level(self.level_index)

    def count_arrows(self):
        return sum(1 for row in self.grid for cell in row if cell is not None)

    def is_path_clear(self, row, col, direction):
        if direction == 'R':
            for c in range(col + 1, COLS):
                if self.grid[row][c] is not None: return False
        elif direction == 'L':
            for c in range(col - 1, -1, -1):
                if self.grid[row][c] is not None: return False
        elif direction == 'U':
            for r in range(row - 1, -1, -1):
                if self.grid[r][col] is not None: return False
        elif direction == 'D':
            for r in range(row + 1, ROWS):
                if self.grid[r][col] is not None: return False
        return True

    def get_block_dist(self, row, col, direction):
        if direction == 'R':
            for c in range(col + 1, COLS):
                if self.grid[row][c] is not None: return (c - col) * CELL_SIZE - 20
        elif direction == 'L':
            for c in range(col - 1, -1, -1):
                if self.grid[row][c] is not None: return (col - c) * CELL_SIZE - 20
        elif direction == 'U':
            for r in range(row - 1, -1, -1):
                if self.grid[r][col] is not None: return (row - r) * CELL_SIZE - 20
        elif direction == 'D':
            for r in range(row + 1, ROWS):
                if self.grid[r][col] is not None: return (r - row) * CELL_SIZE - 20
        return 0

    def handle_click(self, pos):
        if self.state != "PLAYING": return
        x, y = pos
        col = (x - MARGIN_X) // CELL_SIZE
        row = (y - MARGIN_Y) // CELL_SIZE
        if 0 <= row < ROWS and 0 <= col < COLS:
            direction = self.grid[row][col]
            if direction:
                if any(a.row == row and a.col == col for a in self.bumping_arrows): return
                if self.is_path_clear(row, col, direction):
                    self.grid[row][col] = None
                    self.flying_arrows.append(FlyingArrow(row, col, direction))
                    if self.count_arrows() == 0: self.state = "WIN"
                else:
                    self.mistakes += 1
                    dist = self.get_block_dist(row, col, direction)
                    if dist > 0: self.bumping_arrows.append(BumpingArrow(row, col, direction, dist))
                    if self.mistakes >= MAX_MISTAKES: self.state = "LOSE"

    def update(self):
        for arrow in self.flying_arrows[:]:
            arrow.update()
            if arrow.is_off_screen(): self.flying_arrows.remove(arrow)
        for arrow in self.bumping_arrows[:]:
            arrow.update()
            if arrow.finished: self.bumping_arrows.remove(arrow)

    def draw_start_screen(self):
        self.screen.fill(BG_COLOR)
        glow_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (0, 150, 255, 15), (WIDTH // 2, HEIGHT // 3), 300)
        pygame.draw.circle(glow_surf, (0, 100, 255, 8), (WIDTH // 2, HEIGHT // 3), 450)
        self.screen.blit(glow_surf, (0, 0))

        for r in range(ROWS):
            for c in range(COLS):
                rect = pygame.Rect(MARGIN_X + c * CELL_SIZE, MARGIN_Y + r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, GRID_COLOR, rect, 1)

        title_text = "一箭又一箭"
        shadow = self.title_font.render(title_text, True, (0, 0, 0))
        self.screen.blit(shadow, (WIDTH // 2 - shadow.get_width() // 2 + 3, HEIGHT // 4 - 40 + 3))
        title = self.title_font.render(title_text, True, TITLE_COLOR)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4 - 40))

        sub_title = self.font.render("点击箭头，让它飞出棋盘", True, SUB_TITLE_COLOR)
        self.screen.blit(sub_title, (WIDTH // 2 - sub_title.get_width() // 2, HEIGHT // 4 + 40))

        mouse_pos = pygame.mouse.get_pos()
        hover = self.start_btn_rect.collidepoint(mouse_pos)
        btn_color = BTN_HOVER if hover else BTN_COLOR
        pygame.draw.rect(self.screen, btn_color, self.start_btn_rect, border_radius=12)
        border_color = (0, 255, 255) if hover else BTN_BORDER
        pygame.draw.rect(self.screen, border_color, self.start_btn_rect, width=2, border_radius=12)

        btn_text = self.font.render("开始游戏", True, WHITE)
        self.screen.blit(btn_text, (self.start_btn_rect.centerx - btn_text.get_width() // 2,
                                     self.start_btn_rect.centery - btn_text.get_height() // 2))

        help_lines = [
            "规则：点击箭头，若前方无阻挡则飞出并消失。",
            "若前方有阻挡，箭头会碰撞弹回，失误次数 +1。",
            "失误 3 次游戏失败，消除所有箭头则通关。",
            "按 空格键 或 点击按钮开始游戏。"
        ]
        for i, line in enumerate(help_lines):
            help_surf = self.font.render(line, True, HELP_TEXT)
            self.screen.blit(help_surf, (WIDTH // 2 - help_surf.get_width() // 2, HEIGHT - 160 + i * 30))

    def draw_game_screen(self):
        self.screen.fill(BG_COLOR)
        glow_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (0, 150, 255, 10), (WIDTH // 2, HEIGHT // 3), 400)
        self.screen.blit(glow_surf, (0, 0))

        for r in range(ROWS):
            for c in range(COLS):
                x = MARGIN_X + c * CELL_SIZE
                y = MARGIN_Y + r * CELL_SIZE
                rect = pygame.Rect(x + 2, y + 2, CELL_SIZE - 4, CELL_SIZE - 4)
                pygame.draw.rect(self.screen, CELL_BG, rect, border_radius=8)
                pygame.draw.rect(self.screen, CELL_BORDER, rect, width=2, border_radius=8)

        for r in range(ROWS):
            for c in range(COLS):
                direction = self.grid[r][c]
                if direction:
                    is_bumping = any(a.row == r and a.col == c for a in self.bumping_arrows)
                    if not is_bumping:
                        cx = MARGIN_X + c * CELL_SIZE + CELL_SIZE // 2
                        cy = MARGIN_Y + r * CELL_SIZE + CELL_SIZE // 2
                        draw_arrow(self.screen, cx, cy, direction, NEON_BLUE, WHITE)

        for arrow in self.flying_arrows: arrow.draw(self.screen)
        for arrow in self.bumping_arrows: arrow.draw(self.screen)

        info_surf = self.font.render(f"关卡: {self.level_index + 1}   剩余箭头: {self.count_arrows()}   失误: {self.mistakes}/{MAX_MISTAKES}", True, TITLE_COLOR)
        self.screen.blit(info_surf, (20, 20))

        restart_rect = pygame.Rect(WIDTH - 150, 20, 120, 40)
        pygame.draw.rect(self.screen, BTN_COLOR, restart_rect, border_radius=8)
        pygame.draw.rect(self.screen, BTN_BORDER, restart_rect, width=2, border_radius=8)
        restart_text = self.font.render("重新开始", True, WHITE)
        self.screen.blit(restart_text, (restart_rect.centerx - restart_text.get_width() // 2,
                                        restart_rect.centery - restart_text.get_height() // 2))

        if self.state == "WIN":
            win_text = self.big_font.render("通关！", True, NEON_GREEN)
            self.screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2 - 50))
            hint = self.font.render("点击进入下一关", True, TITLE_COLOR)
            self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 20))
        elif self.state == "LOSE":
            lose_text = self.big_font.render("失败！", True, NEON_RED)
            self.screen.blit(lose_text, (WIDTH // 2 - lose_text.get_width() // 2, HEIGHT // 2 - 50))
            hint = self.font.render("点击重新开始", True, TITLE_COLOR)
            self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 20))

    def draw(self):
        if self.state == "START": self.draw_start_screen()
        else: self.draw_game_screen()
        pygame.display.flip()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.state == "START":
                        self.state = "PLAYING"
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = pygame.mouse.get_pos()
                    if self.state == "START":
                        if self.start_btn_rect.collidepoint(pos): self.state = "PLAYING"
                    elif self.state == "PLAYING":
                        restart_rect = pygame.Rect(WIDTH - 150, 20, 120, 40)
                        if restart_rect.collidepoint(pos): self.reset_level()
                        else: self.handle_click(pos)
                    elif self.state == "WIN":
                        if self.level_index + 1 < len(LEVELS): self.load_level(self.level_index + 1)
                        else: self.state = "START"
                    elif self.state == "LOSE": self.reset_level()
            self.update()
            self.draw()
            self.clock.tick(60)

if __name__ == "__main__":
    game = Game()
    game.run()