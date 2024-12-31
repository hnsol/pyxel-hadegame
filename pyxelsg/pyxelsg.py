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
from board_generator import BoardGenerator

# 定数の設定
WINDOW_WIDTH = 256
WINDOW_HEIGHT = 240

#BUTTON_WIDTH = 80
#BUTTON_HEIGHT = 20
BUTTON_WIDTH = 75
BUTTON_HEIGHT = 15
BUTTON_SPACING = 10
#BUTTON_AREA_HEIGHT = 100  # ボタンエリアの高さ（縦にボタンを並べるため拡大）
BUTTON_AREA_HEIGHT = 40  # ボタンエリアの高さ（縦にボタンを並べるため拡大）
STATUS_AREA_HEIGHT = 30   # 表示エリアの高さ

#COLORS = [8, 11, 12, 13, 14, 15, 6, 7]  # 使用可能なPyxelの色番号
#COLORS = [12, 9, 11, 10, 2]  # 色覚多様性対応
#COLORS = [1, 4, 3, 2, 6]  # 色覚多様性対応 rev02
COLORS = [1, 4, 3, 6, 2]  # 色覚多様性対応 rev02
#DEFAULT_TOP_SCORES = [10000, 5000, 2500, 1000, 500, 250, 100, 50, 25, 10]  # デフォルトのトップ10スコア
DEFAULT_TOP_SCORES = [50000, 25000, 7500, 5000, 2500, 750, 500, 250, 75, 50]  # デフォルトのトップ10スコア

translations = {
    "language_button": {"ja": "EN", "en": "JA"},  # 言語切り替えボタンのラベル
#    "titles": {
#        "game_title": {
#            "ja": "さめがめ にようこそ",
#            "en": "Welcome to SameGame"},
#        "difficulty_selection": {"ja": "難易度を選んでください",
#        "en": "Select Difficulty"}
#    },
    "titles": {
        "game_title": {
            "ja": [
                (40, "さめがめ にようこそ", pyxel.COLOR_WHITE),
                (180, "クリックして開始", pyxel.COLOR_WHITE)
            ],
            "en": [
                (40, "Welcome to SameGame", pyxel.COLOR_WHITE),
                (180, "Click to Start", pyxel.COLOR_WHITE)
            ]
        },
        "difficulty_selection": {
#            "ja": "難易度を選んでください",
#            "en": "Select Difficulty"
            "ja": {"y": 40, "text": "難易度を選んでください", "color": pyxel.COLOR_YELLOW},
            "en": {"y": 40, "text": "Select Difficulty", "color": pyxel.COLOR_YELLOW}
        }
    },
#    "instructions": {
#        "intro": [
#            {"line": {"ja": "あそびかた:", "en": "How to Play:"}, "color": pyxel.COLOR_YELLOW},
#            {"line": {"ja": "1. 同じ色のブロックをクリックして消しましょう。", "en": "1. Click connected blocks to remove them."}, "color": pyxel.COLOR_WHITE},
#            {"line": {"ja": "2. 一度に多くのブロックを消すとスコアが上がります。", "en": "2. Remove more blocks at once for higher scores."}, "color": pyxel.COLOR_WHITE},
#            {"line": {"ja": "3. 全てのブロックを消すとボーナス！", "en": "3. Clear all blocks for a bonus!"}, "color": pyxel.COLOR_WHITE},
#            {"line": {"ja": "4. むずかしいほど高いスコアが得られます！", "en": "4. Higher difficulty means higher scores!"}, "color": pyxel.COLOR_WHITE},
#            {"line": {"ja": "5. 消せるブロックがなくなったらゲームオーバー。", "en": "5. No moves left? Game over."}, "color": pyxel.COLOR_WHITE}
#        ]
#    },
    "instructions": {
        "intro": {
            "ja": {
                "base_y": 70,
                "line_spacing": 15,
                "lines": [
                    {"line": "あそびかた:", "color": pyxel.COLOR_YELLOW},
                    {"line": "1. 同色ブロックをクリックで消しましょう。", "color": pyxel.COLOR_WHITE},
                    {"line": "2. 一度に多くのブロックを消すとスコアが上がります。", "color": pyxel.COLOR_WHITE},
                    {"line": "3. 全てのブロックを消すとボーナス！", "color": pyxel.COLOR_WHITE},
                    {"line": "4. むずかしいほど高いスコアが得られます！", "color": pyxel.COLOR_WHITE},
                    {"line": "5. 消せるブロックがなくなったらゲームオーバー。", "color": pyxel.COLOR_WHITE}
                ]
            },
            "en": {
                "base_y": 70,
                "line_spacing": 15,
                "lines": [
                    {"line": "How to Play:", "color": pyxel.COLOR_YELLOW},
                    {"line": "1. Click connected blocks to remove them.", "color": pyxel.COLOR_WHITE},
                    {"line": "2. Remove more blocks at once for higher scores.", "color": pyxel.COLOR_WHITE},
                    {"line": "3. Clear all blocks for a bonus!", "color": pyxel.COLOR_WHITE},
                    {"line": "4. Higher difficulty means higher scores!", "color": pyxel.COLOR_WHITE},
                    {"line": "5. No moves left? Game over.", "color": pyxel.COLOR_WHITE}
                ]
            }
        }
    },
    "difficulty_options": [
        {"key": "easy", "label": {"ja": "かんたん", "en": "Easy"}, "description": {"ja": "小さいばんめん、少ない色", "en": "Small grid, few colors"}},
        {"key": "normal", "label": {"ja": "ふつう", "en": "Normal"}, "description": {"ja": "中ぐらいのばんめん、やや多い色", "en": "Medium-sized grid, slightly more colors"}},
        {"key": "hard", "label": {"ja": "むずかしい", "en": "Hard"}, "description": {"ja": "制限時間あり、多い色", "en": "Timed play, many colors"}},
        {"key": "very_hard", "label": {"ja": "めちゃむず", "en": "Very Hard"}, "description": {"ja": "短い制限時間、大きなばんめん", "en": "Short time limit, large grid"}},
        {"key": "expert", "label": {"ja": "たつじん", "en": "Expert"}, "description": {"ja": "最大ばんめん、最も短い時間", "en": "Largest grid, shortest time limit"}}
    ],
    "game_state_messages": {
        "time_up": {
            "title": {"ja": "タイムアップ！", "en": "Time's Up!"},
            "subtitle": {"ja": "次はスコアが伸びそうですね。", "en": "Try again to improve your score."}
        },
        "no_moves": {
            "title": {"ja": "ああっ！おしい！", "en": "No Moves Available!"},
            "subtitle": {"ja": "次はきっといける！", "en": "Better luck next time!"}
        },
        "game_cleared": {
            "title": {"ja": "おおお！すごいですね！！！", "en": "Congratulations!"},
            "subtitle": {"ja": "ゲームをクリアしました！", "en": "You cleared the game!"},
            "bonus": {"ja": "ボーナス: {bonus}", "en": "Bonus: {bonus}"},
            "action": {"ja": "クリックして続行", "en": "Click to Continue"}
        },
        "score_display": {
            "title": {"ja": "今回の スコア", "en": "Your Score"},
            "action": {"ja": "クリックして つづける", "en": "Click to Continue"}
        },
        "high_score_display": {
            "title": {"ja": "トップ 10スコア", "en": "Top 10 High Scores"},
            "action": {"ja": "クリックして もどる", "en": "Click to Return"}
        }
    },
    "score_and_time": {
        "score_label": {
            "ja": "スコア:",
            "en": "Score:"
        },
        "time_label": {
            "ja": "タイム:",
            "en": "Time:"
        },
        "time_no_limit": {
            "ja": "--",
            "en": "--"
        }
    },
    "button_labels": {
        "retry": {"ja": "やりなおす", "en": "Retry"},
        "quit": {"ja": "ギブアップ", "en": "Quit"}
    }
}

class GameState(Enum):
    OPENING = "opening"
    DIFFICULTY_SELECTION = "difficulty_selection"
    BOARD_GENERATION = "board_generation"      # 盤面生成中
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

#    def draw(self, is_hovered, draw_text_func=None, font=None):
#    def draw(self, is_hovered, draw_text_func=self.draw_text, font=self.font_small):
    def draw(self, is_hovered, draw_text_func, font):
        # ボタンの塗りつぶし
        color = pyxel.COLOR_LIGHT_BLUE if is_hovered else pyxel.COLOR_GRAY
        pyxel.rect(self.x, self.y, self.width, self.height, color)

        # ボタンラベルの描画
        if self.label and draw_text_func:
            # 今までの単純な "pyxel.text()" をやめて、draw_text() を呼び出す
            text_width = font.text_width(self.label)
            text_x = self.x + (self.width - text_width) // 2
            text_y = self.y + (self.height - 10) // 2 # テキスト高さをおおよそ12ピクセルの場合
            draw_text_func(
                y=text_y,
                text=self.label,
                color=pyxel.COLOR_WHITE,
                align="left",        # 中央揃えっぽくしたければ 'left' + x_offset を工夫
                x_offset=text_x,
                font=font,
                border_color=pyxel.COLOR_DARK_BLUE
            )


class SameGame:
    def __init__(self):
        self.current_language = "ja"

        # ベースパスを取得
        self.base_path = os.path.dirname(os.path.abspath(__file__))

        # フォントの読み込み
        try:
            self.font_small = self.load_font("assets/k8x12.bdf")
#            self.font_large = self.load_font("assets/umplus_j12r.bdf")  # 必要であれば
        except FileNotFoundError as e:
            print(f"Error loading font: {e}")
            exit(1)  # フォントがない場合はエラー終了

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
            "easy": {"grid_rows": 5, "grid_cols": 5, "colors": 3, "time_limit": None, "score_multiplier": 1.0},
            "normal": {"grid_rows": 6, "grid_cols": 10, "colors": 4, "time_limit": None, "score_multiplier": 1.2},
            "hard": {"grid_rows": 8, "grid_cols": 12, "colors": 5, "time_limit": 60, "score_multiplier": 1.5},
            "very_hard": {"grid_rows": 9, "grid_cols": 15, "colors": 5, "time_limit": 45, "score_multiplier": 2.0},
            "expert": {"grid_rows": 10, "grid_cols": 18, "colors": 5, "time_limit": 30, "score_multiplier": 3.0},
        }
        self.current_difficulty = "easy"
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

        # BoardGenerator のインスタンスを作成
        self.board_generator = BoardGenerator()

        self.reset_game(use_saved_initial_state=False)

        self.difficulty_buttons = []
        self.create_difficulty_buttons()
        self.create_language_button()  # 言語切り替えボタンを作成
        self.create_game_buttons()
        self.current_bgm = None  # 現在再生中のBGMを記録
        pyxel.run(self.update, self.draw)

    def load_font(self, relative_path):
        """BDFフォントを絶対パスで読み込む"""
        absolute_path = os.path.join(self.base_path, relative_path)
        if not os.path.exists(absolute_path):
            raise FileNotFoundError(f"Font file not found: {absolute_path}")
        return pyxel.Font(absolute_path)

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
            print(f"BGM already playing for state: {state.name}")
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
        else:
            print(f"BGM data not found for state: {state.name}")  # デバッグ用
    
    def stop_bgm(self):
        print(f"Stopping all BGM channels")
#        bgm_channels = [0, 1, 2, 3]  # 全チャンネル消す
        bgm_channels = [1, 2, 3]  # 0以外を消す
        for ch in bgm_channels:
            pyxel.stop(ch)  # チャンネルごとに停止
        self.current_bgm = None  # 現在のBGM状態をリセット

    def create_language_button(self):
        """オープニング画面用の言語切り替えボタンを作成"""
        button_width = 20
        button_height = 20
        x = WINDOW_WIDTH - 30 # 画面右に配置
        y =  10 # 画面上部に配置
        self.language_button = Button(x, y, button_width, button_height, "EN")

    def create_difficulty_buttons(self):
        # 現在の言語で難易度情報を取得
#        difficulty_levels = translations[self.current_language]["difficulty_levels"]
        difficulty_levels = [
            {
                "key": option["key"],
                "label": option["label"][self.current_language],
                "description": option["description"][self.current_language]
            }
            for option in translations["difficulty_options"]
        ]

        # ボタンを縦に並べるための開始位置を計算
        start_x = (WINDOW_WIDTH - BUTTON_WIDTH) // 2 - 60
        start_y = 70
        self.difficulty_buttons = []
    
        for i, diff in enumerate(difficulty_levels):
            x = start_x
            y = start_y + i * (BUTTON_HEIGHT + BUTTON_SPACING)
            button = Button(x, y, BUTTON_WIDTH, BUTTON_HEIGHT, diff["label"])
            button.key = diff["key"]  # 内部キーをボタンに追加
            self.difficulty_buttons.append(button)

    def play_effect(self, blocks_to_remove):
        """消したマスの数に応じて上昇音階の効果音を再生"""
        num_blocks = len(blocks_to_remove)
    
        # 基本となる上昇音階の定義
        base_notes = ["c2", "d2", "e2", "g2", "a2", "c3"]
        max_notes = min(len(base_notes), num_blocks)  # 消したマス数に応じて音階を制限
        notes = base_notes[:max_notes]  # 必要な音階だけを取得
    
        # 再生速度を調整（少ない場合は速く、多い場合は少しゆっくり）
        speed = max(5, 15 - (num_blocks // 2))
    
        # 効果音を設定
        pyxel.sounds[0].set(
            notes="".join(notes),  # 上昇音階を生成
            tones="p",            # パルス音（爽やかな音）
            volumes="5" * max_notes,  # 音量を一定に
            effects="n" * max_notes,  # 効果なし（シンプルに）
            speed=speed,          # スピード設定
        )
    
        # 効果音を再生
        pyxel.play(0, 0)

    def calculate_progress(self):
        """盤面の進行状況を計算"""
        total_cells = self.grid_rows * self.grid_cols
        remaining_cells = sum(1 for row in self.grid for cell in row if cell != -1)
        removed_percentage = (total_cells - remaining_cells) / total_cells
        return remaining_cells, removed_percentage

    def generate_board(self):
        """新しい盤面を生成する"""
        return self.board_generator.generate_filled_solvable_board(
            rows=self.grid_rows,
            cols=self.grid_cols,
            colors=self.num_colors
        )

    def reset_game(self, use_saved_initial_state=False):
#        """
#        ゲームをリセット。盤面生成を別メソッドに分離。
#        use_saved_initial_stateがTrueの場合、保存した初期状態に戻す。
#        それ以外の場合は新しいランダムな盤面を生成する。
#        """
#        if use_saved_initial_state and hasattr(self, 'initial_grid'):
#            # 保存した初期盤面を復元
#            self.grid = copy.deepcopy(self.initial_grid)
#        else:
#            self.stop_bgm()
#            # BoardGenerator を使って盤面を生成
#            self.grid = self.board_generator.generate_filled_solvable_board(
#                rows=self.grid_rows,
#                cols=self.grid_cols,
#                colors=self.num_colors
#            )
##            self.board_generator.print_board(self.grid) #debug
#            print(f"Grid are generated: {self.grid}")  # デバッグ用
#            self.initial_grid = copy.deepcopy(self.grid)
#
#        # ゲームのスコアと時間をリセット
#        self.start_time = pyxel.frame_count if self.time_limit else None
#        self.score = 0
#        self.bonus_added = False  # ゲームリセット時にフラグをリセット
        """
        ゲームをリセット。盤面生成を別メソッドに分離。
        """
        if use_saved_initial_state and hasattr(self, 'initial_grid'):
            self.grid = copy.deepcopy(self.initial_grid)
        else:
            self.grid = self.generate_board()
            self.initial_grid = copy.deepcopy(self.grid)
    
        # スコアと時間をリセット
        self.start_time = pyxel.frame_count if self.time_limit else None
        self.score = 0
        self.bonus_added = False


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
                self.update_high_scores()  # スコアランキングを更新
                self.state = GameState.SCORE_DISPLAY  # SCORE_DISPLAY画面に遷移
                return

        if self.state == GameState.OPENING:
#            print("GameState is OPENING")  # デバッグ出力
            if self.current_bgm != GameState.OPENING:
                self.play_bgm(GameState.OPENING)

            # 言語切り替えボタンのクリック処理
            language_button_clicked = False  # フラグを初期化
            if self.language_button.is_hovered(pyxel.mouse_x, pyxel.mouse_y):
                if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    self.current_language = "en" if self.current_language == "ja" else "ja"
                    print(f"Language changed to: {self.current_language}")  # デバッグ用
                    # ボタンのラベルを翻訳データから取得して更新
#                    self.language_button.label = translations[self.current_language]["language_button_label"]
                    self.language_button.label = translations["language_button"][self.current_language]
                    self.create_difficulty_buttons()  # 言語切り替え時にボタンを再生成
                    language_button_clicked = True  # ボタンが押されたことを記録

            # 言語ボタンがクリックされていない場合のみ、次の処理を実行
            if not language_button_clicked and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                print("Clicked in opening screen")  # デバッグ出力
                self.state = GameState.DIFFICULTY_SELECTION
                print(f"State changed to: {self.state}")  # 状態変更後の確認

        elif self.state == GameState.DIFFICULTY_SELECTION:
#            print(f"GameState is: {self.state}") # デバッグ出力
            if self.current_bgm != GameState.DIFFICULTY_SELECTION:
                self.play_bgm(GameState.DIFFICULTY_SELECTION)
                print(f"Switching to BGM for state state name: {state.name}")  # デバッグ用
                print(f"Switching to BGM for state game state: {GameState.DIFFICULTY_SELECTION}")  # デバッグ用
            for button in self.difficulty_buttons:
                if button.is_hovered(pyxel.mouse_x, pyxel.mouse_y) and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    print(f"Difficulty button clicked: {button.key}")
                    self.apply_difficulty_settings(button.key)
                    self.state = GameState.BOARD_GENERATION
                    self.stop_bgm()

        elif self.state == GameState.BOARD_GENERATION:
            if not hasattr(self, 'generation_complete'):
                self.generation_complete = False
        
                def generate_board():
                    self.reset_game(use_saved_initial_state=False)
                    self.generation_complete = True
        
                import threading
                threading.Thread(target=generate_board).start()
        
#            self.draw_text(WINDOW_HEIGHT // 2, "Generating Board...", pyxel.COLOR_YELLOW, align="center")
        
            if self.generation_complete:
                del self.generation_complete
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

    def apply_difficulty_settings(self, difficulty_key):
        print(f"Applying difficulty: {self.current_difficulty}")  # デバッグ出力
        # ここで現在のdifficultyを更新する
        self.current_difficulty = difficulty_key

        settings = self.difficulty_levels[difficulty_key]  # 内部キーで設定を取得
        self.grid_rows = settings["grid_rows"]
        self.grid_cols = settings["grid_cols"]
        self.num_colors = settings["colors"]
        self.time_limit = settings["time_limit"]
        self.score_multiplier = settings["score_multiplier"]
        print(f"Settings applied: {settings}")
#        # 難易度変更時に盤面をリセット
#        self.reset_game(use_saved_initial_state=False)

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
#                pyxel.play(0, color)
                # 固定の効果音を再生
#                pyxel.play(0, 0)  # サウンド番号 0 をチャンネル 0 で再生
                self.play_effect(blocks_to_remove)
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

#    def draw_text(self, y, text, color, align="center", x_offset=0, font=None):
    def draw_text(self, y, text, color, align="center", x_offset=0, font=None, border_color=None):
        """BDFフォントを使用してテキストを描画"""
        font = font or self.font_small  # デフォルトで self.font_small を使用
#        text_width = len(text) * 4  # フォントの幅を計算（適切に変更可能）
        text_width = font.text_width(text)  # フォントの幅を計算（適切に変更可能）
        
        if align == "center":
            x = (WINDOW_WIDTH - text_width) // 2
        elif align == "left":
            x = x_offset
        elif align == "right":
            x = WINDOW_WIDTH - text_width - x_offset
        else:
            raise ValueError(f"Invalid alignment: {align}")

        if border_color is not None:
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    if dx != 0 or dy != 0:  # 中心位置 (0, 0) はスキップ
                        pyxel.text(x + dx, y + dy, text, border_color, font)

        pyxel.text(x, y, text, color, font)

    def draw(self):
        # 画面をクリア
        pyxel.cls(0)

        # ゲーム状態に応じたメッセージの描画
        messages = translations["game_state_messages"]
    
        if self.state == GameState.OPENING:

            """開始画面のテキストを描画"""
            game_title = translations["titles"]["game_title"][self.current_language]
            for y, text, color in game_title:
                self.draw_text(y, text, color, align="center", border_color=pyxel.COLOR_DARK_BLUE)
    
            """左揃えのテキストを描画"""
            instruction_data = translations["instructions"]["intro"][self.current_language]
            base_y = instruction_data["base_y"]
            line_spacing = instruction_data["line_spacing"]
            
            left_aligned_texts = [
                (base_y + index * line_spacing, line_data["line"], line_data["color"])
                for index, line_data in enumerate(instruction_data["lines"])
            ]
            
            for y, text, color in left_aligned_texts:
                self.draw_text(y, text, color, align="left", x_offset=25, border_color=pyxel.COLOR_DARK_BLUE)

            # 言語切り替えボタンの描画
            is_hovered = self.language_button.is_hovered(pyxel.mouse_x, pyxel.mouse_y)
#            self.language_button.draw(is_hovered)
            self.language_button.draw(is_hovered, draw_text_func=self.draw_text, font=self.font_small)

        elif self.state == GameState.DIFFICULTY_SELECTION:
            # タイトルを描画
            """難易度選択画面のタイトルを描画"""
            difficulty_data = translations["titles"]["difficulty_selection"][self.current_language]
        
            # タイトルを描画
            self.draw_text(
                difficulty_data["y"], 
                difficulty_data["text"], 
                difficulty_data["color"], 
                align="center",
                border_color=pyxel.COLOR_DARK_BLUE
            )
            
            """難易度選択画面のボタンと説明を描画"""
            difficulty_options = translations["difficulty_options"]
            
            for i, button in enumerate(self.difficulty_buttons):
                # 現在の言語に対応するボタンラベルと説明を取得
                option = difficulty_options[i]
                label = option["label"][self.current_language]
                description = option["description"][self.current_language]
            
                # ボタンのホバー状態を確認
                is_hovered = button.is_hovered(pyxel.mouse_x, pyxel.mouse_y)
            
                # ボタンを描画
                button.label = label  # ボタンにラベルをセット
                button.draw(
                    is_hovered,
                    draw_text_func=self.draw_text,
                    font=self.font_small
                )
            
                # 説明文をボタンの右側に描画
                self.draw_text(
                    y=button.y + 2,
                    text=description,
                    color=pyxel.COLOR_WHITE,
                    align="left",
                    x_offset=button.x + button.width + 10,
                    font=self.font_small,
                    border_color=pyxel.COLOR_DARK_BLUE
                )

        elif self.state == GameState.BOARD_GENERATION:
            self.draw_text(
                WINDOW_HEIGHT // 2,
                "Generating Board...",
                pyxel.COLOR_YELLOW,
                align="center",
                border_color=pyxel.COLOR_DARK_BLUE,
            )

        elif self.state in [GameState.GAME_START, GameState.GAME_MID, GameState.GAME_END]:
            # 盤面とボタン・ステータスを描画
#            self.draw_buttons()
            self.draw_game_buttons()
            self.draw_difficulty_label()
            self.draw_grid()
            self.draw_score_and_time()
    
        elif self.state in [GameState.TIME_UP, GameState.NO_MOVES, GameState.GAME_CLEARED]:
#            self.draw_buttons()
            self.draw_game_buttons()
            self.draw_difficulty_label()
            self.draw_grid()
            self.draw_score_and_time()

            
            if self.state == GameState.TIME_UP:
                # タイムアップ画面の描画
                time_up_msg = messages["time_up"]
                self.draw_text(WINDOW_HEIGHT // 2 - 20, time_up_msg["title"][self.current_language], pyxel.COLOR_RED, align="center", border_color=pyxel.COLOR_DARK_BLUE)
                self.draw_text(WINDOW_HEIGHT // 2, time_up_msg["subtitle"][self.current_language], pyxel.COLOR_WHITE, align="center", border_color=pyxel.COLOR_DARK_BLUE)
            
            elif self.state == GameState.NO_MOVES:
                # 手詰まり画面の描画
                no_moves_msg = messages["no_moves"]
                self.draw_text(WINDOW_HEIGHT // 2 - 20, no_moves_msg["title"][self.current_language], pyxel.COLOR_RED, align="center", border_color=pyxel.COLOR_DARK_BLUE)
                self.draw_text(WINDOW_HEIGHT // 2, no_moves_msg["subtitle"][self.current_language], pyxel.COLOR_WHITE, align="center", border_color=pyxel.COLOR_DARK_BLUE)
            
            elif self.state == GameState.GAME_CLEARED:
                # ゲームクリア画面の描画
                cleared_msg = messages["game_cleared"]
                self.draw_text(WINDOW_HEIGHT // 2 - 40, cleared_msg["title"][self.current_language], pyxel.COLOR_YELLOW, align="center", border_color=pyxel.COLOR_DARK_BLUE)
                self.draw_text(WINDOW_HEIGHT // 2 - 20, cleared_msg["subtitle"][self.current_language], pyxel.COLOR_WHITE, align="center", border_color=pyxel.COLOR_DARK_BLUE)
                bonus_text = cleared_msg["bonus"][self.current_language].format(bonus=int(self.score * 0.5))
                self.draw_text(WINDOW_HEIGHT // 2, bonus_text, pyxel.COLOR_YELLOW, align="center", border_color=pyxel.COLOR_DARK_BLUE)
                self.draw_text(WINDOW_HEIGHT // 2 + 20, cleared_msg["action"][self.current_language], pyxel.COLOR_WHITE, align="center", border_color=pyxel.COLOR_DARK_BLUE)
            
        elif self.state == GameState.SCORE_DISPLAY:
            # スコア表示画面の描画
            score_msg = messages["score_display"]
            self.draw_text(WINDOW_HEIGHT // 2 - 20, score_msg["title"][self.current_language], pyxel.COLOR_YELLOW, align="center", border_color=pyxel.COLOR_DARK_BLUE)
            self.draw_text(WINDOW_HEIGHT // 2, f"{int(self.score)}", pyxel.COLOR_YELLOW, align="center", border_color=pyxel.COLOR_DARK_BLUE)
            self.draw_text(WINDOW_HEIGHT // 2 + 20, score_msg["action"][self.current_language], pyxel.COLOR_WHITE, align="center", border_color=pyxel.COLOR_DARK_BLUE)
        
        elif self.state == GameState.HIGH_SCORE_DISPLAY:
            # ハイスコア表示画面の描画
            high_score_msg = messages["high_score_display"]
            self.draw_text(35, high_score_msg["title"][self.current_language], pyxel.COLOR_YELLOW, align="center", border_color=pyxel.COLOR_DARK_BLUE)
            for i, score in enumerate(self.high_scores):
                rank = f"{i + 1:>2}"  # 順位を右詰めで整形
                text = f"{rank}: {score:>6}"  # スコアを右詰めで整形
                color = pyxel.COLOR_YELLOW if i == self.current_score_rank else pyxel.COLOR_WHITE
                self.draw_text(60 + i * 12, text, color, align="center", border_color=pyxel.COLOR_DARK_BLUE)
            self.draw_text(200, high_score_msg["action"][self.current_language], pyxel.COLOR_WHITE, align="center", border_color=pyxel.COLOR_DARK_BLUE)

    def create_game_buttons(self):
        """
        Retry, Quit などのゲーム用ボタンをインスタンス生成
        """
        # Retry ボタン
        retry_x = BUTTON_SPACING
        retry_y = (BUTTON_AREA_HEIGHT - BUTTON_HEIGHT) // 2
        retry_label = translations["button_labels"]["retry"][self.current_language]
        self.retry_button = Button(retry_x, retry_y, BUTTON_WIDTH, BUTTON_HEIGHT, retry_label)
    
        # Quit ボタン
        quit_x = BUTTON_SPACING + BUTTON_WIDTH + BUTTON_SPACING
        quit_y = (BUTTON_AREA_HEIGHT - BUTTON_HEIGHT) // 2
        quit_label = translations["button_labels"]["quit"][self.current_language]
        self.quit_button = Button(quit_x, quit_y, BUTTON_WIDTH, BUTTON_HEIGHT, quit_label)
    
    def update_game_buttons(self):
        """
        Retry, Quit ボタンのクリック判定を行う
        """
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            # Retry
            if self.retry_button.is_hovered(mx, my):
                # リセットしてステートを変更
                self.reset_game(use_saved_initial_state=True)
                self.state = GameState.GAME_START
                return
            
            # Quit
            if self.quit_button.is_hovered(mx, my):
                self.update_high_scores()
                self.state = GameState.SCORE_DISPLAY
                return
    
    def draw_game_buttons(self):
        """
        Retry, Quit ボタンを描画
        """
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        # Retry
        self.retry_button.draw(
            is_hovered=self.retry_button.is_hovered(mx, my),
            draw_text_func=self.draw_text,
            font=self.font_small
        )
        # Quit
        self.quit_button.draw(
            is_hovered=self.quit_button.is_hovered(mx, my),
            draw_text_func=self.draw_text,
            font=self.font_small
        )

    def draw_difficulty_label(self):
        difficulty_options = translations["difficulty_options"]
        difficulty_levels = [
            {"key": option["key"], "label": option["label"][self.current_language]}
            for option in difficulty_options
        ]
        difficulty_keys = [level["key"] for level in difficulty_levels]
        
        current_difficulty_label = None
        for key, level in zip(difficulty_keys, difficulty_levels):
            if key == self.current_difficulty:
                current_difficulty_label = level["label"]
                break
        
        if current_difficulty_label:
            difficulty_text_x = WINDOW_WIDTH - 60
            difficulty_text_y = (BUTTON_AREA_HEIGHT - 14) // 2
            self.draw_text(
                difficulty_text_y,
                current_difficulty_label,
                pyxel.COLOR_WHITE,
                align="right",
                x_offset=10,
                border_color=pyxel.COLOR_DARK_BLUE
            )

    def draw_grid(self):
        """
        盤面を描画
        """
#        game_area_y = BUTTON_AREA_HEIGHT
#        game_area_height = WINDOW_HEIGHT - BUTTON_AREA_HEIGHT - STATUS_AREA_HEIGHT
#        cell_size = min(WINDOW_WIDTH // self.grid_cols, game_area_height // self.grid_rows)
#        grid_x_start = (WINDOW_WIDTH - (cell_size * self.grid_cols)) // 2
#        grid_y_start = game_area_y + (game_area_height - (cell_size * self.grid_rows)) // 2

        left_margin = 4  # 左側の最小余白
        game_area_y = BUTTON_AREA_HEIGHT
        game_area_height = WINDOW_HEIGHT - BUTTON_AREA_HEIGHT - STATUS_AREA_HEIGHT
        
        # グリッドのセルサイズを計算（左右余白を考慮）
        cell_size = min((WINDOW_WIDTH - 2 * left_margin) // self.grid_cols, game_area_height // self.grid_rows)
        
        # グリッドのX座標の開始位置を計算
        grid_x_start = left_margin + ((WINDOW_WIDTH - 2 * left_margin) - (cell_size * self.grid_cols)) // 2
        
        # グリッドのY座標の開始位置を計算
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

#    def draw_score_and_time(self):
#        """
#        画面下部にスコアと時間のみを描画
#        """
#        # スコア表示
#        score_text = f"Score: {int(self.score)}"
#        pyxel.text(10, WINDOW_HEIGHT - STATUS_AREA_HEIGHT + 5, score_text, pyxel.COLOR_WHITE)
#
#        # タイマー表示
#        if self.time_limit:
#            remaining_time = max(0, self.time_limit - (pyxel.frame_count - self.start_time) // 30)
#            time_text = f"Time: {remaining_time}s"
#        else:
#            time_text = "Time: --"
#        time_text_width = len(time_text) * 4  # おおまかな文字幅
#        pyxel.text(WINDOW_WIDTH - time_text_width - 10, WINDOW_HEIGHT - STATUS_AREA_HEIGHT + 5, time_text, pyxel.COLOR_WHITE)

    def draw_score_and_time(self):
        """
        画面下部にスコアと時間を描画
        """
        # スコア表示
        score_label = translations["score_and_time"]["score_label"][self.current_language]
        score_value = f"{int(self.score)}"
        self.draw_text(
            y=WINDOW_HEIGHT - STATUS_AREA_HEIGHT + 5,
            text=f"{score_label} {score_value}",
            color=pyxel.COLOR_WHITE,
            align="left",
            x_offset=10,
            font=self.font_small,
            border_color=pyxel.COLOR_DARK_BLUE
        )
    
        # タイマー表示
        if self.time_limit:
            remaining_time = max(0, self.time_limit - (pyxel.frame_count - self.start_time) // 30)
            time_label = translations["score_and_time"]["time_label"][self.current_language]
            time_value = f"{remaining_time}s"
        else:
            time_label = translations["score_and_time"]["time_label"][self.current_language]
            time_value = translations["score_and_time"]["time_no_limit"][self.current_language]
    
        self.draw_text(
            y=WINDOW_HEIGHT - STATUS_AREA_HEIGHT + 5,
            text=f"{time_label} {time_value}",
            color=pyxel.COLOR_WHITE,
            align="right",
            x_offset=10,
            font=self.font_small,
            border_color=pyxel.COLOR_DARK_BLUE
        )

# ゲームの開始
SameGame()
