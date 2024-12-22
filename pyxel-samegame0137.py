import pyxel

# 定数の設定
GRID_WIDTH = 5
GRID_HEIGHT = 5
CELL_SIZE = 40  # 各セルのサイズ
WINDOW_WIDTH = 240
WINDOW_HEIGHT = 240
BUTTON_WIDTH = 40
BUTTON_HEIGHT = 15
BUTTON_SPACING = 5
BUTTON_Y = 5
COLORS = [8, 11, 12]  # 赤、緑、青を表すPyxelのパレット番号
DEFAULT_TOP_SCORES = [100, 90, 80, 70, 60, 50, 40, 30, 20, 10]  # デフォルトのトップ10スコア
MAX_COLORS = 12  # 最大の色数

class SameGame:
    def __init__(self):
        # 基本設定
        self.low_threshold = 3  # 少ないコマの閾値
        self.mid_threshold = 6  # 中くらいのコマの閾値
        self.base_speed = 15  # 音の長さの基本値
        self.high_octave_shift = 12  # 高いオクターブの音程シフト
        self.mid_octave_shift = 0  # 中くらいオクターブの音程シフト
        self.low_octave_shift = -12  # 低いオクターブの音程シフト

        pyxel.init(WINDOW_WIDTH, WINDOW_HEIGHT)
        pyxel.mouse(True)
        pyxel.title = "SameGame"
        self.state = "opening"
        self.high_scores = DEFAULT_TOP_SCORES[:]  # デフォルトのトップ10スコア
        self.current_score_rank = None  # 今回のスコアの順位
        self.initial_grid = []
        self.reset_game()
        self.create_sounds()
        self.gave_up = False  # ギブアップフラグ
        pyxel.run(self.update, self.draw)

    def create_sounds(self):
        # 各色ごとにベース音風の低音を設定
        self.sounds = {}
        self.base_notes = ["c2", "d2", "e2", "f2", "g2", "a2", "b2", "c3", "d3", "e3", "f3", "g3"]
        for i in range(MAX_COLORS):
            pyxel.sounds[i].set(
                notes=self.base_notes[i % len(self.base_notes)],  # 音階を割り当て
                tones="p",  # パーカッシブ音
                volumes="5",  # 音量
                effects="n",  # ノーマル
                speed=self.base_speed,  # 音の長さの基本値
            )
            self.sounds[i] = self.base_notes[i % len(self.base_notes)]  # 音階を記録

    def reset_game(self):
        self.grid = [[pyxel.rndi(0, len(COLORS) - 1) for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.initial_grid = [row[:] for row in self.grid]
        self.score = 0
        self.gave_up = False

    def restore_initial_state(self):
        self.grid = [row[:] for row in self.initial_grid]
        self.score = 0

    def update(self):
        if self.state == "opening":
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.reset_game()
                self.state = "game"

        elif self.state == "game":
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                mx, my = pyxel.mouse_x, pyxel.mouse_y

                # ボタン判定
                if BUTTON_SPACING <= mx <= BUTTON_SPACING + BUTTON_WIDTH:
                    if BUTTON_Y <= my <= BUTTON_Y + BUTTON_HEIGHT:
                        self.restore_initial_state()  # Retry
                        return
                elif BUTTON_SPACING * 2 + BUTTON_WIDTH <= mx <= BUTTON_SPACING * 2 + BUTTON_WIDTH * 2:
                    if BUTTON_Y <= my <= BUTTON_Y + BUTTON_HEIGHT:
                        self.gave_up = True  # ギブアップフラグを立てる
                        self.state = "no_moves"  # ギブアップ後にno_moves画面へ遷移
                        return

                # コマ判定
                if BUTTON_Y + BUTTON_HEIGHT < my < BUTTON_Y + BUTTON_HEIGHT + GRID_HEIGHT * CELL_SIZE:
                    x = mx // CELL_SIZE
                    y = (my - BUTTON_Y - BUTTON_HEIGHT) // CELL_SIZE
                    if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                        self.handle_click(x, y)

            # **順序変更**: すべてのコマが消えた場合のチェック
            if self.all_cleared():
                self.score += 50  # ボーナススコア
                self.state = "stage_cleared"
            elif not self.has_valid_moves():
                self.state = "no_moves"

        elif self.state == "no_moves":
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.update_high_scores()
                self.state = "score_display"

        elif self.state == "stage_cleared":
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.update_high_scores()
                self.state = "score_display"

        elif self.state == "score_display":
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.state = "high_score_display"

        elif self.state == "high_score_display":
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.state = "opening"

    def handle_click(self, x, y):
        color = self.grid[y][x]
        if color == -1:  # 空白セルは無視
            return

        # 消すコマを探索
        blocks_to_remove = self.find_connected_blocks(x, y, color)
        if len(blocks_to_remove) > 1:  # 隣接するブロックが2個以上なら消去
            note_shift, sound_length = self.get_sound_settings(len(blocks_to_remove))
            base_note = self.sounds[color]  # ベース音の取得
            shifted_note = self.shift_note(base_note, note_shift)  # オクターブシフト適用
            pyxel.sounds[color].set(
                notes=shifted_note,  # シフト後の音階を設定
                tones="p",
                volumes="5",
                effects="n",
                speed=sound_length,
            )
            pyxel.play(0, color)  # コマの色に応じた音を再生
            for bx, by in blocks_to_remove:
                self.grid[by][bx] = -1  # 消去
            self.score += len(blocks_to_remove)
            self.apply_gravity()

            # すべてのコマが消去されたかを判定
            if self.all_cleared():
                self.score += 50  # ボーナススコア
                self.state = "stage_cleared"

    def shift_note(self, base_note, shift):
        """
        ベース音(base_note)をオクターブシフト(shift)させる。
        """
        note_mapping = {"c": 0, "d": 2, "e": 4, "f": 5, "g": 7, "a": 9, "b": 11}
        note, octave = base_note[:-1], int(base_note[-1])  # ノート部分とオクターブを分割
        note_index = note_mapping[note] + shift  # ノート番号にシフトを適用

        new_octave = octave + (note_index // 12)  # オクターブの調整
        new_note = list(note_mapping.keys())[note_index % 12]  # 新しいノート
        return f"{new_note}{new_octave}"

    def get_sound_settings(self, block_count):
        """
        コマの数に応じたオクターブと音の長さを取得
        """
        if block_count <= self.low_threshold:
            note_shift = self.low_octave_shift
            sound_length = self.base_speed + 5  # 長め
        elif block_count <= self.mid_threshold:
            note_shift = self.mid_octave_shift
            sound_length = self.base_speed  # 通常
        else:
            note_shift = self.high_octave_shift
            sound_length = self.base_speed - 5  # 短め
        return note_shift, sound_length

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

    def all_cleared(self):
        """
        すべてのコマが消去されたかを判定
        """
        return all(self.grid[y][x] == -1 for y in range(GRID_HEIGHT) for x in range(GRID_WIDTH))

    def update_high_scores(self):
        """
        スコアをトップ10に追加してソートし、順位を記録
        """
        if self.score not in self.high_scores:
            self.high_scores.append(self.score)
        self.high_scores.sort(reverse=True)  # 高い順にソート
        self.high_scores = self.high_scores[:10]  # トップ10に絞る

        # 現在のスコアがランクインしている場合に順位を記録
        try:
            self.current_score_rank = self.high_scores.index(self.score)
        except ValueError:
            self.current_score_rank = None

    def draw(self):
        pyxel.cls(0)

        if self.state == "opening":
            pyxel.text(80, 50, "Welcome to SameGame", pyxel.COLOR_WHITE)
            pyxel.text(10, 70, "How to Play:", pyxel.COLOR_YELLOW)
            pyxel.text(10, 90, "1. Click blocks of the same color", pyxel.COLOR_WHITE)
            pyxel.text(10, 100, "   that are connected to remove them.", pyxel.COLOR_WHITE)
            pyxel.text(10, 110, "2. The more blocks you remove at once,", pyxel.COLOR_WHITE)
            pyxel.text(10, 120, "   the higher your score.", pyxel.COLOR_WHITE)
            pyxel.text(10, 130, "3. Clear all blocks for a bonus!", pyxel.COLOR_WHITE)
            pyxel.text(10, 140, "4. If no moves are left, the game ends.", pyxel.COLOR_WHITE)
            pyxel.text(80, 170, "Click to Start", pyxel.COLOR_WHITE)

        elif self.state == "game" or self.state == "no_moves":
            # ボタン描画
            pyxel.rect(BUTTON_SPACING, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, pyxel.COLOR_GRAY)
            pyxel.text(BUTTON_SPACING + 5, BUTTON_Y + 3, "Retry", pyxel.COLOR_WHITE)

            pyxel.rect(BUTTON_SPACING * 2 + BUTTON_WIDTH, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, pyxel.COLOR_GRAY)
            pyxel.text(BUTTON_SPACING * 2 + BUTTON_WIDTH + 5, BUTTON_Y + 3, "Quit", pyxel.COLOR_WHITE)

            # コマ描画
            for y in range(GRID_HEIGHT):
                for x in range(GRID_WIDTH):
                    color = self.grid[y][x]
                    if color != -1:
                        pyxel.rect(x * CELL_SIZE, y * CELL_SIZE + BUTTON_Y + BUTTON_HEIGHT, CELL_SIZE, CELL_SIZE, COLORS[color])

            # スコア表示
            pyxel.text(10, WINDOW_HEIGHT - 15, f"Score: {self.score}", pyxel.COLOR_WHITE)

            # "No moves" 表示
            if self.state == "no_moves":
                pyxel.rect(30, 100, 180, 60, pyxel.COLOR_GRAY)  # 背景を塗る
                if self.gave_up:
                    pyxel.text(40, 110, "You gave up this game.", pyxel.COLOR_RED)
                else:
                    pyxel.text(40, 110, "No moves available!", pyxel.COLOR_RED)
                pyxel.text(60, 140, "Click to Continue", pyxel.COLOR_WHITE)

        elif self.state == "stage_cleared":
            pyxel.text(40, 100, "Congratulations!", pyxel.COLOR_YELLOW)
            pyxel.text(40, 120, "Stage Cleared!", pyxel.COLOR_WHITE)
            pyxel.text(50, 140, f"Bonus: +50 Points", pyxel.COLOR_WHITE)
            pyxel.text(60, 160, "Click to Continue", pyxel.COLOR_WHITE)

        elif self.state == "score_display":
            pyxel.text(80, 100, f"Your Score: {self.score}", pyxel.COLOR_YELLOW)
            pyxel.text(90, 120, "Click to Continue", pyxel.COLOR_WHITE)

        elif self.state == "high_score_display":
            pyxel.text(80, 90, "Top 10 High Scores", pyxel.COLOR_YELLOW)
            for i, score in enumerate(self.high_scores):
                if i == self.current_score_rank:
                    pyxel.text(80, 110 + i * 10, f"{i+1}. {score}", pyxel.COLOR_YELLOW)
                else:
                    pyxel.text(80, 110 + i * 10, f"{i+1}. {score}", pyxel.COLOR_WHITE)
            pyxel.text(90, 220, "Click to Return", pyxel.COLOR_WHITE)

# ゲームの開始
SameGame()
