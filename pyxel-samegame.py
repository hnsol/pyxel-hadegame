import pyxel

# 定数の設定
GRID_WIDTH = 5
GRID_HEIGHT = 5
CELL_SIZE = 16
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE + 50
WINDOW_WIDTH = max(GRID_WIDTH * CELL_SIZE, 160)  # ウィンドウ幅を最低160に調整
COLORS = [8, 11, 12]  # 赤、緑、青を表すPyxelのパレット番号

class SameGame:
    def __init__(self):
        pyxel.init(WINDOW_WIDTH, WINDOW_HEIGHT)  # 画面サイズを調整
        pyxel.mouse(True)  # マウスカーソルを表示
        pyxel.title = "SameGame"  # ウィンドウタイトルを設定
        self.state = "opening"  # 初期状態をオープニングに設定
        self.high_score = 0  # ハイスコアを初期化
        self.initial_grid = []  # ゲーム開始時の配置を記録
        self.reset_game()
        self.create_sounds()  # 音を作成
        pyxel.run(self.update, self.draw)

    def create_sounds(self):
        # サウンドの設定
        pyxel.sound(0).set(
            notes="c3e3g3c4",  # 音階
            tones="p",         # 波形
            volumes="7",       # 音量
            effects="n",       # エフェクト
            speed=15           # 再生速度
        )

    def reset_game(self):
        self.grid = [[pyxel.rndi(0, len(COLORS) - 1) for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.initial_grid = [row[:] for row in self.grid]  # 初期状態を記録
        self.score = 0

    def restore_initial_state(self):
        self.grid = [row[:] for row in self.initial_grid]  # 初期状態を復元
        self.score = 0

    def update(self):
        if self.state == "opening":
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.reset_game()  # ゲーム開始時に状態をリセット
                self.state = "game"

        elif self.state == "game":
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                x, y = pyxel.mouse_x // CELL_SIZE, pyxel.mouse_y // CELL_SIZE
                if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                    self.handle_click(x, y)
                elif 10 <= pyxel.mouse_x <= 70 and WINDOW_HEIGHT - 40 <= pyxel.mouse_y <= WINDOW_HEIGHT - 20:
                    self.state = "opening"
                elif 80 <= pyxel.mouse_x <= 150 and WINDOW_HEIGHT - 40 <= pyxel.mouse_y <= WINDOW_HEIGHT - 20:
                    self.restore_initial_state()  # 初期状態に戻す

            if not self.has_valid_moves():
                self.state = "game_over"

        elif self.state == "game_over":
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                if self.score > self.high_score:
                    self.high_score = self.score
                self.state = "opening"

        elif self.state == "high_score":
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.state = "opening"

    def handle_click(self, x, y):
        color = self.grid[y][x]
        if color == -1:
            return

        blocks_to_remove = self.find_connected_blocks(x, y, color)
        if len(blocks_to_remove) > 1:
            pyxel.play(0, 0)  # 音を再生
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
        for x in range(GRID_WIDTH):
            column = [self.grid[y][x] for y in range(GRID_HEIGHT) if self.grid[y][x] != -1]
            for y in range(GRID_HEIGHT):
                self.grid[GRID_HEIGHT - y - 1][x] = column[-(y + 1)] if y < len(column) else -1

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

    def has_valid_moves(self):
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                color = self.grid[y][x]
                if color != -1 and len(self.find_connected_blocks(x, y, color)) > 1:
                    return True
        return False

    def draw(self):
        pyxel.cls(0)

        if self.state == "opening":
            pyxel.text((WINDOW_WIDTH - 120) // 2, 50, "WELCOME TO SAMEGAME", pyxel.COLOR_WHITE)  # 中央揃え
            pyxel.text((WINDOW_WIDTH - 100) // 2, 80, "CLICK TO START", pyxel.COLOR_WHITE)

        elif self.state == "game":
            for y in range(GRID_HEIGHT):
                for x in range(GRID_WIDTH):
                    color = self.grid[y][x]
                    if color != -1:
                        pyxel.rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE, COLORS[color])

            pyxel.rect(10, WINDOW_HEIGHT - 40, 60, 20, pyxel.COLOR_GRAY)
            pyxel.text(20, WINDOW_HEIGHT - 35, "QUIT", pyxel.COLOR_WHITE)

            pyxel.rect(80, WINDOW_HEIGHT - 40, 70, 20, pyxel.COLOR_GRAY)
            pyxel.text(90, WINDOW_HEIGHT - 35, "RESET", pyxel.COLOR_WHITE)

            pyxel.text(10, GRID_HEIGHT * CELL_SIZE - 10, f"SCORE: {self.score}", pyxel.COLOR_WHITE)

        elif self.state == "game_over":
            pyxel.text(20, 50, "GAME OVER", pyxel.COLOR_RED)
            pyxel.text(20, 80, f"FINAL SCORE: {self.score}", pyxel.COLOR_WHITE)
            pyxel.text(20, 100, "CLICK TO CONTINUE", pyxel.COLOR_WHITE)

        elif self.state == "high_score":
            pyxel.text(20, 50, "HIGH SCORE", pyxel.COLOR_YELLOW)
            pyxel.text(20, 80, f"HIGH SCORE: {self.high_score}", pyxel.COLOR_WHITE)
            pyxel.text(20, 100, "CLICK TO RETURN", pyxel.COLOR_WHITE)

# ゲームの開始
SameGame()
