import pygame
import sys

# 初始化 Pygame
pygame.init()

# ---------- 常量设置 ----------
WIDTH, HEIGHT = 800, 600
ROWS, COLS = 5, 5
CELL_SIZE = 80

MARGIN_X = (WIDTH - COLS * CELL_SIZE) // 2
MARGIN_Y = (HEIGHT - ROWS * CELL_SIZE) // 2 + 30

WHITE = (255, 255, 255)
GRAY = (180, 180, 180)
BLUE = (70, 130, 180)   # 箭头颜色
BLACK = (0, 0, 0)

# ---------- 关卡数据（二维数组） ----------
grid = [
    [None, 'R', None, None, None],
    [None, 'D', None, 'L', None],
    [None, None, None, None, None],
    [None, None, None, None, None],
    [None, None, None, None, None]
]

# 创建窗口
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("一箭又一箭")
clock = pygame.time.Clock()

# ---------- 画箭头的函数 ----------
def draw_arrow(surface, x, y, direction):
    """在 (x, y) 位置画一个朝向 direction 的三角形箭头"""
    size = 25  # 箭头大小

    if direction == 'U':      # 向上
        points = [(x, y - size), (x - size, y + size), (x + size, y + size)]
    elif direction == 'D':    # 向下
        points = [(x, y + size), (x - size, y - size), (x + size, y - size)]
    elif direction == 'L':    # 向左
        points = [(x - size, y), (x + size, y - size), (x + size, y + size)]
    elif direction == 'R':    # 向右
        points = [(x + size, y), (x - size, y - size), (x - size, y + size)]
    else:
        return

    # 画实心三角形 + 黑色边框
    pygame.draw.polygon(surface, BLUE, points)
    pygame.draw.polygon(surface, BLACK, points, 2)

# ---------- 主循环 ----------
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(WHITE)

    # 画网格
    for r in range(ROWS):
        for c in range(COLS):
            x = MARGIN_X + c * CELL_SIZE
            y = MARGIN_Y + r * CELL_SIZE
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, GRAY, rect, 2)

    # 画箭头
    for r in range(ROWS):
        for c in range(COLS):
            direction = grid[r][c]
            if direction is not None:
                # 计算格子中心点
                center_x = MARGIN_X + c * CELL_SIZE + CELL_SIZE // 2
                center_y = MARGIN_Y + r * CELL_SIZE + CELL_SIZE // 2
                draw_arrow(screen, center_x, center_y, direction)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()