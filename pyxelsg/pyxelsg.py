# title: Pyxel SameGame
# author: hann-solo
# desc: A simple SameGame puzzle game built with Pyxel. Clear the board by removing groups of blocks with the same color!
# site: https://github.com/hnsol/pyxel-samegame
# license: MIT
# version: 0.1

import pyxel
import os
import json
import random
import copy
from enum import Enum
from board_generator import BoardGenerator
from bgm import BGMGenerator

# 定数の設定
WINDOW_WIDTH = 256
WINDOW_HEIGHT = 240

BUTTON_WIDTH = 75
BUTTON_HEIGHT = 15
BUTTON_SPACING = 10
#BUTTON_AREA_HEIGHT = 100  # ボタンエリアの高さ（縦にボタンを並べるため拡大）
BUTTON_AREA_HEIGHT = 40  # ボタンエリアの高さ（縦にボタンを並べるため拡大）
STATUS_AREA_HEIGHT = 30   # 表示エリアの高さ

COLORS = [1, 4, 3, 6, 2]  # 色覚多様性対応 rev02
#DEFAULT_TOP_SCORES = [10000, 5000, 2500, 1000, 500, 250, 100, 50, 25, 10]  # デフォルトのトップ10スコア
DEFAULT_TOP_SCORES = [50000, 25000, 7500, 5000, 2500, 750, 500, 250, 75, 50]  # デフォルトのトップ10スコア

translations = {
    "language_button": {"ja": "EN", "en": "JA"},  # 言語切り替えボタンのラベル
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
    "instructions": {
        "intro": {
            "ja": {
                "base_y": 70,
                "line_spacing": 15,
                "lines": [
                    {"line": "あそびかた:", "color": pyxel.COLOR_YELLOW},
                    {"line": "1. つながっているブロックを消せます", "color": pyxel.COLOR_WHITE},
                    {"line": "2. 多くのブロックを消すと高得点", "color": pyxel.COLOR_WHITE},
                    {"line": "3. 全てのブロックを消すとボーナス！", "color": pyxel.COLOR_WHITE},
                    {"line": "4. むずかしいほど高得点！", "color": pyxel.COLOR_WHITE},
                    {"line": "5. 消せるブロックがなくなったらおわり", "color": pyxel.COLOR_WHITE}
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
        {"key": "expert", "label": {"ja": "たつじん", "en": "Expert"}, "description": {"ja": "とても短い時間、最大ばんめん", "en": "Largest grid, shortest time limit"}}
    ],
    "game_state_messages": {
        "board_generation": {
            "message": {
                "ja": "ばんめんを生成ちゅう...",
                "en": "Generating Board..."
            },
            "color": pyxel.COLOR_YELLOW
        },
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
            "subtitle": {"ja": "すべてのブロックを消しました！", "en": "You cleared the game!"},
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

class Block:
    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        # 将来的にアニメーション用フラグやパーティクル情報などを持たせたい

    def draw(self, x_offset, y_offset, cell_size):
        """
        実際に画面に描画するときの処理。
        x_offset, y_offset はグリッドの表示開始座標
        cell_size はセルのサイズ
        """
        x = x_offset + self.col * cell_size
        y = y_offset + self.row * cell_size
        pyxel.rect(x, y, cell_size, cell_size, COLORS[self.color])

class Particle:
    def __init__(self, x, y, color, size):
        self.x = x
        self.y = y
        self.vx = random.uniform(-1.5, 1.5)  # X方向のランダム速度
        self.vy = random.uniform(-2.0, -0.5) # Y方向のランダム速度 (ちょっと上向き)
        self.color = color
        self.life = 20  # パーティクルの最大寿命(フレーム数)
        self.age = 0    # 生存経過フレーム
        self.size = size  # コマに対しての相対的な大きさを設定

    def update(self):
        """毎フレーム呼ばれる。位置更新と寿命管理を行う"""
        self.x += self.vx
        self.y += self.vy

        # 重力っぽい効果を加える(任意)
        self.vy += 0.1

        self.age += 1

    def draw(self):
        """描画。Pyxelの画面座標に合わせてドットを打つ"""
#        pyxel.pset(int(self.x), int(self.y), self.color)
        # ここでは円形パーティクルの例
        # size が大きいほど目立つパーティクルになる
#        pyxel.circ(self.x, self.y, self.size, self.color)
        pyxel.rect(
            int(self.x - self.size / 2),  # 左上X座標
            int(self.y - self.size / 2),  # 左上Y座標
            int(self.size),  # 幅
            int(self.size),  # 高さ
            self.color       # 色
        )

    def is_alive(self):
        """寿命を超えていないかどうか"""
        return self.age < self.life

class SameGame:
# 各ゲームステートごとのカスタムパラメータ
    GAME_STATE_BGM_PARAMS = {
        GameState.GAME_START: {
            "preset": 1,
            "speed": 240,
            "transpose": 0,
            "instrumentation": 0,
            "chord": 0,
            "base": [3, 4, 5],
            "base_quantize": 14,
            "drums": 0,
            "melo_tone": 1,
            "melo_lowest_note": 28,
            "melo_density": 2,
            "melo_use16": True,
        },
        GameState.GAME_MID: {
            "preset": 1,
            "speed": 216,
            "transpose": 0,
            "instrumentation": 0,
            "chord": 0,
            "base": [0, 1, 2],
            "base_quantize": 14,
            "drums": 0,
            "melo_tone": 2,
            "melo_lowest_note": 28,
            "melo_density": 0,
            "melo_use16": True,
        },
        GameState.GAME_END: {
            "preset": 1,
            "speed": 192,
            "transpose": 0,
            "instrumentation": 0,
            "chord": 0,
            "base": [6, 7],
            "base_quantize": 14,
            "drums": 0,
            "melo_tone": 1,
            "melo_lowest_note": 28,
            "melo_density": 2,
            "melo_use16": True,
        },
        # 他のステートも追加可能
    }

    def __init__(self):
        self.current_language = "ja"

        # ベースパスを取得
        self.base_path = os.path.dirname(os.path.abspath(__file__))

        # フォントの読み込み
        try:
            self.font_small = self.load_font("assets/fonts/k8x12.bdf")
        except FileNotFoundError as e:
            print(f"Error loading font: {e}")
            exit(1)  # フォントがない場合はエラー終了

        # BGM関連の初期化
        self.bgm = BGMGenerator()
        self.bgm_files = {
            GameState.OPENING: "assets/game_music/opening.json",            # オープニング画面のBGM
            GameState.DIFFICULTY_SELECTION: "assets/game_music/selection.json", # 難易度選択画面のBGM
            GameState.GAME_START: "assets/game_music/gameplay_start.json", # ゲーム序盤のBGM
            GameState.GAME_MID: "assets/game_music/gameplay_mid.json",     # ゲーム中盤のBGM
            GameState.GAME_END: "assets/game_music/gameplay_end.json",     # ゲーム終盤のBGM
            GameState.TIME_UP: "assets/game_music/time_up.json",           # タイムアップ時のBGM
            GameState.NO_MOVES: "assets/game_music/no_moves.json",         # 動ける手がなくなった時のBGM
            GameState.GAME_CLEARED: "assets/game_music/cleared.json",      # ゲームクリア時のBGM
        }
        self.bgm_data = {}
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.current_bgm = None

        self.load_bgms()

        self.difficulty_levels = {
            "easy":      {"grid_rows":  5, "grid_cols":  5, "colors": 3, "time_limit": None, "score_multiplier": 1.0},
            "normal":    {"grid_rows":  6, "grid_cols":  8, "colors": 4, "time_limit": None, "score_multiplier": 1.2},
            "hard":      {"grid_rows":  9, "grid_cols": 12, "colors": 5, "time_limit":  108, "score_multiplier": 1.5},
            "very_hard": {"grid_rows": 10, "grid_cols": 15, "colors": 5, "time_limit":   81, "score_multiplier": 2.0},
            "expert":    {"grid_rows": 12, "grid_cols": 18, "colors": 5, "time_limit":   54, "score_multiplier": 3.0},
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
        self.current_bgm = None

        # BoardGenerator のインスタンスを作成
        self.board_generator = BoardGenerator()
        # パーティクルを格納するリスト
        self.particles = []

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

    def play_bgm(self, state):
        """指定された状態に対応するBGMを再生"""
        if self.current_bgm == state:
            print(f"BGM already playing for state: {state.name}")
            return  # 既に再生中の場合は何もしない
        print(f"Switching to BGM for state in play_bgm: {state.name}")  # デバッグ用

        # 現在のBGMを停止
        self.stop_bgm()

        self.current_bgm = state

        # 指定されたステートがカスタムパラメータを持つ場合
        if state in self.GAME_STATE_BGM_PARAMS:
            custom_parm_options = self.GAME_STATE_BGM_PARAMS[state]
            custom_parm = {
                key: random.choice(values) if isinstance(values, list) else values
                for key, values in custom_parm_options.items()
            }
            print(f"Custom parameters for {state.name}: {custom_parm}")  # デバッグ用
            self.bgm.set_parm(custom_parm)
            self.bgm.generate_music()
            self.bgm.play()
        elif state in self.bgm_data:
            # 既存のデータを使ったBGM再生
            bgm_channels = [1, 2, 3]  # チャンネル1〜3をBGM用に使用
            for ch, sound in zip(bgm_channels, self.bgm_data[state]):
                pyxel.sounds[ch].set(*sound)
                pyxel.play(ch, ch, loop=True)  # チャンネルごとにループ再生
        else:
            print(f"BGM data not found for state: {state.name}")  # デバッグ用

    def stop_bgm(self):
        print(f"Stopping all BGM channels")
#        bgm_channels = [0, 1, 2, 3]  # 全チャンネル消す
#        bgm_channels = [1, 2, 3]  # 0以外を消す
        bgm_channels = [0, 1, 2]  # 0以外を消す
        for ch in bgm_channels:
            # サウンドデータをリセット（空データを設定）
            pyxel.sounds[ch].set(
                notes="",
                tones="",
                volumes="",
                effects="",
                speed=1
            )
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
#        base_notes = ["c2", "d2", "e2", "g2", "a2", "c3"]
        base_notes = ["c2", "d2", "e2", "g2", "a2", "c3", "d3", "e3", "g3", "a3"]
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
        pyxel.play(3, 0)

    def calculate_progress(self):
        """盤面の進行状況を計算"""
        total_cells = self.grid_rows * self.grid_cols
        remaining_cells = sum(1 for row in self.grid for cell in row if cell != -1)
        removed_percentage = (total_cells - remaining_cells) / total_cells
        return remaining_cells, removed_percentage

#    def generate_board(self):
#        """新しい盤面を生成する"""
#        return self.board_generator.generate_filled_solvable_board(
#            rows=self.grid_rows,
#            cols=self.grid_cols,
#            colors=self.num_colors,
#            timeout=3  # 3秒タイムアウト
#        )

#    def reset_game(self, use_saved_initial_state=False):
#        """
#        ゲームをリセット。盤面生成を別メソッドに分離。
#        """
#        if use_saved_initial_state and hasattr(self, 'initial_grid'):
#            self.grid = copy.deepcopy(self.initial_grid)
#        else:
#            self.grid = self.generate_board()
#            self.initial_grid = copy.deepcopy(self.grid)
#    
#        # スコアと時間をリセット
##        self.start_time = pyxel.frame_count if self.time_limit else 0
#        self.start_time = pyxel.frame_count  # 常に現在のフレーム数で初期化
#        self.score = 0
#        self.bonus_added = False

    def reset_game_state(self):
        """
        盤面以外の情報（スコアやタイマーなど）だけをリセットする処理。
        """
        # タイマーリセット
        self.start_time = pyxel.frame_count if self.time_limit else 0
        
        # スコアやボーナスフラグのリセット
        self.score = 0
        self.bonus_added = False
        
        # BGM停止などが必要であればここに入れる
        self.stop_bgm()

#    def generate_new_board(self, use_saved_initial_state=False):
#        """
#        新たに盤面を生成する。
#        すでに self.initial_grid を持っているなら使う／使わないの制御もここで。
#        """
#        if use_saved_initial_state and hasattr(self, 'initial_grid'):
#            self.grid = copy.deepcopy(self.initial_grid)
#        else:
#            self.grid = self.board_generator.generate_filled_solvable_board(
#                rows=self.grid_rows,
#                cols=self.grid_cols,
#                colors=self.num_colors,
#                timeout=3
#            )
#            self.initial_grid = copy.deepcopy(self.grid)

    def generate_new_board(self, use_saved_initial_state=False):
        if use_saved_initial_state and hasattr(self, 'initial_grid'):
            # すでに保存済みの Block 配列があるなら、それを deepcopy で再現
            self.grid = copy.deepcopy(self.initial_grid)
        else:
            # まずは BoardGenerator で「色番号の2次元リスト」を取得
            int_grid = self.board_generator.generate_filled_solvable_board(
                rows=self.grid_rows,
                cols=self.grid_cols,
                colors=self.num_colors,
                timeout=3
            )
    
            # これを「Block (または None) の2次元リスト」に変換
            block_grid = []
            for row in range(self.grid_rows):
                block_row = []
                for col in range(self.grid_cols):
                    color = int_grid[row][col]
                    if color == -1:
                        block_row.append(None)
                    else:
                        block_row.append(Block(row, col, color))
                block_grid.append(block_row)
    
            self.grid = block_grid
            self.initial_grid = copy.deepcopy(self.grid)  # 保存

    def update(self):
        """ゲームの状態を更新"""
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        previous_state = self.state  # ステータスの変更を追跡

        # RetryボタンとQuitボタンの処理を特定の状態に限定
#        if self.state in [GameState.GAME_START, GameState.GAME_MID, GameState.GAME_END]:
        if self.state in [GameState.GAME_START, GameState.GAME_MID]:
            # Retryボタンの処理
            retry_x = BUTTON_SPACING
            retry_y = (BUTTON_AREA_HEIGHT - BUTTON_HEIGHT) // 2
            if (
                retry_x <= mx <= retry_x + BUTTON_WIDTH
                and retry_y <= my <= retry_y + BUTTON_HEIGHT
                and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)
            ):
                print("Retry button clicked")
#                self.reset_game(use_saved_initial_state=True)  # 保存済みの初期状態に戻す
                self.generate_new_board(use_saved_initial_state=True) # 盤面は変えずに
                self.reset_game_state()  # タイマーとスコアだけリセット
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
            if not hasattr(self, 'board_generated'):
                self.board_generated = False
        
            if not self.board_generated:

                # 盤面を新たに生成（リセットはタイミングに応じて）
                self.generate_new_board(use_saved_initial_state=False)
                
                # スコアやタイマーはここでリセットしたい場合に呼ぶ
                self.reset_game_state()
                
                self.board_generated = True
 
            else:
                # 生成が完了したら次のステートへ移行
                del self.board_generated
                self.state = GameState.GAME_START
                self.play_bgm(GameState.GAME_START)  # BGM開始


    
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

        # === パーティクルの更新 ===
        self.update_particles()

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

    def get_grid_layout(self):
        """
        グリッドを描画・クリックする際の cell_size / grid_x_start / grid_y_start を統一計算する
        """
        left_margin = 4
        game_area_y = BUTTON_AREA_HEIGHT
        game_area_height = WINDOW_HEIGHT - BUTTON_AREA_HEIGHT - STATUS_AREA_HEIGHT
        
        cell_size = min((WINDOW_WIDTH - 2 * left_margin) // self.grid_cols,
                        game_area_height // self.grid_rows)
        grid_x_start = left_margin + ((WINDOW_WIDTH - 2 * left_margin)
                                      - (cell_size * self.grid_cols)) // 2
        grid_y_start = game_area_y + (game_area_height - (cell_size * self.grid_rows)) // 2
    
        return cell_size, grid_x_start, grid_y_start

    def handle_click(self, mx, my):
        """盤面クリック時の処理"""
        cell_size, grid_x_start, grid_y_start = self.get_grid_layout()
    
        x = (mx - grid_x_start) // cell_size
        y = (my - grid_y_start) // cell_size
    
        if 0 <= x < self.grid_cols and 0 <= y < self.grid_rows:
#            color = self.grid[y][x]
#            if color == -1:
#                return
            block = self.grid[y][x]
            # ブロックが存在しないなら (= None) 何もしない
            if block is None:
                return
    
            # ブロックの色を取得
            color = block.color
    
            # 消去処理
            blocks_to_remove = self.find_connected_blocks(x, y, color)
            if len(blocks_to_remove) > 1:
                # 今回の消去で得られるスコアを一時変数に入れる
                points_gained = int(len(blocks_to_remove) 
                                    * (len(blocks_to_remove) ** 2) 
                                    * self.score_multiplier)

                # 1) パーティクルの発生
#                self.spawn_particles(blocks_to_remove, cell_size, grid_x_start, grid_y_start)
                self.spawn_particles(blocks_to_remove, points_gained, cell_size, grid_x_start, grid_y_start)

                # 2) ブロック消去
                for bx, by in blocks_to_remove:
                    self.grid[by][bx] = None

                # 3) 効果音・スコア等
                self.play_effect(blocks_to_remove)
#                self.score += int(len(blocks_to_remove) * (len(blocks_to_remove) ** 2) * self.score_multiplier)
                self.score += points_gained

                # 4) 重力 & 列詰め
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

#    def find_connected_blocks(self, x, y, color):
#        stack = [(x, y)]
#        visited = set()
#        connected = []
#
#        while stack:
#            cx, cy = stack.pop()
#            if (cx, cy) in visited:
#                continue
#            visited.add((cx, cy))
#            if self.grid[cy][cx] == color:
#                connected.append((cx, cy))
#                for nx, ny in [(cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)]:
#                    if 0 <= nx < self.grid_cols and 0 <= ny < self.grid_rows:
#                        stack.append((nx, ny))
#        return connected

    def find_connected_blocks(self, x, y, color):
        stack = [(x, y)]
        visited = set()
        connected = []
    
        while stack:
            cx, cy = stack.pop()
            if (cx, cy) in visited:
                continue
            visited.add((cx, cy))
    
            block = self.grid[cy][cx]
            if block is not None and block.color == color:
                connected.append((cx, cy))
    
                for nx, ny in [(cx-1, cy), (cx+1, cy), (cx, cy-1), (cx, cy+1)]:
                    if 0 <= nx < self.grid_cols and 0 <= ny < self.grid_rows:
                        stack.append((nx, ny))
    
        return connected

#    def apply_gravity(self):
#        for x in range(self.grid_cols):
#            column = [self.grid[y][x] for y in range(self.grid_rows) if self.grid[y][x] != -1]
#            for y in range(self.grid_rows):
#                self.grid[self.grid_rows - y - 1][x] = column[-(y + 1)] if y < len(column) else -1

    def apply_gravity(self):
        for col in range(self.grid_cols):
            # "None じゃないブロック" を上から順に集めたリストを作る
            column_blocks = [self.grid[row][col] for row in range(self.grid_rows) if self.grid[row][col] is not None]
            # 下から埋める形で再配置
            for row in range(self.grid_rows):
                # 下の行(y=grid_rows-1)ほど先に埋まる
                target_row = self.grid_rows - 1 - row
                if row < len(column_blocks):
                    block = column_blocks[-(row+1)]
                    block.row = target_row  # Block自体の row も更新しておく
                    self.grid[target_row][col] = block
                else:
                    self.grid[target_row][col] = None

#    def shift_columns_left(self):
#        new_grid = []
#        for x in range(self.grid_cols):
#            # 列が全て -1 ではないときだけ新しいグリッドに追加
#            if any(self.grid[y][x] != -1 for y in range(self.grid_rows)):
#                new_grid.append([self.grid[y][x] for y in range(self.grid_rows)])
#        # 空の列を追加してグリッドサイズを維持
#        while len(new_grid) < self.grid_cols:
#            new_grid.append([-1] * self.grid_rows)
#        # グリッドを更新
#        for x in range(self.grid_cols):
#            for y in range(self.grid_rows):
#                self.grid[y][x] = new_grid[x][y]

    def shift_columns_left(self):
        """
        列が全て None なら、その列を左に詰める。
        動かしたブロックは .col を更新しておく。
        """
        new_columns = []
        
        # 1. 空でない列 (少なくとも1つ Block がある列) だけ収集
        for col in range(self.grid_cols):
            # この列のブロック情報を縦にスキャン
            column_data = [self.grid[row][col] for row in range(self.grid_rows)]
            # ひとつでも None でないマスがあれば「有効な列」
            if any(block is not None for block in column_data):
                new_columns.append(column_data)
        
        # 2. 足りない列は全て None 列で埋める
        while len(new_columns) < self.grid_cols:
            new_columns.append([None] * self.grid_rows)
        
        # 3. new_columns を grid に書き戻し + 移動したブロックの col を更新
        for new_col_index, column_data in enumerate(new_columns):
            for row_index, block in enumerate(column_data):
                self.grid[row_index][new_col_index] = block
                if block is not None:
                    block.col = new_col_index

#    def has_valid_moves(self):
#        for y in range(self.grid_rows):
#            for x in range(self.grid_cols):
#                color = self.grid[y][x]
#                if color != -1 and len(self.find_connected_blocks(x, y, color)) > 1:
#                    return True
#        return False

    def has_valid_moves(self):
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                block = self.grid[row][col]
                if block is not None:
                    # 隣接チェック
                    connected = self.find_connected_blocks(col, row, block.color)
                    if len(connected) > 1:
                        return True
        return False

    def is_grid_empty(self):
        for row in self.grid:
#            for cell in row:
#                if cell != -1:
            for block in row:
                if block is not None:
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

#    def spawn_particles(self, blocks_to_remove, cell_size, grid_x_start, grid_y_start):
#        """
#        消えるブロックの画面上の位置あたりにパーティクルを出す。
#        """
#        for (bx, by) in blocks_to_remove:
#            block = self.grid[by][bx]
#            if block is None:
#                # すでに消されている場合はスキップ（2回呼ばれても大丈夫なように）
#                continue
#    
#            # ブロックの左上座標
#            x = grid_x_start + block.col * cell_size + cell_size / 2
#            y = grid_y_start + block.row * cell_size + cell_size / 2
#            # ブロックの色に対応するPyxel上のカラー
#            pyxel_color = COLORS[block.color]
#    
#            # ここで例として 6 個くらいパーティクルを出す
#            for _ in range(6):
#                p = Particle(x, y, pyxel_color)
#                self.particles.append(p)

#    def spawn_particles(self, blocks_to_remove, cell_size, grid_x_start, grid_y_start):
#        num_removed = len(blocks_to_remove)
#        # 派手さを指数的にする例（連鎖数が大きいほど一気に増加）
#        # 例： double くらいのイメージでexp成長させる
##        particle_factor = 2 ** (num_removed / 10.0)  # 10ブロックで倍々くらい
#        particle_factor = 1.0 + (self.score / 500.0) # ある程度線形で増加
#        # 必要に応じて上限を設ける
##        particle_factor = min(particle_factor, 10.0)
#        particle_factor = min(particle_factor, 20.0)
#    
#        for (bx, by) in blocks_to_remove:
#            block = self.grid[by][bx]
#            if block is None:
#                continue
#            x = grid_x_start + block.col * cell_size + cell_size / 2
#            y = grid_y_start + block.row * cell_size + cell_size / 2
#            color = COLORS[block.color]
#    
#            # コマの大きさに基づくパーティクルサイズ (例: 20% にする)
#            p_size = max(1, int(cell_size * 0.2))
#    
#            # 連鎖数から決まる “派手さ係数”
#            # これを使ってパーティクル数や速度レンジを変化
#            base_particle_count = int(5 * particle_factor)  # 最低5個、指数で増加
#    
#            for _ in range(base_particle_count):
#                # 飛び散るスピードを particle_factor に応じて拡大
#                vx = random.uniform(-1.0 * particle_factor, 1.0 * particle_factor)
#                vy = random.uniform(-2.0 * particle_factor, -0.5 * particle_factor)
#    
#                # Particleクラスのコンストラクタ引数を可変にしてカスタマイズ
#                p = Particle(x, y, color, p_size)
#                p.vx = vx
#                p.vy = vy
#    
#                self.particles.append(p)

    def spawn_particles(self, blocks_to_remove, points_gained, cell_size, grid_x_start, grid_y_start):
        """
        今回の消去で獲得した points_gained を受け取り、
        それに応じてパーティクルの数や速さ・サイズを変えてみる。
        """
        # たとえば「派手さ係数」をスコアに応じて計算する
        # 例:  スコアの大きさに比例 or 指数 or ステップでもOK
        particle_factor = min(5.0, 1.0 + (points_gained / 500.0))  
        # → 1000点につき +1、ただし最大5倍に制限
        print(f"particle factore(max 5.0): {particle_factor}")

    
        # cell_size にもとづくパーティクルの大きさ
#        base_particle_size = max(1, int(cell_size * 0.2))
        base_particle_size = max(1, int(cell_size * 0.4))
    
        for (bx, by) in blocks_to_remove:
            block = self.grid[by][bx]
            # クリックで消し終わった後だと None になっているかもしれないので要チェック
            if block is None:
                continue
    
            # 画面上の座標
            x = grid_x_start + block.col * cell_size + cell_size / 2
            y = grid_y_start + block.row * cell_size + cell_size / 2
            color = COLORS[block.color]
    
            # パーティクル個数をスコアに応じて増やす例
            base_count = int(5 * particle_factor)
            for _ in range(base_count):
                # スピードも派手さに応じて変化させる例
                vx = random.uniform(-1.0 * particle_factor, 1.0 * particle_factor)
                vy = random.uniform(-2.0 * particle_factor, -0.5 * particle_factor)
    
                # 例: Particle のコンストラクタに size を追加している
                p = Particle(x, y, color, base_particle_size)
                p.vx = vx
                p.vy = vy
    
                self.particles.append(p)

    def update_particles(self):
        """self.particles 内のパーティクルを更新し、寿命が切れたものを除去"""
        alive_particles = []
        for p in self.particles:
            p.update()
            if p.is_alive():
                alive_particles.append(p)
        self.particles = alive_particles

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
                self.draw_text(y, text, color, align="left", x_offset=50, border_color=pyxel.COLOR_DARK_BLUE)

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
            board_gen_msg = translations["game_state_messages"]["board_generation"]
            text = board_gen_msg["message"][self.current_language]
            color = board_gen_msg["color"]
            self.draw_text(
                WINDOW_HEIGHT // 2,
                text,
                color,
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
#            self.draw_game_buttons()
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

        # === パーティクル描画 ===
        self.draw_particles()

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
                # ゲーム状態を初期化してOPENINGに戻る
                self.reset_game(use_saved_initial_state=False)
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

#    def draw_grid(self):
#        """
#        盤面を描画
#        """
#        cell_size, grid_x_start, grid_y_start = self.get_grid_layout()
#
#        for y in range(self.grid_rows):
#            for x in range(self.grid_cols):
#                color = self.grid[y][x]
#                if color != -1:
#                    pyxel.rect(
#                        grid_x_start + x * cell_size,
#                        grid_y_start + y * cell_size,
#                        cell_size,
#                        cell_size,
#                        COLORS[color]
#                    )

    def draw_grid(self):
        cell_size, grid_x_start, grid_y_start = self.get_grid_layout()
    
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                block = self.grid[row][col]
                if block is not None:
                    # block.draw(...) メソッドを呼ぶ形に変更
                    block.draw(grid_x_start, grid_y_start, cell_size)

    def draw_particles(self):
        for p in self.particles:
            p.draw()

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
