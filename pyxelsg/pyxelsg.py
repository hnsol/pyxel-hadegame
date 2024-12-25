# title: Pyxel SameGame
# author: hann-solo
# desc: A simple SameGame puzzle game built with Pyxel. Clear the board by removing groups of blocks with the same color!
# site: https://github.com/hnsol/pyxel-samegame
# license: MIT
# version: 0.1

import pyxel
import os
import json
import copy
from enum import Enum

# 定数の設定
WINDOW_WIDTH = 240
WINDOW_HEIGHT = 240

#BUTTON_WIDTH = 80
#BUTTON_HEIGHT = 20
BUTTON_WIDTH = 75
BUTTON_HEIGHT = 15
BUTTON_SPACING = 10
BUTTON_AREA_HEIGHT = 100  # ボタンエリアの高さ（縦にボタンを並べるため拡大）
STATUS_AREA_HEIGHT = 30   # 表示エリアの高さ

COLORS = [8, 11, 12, 13, 14, 15, 6, 7]  # 使用可能なPyxelの色番号
DEFAULT_TOP_SCORES = [10000, 5000, 2500, 1000, 500, 250, 100, 50, 25, 10]  # デフォルトのトップ10スコア

class GameState(Enum):
    OPENING = "opening"
    DIFFICULTY_SELECTION = "difficulty_selection"
    GAME_START = "game_start"
    GAME_MID = "game_mid"
    GAME_END = "game_end"
    TIME_UP = "time_up"
    NO_MOVES = "no_moves"
    GAME_CLEARED = "game_cleared"
    SCORE_DISPLAY = "score_display"
    HIGH_SCORE_DISPLAY = "high_score_display"

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
        # BGM関連の初期化
        self.bgm_files = {
            GameState.OPENING: "assets/opening_music.json",            # オープニング画面のBGM
            GameState.DIFFICULTY_SELECTION: "assets/selection_music.json", # 難易度選択画面のBGM
            GameState.GAME_START: "assets/gameplay_start_music.json", # ゲーム序盤のBGM
            GameState.GAME_MID: "assets/gameplay_mid_music.json",     # ゲーム中盤のBGM
            GameState.GAME_END: "assets/gameplay_end_music.json",     # ゲーム終盤のBGM
            GameState.TIME_UP: "assets/time_up_music.json",           # タイムアップ時のBGM
            GameState.NO_MOVES: "assets/no_moves_music.json",         # 動ける手がなくなった時のBGM
            GameState.GAME_CLEARED: "assets/cleared_music.json",      # ゲームクリア時のBGM
        }
        self.bgm_data = {}
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.current_bgm = None

        self.load_bgms()

        self.difficulty_levels = {
            "Easy": {"grid_rows": 5, "grid_cols": 5, "colors": 3, "time_limit": None, "score_multiplier": 1.0},
            "Normal": {"grid_rows": 6, "grid_cols": 10, "colors": 4, "time_limit": None, "score_multiplier": 1.2},
            "Hard": {"grid_rows": 8, "grid_cols": 12, "colors": 5, "time_limit": 90, "score_multiplier": 1.5},
            "Very Hard": {"grid_rows": 9, "grid_cols": 15, "colors": 6, "time_limit": 60, "score_multiplier": 2.0},
            "Expert": {"grid_rows": 10, "grid_cols": 18, "colors": 8, "time_limit": 45, "score_multiplier": 2.7},
        }
        self.current_difficulty = "Easy"
        self.grid_rows = self.difficulty_levels[self.current_difficulty]["grid_rows"]
        self.grid_cols = self.difficulty_levels[self.current_difficulty]["grid_cols"]
        self.num_colors = self.difficulty_levels[self.current_difficulty]["colors"]
        self.time_limit = self.difficulty_levels[self.current_difficulty]["time_limit"]
        self.score_multiplier = self.difficulty_levels[self.current_difficulty]["score_multiplier"]
        self.bonus_added = False  # ボーナススコア加算済みかを判定するフラグ

        pyxel.init(WINDOW_WIDTH, WINDOW_HEIGHT)
        pyxel.mouse(True)
        pyxel.title = "SameGame"
        self.state = GameState.OPENING
        self.high_scores = DEFAULT_TOP_SCORES[:]
        self.current_score_rank = None
        self.start_time = None
        self.initial_grid = []
        self.bgm_tracks = self.setup_bgm()
        self.current_bgm = None

        self.reset_game(use_saved_initial_state=False)
        self.create_sounds()

        self.difficulty_buttons = []
        self.create_difficulty_buttons()

        self.current_bgm = None  # 現在再生中のBGMを記録
        pyxel.run(self.update, self.draw)

    def load_bgms(self):
        for state, file_path in self.bgm_files.items():
            # 絶対パスを計算
            absolute_path = os.path.join(self.base_path, file_path)
            try:
                if not os.path.exists(absolute_path):
                    raise FileNotFoundError(f"File not found: {absolute_path}")
                with open(absolute_path, "r") as fin:
                    self.bgm_data[state] = json.loads(fin.read())
            except FileNotFoundError:
                print(f"BGM file not found: {absolute_path}")
            except json.JSONDecodeError:
                print(f"BGM file is not valid JSON: {absolute_path}")
            except Exception as e:
                print(f"Error loading BGM file for state {state.name}: {e}")

    def setup_bgm(self):
        """Initialize BGM mappings for states and game logic."""
        return {
            GameState.OPENING: 0,              # Intro BGM (track 0)
            GameState.DIFFICULTY_SELECTION: 1, # Difficulty selection BGM (track 1)
            GameState.GAME_START: 2,           # Main game BGM (track 2)
            GameState.TIME_UP: 3,              # Game over BGM (track 3)
            GameState.NO_MOVES: 4,             # No moves BGM (track 4)
            GameState.GAME_CLEARED: 5,         # Game cleared BGM (track 5)
        }

    def play_bgm(self, state):
        """指定された状態に対応するBGMを再生"""
        if self.current_bgm == state:
            return  # 既に再生中の場合は何もしない
    
        print(f"Switching to BGM for state in play_bgm: {state.name}")  # デバッグ用

        # 現在のBGMを停止
        self.stop_bgm()

        self.current_bgm = state
    
        # 指定されたステートのBGMが存在する場合、再生
        if state in self.bgm_data:
            bgm_channels = [1, 2, 3]  # チャンネル1〜3をBGM用に使用
            for ch, sound in zip(bgm_channels, self.bgm_data[state]):
                pyxel.sounds[ch].set(*sound)
                pyxel.play(ch, ch, loop=True)  # チャンネルごとにループ再生
#                if not pyxel.play_pos(ch):  # チャンネルが再生されていない場合のみ再生
#                    pyxel.play(ch, ch, loop=True)
        else:
            print(f"BGM data not found for state: {state.name}")  # デバッグ用
    
    def stop_bgm(self):
#        """現在再生中のBGMを停止する"""
#        if self.current_bgm is not None:
#            bgm_channels = [1, 2, 3]  # BGM用のチャンネル
#            for ch in bgm_channels:
#                pyxel.stop(ch)
#            self.current_bgm = None  # 現在のBGM状態をリセット
#        bgm_channels = [1, 2, 3]  # BGM用のチャンネル
        bgm_channels = [0, 1, 2, 3]  # 全チャンネル消す
        for ch in bgm_channels:
            pyxel.stop(ch)  # チャンネルごとに停止
        self.current_bgm = None  # 現在のBGM状態をリセット

    def create_difficulty_buttons(self):
        # 各難易度のラベルと説明
        difficulties = [
            {"label": "Easy",      "description": "Small grid, few colors"},
            {"label": "Normal",    "description": "Larger grid, more colors"},
            {"label": "Hard",      "description": "Timed play, more colors"},
            {"label": "Very Hard", "description": "Shorter time, even more colors"},
            {"label": "Expert",    "description": "Maximum grid size, most colors"},
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
        """ゲーム内の効果音を準備"""
        self.base_notes = ["c2", "d2", "e2", "f2", "g2", "a2", "b2", "c3"]
        pyxel.sounds[0].set(
            notes=self.base_notes[0], #消したマスの色によって音を変えるのは未実装
            tones="p",
            volumes="5",
            effects="n",
            speed=15,
        )

    def calculate_progress(self):
        """盤面の進行状況を計算"""
        total_cells = self.grid_rows * self.grid_cols
        remaining_cells = sum(1 for row in self.grid for cell in row if cell != -1)
        removed_percentage = (total_cells - remaining_cells) / total_cells
        return remaining_cells, removed_percentage

    def reset_game(self, use_saved_initial_state=False):
        """
        ゲームをリセット
        use_saved_initial_stateがTrueの場合、保存した初期状態に戻す。
        それ以外の場合は新しいランダムな盤面を生成する。
        """
        if use_saved_initial_state and hasattr(self, 'initial_grid'):
            # 保存した初期盤面を復元
            self.grid = copy.deepcopy(self.initial_grid)
        else:
            # 新しいランダムな盤面を生成し、初期状態を保存
            self.grid = [
                [pyxel.rndi(0, self.num_colors - 1) for _ in range(self.grid_cols)]
                for _ in range(self.grid_rows)
            ]
            self.initial_grid = copy.deepcopy(self.grid)

        # ゲームのスコアと時間をリセット
        self.start_time = pyxel.frame_count if self.time_limit else None
        self.score = 0
        self.bonus_added = False  # ゲームリセット時にフラグをリセット

    def update(self):
        """ゲームの状態を更新"""
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        previous_state = self.state  # ステータスの変更を追跡

        # RetryボタンとQuitボタンの処理を特定の状態に限定
        if self.state in [GameState.GAME_START, GameState.GAME_MID, GameState.GAME_END]:
            # Retryボタンの処理
            retry_x = BUTTON_SPACING
            retry_y = (BUTTON_AREA_HEIGHT - BUTTON_HEIGHT) // 2
            if (
                retry_x <= mx <= retry_x + BUTTON_WIDTH
                and retry_y <= my <= retry_y + BUTTON_HEIGHT
                and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)
            ):
                print("Retry button clicked")
                self.reset_game(use_saved_initial_state=True)  # 保存済みの初期状態に戻す
                self.state = GameState.GAME_START  # ゲームを最初から開始
                return
    
            # Quitボタンの処理
            quit_x = BUTTON_SPACING + BUTTON_WIDTH + BUTTON_SPACING
            quit_y = (BUTTON_AREA_HEIGHT - BUTTON_HEIGHT) // 2
            if (
                quit_x <= mx <= quit_x + BUTTON_WIDTH
                and quit_y <= my <= quit_y + BUTTON_HEIGHT
                and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)
            ):
                print("Quit button clicked")
                self.state = GameState.OPENING  # OPENING画面に戻る
                return

        if self.state == GameState.OPENING:
#            print("GameState is OPENING")  # デバッグ出力
            if self.current_bgm != GameState.OPENING:
                self.play_bgm(GameState.OPENING)
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                print("Clicked in opening screen")  # デバッグ出力
                self.state = GameState.DIFFICULTY_SELECTION
                print(f"State changed to: {self.state}")  # 状態変更後の確認

        elif self.state == GameState.DIFFICULTY_SELECTION:
#            print(f"GameState is: {self.state}") # デバッグ出力
            if self.current_bgm != GameState.DIFFICULTY_SELECTION:
                self.play_bgm(GameState.DIFFICULTY_SELECTION)
                print(f"Switching to BGM for state state name: {state.name}")  # デバッグ用
                print(f"Switching to BGM for state game state: {GameState.DIFFICULTY_SELECTION}")  # デバッグ用
            self.reset_game(use_saved_initial_state=False)
            for button in self.difficulty_buttons:
                if button.is_hovered(mx, my):
                    if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                        self.current_difficulty = button.label
                        print(f"Difficulty button clicked: {self.current_difficulty}")  # デバッグ出力
                        self.apply_difficulty_settings()
                        print(f"Current difficulty after apply: {self.current_difficulty}")  # デバッグ出力
                        self.state = GameState.GAME_START
    
        elif self.state in [GameState.GAME_START, GameState.GAME_MID, GameState.GAME_END]:
            # 序盤、中盤、終盤の進行状態を確認
            remaining_cells, removed_percentage = self.calculate_progress()

            if self.state == GameState.GAME_START:
                if self.current_bgm != GameState.GAME_START:
                    self.play_bgm(GameState.GAME_START)

                if removed_percentage >= 0.2:  # コマ数が20%減少したら中盤へ移行
                    self.state = GameState.GAME_MID
    
            elif self.state == GameState.GAME_MID:
                if self.current_bgm != GameState.GAME_MID:
                    self.play_bgm(GameState.GAME_MID)
                is_low_time = (
                    self.time_limit
                    and (self.time_limit - (pyxel.frame_count - self.start_time) // 30) <= 10
                )
                if remaining_cells / (self.grid_rows * self.grid_cols) <= 0.25 or is_low_time:
                    self.state = GameState.GAME_END
            elif self.state == GameState.GAME_END:
                if self.current_bgm != GameState.GAME_END:
                    self.play_bgm(GameState.GAME_END)
    
            # 共通ゲーム進行処理
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.handle_click(mx, my)
            if self.time_limit and pyxel.frame_count - self.start_time > self.time_limit * 30:
                self.state = GameState.TIME_UP
            elif self.is_grid_empty():
                self.state = GameState.GAME_CLEARED
            elif not self.has_valid_moves():
                self.state = GameState.NO_MOVES
    
        elif self.state == GameState.TIME_UP:
            if self.current_bgm != GameState.TIME_UP:
                self.play_bgm(GameState.TIME_UP)
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.update_high_scores()
                self.state = GameState.SCORE_DISPLAY
    
        elif self.state == GameState.NO_MOVES:
            if self.current_bgm != GameState.NO_MOVES:
                self.play_bgm(GameState.NO_MOVES)
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.update_high_scores()
                self.state = GameState.SCORE_DISPLAY
    
        elif self.state == GameState.GAME_CLEARED:
            if self.current_bgm != GameState.GAME_CLEARED:
                self.play_bgm(GameState.GAME_CLEARED)

            # ボーナススコアの加算を1度だけ実行
            if not self.bonus_added:
                bonus_score = int(self.score * 0.5)  # 現在のスコアの50%をボーナス
                self.score += bonus_score
                self.bonus_added = True  # フラグを立てる
                print(f"Bonus Score Added: {bonus_score}")  # デバッグ用

            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.update_high_scores()
                self.state = GameState.SCORE_DISPLAY
    
        elif self.state == GameState.SCORE_DISPLAY:
            if self.current_bgm != GameState.OPENING:
                self.play_bgm(GameState.OPENING)
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.state = GameState.HIGH_SCORE_DISPLAY
    
        elif self.state == GameState.HIGH_SCORE_DISPLAY:
            if self.current_bgm != GameState.OPENING:
                self.play_bgm(GameState.OPENING)
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.state = GameState.OPENING
    
        # ステータス変更時のBGM切り替え
        if self.state != previous_state:
            self.handle_state_change()

    def apply_difficulty_settings(self):
        print(f"Applying difficulty: {self.current_difficulty}")  # デバッグ出力
        settings = self.difficulty_levels[self.current_difficulty]
        self.grid_rows = settings["grid_rows"]
        self.grid_cols = settings["grid_cols"]
        self.num_colors = settings["colors"]
        self.time_limit = settings["time_limit"]
        self.score_multiplier = settings["score_multiplier"]
        print(f"Settings applied: rows={self.grid_rows}, cols={self.grid_cols}, colors={self.num_colors}, time_limit={self.time_limit}, multiplier={self.score_multiplier}")
        # 難易度変更時に盤面をリセット
        self.reset_game(use_saved_initial_state=False)

    def handle_click(self, mx, my):
        """盤面クリック時の処理"""
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
    
            # 消去処理
            blocks_to_remove = self.find_connected_blocks(x, y, color)
            if len(blocks_to_remove) > 1:
                for bx, by in blocks_to_remove:
                    self.grid[by][bx] = -1
    
                # 効果音専用チャンネル（0番）で再生
                pyxel.play(0, color)
                self.score += int(len(blocks_to_remove) * (len(blocks_to_remove) ** 2) * self.score_multiplier)
                self.apply_gravity()
                self.shift_columns_left()

    def handle_state_change(self):
        """ステータス変更時のBGMを再生"""
        bgm_mapping = {
            GameState.GAME_START: GameState.GAME_START,
            GameState.GAME_MID: GameState.GAME_MID,
            GameState.GAME_END: GameState.GAME_END,
            GameState.TIME_UP: GameState.TIME_UP,
            GameState.NO_MOVES: GameState.NO_MOVES,
            GameState.GAME_CLEARED: GameState.GAME_CLEARED,
            GameState.OPENING: GameState.OPENING,
            GameState.DIFFICULTY_SELECTION: GameState.DIFFICULTY_SELECTION,
        }
        bgm_state = bgm_mapping.get(self.state)
        if bgm_state:
            self.play_bgm(bgm_state)

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
        new_grid = []
        for x in range(self.grid_cols):
            # 列が全て -1 ではないときだけ新しいグリッドに追加
            if any(self.grid[y][x] != -1 for y in range(self.grid_rows)):
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
        # 画面をクリア
        pyxel.cls(0)
    
        if self.state == GameState.OPENING:
            pyxel.text(80, 50, "Welcome to SameGame", pyxel.COLOR_WHITE)
            pyxel.text(30, 70, "How to Play:", pyxel.COLOR_YELLOW)
            pyxel.text(30, 90, "1. Click connected blocks to remove them.", pyxel.COLOR_WHITE)
            pyxel.text(30, 100, "2. Remove more blocks at once for higher scores.", pyxel.COLOR_WHITE)
            pyxel.text(30, 110, "3. Clear all blocks for a bonus!", pyxel.COLOR_WHITE)
            pyxel.text(30, 120, "4. Higher difficulty means higher scores!", pyxel.COLOR_WHITE)
            pyxel.text(30, 130, "5. No moves left? Game over.", pyxel.COLOR_WHITE)
            pyxel.text(80, 160, "Click to Start", pyxel.COLOR_WHITE)

        elif self.state == GameState.DIFFICULTY_SELECTION:
            pyxel.text(WINDOW_WIDTH // 2 - 60, 10, "Select Difficulty", pyxel.COLOR_YELLOW)
            for i, button in enumerate(self.difficulty_buttons):
                is_hovered = button.is_hovered(pyxel.mouse_x, pyxel.mouse_y)
                button.draw(is_hovered)
                # 説明文をボタンの右側に表示
                description = self.difficulties[i]["description"]
                pyxel.text(button.x + button.width + 10, button.y + 5, description, pyxel.COLOR_WHITE)
    
        elif self.state in [GameState.GAME_START, GameState.GAME_MID, GameState.GAME_END]:
            # 盤面とボタン・ステータスを描画
            self.draw_buttons()
            self.draw_grid()
            self.draw_score_and_time()
    
        elif self.state in [GameState.TIME_UP, GameState.NO_MOVES, GameState.GAME_CLEARED]:
            # 盤面を消さずにそのまま描画し、上にテキストを重ねる
            self.draw_buttons()
            self.draw_grid()
            self.draw_score_and_time()
    
            # それぞれの状態に応じたメッセージを上書き
            if self.state == GameState.TIME_UP:
                pyxel.text(WINDOW_WIDTH // 2 - 30, WINDOW_HEIGHT // 2 - 10, "Time's Up!", pyxel.COLOR_RED)
            elif self.state == GameState.NO_MOVES:
                pyxel.text(WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT // 2 - 10, "No Moves Available!", pyxel.COLOR_RED)
            elif self.state == GameState.GAME_CLEARED:
                pyxel.text(WINDOW_WIDTH // 2 - 70, WINDOW_HEIGHT // 2 - 10, "Congratulations!", pyxel.COLOR_GREEN)
                pyxel.text(WINDOW_WIDTH // 2 - 80, WINDOW_HEIGHT // 2 + 10, "You cleared the game!", pyxel.COLOR_WHITE)
                pyxel.text(WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT // 2 + 30, f"Bonus: {int(self.score * 0.5)}", pyxel.COLOR_YELLOW)
                pyxel.text(WINDOW_WIDTH // 2 - 40, WINDOW_HEIGHT // 2 + 50, "Click to Continue", pyxel.COLOR_WHITE)

        elif self.state == GameState.SCORE_DISPLAY:
            pyxel.text(WINDOW_WIDTH // 2 - 30, WINDOW_HEIGHT // 2 - 20, "Your Score", pyxel.COLOR_YELLOW)
            pyxel.text(WINDOW_WIDTH // 2 - 20, WINDOW_HEIGHT // 2, f"{int(self.score)}", pyxel.COLOR_YELLOW)
            pyxel.text(WINDOW_WIDTH // 2 - 40, WINDOW_HEIGHT // 2 + 20, "Click to Continue", pyxel.COLOR_WHITE)
    
        elif self.state == GameState.HIGH_SCORE_DISPLAY:
            pyxel.text(WINDOW_WIDTH // 2 - 60, 10, "Top 10 High Scores", pyxel.COLOR_YELLOW)
            for i, score in enumerate(self.high_scores):
                color = pyxel.COLOR_YELLOW if i == self.current_score_rank else pyxel.COLOR_WHITE
                pyxel.text(WINDOW_WIDTH // 2 - 30, 30 + i * 10, f"{i + 1}: {score}", color)
            pyxel.text(WINDOW_WIDTH // 2 - 40, WINDOW_HEIGHT - 20, "Click to Return", pyxel.COLOR_WHITE)

    def draw_buttons(self):
        """
        ボタンエリア(上部)の描画
        Retry/ Quit ボタンを左に配置し、
        難易度を右端に表示する。
        """
        # Retry ボタン
        retry_x = BUTTON_SPACING
        retry_y = (BUTTON_AREA_HEIGHT - BUTTON_HEIGHT) // 2
        pyxel.rect(retry_x, retry_y, BUTTON_WIDTH, BUTTON_HEIGHT, pyxel.COLOR_GRAY)
        pyxel.text(retry_x + 10, retry_y + 5, "Retry", pyxel.COLOR_WHITE)

        # Quit ボタン
        quit_x = BUTTON_SPACING + BUTTON_WIDTH + BUTTON_SPACING
        quit_y = (BUTTON_AREA_HEIGHT - BUTTON_HEIGHT) // 2
        pyxel.rect(quit_x, quit_y, BUTTON_WIDTH, BUTTON_HEIGHT, pyxel.COLOR_GRAY)
        pyxel.text(quit_x + 10, quit_y + 5, "Quit", pyxel.COLOR_WHITE)

        # 難易度名をボタンエリア右端に表示
        difficulty_text_x = WINDOW_WIDTH - 60
        difficulty_text_y = (BUTTON_AREA_HEIGHT - 8) // 2
        pyxel.text(difficulty_text_x, difficulty_text_y, self.current_difficulty, pyxel.COLOR_WHITE)

    def draw_grid(self):
        """
        盤面を描画
        """
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

    def draw_score_and_time(self):
        """
        画面下部にスコアと時間のみを描画
        """
        # スコア表示
        score_text = f"Score: {int(self.score)}"
        pyxel.text(10, WINDOW_HEIGHT - STATUS_AREA_HEIGHT + 5, score_text, pyxel.COLOR_WHITE)

        # タイマー表示
        if self.time_limit:
            remaining_time = max(0, self.time_limit - (pyxel.frame_count - self.start_time) // 30)
            time_text = f"Time: {remaining_time}s"
        else:
            time_text = "Time: --"
        time_text_width = len(time_text) * 4  # おおまかな文字幅
        pyxel.text(WINDOW_WIDTH - time_text_width - 10, WINDOW_HEIGHT - STATUS_AREA_HEIGHT + 5, time_text, pyxel.COLOR_WHITE)


# ゲームの開始
SameGame()
