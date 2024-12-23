import pyxel

# 定数の設定
GRID_WIDTH = 5
GRID_HEIGHT = 5
CELL_SIZE = 16
COLORS = [8, 11, 12]  # 赤、緑、青を表すPyxelのパレット番号

class SameGame:
    def __init__(self):
        pyxel.init(GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE)
        pyxel.mouse(True)  # マウスカーソルを表示
        pyxel.title = "SameGame"  # ウィンドウタイトルを設定
        self.grid = [[pyxel.rndi(0, len(COLORS) - 1) for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.create_sounds()  # サウンドを作成
        pyxel.run(self.update, self.draw)

    def create_sounds(self):
        # サウンドの設定
        pyxel.sound(0).set(
            notes="c3e3g3c4",  # 音の高さ
            tones="p",         # 波形 (p: パルス波)
            volumes="7",       # 音量
            effects="n",       # エフェクト (n: エフェクトなし)
            speed=15           # 再生速度
        )

    def update(self):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            x = pyxel.mouse_x // CELL_SIZE
            y = pyxel.mouse_y // CELL_SIZE
            if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                self.handle_click(x, y)

    def handle_click(self, x, y):
        color = self.grid[y][x]
        if color == -1:
            return

        blocks_to_remove = self.find_connected_blocks(x, y, color)
        if len(blocks_to_remove) > 1:
            pyxel.play(0, 0)  # ブロックが消えるときにサウンドを再生
            for bx, by in blocks_to_remove:
                self.grid[by][bx] = -1
            self.score += len(blocks_to_remove)
            self.apply_gravity()

    def find_connected_blocks(self, x, y, color):
        stack = [(x, y)]
        visited = set()
        connected = []

        while stack:
            cx, cy = stack.pop()
            if (cx, cy) in visited:
                continue
            visited.add((cx, cy))
            if self.grid[cy][cx] == color:
                connected.append((cx, cy))
                for nx, ny in [(cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)]:
                    if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                        stack.append((nx, ny))
        return connected

    def apply_gravity(self):
        # 下に詰める
        for x in range(GRID_WIDTH):
            column = [self.grid[y][x] for y in range(GRID_HEIGHT) if self.grid[y][x] != -1]
            for y in range(GRID_HEIGHT):
                self.grid[GRID_HEIGHT - y - 1][x] = column[-(y + 1)] if y < len(column) else -1

        # 左に詰める
        new_grid = []
        for x in range(GRID_WIDTH):
            if any(self.grid[y][x] != -1 for y in range(GRID_HEIGHT)):
                new_grid.append([self.grid[y][x] for y in range(GRID_HEIGHT)])
        
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                if x < len(new_grid):
                    self.grid[y][x] = new_grid[x][y]
                else:
                    self.grid[y][x] = -1

    def draw(self):
        pyxel.cls(0)
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                color = self.grid[y][x]
                if color != -1:
                    pyxel.rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE, COLORS[color])
        pyxel.text(5, 5, f"Score: {self.score}", 7)

# ゲームの開始
SameGame()
