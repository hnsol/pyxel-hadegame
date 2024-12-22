import pyxel
import copy

# 定数の設定
WINDOW_WIDTH = 240
WINDOW_HEIGHT = 240

BUTTON_WIDTH = 80
BUTTON_HEIGHT = 20
BUTTON_SPACING = 10
BUTTON_AREA_HEIGHT = 100  # ボタンエリアの高さ（縦にボタンを並べるため拡大）
STATUS_AREA_HEIGHT = 30  # 表示エリアの高さ

COLORS = [8, 11, 12, 13, 14, 15, 6, 7]  # 使用可能なPyxelの色番号
DEFAULT_TOP_SCORES = [5120, 2560, 1280, 640, 320, 160, 80, 40, 20, 10]  # デフォルトのトップ10スコア

class Button:
    def __init__(self, x, y, width, height, label):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.label = label

    def is_hovered(self, mx, my):
        return self.x <= mx <= self.x + self.width and self.y <= my <= self.y + self.height

    def draw(self, is_hovered):
        color = pyxel.COLOR_LIGHT_BLUE if is_hovered else pyxel.COLOR_GRAY
        pyxel.rect(self.x, self.y, self.width, self.height, color)
        text_x = self.x + (self.width // 2) - (len(self.label) * 2)
        text_y = self.y + (self.height // 2) - 4
        pyxel.text(text_x, text_y, self.label.capitalize(), pyxel.COLOR_WHITE)

class SameGame:
    def __init__(self):
        self.difficulty_levels = {
            "Easy": {"grid_rows": 5, "grid_cols": 5, "colors": 3, "time_limit": None, "score_multiplier": 1.0},
            "Normal": {"grid_rows": 7, "grid_cols": 12, "colors": 4, "time_limit": None, "score_multiplier": 1.2},
            "Hard": {"grid_rows": 9, "grid_cols": 15, "colors": 5, "time_limit": 60, "score_multiplier": 1.5},
            "Very Hard": {"grid_rows": 8, "grid_cols": 15, "colors": 6, "time_limit": 45, "score_multiplier": 2.0},
            "Expert": {"grid_rows": 10, "grid_cols": 20, "colors": 8, "time_limit": 30, "score_multiplier": 3.0},
        }
        self.current_difficulty = "Easy"
        self.grid_rows = self.difficulty_levels[self.current_difficulty]["grid_rows"]
        self.grid_cols = self.difficulty_levels[self.current_difficulty]["grid_cols"]
        self.num_colors = self.difficulty_levels[self.current_difficulty]["colors"]
        self.time_limit = self.difficulty_levels[self.current_difficulty]["time_limit"]
        self.score_multiplier = self.difficulty_levels[self.current_difficulty]["score_multiplier"]

        pyxel.init(WINDOW_WIDTH, WINDOW_HEIGHT)
        pyxel.mouse(True)
        pyxel.title = "SameGame"
        self.state = "opening"
        self.high_scores = DEFAULT_TOP_SCORES[:]
        self.current_score_rank = None
        self.start_time = None
        self.initial_grid = []
        self.reset_game(initial=True)
        self.create_sounds()

        # 難易度選択用ボタンの作成
        self.difficulty_buttons = []
        self.create_difficulty_buttons()

        pyxel.run(self.update, self.draw)

    def create_difficulty_buttons(self):
        # 各難易度のラベルと説明
        difficulties = [
            {"label": "Easy", "description": "Small grid, few colors"},
            {"label": "Normal", "description": "Larger grid, more colors"},
            {"label": "Hard", "description": "Timed play"},
            {"label": "Very Hard", "description": "Shorter time"},
            {"label": "Expert", "description": "Maximum challenge"},
        ]
        # ボタンを縦に並べるための開始位置を計算（中央に配置）
        start_x = (WINDOW_WIDTH - BUTTON_WIDTH) // 2 - 60
        start_y = 40
        for i, diff in enumerate(difficulties):
            x = start_x
            y = start_y + i * (BUTTON_HEIGHT + BUTTON_SPACING)
            self.difficulty_buttons.append(Button(x, y, BUTTON_WIDTH, BUTTON_HEIGHT, diff["label"]))
        self.difficulties = difficulties  # 説明のために保持

    def create_sounds(self):
        self.sounds = {}
        self.base_notes = ["c2", "d2", "e2", "f2", "g2", "a2", "b2", "c3"]
        for i in range(len(COLORS)):
            pyxel.sounds[i].set(
                notes=self.base_notes[i % len(self.base_notes)],
                tones="p",
                volumes="5",
                effects="n",
                speed=15,
            )

    def reset_game(self, initial=False):
        if initial or not hasattr(self, 'initial_grid'):
            self.grid = [
                [pyxel.rndi(0, self.num_colors - 1) for _ in range(self.grid_cols)]
                for _ in range(self.grid_rows)
            ]
            self.initial_grid = copy.deepcopy(self.grid)
        else:
            self.grid = copy.deepcopy(self.initial_grid)
        self.start_time = pyxel.frame_count if self.time_limit else None
        self.score = 0

    def update(self):
        mx, my = pyxel.mouse_x, pyxel.mouse_y

        if self.state == "opening":
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.state = "difficulty_selection"

        elif self.state == "difficulty_selection":
            for button in self.difficulty_buttons:
                if button.is_hovered(mx, my):
                    if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                        self.current_difficulty = button.label
                        self.apply_difficulty_settings()
                        self.state = "game"
                        break

        elif self.state == "game":
            if self.time_limit and pyxel.frame_count - self.start_time > self.time_limit * 30:
                self.state = "time_up"

            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                # ボタンエリア内のクリック判定
                if 0 <= my <= BUTTON_AREA_HEIGHT:
                    # Retryボタン
                    if BUTTON_SPACING <= mx <= BUTTON_SPACING + BUTTON_WIDTH:
                        self.reset_game()
                        return
                    # Quitボタン
                    elif 2 * BUTTON_SPACING + BUTTON_WIDTH <= mx <= 2 * BUTTON_SPACING + BUTTON_WIDTH * 2:
                        self.state = "gave_up"
                        return
                else:
                    self.handle_click(mx, my)

            if not self.has_valid_moves():
                self.state = "no_moves"

            # すべてのブロックが消去されたかをチェック
            if self.is_grid_empty():
                self.state = "game_cleared"

        elif self.state in ["time_up", "no_moves", "gave_up", "game_cleared"]:
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.update_high_scores()
                self.state = "score_display"

        elif self.state == "score_display":
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.state = "high_score_display"

        elif self.state == "high_score_display":
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.state = "opening"

    def apply_difficulty_settings(self):
        settings = self.difficulty_levels[self.current_difficulty]
        self.grid_rows = settings["grid_rows"]
        self.grid_cols = settings["grid_cols"]
        self.num_colors = settings["colors"]
        self.time_limit = settings["time_limit"]
        self.score_multiplier = settings["score_multiplier"]
        self.reset_game(initial=True)  # 新しい難易度では初期盤面を生成

    def handle_click(self, mx, my):
        # 盤面エリアのY座標を調整
        game_area_y = BUTTON_AREA_HEIGHT
        game_area_height = WINDOW_HEIGHT - BUTTON_AREA_HEIGHT - STATUS_AREA_HEIGHT
        cell_size = min(WINDOW_WIDTH // self.grid_cols, game_area_height // self.grid_rows)
        grid_x_start = (WINDOW_WIDTH - (cell_size * self.grid_cols)) // 2
        grid_y_start = game_area_y + (game_area_height - (cell_size * self.grid_rows)) // 2

        x = (mx - grid_x_start) // cell_size
        y = (my - grid_y_start) // cell_size
        if 0 <= x < self.grid_cols and 0 <= y < self.grid_rows:
            color = self.grid[y][x]
            if color == -1:
                return

            blocks_to_remove = self.find_connected_blocks(x, y, color)
            if len(blocks_to_remove) > 1:
                for bx, by in blocks_to_remove:
                    self.grid[by][bx] = -1
                pyxel.play(0, color)
                self.score += int(len(blocks_to_remove) * (len(blocks_to_remove) ** 2) * self.score_multiplier)
                self.apply_gravity()
                self.shift_columns_left()

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
                    if 0 <= nx < self.grid_cols and 0 <= ny < self.grid_rows:
                        stack.append((nx, ny))
        return connected

    def apply_gravity(self):
        for x in range(self.grid_cols):
            column = [self.grid[y][x] for y in range(self.grid_rows) if self.grid[y][x] != -1]
            for y in range(self.grid_rows):
                self.grid[self.grid_rows - y - 1][x] = column[-(y + 1)] if y < len(column) else -1

    def shift_columns_left(self):
        # 新しいグリッドを作成
        new_grid = []
        for x in range(self.grid_cols):
            # 各列がすべて -1 かどうかをチェック
            if any(self.grid[y][x] != -1 for y in range(self.grid_rows)):
                # 空でない列を追加
                new_grid.append([self.grid[y][x] for y in range(self.grid_rows)])
        # 空の列を追加してグリッドサイズを維持
        while len(new_grid) < self.grid_cols:
            new_grid.append([-1] * self.grid_rows)
        # グリッドを更新
        for x in range(self.grid_cols):
            for y in range(self.grid_rows):
                self.grid[y][x] = new_grid[x][y]

    def has_valid_moves(self):
        for y in range(self.grid_rows):
            for x in range(self.grid_cols):
                color = self.grid[y][x]
                if color != -1 and len(self.find_connected_blocks(x, y, color)) > 1:
                    return True
        return False

    def is_grid_empty(self):
        for row in self.grid:
            for cell in row:
                if cell != -1:
                    return False
        return True

    def update_high_scores(self):
        if self.score not in self.high_scores:
            self.high_scores.append(self.score)
        self.high_scores.sort(reverse=True)
        self.high_scores = self.high_scores[:10]
        try:
            self.current_score_rank = self.high_scores.index(self.score)
        except ValueError:
            self.current_score_rank = None

    def draw(self):
        pyxel.cls(0)

        if self.state == "opening":
            pyxel.text(WINDOW_WIDTH // 2 - 60, WINDOW_HEIGHT // 2 - 10, "Welcome to SameGame", pyxel.COLOR_WHITE)
            pyxel.text(WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT // 2 + 10, "Click to Start", pyxel.COLOR_WHITE)

        elif self.state == "difficulty_selection":
            pyxel.text(WINDOW_WIDTH // 2 - 60, 10, "Select Difficulty", pyxel.COLOR_YELLOW)
            # 各ボタンと説明を描画
            for i, button in enumerate(self.difficulty_buttons):
                is_hovered = button.is_hovered(pyxel.mouse_x, pyxel.mouse_y)
                button.draw(is_hovered)
                # 説明文をボタンの右側に表示
                description = self.difficulties[i]["description"]
                pyxel.text(button.x + button.width + 10, button.y + 5, description, pyxel.COLOR_WHITE)

        elif self.state == "game":
            self.draw_buttons()
            self.draw_grid()
            self.draw_status()

        elif self.state == "time_up":
            pyxel.text(WINDOW_WIDTH // 2 - 30, WINDOW_HEIGHT // 2 - 10, "Time's Up!", pyxel.COLOR_RED)
            pyxel.text(WINDOW_WIDTH // 2 - 30, WINDOW_HEIGHT // 2 + 10, f"Score: {int(self.score)}", pyxel.COLOR_WHITE)
            pyxel.text(WINDOW_WIDTH // 2 - 40, WINDOW_HEIGHT // 2 + 30, "Click to Continue", pyxel.COLOR_WHITE)

        elif self.state == "no_moves":
            pyxel.text(WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT // 2 - 10, "No Moves Available!", pyxel.COLOR_RED)
            pyxel.text(WINDOW_WIDTH // 2 - 30, WINDOW_HEIGHT // 2 + 10, f"Score: {int(self.score)}", pyxel.COLOR_WHITE)
            pyxel.text(WINDOW_WIDTH // 2 - 40, WINDOW_HEIGHT // 2 + 30, "Click to Continue", pyxel.COLOR_WHITE)

        elif self.state == "gave_up":
            pyxel.text(WINDOW_WIDTH // 2 - 60, WINDOW_HEIGHT // 2 - 10, "You gave up this game.", pyxel.COLOR_RED)
            pyxel.text(WINDOW_WIDTH // 2 - 30, WINDOW_HEIGHT // 2 + 10, f"Score: {int(self.score)}", pyxel.COLOR_WHITE)
            pyxel.text(WINDOW_WIDTH // 2 - 40, WINDOW_HEIGHT // 2 + 30, "Click to Continue", pyxel.COLOR_WHITE)

        elif self.state == "game_cleared":
            pyxel.text(WINDOW_WIDTH // 2 - 70, WINDOW_HEIGHT // 2 - 10, "Congratulations!", pyxel.COLOR_GREEN)
            pyxel.text(WINDOW_WIDTH // 2 - 80, WINDOW_HEIGHT // 2 + 10, "You cleared the game!", pyxel.COLOR_WHITE)
            pyxel.text(WINDOW_WIDTH // 2 - 40, WINDOW_HEIGHT // 2 + 30, "Click to Continue", pyxel.COLOR_WHITE)

        elif self.state == "score_display":
            pyxel.text(WINDOW_WIDTH // 2 - 30, WINDOW_HEIGHT // 2 - 20, "Your Score", pyxel.COLOR_YELLOW)
            pyxel.text(WINDOW_WIDTH // 2 - 20, WINDOW_HEIGHT // 2, f"{int(self.score)}", pyxel.COLOR_YELLOW)
            pyxel.text(WINDOW_WIDTH // 2 - 40, WINDOW_HEIGHT // 2 + 20, "Click to Continue", pyxel.COLOR_WHITE)

        elif self.state == "high_score_display":
            pyxel.text(WINDOW_WIDTH // 2 - 60, 10, "Top 10 High Scores", pyxel.COLOR_YELLOW)
            for i, score in enumerate(self.high_scores):
                color = pyxel.COLOR_YELLOW if i == self.current_score_rank else pyxel.COLOR_WHITE
                pyxel.text(WINDOW_WIDTH // 2 - 30, 30 + i * 10, f"{i + 1}: {score}", color)
            pyxel.text(WINDOW_WIDTH // 2 - 40, WINDOW_HEIGHT - 20, "Click to Return", pyxel.COLOR_WHITE)

    def draw_buttons(self):
        # Retryボタン
        retry_x = BUTTON_SPACING
        retry_y = (BUTTON_AREA_HEIGHT - BUTTON_HEIGHT) // 2
        pyxel.rect(retry_x, retry_y, BUTTON_WIDTH, BUTTON_HEIGHT, pyxel.COLOR_GRAY)
        pyxel.text(retry_x + 10, retry_y + 5, "Retry", pyxel.COLOR_WHITE)

        # Quitボタン
        quit_x = BUTTON_SPACING + BUTTON_WIDTH + BUTTON_SPACING
        quit_y = (BUTTON_AREA_HEIGHT - BUTTON_HEIGHT) // 2
        pyxel.rect(quit_x, quit_y, BUTTON_WIDTH, BUTTON_HEIGHT, pyxel.COLOR_GRAY)
        pyxel.text(quit_x + 10, quit_y + 5, "Quit", pyxel.COLOR_WHITE)

    def draw_grid(self):
        game_area_y = BUTTON_AREA_HEIGHT
        game_area_height = WINDOW_HEIGHT - BUTTON_AREA_HEIGHT - STATUS_AREA_HEIGHT
        cell_size = min(WINDOW_WIDTH // self.grid_cols, game_area_height // self.grid_rows)
        grid_x_start = (WINDOW_WIDTH - (cell_size * self.grid_cols)) // 2
        grid_y_start = game_area_y + (game_area_height - (cell_size * self.grid_rows)) // 2

        for y in range(self.grid_rows):
            for x in range(self.grid_cols):
                color = self.grid[y][x]
                if color != -1:
                    pyxel.rect(
                        grid_x_start + x * cell_size,
                        grid_y_start + y * cell_size,
                        cell_size,
                        cell_size,
                        COLORS[color]
                    )

    def draw_status(self):
        # 難易度表示
        difficulty_text = f"Difficulty: {self.current_difficulty}"
        pyxel.text(10, WINDOW_HEIGHT - STATUS_AREA_HEIGHT + 5, difficulty_text, pyxel.COLOR_WHITE)

        # スコア表示（難易度表示の右側に配置）
        score_text = f"Score: {int(self.score)}"
        score_x = 10 + len(difficulty_text) * 8  # フォントサイズに合わせて調整
        pyxel.text(score_x, WINDOW_HEIGHT - STATUS_AREA_HEIGHT + 5, score_text, pyxel.COLOR_WHITE)

        # タイマー表示
        if self.time_limit:
            remaining_time = max(0, self.time_limit - (pyxel.frame_count - self.start_time) // 30)
            time_text = f"Time: {remaining_time}s"
        else:
            time_text = "Time: --"  # 時間無制限時は "--" を表示
        # 画面右側に表示
        time_text_width = len(time_text) * 4  # フォント幅を推定
        pyxel.text(WINDOW_WIDTH - time_text_width - 10, WINDOW_HEIGHT - STATUS_AREA_HEIGHT + 5, time_text, pyxel.COLOR_WHITE)

# ゲームの開始
SameGame()
