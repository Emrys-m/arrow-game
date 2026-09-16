import pygame
import sys

# 初始化
pygame.init()

# ---------- 常量 ----------
WIDTH, HEIGHT = 800, 600
ROWS, COLS = 5, 5
CELL_SIZE = 80
MARGIN_X = (WIDTH - COLS * CELL_SIZE) // 2
MARGIN_Y = (HEIGHT - ROWS * CELL_SIZE) // 2 + 30

WHITE = (255, 255, 255)
GRAY = (180, 180, 180)
BLUE = (70, 130, 180)
BLACK = (0, 0, 0)
RED = (220, 20, 60)

MAX_MISTAKES = 3

# ---------- 关卡数据 ----------
# R=右 L=左 U=上 D=下
grid = [
    [None, 'R', None, None, None],
    [None, 'D', None, 'L', None],
    [None, None, None, None, None],
    [None, None, None, None, None],
    [None, None, None, None, None]
]

mistakes = 0

# 创建窗口
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("一箭又一箭")
clock = pygame.time.Clock()
font = pygame.font.SysFont("simhei", 24)

# ---------- 画箭头 ----------
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

# ---------- 路径检测（核心） ----------
def is_path_clear(grid, row, col, direction):
    """返回 True 表示前方无阻挡，False 表示有阻挡"""
    if direction == 'R':
        for c in range(col + 1, COLS):
            if grid[row][c] is not None:
                return False
    elif direction == 'L':
        for c in range(col - 1, -1, -1):
            if grid[row][c] is not None:
                return False
    elif direction == 'U':
        for r in range(row - 1, -1, -1):
            if grid[r][col] is not None:
                return False
    elif direction == 'D':
        for r in range(row + 1, ROWS):
            if grid[r][col] is not None:
                return False
    return True

# ---------- 统计剩余箭头 ----------
def count_arrows(grid):
    count = 0
    for r in range(ROWS):
        for c in range(COLS):
            if grid[r][c] is not None:
                count += 1
    return count

# ---------- 主循环 ----------
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # 鼠标点击
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()
            # 把像素坐标转换成棋盘的行列坐标
            col = (mx - MARGIN_X) // CELL_SIZE
            row = (my - MARGIN_Y) // CELL_SIZE

            # 判断点击是否在棋盘内
            if 0 <= row < ROWS and 0 <= col < COLS:
                direction = grid[row][col]
                if direction is not None:
                    # 调用路径检测
                    if is_path_clear(grid, row, col, direction):
                        grid[row][col] = None  # 前方畅通，消除
                        print(f"消除成功！剩余: {count_arrows(grid)}")
                    else:
                        mistakes += 1          # 被阻挡，失误+1
                        print(f"碰撞！失误次数: {mistakes}")

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
                cx = MARGIN_X + c * CELL_SIZE + CELL_SIZE // 2
                cy = MARGIN_Y + r * CELL_SIZE + CELL_SIZE // 2
                draw_arrow(screen, cx, cy, direction)

    # 显示信息
    info = font.render(f"剩余箭头: {count_arrows(grid)}   失误: {mistakes}/{MAX_MISTAKES}", True, BLACK)
    screen.blit(info, (20, 20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()