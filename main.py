import pygame
import sys
import math
import random

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
BG_COLOR = (10, 12, 20)
GRID_COLOR = (25, 30, 45)
CELL_BG = (22, 26, 40)
CELL_BORDER = (45, 55, 75)
SHADOW_COLOR = (4, 5, 10)

# 霓虹色
NEON_BLUE = (0, 200, 255)
NEON_PURPLE = (170, 140, 255)
NEON_RED = (255, 80, 80)
NEON_GREEN = (80, 255, 120)
NEON_YELLOW = (255, 210, 70)
NEON_ORANGE = (255, 140, 0)
NEON_CYAN = (100, 255, 230)

TITLE_COLOR = (240, 245, 255)
SUB_TITLE_COLOR = (110, 120, 150)
HELP_TEXT = (100, 110, 140)

BTN_COLOR = (20, 28, 45)
BTN_HOVER = (35, 50, 80)
BTN_BORDER = (0, 200, 255)

DIRS = {'U': (0, -1), 'D': (0, 1), 'L': (-1, 0), 'R': (1, 0)}
MAX_MISTAKES = 3

# ---------- 关卡数据 ----------
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

# ---------- 画箭头函数（新：箭身 + 箭头） ----------
def draw_arrow(surface, x, y, direction, color=NEON_BLUE, outline_color=WHITE, scale=1.0):
    length = int(26 * scale)  # 箭总长（一半）
    if length <= 3:
        return

    shaft_w = max(3, int(7 * scale))       # 箭身粗细
    head_w = max(6, int(22 * scale))       # 箭头宽度
    head_len = max(8, int(18 * scale))     # 箭头长度

    if direction == 'R':
        tail = (x - length, y)
        head_base = (x + length - head_len, y)
        tip = (x + length, y)
        h1 = (x + length - head_len, y - head_w // 2)
        h2 = (x + length - head_len, y + head_w // 2)
    elif direction == 'L':
        tail = (x + length, y)
        head_base = (x - length + head_len, y)
        tip = (x - length, y)
        h1 = (x - length + head_len, y - head_w // 2)
        h2 = (x - length + head_len, y + head_w // 2)
    elif direction == 'U':
        tail = (x, y + length)
        head_base = (x, y - length + head_len)
        tip = (x, y - length)
        h1 = (x - head_w // 2, y - length + head_len)
        h2 = (x + head_w // 2, y - length + head_len)
    elif direction == 'D':
        tail = (x, y - length)
        head_base = (x, y + length - head_len)
        tip = (x, y + length)
        h1 = (x - head_w // 2, y + length - head_len)
        h2 = (x + head_w // 2, y + length - head_len)
    else:
        return

    # 1) 箭身（先画描边粗线，再画彩色细线）
    pygame.draw.line(surface, outline_color, tail, head_base, shaft_w + 2)
    pygame.draw.line(surface, color, tail, head_base, shaft_w)
    # 尾部圆端点
    pygame.draw.circle(surface, outline_color, tail, (shaft_w + 2) // 2)
    pygame.draw.circle(surface, color, tail, shaft_w // 2)

    # 2) 箭头（三角形填充 + 描边）
    pygame.draw.polygon(surface, outline_color, [tip, h1, h2])
    inner_scale = 0.72
    inner_tip = (tip[0] + (h1[0] - tip[0]) * (1 - inner_scale) * 0.5 + (h2[0] - tip[0]) * (1 - inner_scale) * 0.5,
                 tip[1] + (h1[1] - tip[1]) * (1 - inner_scale) * 0.5 + (h2[1] - tip[1]) * (1 - inner_scale) * 0.5)
    inner_h1 = (tip[0] + (h1[0] - tip[0]) * inner_scale,
                tip[1] + (h1[1] - tip[1]) * inner_scale)
    inner_h2 = (tip[0] + (h2[0] - tip[0]) * inner_scale,
                tip[1] + (h2[1] - tip[1]) * inner_scale)
    pygame.draw.polygon(surface, color, [inner_tip, inner_h1, inner_h2])

# ---------- 时间格式化 ----------
def format_time(t):
    if t < 60:
        return f"{t:.1f}s"
    m = int(t // 60)
    s = t - m * 60
    return f"{m}:{s:04.1f}"

# ---------- 漂移粒子类 ----------
class Particle:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.uniform(0, WIDTH)
        self.y = random.uniform(0, HEIGHT)
        self.size = random.uniform(0.5, 2.5)
        self.speed_x = random.uniform(-0.3, 0.3)
        self.speed_y = random.uniform(-0.5, -0.1)
        self.alpha = random.randint(30, 100)

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        if self.y < -10 or self.x < -10 or self.x > WIDTH + 10:
            self.reset()
            self.y = HEIGHT + 10

    def draw(self, surface):
        s = pygame.Surface((int(self.size * 4), int(self.size * 4)), pygame.SRCALPHA)
        pygame.draw.circle(s, (0, 200, 255, self.alpha), (int(self.size * 2), int(self.size * 2)), int(self.size * 2))
        surface.blit(s, (self.x - self.size * 2, self.y - self.size * 2))

# ---------- 飞行动画类 ----------
class FlyingArrow:
    def __init__(self, row, col, direction):
        self.direction = direction
        self.x = MARGIN_X + col * CELL_SIZE + CELL_SIZE // 2
        self.y = MARGIN_Y + row * CELL_SIZE + CELL_SIZE // 2
        self.speed = 6
        dx, dy = DIRS[direction]
        self.vx = dx * self.speed
        self.vy = dy * self.speed
        self.trail = []

    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 7: self.trail.pop(0)
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
        for i, (tx, ty) in enumerate(self.trail):
            scale = (i + 1) / len(self.trail) * 0.7
            trail_color = (0, int(150 * (i / len(self.trail))), 200)
            draw_arrow(screen, tx, ty, self.direction, trail_color, NEON_BLUE, scale)
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
                self.vx = -self.vx * 1.5
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

        # 字体
        self.font = pygame.font.SysFont("simhei", 24)
        self.label_font = pygame.font.SysFont("simhei", 14)
        self.value_font = pygame.font.SysFont("simhei", 24)
        self.value_font.set_bold(True)
        self.big_font = pygame.font.SysFont("simhei", 48)
        self.big_font.set_bold(True)
        self.title_font = pygame.font.SysFont("simhei", 64)
        self.title_font.set_bold(True)

        self.state = "START"
        self.level_index = 0
        self.grid = []
        self.mistakes = 0
        self.score = 0
        self.elapsed_time = 0.0
        self.flying_arrows = []
        self.bumping_arrows = []

        self.time = 0
        self.particles = [Particle() for _ in range(40)]

        self.start_btn_rect = pygame.Rect(WIDTH // 2 - 110, HEIGHT // 2 + 20, 220, 65)

        self.load_level(0)
        self.state = "START"

    def load_level(self, index):
        self.level_index = index
        self.grid = [row[:] for row in LEVELS[index]]
        self.mistakes = 0
        self.elapsed_time = 0.0
        self.flying_arrows = []
        self.bumping_arrows = []
        self.state = "PLAYING"

    def reset_level(self):
        self.score = 0
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
                    self.score += 10
                    if self.count_arrows() == 0:
                        self.state = "WIN"
                        self.score += 50
                else:
                    self.mistakes += 1
                    dist = self.get_block_dist(row, col, direction)
                    if dist > 0: self.bumping_arrows.append(BumpingArrow(row, col, direction, dist))
                    self.score = max(0, self.score - 5)
                    if self.mistakes >= MAX_MISTAKES: self.state = "LOSE"

    def update(self):
        self.time += 1
        if self.state == "PLAYING":
            self.elapsed_time += 1.0 / 60.0
        for p in self.particles:
            p.update()
        for arrow in self.flying_arrows[:]:
            arrow.update()
            if arrow.is_off_screen(): self.flying_arrows.remove(arrow)
        for arrow in self.bumping_arrows[:]:
            arrow.update()
            if arrow.finished: self.bumping_arrows.remove(arrow)

    def draw_start_screen(self):
        self.screen.fill(BG_COLOR)

        pulse = 1.0 + 0.1 * math.sin(self.time * 0.03)
        glow_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (0, 150, 255, 15), (WIDTH // 2, HEIGHT // 3), int(300 * pulse))
        pygame.draw.circle(glow_surf, (0, 100, 255, 8), (WIDTH // 2, HEIGHT // 3), int(450 * pulse))
        self.screen.blit(glow_surf, (0, 0))

        for p in self.particles:
            p.draw(self.screen)

        for r in range(ROWS):
            for c in range(COLS):
                rect = pygame.Rect(MARGIN_X + c * CELL_SIZE, MARGIN_Y + r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, GRID_COLOR, rect, 1)

        title_scale = 1.0 + 0.02 * math.sin(self.time * 0.05)
        title_text = "一箭又一箭"
        title_base = self.title_font.render(title_text, True, TITLE_COLOR)
        title_w = int(title_base.get_width() * title_scale)
        title_h = int(title_base.get_height() * title_scale)
        title = pygame.transform.smoothscale(title_base, (title_w, title_h))
        shadow = self.title_font.render(title_text, True, (0, 0, 0))
        shadow_w = int(shadow.get_width() * title_scale)
        shadow_h = int(shadow.get_height() * title_scale)
        shadow = pygame.transform.smoothscale(shadow, (shadow_w, shadow_h))
        self.screen.blit(shadow, (WIDTH // 2 - shadow.get_width() // 2 + 3, HEIGHT // 4 - 40 + 3))
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

    def draw_hud_card(self, x, y, w, h, label, value, accent_color):
        shadow_rect = pygame.Rect(x + 2, y + 2, w, h)
        pygame.draw.rect(self.screen, SHADOW_COLOR, shadow_rect, border_radius=10)
        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(self.screen, CELL_BG, rect, border_radius=10)
        accent_rect = pygame.Rect(x, y, w, 3)
        pygame.draw.rect(self.screen, accent_color, accent_rect,
                         border_top_left_radius=10, border_top_right_radius=10)
        pygame.draw.rect(self.screen, CELL_BORDER, rect, width=1, border_radius=10)
        label_surf = self.label_font.render(label, True, SUB_TITLE_COLOR)
        self.screen.blit(label_surf, (x + w // 2 - label_surf.get_width() // 2, y + 12))
        value_surf = self.value_font.render(value, True, accent_color)
        self.screen.blit(value_surf, (x + w // 2 - value_surf.get_width() // 2, y + 32))

    def draw_result_panel(self, is_win):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((6, 8, 15, 200))
        self.screen.blit(overlay, (0, 0))

        panel_w, panel_h = 460, 420
        panel_x = WIDTH // 2 - panel_w // 2
        panel_y = HEIGHT // 2 - panel_h // 2

        accent = NEON_GREEN if is_win else NEON_RED

        pulse = 1.0 + 0.08 * math.sin(self.time * 0.06)
        glow = pygame.Surface((panel_w + 80, panel_h + 80), pygame.SRCALPHA)
        for i in range(5, 0, -1):
            alpha = 12 - i
            pygame.draw.rect(glow, (*accent, max(alpha, 3)),
                             (40 - i * 3, 40 - i * 3, panel_w + i * 6, panel_h + i * 6),
                             border_radius=20 + i * 2)
        self.screen.blit(glow, (panel_x - 40, panel_y - 40))

        shadow = pygame.Surface((panel_w + 20, panel_h + 20), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 160), (0, 0, panel_w + 20, panel_h + 20), border_radius=22)
        self.screen.blit(shadow, (panel_x - 10, panel_y - 10))

        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        pygame.draw.rect(self.screen, (22, 28, 45), panel_rect, border_radius=18)

        inner_clip = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        for i in range(0, panel_w, 24):
            pygame.draw.line(inner_clip, (40, 50, 75, 50), (i, 0), (i, panel_h))
        for j in range(0, panel_h, 24):
            pygame.draw.line(inner_clip, (40, 50, 75, 50), (0, j), (panel_w, j))
        self.screen.blit(inner_clip, (panel_x, panel_y))

        top_glow = pygame.Surface((panel_w, 200), pygame.SRCALPHA)
        for i in range(200, 0, -10):
            alpha = max(0, int(30 * (i / 200) * pulse))
            pygame.draw.circle(top_glow, (*accent, alpha), (panel_w // 2, 0), i * 2)
        self.screen.blit(top_glow, (panel_x, panel_y))

        pygame.draw.rect(self.screen, accent, panel_rect, width=2, border_radius=18)
        inner_rect = pygame.Rect(panel_x + 6, panel_y + 6, panel_w - 12, panel_h - 12)
        pygame.draw.rect(self.screen, accent, inner_rect, width=1, border_radius=14)

        corner_len = 18
        corner_thickness = 3
        corners = [
            (panel_x + 12, panel_y + 12, 1, 1),
            (panel_x + panel_w - 12, panel_y + 12, -1, 1),
            (panel_x + 12, panel_y + panel_h - 12, 1, -1),
            (panel_x + panel_w - 12, panel_y + panel_h - 12, -1, -1),
        ]
        for cx, cy, dx, dy in corners:
            pygame.draw.line(self.screen, accent,
                             (cx, cy), (cx + corner_len * dx, cy), corner_thickness)
            pygame.draw.line(self.screen, accent,
                             (cx, cy), (cx, cy + corner_len * dy), corner_thickness)

        pygame.draw.rect(self.screen, accent, (panel_x, panel_y, panel_w, 4),
                         border_top_left_radius=18, border_top_right_radius=18)

        icon_cy = panel_y + 78
        icon_r = 40
        ring_r = int(icon_r + 10 + 5 * pulse)
        for angle in range(0, 360, 30):
            rad = math.radians(angle + self.time * 0.8)
            x1 = WIDTH // 2 + math.cos(rad) * ring_r
            y1 = icon_cy + math.sin(rad) * ring_r
            x2 = WIDTH // 2 + math.cos(rad) * (ring_r - 6)
            y2 = icon_cy + math.sin(rad) * (ring_r - 6)
            pygame.draw.line(self.screen, accent, (x1, y1), (x2, y2), 2)
        pygame.draw.circle(self.screen, (15, 20, 32), (WIDTH // 2, icon_cy), icon_r)
        pygame.draw.circle(self.screen, accent, (WIDTH // 2, icon_cy), icon_r, 3)
        inner_glow = pygame.Surface((icon_r * 2, icon_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(inner_glow, (*accent, 60), (icon_r, icon_r), icon_r - 6)
        self.screen.blit(inner_glow, (WIDTH // 2 - icon_r, icon_cy - icon_r))
        icon_char = "通" if is_win else "败"
        icon_font = pygame.font.SysFont("simhei", 40)
        icon_font.set_bold(True)
        icon_surf = icon_font.render(icon_char, True, accent)
        self.screen.blit(icon_surf, (WIDTH // 2 - icon_surf.get_width() // 2,
                                      icon_cy - icon_surf.get_height() // 2))

        title_text = "通 关" if is_win else "失 败"
        title = self.big_font.render(title_text, True, TITLE_COLOR)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, panel_y + 140))

        line_y = panel_y + 210
        line_w = 260
        line_x = WIDTH // 2 - line_w // 2
        line_surf = pygame.Surface((line_w, 2), pygame.SRCALPHA)
        for i in range(line_w):
            alpha = int(255 * (1 - abs(i - line_w / 2) / (line_w / 2)))
            pygame.draw.line(line_surf, (*accent, alpha), (i, 0), (i, 2))
        self.screen.blit(line_surf, (line_x, line_y))

        score_label = self.label_font.render("本 局 得 分", True, SUB_TITLE_COLOR)
        self.screen.blit(score_label, (WIDTH // 2 - score_label.get_width() // 2, panel_y + 228))

        big_score_font = pygame.font.SysFont("simhei", 46)
        big_score_font.set_bold(True)
        score_surf = big_score_font.render(str(self.score), True, NEON_YELLOW)
        self.screen.blit(score_surf, (WIDTH // 2 - score_surf.get_width() // 2, panel_y + 248))

        time_label = self.label_font.render("本 局 用 时", True, SUB_TITLE_COLOR)
        self.screen.blit(time_label, (WIDTH // 2 - time_label.get_width() // 2, panel_y + 318))

        big_time_font = pygame.font.SysFont("simhei", 32)
        big_time_font.set_bold(True)
        time_surf = big_time_font.render(format_time(self.elapsed_time), True, NEON_CYAN)
        self.screen.blit(time_surf, (WIDTH // 2 - time_surf.get_width() // 2, panel_y + 338))

        hint_text = "点击屏幕，进入下一关" if is_win else "点击屏幕，重新挑战"
        hint_pulse = 0.5 + 0.5 * math.sin(self.time * 0.1)
        hint_color = (
            int(120 + 130 * hint_pulse),
            int(140 + 110 * hint_pulse),
            int(180 + 75 * hint_pulse),
        )
        hint = self.font.render(hint_text, True, hint_color)
        self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, panel_y + panel_h - 45))

    def draw_game_screen(self):
        self.screen.fill(BG_COLOR)

        pulse = 1.0 + 0.08 * math.sin(self.time * 0.03)
        glow_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (0, 150, 255, 10), (WIDTH // 2, HEIGHT // 3), int(400 * pulse))
        self.screen.blit(glow_surf, (0, 0))

        for p in self.particles:
            p.draw(self.screen)

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

        if self.mistakes == 0: mistake_color = NEON_GREEN
        elif self.mistakes == 1: mistake_color = NEON_YELLOW
        elif self.mistakes == 2: mistake_color = NEON_ORANGE
        else: mistake_color = NEON_RED

        card_w, card_h = 116, 66
        gap = 10
        start_x = 20
        y = 12

        self.draw_hud_card(start_x, y, card_w, card_h, "关卡", str(self.level_index + 1), NEON_BLUE)
        self.draw_hud_card(start_x + (card_w + gap), y, card_w, card_h, "剩余箭头", str(self.count_arrows()), NEON_PURPLE)
        self.draw_hud_card(start_x + (card_w + gap) * 2, y, card_w, card_h, "失误", f"{self.mistakes}/{MAX_MISTAKES}", mistake_color)
        self.draw_hud_card(start_x + (card_w + gap) * 3, y, card_w, card_h, "得分", str(self.score), NEON_YELLOW)
        self.draw_hud_card(start_x + (card_w + gap) * 4, y, card_w, card_h, "用时", format_time(self.elapsed_time), NEON_CYAN)

        restart_rect = pygame.Rect(WIDTH - 140, 15, 120, 60)
        pygame.draw.rect(self.screen, BTN_COLOR, restart_rect, border_radius=10)
        pygame.draw.rect(self.screen, BTN_BORDER, restart_rect, width=2, border_radius=10)
        restart_text = self.font.render("重新开始", True, WHITE)
        self.screen.blit(restart_text, (restart_rect.centerx - restart_text.get_width() // 2,
                                        restart_rect.centery - restart_text.get_height() // 2))

        if self.state == "WIN":
            self.draw_result_panel(is_win=True)
        elif self.state == "LOSE":
            self.draw_result_panel(is_win=False)

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
                        self.elapsed_time = 0.0
                        self.state = "PLAYING"
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = pygame.mouse.get_pos()
                    if self.state == "START":
                        if self.start_btn_rect.collidepoint(pos):
                            self.elapsed_time = 0.0
                            self.state = "PLAYING"
                    elif self.state == "PLAYING":
                        restart_rect = pygame.Rect(WIDTH - 140, 15, 120, 60)
                        if restart_rect.collidepoint(pos): self.reset_level()
                        else: self.handle_click(pos)
                    elif self.state == "WIN":
                        if self.level_index + 1 < len(LEVELS):
                            self.load_level(self.level_index + 1)
                        else:
                            self.score = 0
                            self.state = "START"
                    elif self.state == "LOSE":
                        self.reset_level()
            self.update()
            self.draw()
            self.clock.tick(60)

if __name__ == "__main__":
    game = Game()
    game.run()