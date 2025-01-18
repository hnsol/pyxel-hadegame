# title: Pyxel SameGame
# author: hann-solo
# desc: A simple SameGame puzzle game built with Pyxel. Clear the board by removing groups of blocks with the same color!
# site: https://github.com/hnsol/pyxel-samegame
# license: MIT
# version: 0.9

import pyxel
import os
import json
import math
import random
import copy
from enum import Enum
from board_generator import BoardGenerator
from bgm import BGMGenerator

# 定数の設定
WINDOW_WIDTH = 256
WINDOW_HEIGHT = 240
WINDOW_TITLE = "Pyxel SameGame"

BUTTON_WIDTH = 75
BUTTON_HEIGHT = 15
BUTTON_SPACING = 10
BUTTON_AREA_HEIGHT = 40  # ボタンエリアの高さ（縦にボタンを並べるため拡大）
STATUS_AREA_HEIGHT = 30   # 表示エリアの高さ

COLORS = [1, 4, 3, 6, 2]  # 色覚多様性対応 rev02
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
                "base_y": 80,
                "line_spacing": 20,
                "lines": [
                    {"line": "あそびかた:", "color": pyxel.COLOR_YELLOW},
                    {"line": "1. つながっているブロックを消せます", "color": pyxel.COLOR_WHITE},
                    {"line": "2. 多くのブロックを消すと高得点", "color": pyxel.COLOR_WHITE},
                    {"line": "3. 全てのブロックを消せるかな？", "color": pyxel.COLOR_WHITE},
#                    {"line": "4. むずかしいほど高得点！", "color": pyxel.COLOR_WHITE},
#                    {"line": "5. 消せるブロックがなくなったらおわり", "color": pyxel.COLOR_WHITE}
                ]
            },
            "en": {
                "base_y": 80,
                "line_spacing": 20,
                "lines": [
                    {"line": "How to Play:", "color": pyxel.COLOR_YELLOW},
                    {"line": "1. Click blocks to remove them.", "color": pyxel.COLOR_WHITE},
                    {"line": "2. Remove more blocks for higher scores.", "color": pyxel.COLOR_WHITE},
                    {"line": "3. Try to clear all blocks!", "color": pyxel.COLOR_WHITE},
#                    {"line": "4. Higher difficulty means higher scores!", "color": pyxel.COLOR_WHITE},
#                    {"line": "5. No moves left? Game over.", "color": pyxel.COLOR_WHITE}
                ]
            }
        }
    },
    "difficulty_options": [
        {"key": "easy", "label": {"ja": "かんたん", "en": "Easy"}, "description": {"ja": "小さいばんめん、少ない色", "en": "Small grid, few colors"}},
        {"key": "normal", "label": {"ja": "ふつう", "en": "Normal"}, "description": {"ja": "中ぐらいのばんめん、やや多い色", "en": "Medium-sized grid, more colors"}},
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
    def __init__(self, row, col, color, cell_size, x_offset, y_offset):
        self.row = row
        self.col = col
        self.color = color

        # ここでセルサイズをインスタンス変数として保持
        self.cell_size = cell_size

        # 画面上の描画用座標（浮動小数）
        self.x = x_offset + col * cell_size
        self.y = y_offset + row * cell_size
        
        # 目標座標（落下やシフト後の座標）
        self.target_x = self.x
        self.target_y = self.y
        
        # 移動速度やアニメーション速度係数
#        self.move_speed = 3.0  # 1フレームあたりに何ピクセル移動するか
        self.move_speed = cell_size * 0.3  # 1フレームあたりに何ピクセル移動するか

    def update(self):
        """
        毎フレーム呼ばれて、self.x, self.y が target_x, target_y に近づくようにする
        """
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        
        # 距離が move_speed 以下なら一気に到達、それ以上なら少しずつ近づく
        dist_sq = dx*dx + dy*dy
        if dist_sq < self.move_speed * self.move_speed:
            # 到達とみなす
            self.x = self.target_x
            self.y = self.target_y
        else:
            # normalizeして move_speed だけ動く
            dist = dist_sq**0.5
            self.x += (dx / dist) * self.move_speed
            self.y += (dy / dist) * self.move_speed

    def draw(self):
        """
        実際に画面に描画するときの処理。
        """
        pyxel.rect(int(self.x), int(self.y), self.cell_size, self.cell_size, COLORS[self.color])


class Particle:
    def __init__(self, x, y, color, size):
        self.x = x
        self.y = y
        self.vx = random.uniform(-1.5, 1.5)  # ランダムなX方向速度
        self.vy = random.uniform(-2.0, 1.5)  # ランダムなY方向速度
        self.gravity = 0.25  # 重力
        self.is_special = random.random() < 0.15  # 10%で他の色を混ぜる（赤黄色黒）

        # 5%の確率で赤またはダークグレー
        if self.is_special:
            self.color = random.choice([pyxel.COLOR_RED, pyxel.COLOR_PINK, pyxel.COLOR_YELLOW, pyxel.COLOR_BLACK])
            self.size = size * random.uniform(0.5, 0.75)  # サイズを半分程度に縮小
        else:
            self.color = color
            self.size = size * random.uniform(1.5, 2.5)  # 通常サイズのランダム化

        self.life = 20  # 最大寿命
        self.age = 0    # 経過フレーム

    def update(self):
        """位置と速度を更新"""
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity  # 重力を適用
#        self.size *= 0.98  # 寿命に応じて縮小
        self.size *= 0.97  # 寿命に応じて縮小
        self.age += 1

    def draw(self):
        """パーティクルの描画"""
        if self.size > 0:
            pyxel.rect(
                int(self.x - self.size / 2),
                int(self.y - self.size / 2),
                int(self.size),
                int(self.size),
                self.color
            )

    def is_alive(self):
        """寿命チェック"""
        return self.age < self.life

class ScorePopup:
    # ティア設定（データ定義）
    TIERS = [
        {"max_score": 99, "color": pyxel.COLOR_WHITE, "vy": -1.0, "font": "font_medium"},
        {"max_score": 999, "color": pyxel.COLOR_WHITE, "vy": -1.5, "font": "font_medium"},
#        {"max_score": 4999, "color": pyxel.COLOR_YELLOW, "vy": -3.0, "font": "font_medium"},
        {"max_score": 4999, "color": pyxel.COLOR_YELLOW, "vy": -2.0, "font": "font_large"},
        {"max_score": float("inf"), "color": pyxel.COLOR_RED, "vy": -2.5, "font": "font_large"},
    ]

    def __init__(self, x, y, score, color, game):
        self.x = x
        self.y = y
        self.score = score
        self.color = color
        self.game = game  # ゲームオブジェクトを保持
        self.lifetime = 20
        self.age = 0


        # スコアに応じたティア設定を適用
        tier = self.get_tier(score)
        self.color = tier["color"]
        self.vy = tier["vy"]
        self.font = getattr(self.game, tier["font"])  # フォント名からゲームオブジェクトの属性を取得

    def get_tier(self, score):
        """スコアに応じたティア設定を取得"""
        for tier in self.TIERS:
            if score <= tier["max_score"]:
                return tier
        raise ValueError(f"Invalid score: {score}")

        # デバッグ出力: 初期設定確認
#        print(f"[DEBUG] ScorePopup initialized: score={self.score}, color={self.color}, scale={self.scale}, vy={self.vy}")


    def update(self):
        self.y += self.vy
        self.age += 1

    def draw(self):
        text = f"+{self.score}"
        text_width = self.font.text_width(text)  # 使用するフォントでテキスト幅を計算
        x = int(self.x - text_width / 2)  # テキスト幅を考慮した中心位置
        y = int(self.y)
        # 袋文字付きの描画を draw_text に置き換え
        self.game.draw_text(
            y=y,
            text=text,
            color=self.color,
            align="left",
            x_offset=x,
            font=self.font,
            border_color=pyxel.COLOR_BLACK,  # 袋文字の色
        )

    def is_alive(self):
        return self.age < self.lifetime


class Stars:
    def __init__(self, num_stars, bpm):
        self.num_stars = num_stars
        self.bpm = bpm
        self.initial_positions = [
            {"x": pyxel.rndi(0, pyxel.width), "y": pyxel.rndi(0, pyxel.height), "vy": 0}
            for _ in range(num_stars)
        ]
        self.stars = self.initial_positions[:]
        self.frame_count = 0
        self.frames_per_beat = 30 * 60 / bpm
        self.effect_mode = "playing"  # "playing" または "transition"
        self.transition_type = None
        self.transition_frame = 0
        self.gravity = 0.2  # 重力加速度

    def set_transition(self, transition_type):
        """トランジション開始設定"""
        self.effect_mode = "transition"
        self.transition_type = transition_type
        self.transition_frame = 0

    def update(self):
#        print(f"Updating stars: effect_mode={self.effect_mode}")
        """更新処理"""
        self.frame_count += 1
        if self.effect_mode == "playing":
            self._update_playing()
        elif self.effect_mode == "transition":
            self._update_transition()

    def _update_playing(self):
        """通常プレイ中の動き"""
        scale = 1 - 0.01 * math.sin(2 * math.pi * self.frame_count / self.frames_per_beat)
        center_x, center_y = pyxel.width // 2, pyxel.height // 2
        for i, initial in enumerate(self.initial_positions):
            dx, dy = initial["x"] - center_x, initial["y"] - center_y
            new_x = center_x + dx * scale
            new_y = center_y + dy * scale
            self.stars[i]["x"] = new_x
            self.stars[i]["y"] = new_y

    def _update_transition(self):
        """トランジション時の動き"""
        self.transition_frame += 1
        center_x, center_y = pyxel.width // 2, pyxel.height // 2  # 常にここで定義

        if self.transition_type == "fall":
            # 重力加速度を適用
            for star in self.stars:
                star["vy"] += self.gravity  # 加速度を適用
                star["y"] += star["vy"]    # 速度を適用して位置を更新

        elif self.transition_type == "gather":
            for star in self.stars:
                dx = center_x - star["x"]
                dy = center_y - star["y"]
                # 星を中央に向かって進ませる速度を増加
                star["x"] += dx * 0.05
                star["y"] += dy * 0.05

        elif self.transition_type == "radiate":
            for star in self.stars:
                dx = center_x - star["x"]
                dy = center_y - star["y"]
                distance = math.sqrt(dx**2 + dy**2)
    
                # フェーズ1: 星から中央方向と外方向に線を徐々に伸ばす
                if self.transition_frame <= 30:
                    extend_length = distance * (self.transition_frame / 30)  # 徐々に線を伸ばす
#                    star["inner_line"] = extend_length * 0.3  # 中央側の線の長さ
#                    star["outer_line"] = extend_length * 0.7  # 外側の線の長さ
#                    star["inner_line"] = extend_length * 0.3  # 中央側の線の長さ
#                    star["outer_line"] = extend_length * 0.5  # 外側の線の長さ
                    star["inner_line"] = extend_length * 0.2  # 中央側の線の長さ
                    star["outer_line"] = extend_length * 0.3  # 外側の線の長さ
    
                # フェーズ2: 伸びた線が外方向にゆっくり移動
                elif self.transition_frame <= 45:
#                    star["inner_line"] += 1  # 中央側の線が少しずつ外に
#                    star["outer_line"] += 1  # 外側の線も少しずつ外に
                    speed_factor = 1 + (distance / (pyxel.width // 2))  # 距離に応じて速度を調整
#                    star["inner_line"] += 0.5 * speed_factor  # 中央側の線は遅い速度
#                    star["outer_line"] += 2.0 * speed_factor  # 外側の線は速い速度
                    star["outer_line"] += 1.0 * speed_factor  # 外側の線は速い速度

                    # 線の始点も中央から外側に向かって移動
#                    star["x"] += dx * 0.02 * speed_factor  # 始点の移動速度を調整
#                    star["y"] += dy * 0.02 * speed_factor
                    star["x"] -= dx * 0.005 * speed_factor  # 始点の移動速度を調整
                    star["y"] -= dy * 0.005 * speed_factor

                # フェーズ3: 線が急に速度を上げて移動
                elif self.transition_frame <= 60:
                    speed_factor = 1 + (distance / (pyxel.width // 2))  # 距離に応じて速度を調整
#                    star["inner_line"] += 3  # 中央側の線が急速に外に
#                    star["outer_line"] += 3  # 外側の線も急速に外に
#                    star["inner_line"] += 1.0  # 中央側も少し速く
#                    star["outer_line"] += 4.0  # 外側をさらに速く移動
                    star["x"] -= dx * 0.02 * speed_factor  # 始点の移動速度を調整
                    star["y"] -= dy * 0.02 * speed_factor

        # トランジションの終了条件を設定
        if self.transition_frame >= 60:
            self.effect_mode = "playing"
            self.transition_type = None
            self.transition_frame = 0

    def draw(self):
        """星の描画"""
#        for star in self.stars:
#            pyxel.pset(int(star["x"]), int(star["y"]), pyxel.COLOR_WHITE)
        center_x, center_y = pyxel.width // 2, pyxel.height // 2

        if self.transition_type == "gather":
            # ワープエフェクトとして線を描画
            for star in self.stars:
                pyxel.line(int(star["x"]), int(star["y"]), center_x, center_y, pyxel.COLOR_WHITE)

        elif self.transition_type == "radiate":
            for star in self.stars:
                dx = star["x"] - center_x
                dy = star["y"] - center_y
                distance = math.sqrt(dx**2 + dy**2)
                unit_dx, unit_dy = dx / distance, dy / distance  # 単位ベクトル計算
    
                # 星の現在位置
                start_x, start_y = star["x"], star["y"]
    
                # 中央方向に伸びる線の終点
                inner_x = start_x - unit_dx * star.get("inner_line", 0)
                inner_y = start_y - unit_dy * star.get("inner_line", 0)
    
                # 外方向に伸びる線の終点
                outer_x = start_x + unit_dx * star.get("outer_line", 0)
                outer_y = start_y + unit_dy * star.get("outer_line", 0)
    
                # 線を描画
#                pyxel.line(int(start_x), int(start_y), int(inner_x), int(inner_y), pyxel.COLOR_WHITE)
#                pyxel.line(int(start_x), int(start_y), int(outer_x), int(outer_y), pyxel.COLOR_LIGHT_BLUE)
                pyxel.line(int(start_x), int(start_y), int(inner_x), int(inner_y), pyxel.COLOR_LIGHT_BLUE)
                pyxel.line(int(start_x), int(start_y), int(outer_x), int(outer_y), pyxel.COLOR_WHITE)
    
        else:
            # 通常の星描画
            for star in self.stars:
                pyxel.pset(int(star["x"]), int(star["y"]), pyxel.COLOR_WHITE)

    def clear(self, num_stars=None, bpm=None):
#        print(f"Clearing stars: num_stars={num_stars}, bpm={bpm}")
        """星をリセット"""
        if num_stars is not None:
            self.num_stars = num_stars
        self.initial_positions = [
            {"x": pyxel.rndi(0, pyxel.width), "y": pyxel.rndi(0, pyxel.height), "vy": 0}
            for _ in range(self.num_stars)
        ]
        self.stars = self.initial_positions[:]
        if bpm is not None:
            self.bpm = bpm
            self.frames_per_beat = 30 * 60 / bpm
        self.effect_mode = "playing"
        self.transition_type = None
        self.transition_frame = 0
#        print(f"Effect mode after clear: {self.effect_mode}")

    def set_bpm(self, bpm):
        """BPMを設定"""
        self.bpm = bpm
        self.frames_per_beat = 30 * 60 / bpm

    def is_transition_active(self):
        """トランジションがアクティブかどうか"""
        return self.effect_mode == "transition"

#class TransitionEffect:
#    def __init__(self):
#        self.active = False
#        self.timer = 0
#        self.duration = 60
#        self.phase_delay = 15  # 白い点を静止させる時間
#        self.effect_type = "warp"
#        self.particles = []
#        self.center_x = pyxel.width // 2
#        self.center_y = pyxel.height // 2
#
#    def start(self, effect_type="warp", duration=60, phase_delay=15):
#        """エフェクトを開始"""
#        self.active = True
#        self.effect_type = effect_type
#        self.timer = 0
#        self.duration = duration
#        self.phase_delay = phase_delay
#
#        if effect_type == "warp":
#            self.particles = [
#                {
#                    "x": random.randint(0, pyxel.width),
#                    "y": random.randint(0, pyxel.height),
#                    "original_x": None,
#                    "original_y": None,
#                    "target_x": self.center_x,
#                    "target_y": self.center_y,
#                    "speed": random.uniform(1, 4),
#                    "color": pyxel.COLOR_WHITE,
#                }
##                for _ in range(100)
#                for _ in range(100)
#            ]
#            for particle in self.particles:
#                particle["original_x"] = particle["x"]
#                particle["original_y"] = particle["y"]
#
#        elif effect_type == "rays":
#            self.particles = [
#                {
##                    "center_x": self.center_x + random.uniform(-50, 50),  # 中心位置をランダムにずらす
##                    "center_x": self.center_x + random.uniform(-100, 100),  # 中心位置をランダムにずらす
##                    "center_y": self.center_y + random.uniform(-100, 100),
#                    "center_x": self.center_x,
#                    "center_y": self.center_y,
#                    "angle": random.uniform(0, 360),
#                    "radius": 0,
##                    "speed": random.uniform(2, 8),
#                    "speed": random.uniform(4, 16),
##                    "color": pyxel.COLOR_WHITE,
#                    "color": pyxel.COLOR_YELLOW if random.random() < 0.1 else pyxel.COLOR_WHITE,
##                    "color": pyxel.COLOR_YELLOW,
#                    "rotation_speed": random.uniform(0.5, 3.0),
#                }
##                for _ in range(50)
#                for _ in range(100)
#            ]
#
#    def update(self):
#        """エフェクトの進行"""
#        if not self.active:
#            return
#
#        self.timer += 1
#
#        if self.effect_type == "warp":
#            self._update_warp()
#        elif self.effect_type == "rays":
#            self._update_rays()
#
#        # エフェクト終了
#        if self.timer >= self.duration:
#            self.active = False
#
#    def is_active(self):
#        return self.active
#
#    def draw(self):
#        """エフェクトの描画"""
#        if not self.active:
#            return
#
#        if self.effect_type == "warp":
#            self._draw_warp()
#        elif self.effect_type == "rays":
#            self._draw_rays()
#
#    def _update_warp(self):
#        """ワープエフェクトの更新処理"""
#        if self.timer < self.phase_delay:
#            # 静止フェーズ: 点はその場にとどまる
#            return
#
#        # 動き出すフェーズ
#        for particle in self.particles:
#            dx = particle["target_x"] - particle["x"]
#            dy = particle["target_y"] - particle["y"]
#            dist = (dx**2 + dy**2) ** 0.5
#
#            # 線を伸ばす速度
#            step = particle["speed"]
#
#            if dist > step:
#                # 中心に向かって進む
#                particle["x"] += step * (dx / dist)
#                particle["y"] += step * (dy / dist)
#            else:
#                # 中心に到達した場合
#                particle["x"], particle["y"] = particle["target_x"], particle["target_y"]
#
#    def _draw_warp(self):
#        """ワープエフェクトの描画処理"""
##        pyxel.cls(pyxel.COLOR_BLACK)
#
#        for particle in self.particles:
#            # 静止フェーズ: 初期位置に白い点を描画
#            if self.timer < self.phase_delay:
#                pyxel.pset(int(particle["original_x"]), int(particle["original_y"]), particle["color"])
#            else:
#                # 放射状の線を描画
#                pyxel.line(
#                    int(particle["original_x"]),
#                    int(particle["original_y"]),
#                    int(particle["x"]),
#                    int(particle["y"]),
#                    particle["color"],
#                )
#
##    def _update_rays(self):
##        """放射状の光線エフェクトの更新処理"""
##        for particle in self.particles:
###            particle["radius"] += particle["speed"]
##            # phase_delay の間は速度を半分に
##            if self.timer < self.phase_delay:
##                particle["radius"] += particle["speed"]
##            else:
##                particle["radius"] += particle["speed"] * 0.5
#
#    def _update_rays(self):
#        """放射状の光線エフェクトの更新処理"""
#        rotation_speed = 1  # 1度/フレームで反時計回りに回転
#
#        for particle in self.particles:
#            if self.timer < self.phase_delay:
#                # フェーズ遅延中は線を伸ばす
#                particle["radius"] += particle["speed"]
#            else:
##                # フェーズ遅延後は回転のみ
##                particle["angle"] += rotation_speed
##                if particle["angle"] >= 360:
##                    particle["angle"] -= 360
#            # フェーズ遅延後は個別の回転速度で回転
#                particle["angle"] += particle["rotation_speed"]
#                if particle["angle"] >= 360:
#                    particle["angle"] -= 360
#                elif particle["angle"] < 0:
#                    particle["angle"] += 360
#
#    def _draw_rays(self):
#        """放射状の光線エフェクトの描画処理"""
#        for particle in self.particles:
#            x_end = int(self.center_x + particle["radius"] * pyxel.cos(particle["angle"]))
#            y_end = int(self.center_y + particle["radius"] * pyxel.sin(particle["angle"]))
#
#            pyxel.line(self.center_x, self.center_y, x_end, y_end, particle["color"])
#
#        # 中央から広がる白い円を描画
#        # 半径はタイマーの進行に応じて増加
#        max_radius = max(pyxel.width, pyxel.height)
#        progress = self.timer / self.duration
##        current_radius = int(progress * max_radius)
#        # 加速的な増加: 進行度の2乗を使用
#        accelerated_progress = progress ** 2  # 0 <= accelerated_progress <= 1
#        current_radius = int(accelerated_progress * max_radius)
#
#        # 半径がmax_radiusを超えないように制限
#        current_radius = min(current_radius, max_radius)
#    
#        pyxel.circ(
#            self.center_x,
#            self.center_y,
#            current_radius,
#            pyxel.COLOR_WHITE
#        )


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
        """ゲーム全体の初期化"""

        # 言語設定
        self.current_language = "ja"

        # ベースパス設定
        self.base_path = os.path.dirname(os.path.abspath(__file__))

        # Pyxel初期化
        pyxel.init(WINDOW_WIDTH, WINDOW_HEIGHT, title=WINDOW_TITLE)
        pyxel.mouse(True)
        pyxel.title = "SameGame"

        # ゲームステート
        self.state = GameState.OPENING

        # フォント読み込み
        try:
            self.font_small = self.load_font("assets/fonts/k8x12.bdf")
            self.font_medium = self.load_font("assets/fonts/umplus_j10r.bdf")
            self.font_large = self.load_font("assets/fonts/umplus_j12r.bdf")
        except FileNotFoundError as e:
            print(f"Error loading font: {e}")
            exit(1)

        # BGM設定
        self.bgm = BGMGenerator()
        self.bgm_files = {
            GameState.OPENING: "assets/game_music/opening.json",
            GameState.DIFFICULTY_SELECTION: "assets/game_music/selection.json",
            GameState.GAME_START: "assets/game_music/gameplay_start.json",
            GameState.GAME_MID: "assets/game_music/gameplay_mid.json",
            GameState.GAME_END: "assets/game_music/gameplay_end.json",
            GameState.TIME_UP: "assets/game_music/time_up.json",
            GameState.NO_MOVES: "assets/game_music/no_moves.json",
            GameState.GAME_CLEARED: "assets/game_music/cleared.json",
        }
        self.bgm_data = {}
        self.current_bgm = None
        self.load_bgms()

        # 難易度設定
        self.difficulty_levels = {
            "easy": {"grid_rows": 5, "grid_cols": 5, "colors": 3, "time_limit": None, "score_multiplier": 1.0},
            "normal": {"grid_rows": 6, "grid_cols": 8, "colors": 4, "time_limit": None, "score_multiplier": 1.2},
            "hard": {"grid_rows": 9, "grid_cols": 12, "colors": 5, "time_limit": 108, "score_multiplier": 1.5},
            "very_hard": {"grid_rows": 10, "grid_cols": 15, "colors": 5, "time_limit": 54, "score_multiplier": 2.0},
            "expert": {"grid_rows": 12, "grid_cols": 18, "colors": 5, "time_limit": 27, "score_multiplier": 3.0},
        }
        self.current_difficulty = "easy"
        self.update_difficulty_settings()

        # スコア関連
        self.high_scores = DEFAULT_TOP_SCORES[:]
        self.current_score_rank = None
        self.start_time = None
        self.score = 0
        self.bonus_added = False

        # 盤面設定
        self.board_generator = BoardGenerator()
        self.initial_grid = []
        self.grid = []

        # ボタン設定
        self.difficulty_buttons = []
        self.create_difficulty_buttons()
        self.create_language_button()
        self.create_game_buttons()

        # パーティクル設定
        self.particles = []

        # スコア表示設定
        self.score_popups = []

        # 背景のstars設定
        self.stars = Stars(num_stars=0, bpm=120)
        self.show_message = False  # メッセージ表示のフラグ

        # トランジション設定
#        self.transition_effect = TransitionEffect()
#        self.show_message = False  # メッセージ表示のフラグ

        # 画面シェイク関連の変数
        self.shake_timer = 0      # シェイクが発生しているフレーム数
        self.shake_magnitude = 0  # シェイクの強さ（ピクセル単位）

        # **アニメーション中フラグを追加**
        self.is_falling = False     # 落下アニメーションフラグ
        self.is_shifting = False    # 横シフトアニメーションフラグ

        # ゲームループ開始
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

    def update_difficulty_settings(self):
        """現在の難易度設定を反映"""
        settings = self.difficulty_levels[self.current_difficulty]
        self.grid_rows = settings["grid_rows"]
        self.grid_cols = settings["grid_cols"]
        self.num_colors = settings["colors"]
        self.time_limit = settings["time_limit"]
        self.score_multiplier = settings["score_multiplier"]

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
        # 毎フレーム、最新言語のラベルを代入
        retry_label = translations["button_labels"]["retry"][self.current_language]
        quit_label  = translations["button_labels"]["quit"][self.current_language]
    
        self.retry_button.label = retry_label
        self.quit_button.label  = quit_label

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


    def play_effect(self, blocks_to_remove):
        num_blocks = len(blocks_to_remove)
    
        # I - VII♭ のコード進行に基づく音階
        base_notes = [
            "C2", "E2", "G2",  # I (Cメジャー)
            "C3", "E3", "G3",
            "C4", "E4", "G4",
            "B-2", "D3", "F3",  # VII♭ (B♭メジャー)
            "B-3", "D4", "F4",
        ]

        # 連鎖数が多いほど高音域を使う
        max_notes = min(len(base_notes), int(3 * (1.2 ** num_blocks)))
        selected_notes = base_notes[:max_notes]
    
        # 音をランダムに選択または順に鳴らす
        notes = selected_notes if random.random() < 0.5 else random.sample(selected_notes, len(selected_notes))
    
        # トーンを連鎖数に応じて調整
        noise_ratio = min(0.5, 0.2 + num_blocks * 0.05)  # ノイズ割合（最大50%）
        pulse_ratio = 1 - noise_ratio  # パルスの割合
        tones = "".join([
            "p" if r < pulse_ratio else "n" if r < pulse_ratio + noise_ratio else "t"
            for r in [random.random() for _ in notes]
        ])
    
        # ボリューム設定：強弱を付けつつ大きめに
        base_volume = 5
        volumes = [
            base_volume + int((i / len(notes)) * 2) if tones[i] in "pt" else base_volume - 1
            for i in range(len(notes))
        ]
        volumes = "".join([str(min(7, max(1, int(v)))) for v in volumes])
    
        # 効果を上昇感があるように設定
        effects = "".join([
            "f" if i % 3 == 0 else "n" if i % 3 == 1 else "s"  # フェード、ノイズ、スライド
            for i in range(len(notes))
        ])
    
        # 速度を連鎖数に応じて遅くする
        speed = min(8, 2 + int(num_blocks ** 0.8))
    
        # デバッグ情報
#        print(f"[DEBUG] base_notes: {base_notes}")
#        print(f"[DEBUG] max_notes: {max_notes}")
#        print(f"[DEBUG] Notes: {' '.join(notes)}")
#        print(f"[DEBUG] Tones: {tones}")
#        print(f"[DEBUG] Volumes: {volumes}")
#        print(f"[DEBUG] Effects: {effects}")
#        print(f"[DEBUG] Speed: {speed}")
    
        # Pyxel サウンド設定
        try:
            pyxel.sounds[0].set(
                notes=" ".join(notes),
                tones=tones,
                volumes=volumes,
                effects=effects,
                speed=speed,
            )
            pyxel.play(3, 0)
        except Exception as e:
            print(f"[ERROR] Failed to set sound: {e}")

#    def play_effect(self, blocks_to_remove):
#        num_blocks = len(blocks_to_remove)
#        
#        # 音階：I - VII♭ のコード進行
#        base_notes = [
#            "C2", "E2", "G2",  # I (Cメジャー)
#            "C3", "E3", "G3",
#            "C4", "E4", "G4",
#            "B-2", "D3", "F3",  # VII♭ (B♭メジャー)
#            "B-3", "D4", "F4",
#        ]
#    
#        # 音階を連鎖数に応じて高音域にする
#        max_notes = min(len(base_notes), int(4 * (1.3 ** min(num_blocks, 10))))  # 最大10連鎖程度を上限
#        selected_notes = random.sample(base_notes[:max_notes], min(8, max_notes))  # 最大8音をランダム選択
#    
#        # トーン設定：ノイズを多用してRez風の雰囲気を強調
#        noise_ratio = min(0.7, 0.3 + num_blocks * 0.05)  # ノイズ割合（最大70%）
#        pulse_ratio = 1 - noise_ratio  # パルスの割合
#        tones = "".join([
#            "p" if r < pulse_ratio else "n" if r < pulse_ratio + noise_ratio else "t"
#            for r in [random.random() for _ in selected_notes]
#        ])
#    
#        # ボリューム設定：最初は大きく、徐々に減衰
#        base_volume = 6
#        volumes = [
#            base_volume - int(i / len(selected_notes) * 3) if tones[i] in "pn" else base_volume - 2
#            for i in range(len(selected_notes))
#        ]
#        volumes = "".join([str(min(7, max(1, v))) for v in volumes])
#    
#        # 効果：フェードアウト、スライド、ノイズを動的に設定
#        effects = "".join([
#            "f" if i % 3 == 0 else "n" if i % 3 == 1 else "s"
#            for i in range(len(selected_notes))
#        ])
#    
#        # 再生速度：連鎖数が多いほど速くなる（エネルギー感を演出）
#        speed = max(2, 10 - int(num_blocks ** 0.5))  # 大連鎖ほど速くなる
#    
#        # デバッグ情報
#        print(f"[DEBUG] Selected Notes: {selected_notes}")
#        print(f"[DEBUG] Tones: {tones}")
#        print(f"[DEBUG] Volumes: {volumes}")
#        print(f"[DEBUG] Effects: {effects}")
#        print(f"[DEBUG] Speed: {speed}")
#        
#        # Pyxel サウンド設定
#        try:
#            pyxel.sounds[0].set(
#                notes=" ".join(selected_notes),
#                tones=tones,
#                volumes=volumes,
#                effects=effects,
#                speed=speed,
#            )
#            pyxel.play(3, 0)  # チャンネル3で再生
#        except Exception as e:
#            print(f"[ERROR] Failed to set sound: {e}")


#    def play_effect(self, blocks_to_remove):
#        num_blocks = len(blocks_to_remove)
#    
#        # ロック音の設定
#        lock_notes = ["C4", "E4", "G4", "B4"]
#        lock_tones = "p" * len(lock_notes)  # パルス波のみ
#        lock_volumes = "5555"  # 一定の音量
#        lock_effects = "nfsn"  # フェードとスライドを少し
#        lock_speed = 10  # ロック音は比較的ゆっくり
#    
#        # Pyxel サウンドでロック音を再生
#        try:
#            pyxel.sounds[1].set(
#                notes=" ".join(lock_notes),
#                tones=lock_tones,
#                volumes=lock_volumes,
#                effects=lock_effects,
#                speed=lock_speed,
#            )
#            pyxel.play(2, 1)  # チャンネル2でロック音を再生
#        except Exception as e:
#            print(f"[ERROR] Failed to set lock sound: {e}")
#    
#        # 破壊音の設定
#        destroy_notes = [
#            "C1", "E1", "G1", "B1",  # 高音域
#            "C2", "D2", "F2", "G2",  # 爆発的な音
#        ]
#        destroy_tones = "".join([
#            "n" if i % 2 == 0 else "t"
#            for i in range(len(destroy_notes))
#        ])  # ノイズと三角波を交互に
#        destroy_volumes = "".join([
#            str(7 - (i // 2)) for i in range(len(destroy_notes))
#        ])  # 音量を段階的に減衰
#        destroy_effects = "".join([
#            "s" if i % 3 == 0 else "f" if i % 3 == 1 else "n"
#            for i in range(len(destroy_notes))
#        ])  # スライド、フェード、ノイズを適用
#        destroy_speed = max(2, 10 - int(num_blocks ** 0.5))  # 連鎖数に応じて速く
#    
#        # Pyxel サウンドで破壊音を再生
#        try:
#            pyxel.sounds[2].set(
#                notes=" ".join(destroy_notes),
#                tones=destroy_tones,
#                volumes=destroy_volumes,
#                effects=destroy_effects,
#                speed=destroy_speed,
#            )
#            pyxel.play(3, 2)  # チャンネル3で破壊音を再生
#        except Exception as e:
#            print(f"[ERROR] Failed to set destroy sound: {e}")

#    def play_effect(self, blocks_to_remove):
#        num_blocks = len(blocks_to_remove)
#    
#        # **ロックオン音の設定**
#        lock_notes = [
#            "C4", "E4", "G4",  # 高音域のIメジャーコード
#            "D4", "F4", "A4",  # 次の音に遷移（Dマイナー風）
#            "E4", "G4", "B4",  # 再び高音域
#        ]
#        # 連鎖数に応じて音符を追加
#        lock_notes = lock_notes[: min(len(lock_notes), num_blocks)]
#        lock_tones = "p" * len(lock_notes)  # パルス波のみ
#        lock_volumes = "7" * len(lock_notes)  # 最大音量で一定
#        lock_effects = "s" * len(lock_notes)  # スライドで軽快感を演出
#        lock_speed = max(4, 16 - int(num_blocks ** 0.5))  # ブロック数が多いほど速く
#    
#        # ロックオン音を再生
#        try:
#            pyxel.sounds[1].set(
#                notes=" ".join(lock_notes),
#                tones=lock_tones,
#                volumes=lock_volumes,
#                effects=lock_effects,
#                speed=lock_speed,
#            )
#            pyxel.play(2, 1)  # チャンネル2でロックオン音を再生
#        except Exception as e:
#            print(f"[ERROR] Failed to set lock sound: {e}")
#    
#        # **爆発音の設定**
#        destroy_notes = [
#            "C3", "G2", "C2",  # 低音域で迫力を演出
#            "R",                # 休符で間を作る
#        ]
#        destroy_tones = "nntn"  # ノイズと三角波で爆発感を表現
#        destroy_volumes = "7766"  # 音量を少しずつ減衰
#        destroy_effects = "sffs"  # スライドとフェードで余韻を演出
#        destroy_speed = 8  # 爆発音はゆっくり
#    
#        # 爆発音を再生
#        try:
#            pyxel.sounds[2].set(
#                notes=" ".join(destroy_notes),
#                tones=destroy_tones,
#                volumes=destroy_volumes,
#                effects=destroy_effects,
#                speed=destroy_speed,
#            )
##            pyxel.play(3, 2)  # チャンネル3で爆発音を再生
#        except Exception as e:
#            print(f"[ERROR] Failed to set destroy sound: {e}")

#    def play_effect(self, blocks_to_remove):
#        num_blocks = len(blocks_to_remove)
#        
#        # **ロックオン音の設定**
#        lock_notes = []
#        for _ in range(num_blocks):
#            lock_notes.extend(["C4", "R", "E4", "R", "G4", "R"])  # 音符と休符を交互に配置
#        
#        # 最大音符数を制限（あまり長すぎないようにする）
#        max_notes = min(len(lock_notes), 9)
#        lock_notes = lock_notes[:max_notes]
#        
#        lock_tones = "".join(["p" if note != "R" else " " for note in lock_notes])  # 休符は空白
#        lock_volumes = "".join(["7" if note != "R" else "0" for note in lock_notes])  # 休符は音量0
#        lock_effects = "".join(["s" if note != "R" else "n" for note in lock_notes])  # スライド効果を適用
#        lock_speed = 8  # ロックオン音は速め
#    
#        # ロックオン音を再生
#        try:
#            pyxel.sounds[1].set(
#                notes=" ".join(lock_notes),
#                tones=lock_tones,
#                volumes=lock_volumes,
#                effects=lock_effects,
#                speed=lock_speed,
#            )
#            pyxel.play(2, 1)  # チャンネル2でロックオン音を再生
#        except Exception as e:
#            print(f"[ERROR] Failed to set lock sound: {e}")
#        
#        # **爆発音の設定**
#        destroy_notes = ["C3", "R", "G2", "R", "C2"]  # 低音と休符で迫力を演出
#        destroy_tones = "nntnn"  # ノイズと三角波で爆発感を表現
#        destroy_volumes = "77660"  # 音量を減衰しつつ休符を挿入
#        destroy_effects = "sfsff"  # スライドとフェードで余韻を追加
#        destroy_speed = 10  # 爆発音は少しゆっくり
#    
#        # 爆発音を再生
#        try:
#            pyxel.sounds[2].set(
#                notes=" ".join(destroy_notes),
#                tones=destroy_tones,
#                volumes=destroy_volumes,
#                effects=destroy_effects,
#                speed=destroy_speed,
#            )
#            pyxel.play(3, 2)  # チャンネル3で爆発音を再生
#        except Exception as e:
#            print(f"[ERROR] Failed to set destroy sound: {e}")


    def update(self):
        # A. 今のステートに応じて行うゲームロジック（難易度選択・スコア更新など）
#        print(f"in update func: {self.state}")  # デバッグ用
        self.handle_current_state()
    
        # B. ゲームステートやアニメフラグに応じたブロックアニメ更新
        self.handle_animations()

    def handle_current_state(self):
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        previous_state = self.state  # ステータスの変更を追跡

        # stars更新
        self.stars.update()

#        # トランジション更新
#        self.transition_effect.update()
#        # トランジション終了後にメッセージ表示フラグをオンにする
#        if not self.transition_effect.is_active() and not self.show_message:
#            self.show_message = True

        # トランジション終了後にメッセージ表示フラグをオンにする
        if not self.stars.is_transition_active() and not self.show_message:
            self.show_message = True

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
#                print("Quit button clicked")
                self.update_high_scores()  # スコアランキングを更新
                self.state = GameState.SCORE_DISPLAY  # SCORE_DISPLAY画面に遷移
                return

        # 1. OPENING のとき
        if self.state == GameState.OPENING:
#            print("GameState is OPENING")  # デバッグ出力
            if self.current_bgm != GameState.OPENING:
                self.play_bgm(GameState.OPENING)

            # 言語切り替えボタンのクリック処理
            language_button_clicked = False  # フラグを初期化
            if self.language_button.is_hovered(pyxel.mouse_x, pyxel.mouse_y):
                if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    self.current_language = "en" if self.current_language == "ja" else "ja"
#                    print(f"Language changed to: {self.current_language}")  # デバッグ用
                    # ボタンのラベルを翻訳データから取得して更新
#                    self.language_button.label = translations[self.current_language]["language_button_label"]
                    self.language_button.label = translations["language_button"][self.current_language]
                    self.create_difficulty_buttons()  # 言語切り替え時にボタンを再生成
                    language_button_clicked = True  # ボタンが押されたことを記録

            # 言語ボタンがクリックされていない場合のみ、次の処理を実行
            if not language_button_clicked and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
#                print("Clicked in opening screen")  # デバッグ出力
                self.state = GameState.DIFFICULTY_SELECTION
#                print(f"State changed to: {self.state}")  # 状態変更後の確認

        # 2. DIFFICULTY_SELECTION のとき
        elif self.state == GameState.DIFFICULTY_SELECTION:
#            print(f"GameState is: {self.state}") # デバッグ出力
            if self.current_bgm != GameState.DIFFICULTY_SELECTION:
                self.play_bgm(GameState.DIFFICULTY_SELECTION)
                print(f"Switching to BGM for state state name: {state.name}")  # デバッグ用
            for button in self.difficulty_buttons:
                if button.is_hovered(pyxel.mouse_x, pyxel.mouse_y) and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    print(f"Difficulty button clicked: {button.key}")
                    self.apply_difficulty_settings(button.key)
                    self.state = GameState.BOARD_GENERATION
                    self.stop_bgm()

        # 3. BOARD_GENERATION のとき
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

        # 4. ゲームプレイ（GAME_START, GAME_MID, GAME_ENDなど）
        elif self.state in [GameState.GAME_START, GameState.GAME_MID, GameState.GAME_END]:
            # 序盤、中盤、終盤の進行状態を確認
            remaining_cells, removed_percentage = self.calculate_progress()

            if self.state == GameState.GAME_START:
                if self.current_bgm != GameState.GAME_START:
                    self.play_bgm(GameState.GAME_START)

#                print(f"[DEBUG] Remaining cells: {remaining_cells}, Removed percentage: {removed_percentage}")
                if removed_percentage >= 0.2:  # コマ数が20%減少したら中盤へ移行
                    print(f"[DEBUG] Moved to GameState.GAME_MID")
                    self.state = GameState.GAME_MID
    
            elif self.state == GameState.GAME_MID:
                if self.current_bgm != GameState.GAME_MID:
                    self.play_bgm(GameState.GAME_MID)
                is_low_time = (
                    self.time_limit
                    and (self.time_limit - (pyxel.frame_count - self.start_time) // 30) <= 15
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
            if not self.is_falling and not self.is_shifting:
                if self.is_grid_empty():
                    self.state = GameState.GAME_CLEARED
                elif not self.has_valid_moves():  # 盤面にコマはあるが手がない
                    self.state = GameState.NO_MOVES

        # 5. TIME_UP, NO_MOVES, GAME_CLEARED
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
#                print(f"Bonus Score Added: {bonus_score}")  # デバッグ用

            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.update_high_scores()
                self.state = GameState.SCORE_DISPLAY

        # 6. SCORE_DISPLAY, HIGH_SCORE_DISPLAY
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

        # シェイクタイマーの更新
        if self.shake_timer > 0:
            self.shake_timer -= 1

    def handle_animations(self):
        if self.state in [GameState.GAME_START, 
                  GameState.GAME_MID, 
                  GameState.GAME_END, 
                  GameState.TIME_UP, 
                  GameState.NO_MOVES, 
                  GameState.GAME_CLEARED]:
            # もし is_falling が True なら「全ブロック停止したか」をチェック
            if self.is_falling:
                if self.all_blocks_stopped():
                    self.is_falling = False
                    # 横シフト開始
                    self.shift_columns_left_animated()
                    self.is_shifting = True
    
            elif self.is_shifting:
                if self.all_blocks_stopped():
                    self.is_shifting = False
    
            # パーティクルやブロック更新
            self.update_particles()
            
            for row in range(self.grid_rows):
                for col in range(self.grid_cols):
                    block = self.grid[row][col]
                    if block:
                        block.update()

            # スコアポップアップの更新
            alive_popups = []
            for popup in self.score_popups:
                popup.update()
                if popup.is_alive():
                    alive_popups.append(popup)
            self.score_popups = alive_popups

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
#        print(f"Settings applied: {settings}")

    def handle_click(self, mx, my):
        # アニメ中はクリック無視
        if self.is_falling or self.is_shifting:
            return

        """盤面クリック時の処理"""
        cell_size, grid_x_start, grid_y_start = self.get_grid_layout()
    
        x = (mx - grid_x_start) // cell_size
        y = (my - grid_y_start) // cell_size
    
        if 0 <= x < self.grid_cols and 0 <= y < self.grid_rows:
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
#                print(f"First Click Debug: blocks_to_remove={len(blocks_to_remove)}, score_multiplier={self.score_multiplier}, points_gained={points_gained}")

                # 1) パーティクルの発生
#                self.spawn_particles(blocks_to_remove, cell_size, grid_x_start, grid_y_start)
                self.spawn_particles(blocks_to_remove, points_gained, cell_size, grid_x_start, grid_y_start)

                # 2) 効果音・スコア等
                self.play_effect(blocks_to_remove)
#                self.score += int(len(blocks_to_remove) * (len(blocks_to_remove) ** 2) * self.score_multiplier)
                self.score += points_gained

                # 3) スコアポップアップの生成（最初のブロックを使用）
                if blocks_to_remove:
                    # 最初のブロックを取得
                    bx, by = blocks_to_remove[0]
                    block = self.grid[by][bx]
                    if block:
                        x = grid_x_start + block.col * cell_size + cell_size / 2
                        y = grid_y_start + block.row * cell_size + cell_size / 2
#                        popup = ScorePopup(x, y, points_gained, COLORS[block.color])
                        popup = ScorePopup(x, y, points_gained, pyxel.COLOR_WHITE, game=self)
                        self.score_popups.append(popup)
                        # デバッグメッセージ
#                        print(f"[DEBUG] ScorePopup created at ({x}, {y}) with score: {points_gained}")
#                    else:
#                        print(f"[DEBUG] Block at ({bx}, {by}) is None. No ScorePopup created.")
#                else:
#                    print("[DEBUG] blocks_to_remove is empty. No ScorePopup created.")

                # 4) ブロック消去
                for bx, by in blocks_to_remove:
                    self.grid[by][bx] = None

                # 5) 重力 & 列詰め

                # まず落下アニメだけを始める
                self.apply_gravity_animated()
                self.is_falling = True

                # 6) 画面を揺らすフラグをセット
                # シェイクレベルをポイントに応じて増やす
                # 点数ごとに+1, 最長20フレーム
#                self.shake_magnitude = min(5, 1 + points_gained // 500)
#                self.shake_magnitude = min(8, 1 + points_gained // 500)
#                self.shake_timer = min(20, 2 + points_gained // 100)
                self.shake_magnitude = min(15, 2 + points_gained // 100)
                self.shake_timer = min(30, 4 + points_gained // 100)
#                print(f"Debug: shake_magnitude={self.shake_magnitude}, shake_timer={self.shake_timer}, points_gained={points_gained}")

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
        
        if self.state in [GameState.GAME_START]:
            bpm = 28800 // self.GAME_STATE_BGM_PARAMS[self.state]["speed"]
#            print(f"Setting stars for GAME_START with bpm={bpm}")
            self.stars.clear(num_stars=108, bpm=bpm)  # 必要な数の星を生成
        elif self.state in [GameState.GAME_MID]:
            new_bpm = 28800 // self.GAME_STATE_BGM_PARAMS[self.state]["speed"]
            self.stars.set_bpm(new_bpm)
        elif self.state in [GameState.GAME_END]:
            new_bpm = 28800 // self.GAME_STATE_BGM_PARAMS[self.state]["speed"]
            self.stars.set_bpm(new_bpm)
        elif self.state in [GameState.TIME_UP, GameState.NO_MOVES]:
#            self.stars.clear(num_stars=0)  # 星をクリア
            self.stars.set_transition("fall")  # 例: "fall", "gather", "radiate"
#            self.stars.set_transition("radiate")  # 例: "fall", "gather", "radiate"
            self.show_message = False  # メッセージを非表示にする
        elif self.state in [GameState.GAME_CLEARED]:
#            self.stars.clear(num_stars=0)  # 星をクリア
            self.stars.clear(num_stars=216)  # 必要な数の星を生成
            self.stars.set_transition("radiate")
            self.show_message = False  # メッセージを非表示にする
        elif self.state in [GameState.SCORE_DISPLAY]:
            self.stars.clear(num_stars=0)  # 星をクリア
 
    def update_high_scores(self):
        if self.score not in self.high_scores:
            self.high_scores.append(self.score)
        self.high_scores.sort(reverse=True)
        self.high_scores = self.high_scores[:10]
        try:
            self.current_score_rank = self.high_scores.index(self.score)
        except ValueError:
            self.current_score_rank = None

    def calculate_progress(self):
        """盤面の進行状況を計算"""
        total_cells = self.grid_rows * self.grid_cols
        # `Block` オブジェクトが存在するセルをカウント
        remaining_cells = sum(1 for row in self.grid for cell in row if cell is not None)
        removed_percentage = (total_cells - remaining_cells) / total_cells
#        print(f"[DEBUG] Remaining cells: {remaining_cells}, Removed percentage: {removed_percentage}")
        return remaining_cells, removed_percentage

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

    def generate_new_board(self, use_saved_initial_state=False):
        # ここで先にセルサイズ等を更新
        self.cell_size, self.grid_x_start, self.grid_y_start = self.get_grid_layout()

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
                        block_row.append(Block(
                            row, col, color,
                            self.cell_size,
                            self.grid_x_start,
                            self.grid_y_start
                        ))
                block_grid.append(block_row)
    
            self.grid = block_grid
            self.initial_grid = copy.deepcopy(self.grid)  # 保存

    def all_blocks_stopped(self):
        """
        全ブロックの (x, y) が (target_x, target_y) に到達していれば True を返す
        """
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                block = self.grid[row][col]
                if block is not None:
                    # まだ動いているブロックがあったら False
                    if abs(block.x - block.target_x) > 0.1 or abs(block.y - block.target_y) > 0.1:
                        return False
        return True

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

    def apply_gravity_animated(self):
        """
        従来の apply_gravity() と同じように「最終 row」を計算しつつ、
        実際に block.row を書き換え、block.target_y を更新してあげる。
        """
        for col in range(self.grid_cols):
            # この列にあるブロックを抽出
            column_blocks = []
            for row in range(self.grid_rows):
                if self.grid[row][col] is not None:
                    column_blocks.append(self.grid[row][col])
            
            # 下から詰めるように最終 row を割り当て
            # 例：最後の行 (grid_rows-1) から順番に
            curr_row = self.grid_rows - 1
            for block in reversed(column_blocks):
                block.row = curr_row  # ここで row を更新
                # block.target_y = y_offset + curr_row * cell_size
                block.target_y = self.grid_y_start + curr_row * self.cell_size  
                self.grid[curr_row][col] = block
                curr_row -= 1
            
            # 残りは None 埋め
            for r in range(curr_row, -1, -1):
                self.grid[r][col] = None

    def shift_columns_left_animated(self):
        new_columns = []
        for col in range(self.grid_cols):
            column_data = [self.grid[row][col] for row in range(self.grid_rows)]
            if any(block is not None for block in column_data):
                new_columns.append(column_data)
        
        while len(new_columns) < self.grid_cols:
            new_columns.append([None]*self.grid_rows)
        
        for new_col_index, column_data in enumerate(new_columns):
            for row_index, block in enumerate(column_data):
                self.grid[row_index][new_col_index] = block
                if block is not None:
                    block.col = new_col_index
                    block.target_x = self.grid_x_start + new_col_index * self.cell_size

    def has_valid_moves(self):
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                block = self.grid[row][col]
                if block is not None:
                    # 隣接チェック
                    connected = self.find_connected_blocks(col, row, block.color)
                    if len(connected) > 1:
                        return True
#                else:
#                    print(f"[DEBUG] Block at row={row}, col={col} is None.")
        # すべてのブロックをチェックした後
#        print(f"[DEBUG] No valid moves. Last checked block: None or invalid.")
        return False

    def is_grid_empty(self):
        for row in self.grid:
#            for cell in row:
#                if cell != -1:
            for block in row:
                if block is not None:
                    return False
        return True


    def spawn_particles(self, blocks_to_remove, points_gained, cell_size, grid_x_start, grid_y_start):
        """
        今回の消去で獲得した points_gained を受け取り、
        それに応じてパーティクルの数や速さ・サイズを変えてみる。
        """
        # 「派手さ係数」をスコアに応じて計算
        particle_factor = min(5.0, 1.0 + (points_gained / 500.0))  
        # → 500点につき +1、ただし最大5倍に制限
    
        # cell_size にもとづくパーティクルの大きさ
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
    
            # 普通のパーティクル生成（ランダムな速度と派手さ調整を復元）
            base_count = int(5 * particle_factor)
            for _ in range(base_count):
                p = Particle(x, y, color, base_particle_size)
                p.vx = random.uniform(-1.0 * particle_factor, 1.0 * particle_factor)  # ランダムな速度 (X)
                p.vy = random.uniform(-2.0 * particle_factor, -0.5 * particle_factor)  # ランダムな速度 (Y)
                self.particles.append(p)
    
    def update_particles(self):
        """self.particles 内のパーティクルを更新し、寿命が切れたものを除去"""
        alive_particles = []
        for p in self.particles:
            p.update()
            if p.is_alive():
                alive_particles.append(p)
        self.particles = alive_particles

    def reset_particles(self):
        """パーティクルをリセットする"""
        self.particles = []

    def draw_particles(self):
        for p in self.particles:
            p.draw()


#    def draw(self):
#        # まずシェイクのオフセットを決定
#        # シェイクタイマーが残っていればランダムにオフセット
#        if self.shake_timer > 0:
#            # 残りタイマーに基づいて非線形減衰を計算
#            normalized_timer = self.shake_timer / 20  # 0〜1に正規化
##            current_magnitude = max(1, self.shake_magnitude * (normalized_timer ** 2))  # 平方減衰
##            shake_x = random.uniform(-current_magnitude, current_magnitude)
##            shake_y = random.uniform(-current_magnitude, current_magnitude)
#
#            # 減衰を緩やかに（直線減衰や平方根を使用）
#            current_magnitude = self.shake_magnitude * (normalized_timer ** 0.5)  # 緩やかな減衰
#            # ランダム性を強化（ノイズのような動きを追加）
#            shake_x = random.uniform(-current_magnitude, current_magnitude) + math.sin(pyxel.frame_count * 0.1) * current_magnitude * 0.2
#            shake_y = random.uniform(-current_magnitude, current_magnitude) + math.cos(pyxel.frame_count * 0.1) * current_magnitude * 0.2
#        else:
#            shake_x = 0
#            shake_y = 0
#    
#        # Pyxel のカメラをセット
#        pyxel.camera(shake_x, shake_y)
#
#        # 画面をクリア
#        pyxel.cls(0)
#
#        # トランジション更新
#        self.transition_effect.draw()
#
#        # ゲーム状態に応じたメッセージの描画
#        messages = translations["game_state_messages"]
#    
#        if self.state == GameState.OPENING:
#
#            """開始画面のテキストを描画"""
#            game_title = translations["titles"]["game_title"][self.current_language]
#            for y, text, color in game_title:
#                self.draw_text(y, text, color, align="center", border_color=pyxel.COLOR_DARK_BLUE)
#    
#            """左揃えのテキストを描画"""
#            instruction_data = translations["instructions"]["intro"][self.current_language]
#            base_y = instruction_data["base_y"]
#            line_spacing = instruction_data["line_spacing"]
#            
#            left_aligned_texts = [
#                (base_y + index * line_spacing, line_data["line"], line_data["color"])
#                for index, line_data in enumerate(instruction_data["lines"])
#            ]
#            
#            for y, text, color in left_aligned_texts:
#                self.draw_text(y, text, color, align="left", x_offset=50, border_color=pyxel.COLOR_DARK_BLUE)
#
#            # 言語切り替えボタンの描画
#            is_hovered = self.language_button.is_hovered(pyxel.mouse_x, pyxel.mouse_y)
##            self.language_button.draw(is_hovered)
#            self.language_button.draw(is_hovered, draw_text_func=self.draw_text, font=self.font_small)
#
#        elif self.state == GameState.DIFFICULTY_SELECTION:
#            # タイトルを描画
#            """難易度選択画面のタイトルを描画"""
#            difficulty_data = translations["titles"]["difficulty_selection"][self.current_language]
#        
#            # タイトルを描画
#            self.draw_text(
#                difficulty_data["y"], 
#                difficulty_data["text"], 
#                difficulty_data["color"], 
#                align="center",
#                border_color=pyxel.COLOR_DARK_BLUE
#            )
#            
#            """難易度選択画面のボタンと説明を描画"""
#            difficulty_options = translations["difficulty_options"]
#            
#            for i, button in enumerate(self.difficulty_buttons):
#                # 現在の言語に対応するボタンラベルと説明を取得
#                option = difficulty_options[i]
#                label = option["label"][self.current_language]
#                description = option["description"][self.current_language]
#            
#                # ボタンのホバー状態を確認
#                is_hovered = button.is_hovered(pyxel.mouse_x, pyxel.mouse_y)
#            
#                # ボタンを描画
#                button.label = label  # ボタンにラベルをセット
#                button.draw(
#                    is_hovered,
#                    draw_text_func=self.draw_text,
#                    font=self.font_small
#                )
#            
#                # 説明文をボタンの右側に描画
#                self.draw_text(
#                    y=button.y + 2,
#                    text=description,
#                    color=pyxel.COLOR_WHITE,
#                    align="left",
#                    x_offset=button.x + button.width + 10,
#                    font=self.font_small,
#                    border_color=pyxel.COLOR_DARK_BLUE
#                )
#
#        elif self.state == GameState.BOARD_GENERATION:
#            board_gen_msg = translations["game_state_messages"]["board_generation"]
#            text = board_gen_msg["message"][self.current_language]
#            color = board_gen_msg["color"]
#            self.draw_text(
#                WINDOW_HEIGHT // 2,
#                text,
#                color,
#                align="center",
#                border_color=pyxel.COLOR_DARK_BLUE,
#            )
#
#        elif self.state in [GameState.GAME_START, GameState.GAME_MID, GameState.GAME_END]:
#            # 盤面とボタン・ステータスを描画
##            self.draw_buttons()
#            self.draw_game_buttons()
#            self.draw_difficulty_label()
#            self.draw_grid()
#            self.draw_score_and_time()
#    
#        elif self.state in [GameState.TIME_UP, GameState.NO_MOVES, GameState.GAME_CLEARED]:
##            self.draw_buttons()
##            self.draw_game_buttons()
#            self.draw_difficulty_label()
#            self.draw_grid()
#            self.draw_score_and_time()
#
#            
#            # トランジションが終了した場合のみメッセージを描画
#            if self.show_message:
#                if self.state == GameState.TIME_UP:
#                    # タイムアップ画面の描画
#                    time_up_msg = messages["time_up"]
#                    self.draw_text(WINDOW_HEIGHT // 2 - 20, time_up_msg["title"][self.current_language], pyxel.COLOR_RED, align="center", border_color=pyxel.COLOR_DARK_BLUE)
#                    self.draw_text(WINDOW_HEIGHT // 2, time_up_msg["subtitle"][self.current_language], pyxel.COLOR_WHITE, align="center", border_color=pyxel.COLOR_DARK_BLUE)
#                
#                elif self.state == GameState.NO_MOVES:
#                    # 手詰まり画面の描画
#                    no_moves_msg = messages["no_moves"]
#                    self.draw_text(WINDOW_HEIGHT // 2 - 20, no_moves_msg["title"][self.current_language], pyxel.COLOR_RED, align="center", border_color=pyxel.COLOR_DARK_BLUE)
#                    self.draw_text(WINDOW_HEIGHT // 2, no_moves_msg["subtitle"][self.current_language], pyxel.COLOR_WHITE, align="center", border_color=pyxel.COLOR_DARK_BLUE)
#                
#                elif self.state == GameState.GAME_CLEARED:
#                    # ゲームクリア画面の描画
#                    # 画面をクリア
#                    pyxel.cls(pyxel.COLOR_WHITE)
#
#                    cleared_msg = messages["game_cleared"]
#                    self.draw_text(WINDOW_HEIGHT // 2 - 40, cleared_msg["title"][self.current_language], pyxel.COLOR_YELLOW, align="center", border_color=pyxel.COLOR_DARK_BLUE)
#                    self.draw_text(WINDOW_HEIGHT // 2 - 20, cleared_msg["subtitle"][self.current_language], pyxel.COLOR_WHITE, align="center", border_color=pyxel.COLOR_DARK_BLUE)
#                    bonus_text = cleared_msg["bonus"][self.current_language].format(bonus=int(self.score * 0.5))
#                    self.draw_text(WINDOW_HEIGHT // 2, bonus_text, pyxel.COLOR_YELLOW, align="center", border_color=pyxel.COLOR_DARK_BLUE)
#                    self.draw_text(WINDOW_HEIGHT // 2 + 20, cleared_msg["action"][self.current_language], pyxel.COLOR_WHITE, align="center", border_color=pyxel.COLOR_DARK_BLUE)
#
#                    self.draw_difficulty_label()
#                    self.draw_score_and_time()
#
#            
#        elif self.state == GameState.SCORE_DISPLAY:
#            # 画面をクリア
#            pyxel.cls(pyxel.COLOR_GRAY)
#        
#            # パーティクルをリセット
#            self.reset_particles()
#
#            # スコアメッセージを描画
#            score_msg = messages["score_display"]
#            self.draw_text(WINDOW_HEIGHT // 2 - 20, score_msg["title"][self.current_language], pyxel.COLOR_YELLOW, align="center", border_color=pyxel.COLOR_DARK_BLUE)
#            self.draw_text(WINDOW_HEIGHT // 2, f"{int(self.score)}", pyxel.COLOR_YELLOW, align="center", border_color=pyxel.COLOR_DARK_BLUE)
#            self.draw_text(WINDOW_HEIGHT // 2 + 20, score_msg["action"][self.current_language], pyxel.COLOR_WHITE, align="center", border_color=pyxel.COLOR_DARK_BLUE)
#        
#        elif self.state == GameState.HIGH_SCORE_DISPLAY:
#            # 画面をクリア
#            pyxel.cls(pyxel.COLOR_GRAY)
#
#            # ハイスコア表示画面の描画
#            high_score_msg = messages["high_score_display"]
#            self.draw_text(35, high_score_msg["title"][self.current_language], pyxel.COLOR_YELLOW, align="center", border_color=pyxel.COLOR_DARK_BLUE)
#            for i, score in enumerate(self.high_scores):
#                rank = f"{i + 1:>2}"  # 順位を右詰めで整形
#                text = f"{rank}: {score:>6}"  # スコアを右詰めで整形
#                color = pyxel.COLOR_YELLOW if i == self.current_score_rank else pyxel.COLOR_WHITE
#                self.draw_text(60 + i * 12, text, color, align="center", border_color=pyxel.COLOR_DARK_BLUE)
#            self.draw_text(200, high_score_msg["action"][self.current_language], pyxel.COLOR_WHITE, align="center", border_color=pyxel.COLOR_DARK_BLUE)
#
#        # === パーティクル描画 ===
#        self.draw_particles()
#        # スコアポップアップの描画
#        for popup in self.score_popups:
#            popup.draw()

    def draw(self):
        # シェイクのオフセット計算
        shake_x, shake_y = self.calculate_shake_offset()
        pyxel.camera(shake_x, shake_y)
    
        # 画面クリア、stars、トランジション描画
        pyxel.cls(0)
        self.stars.draw()
#        self.transition_effect.draw()
    
        # ステートに基づいて適切な描画処理を呼び出す
        draw_methods = {
            GameState.OPENING: self.draw_opening,
            GameState.DIFFICULTY_SELECTION: self.draw_difficulty_selection,
            GameState.BOARD_GENERATION: self.draw_board_generation,
            GameState.GAME_START: self.draw_gameplay,
            GameState.GAME_MID: self.draw_gameplay,
            GameState.GAME_END: self.draw_gameplay,
            GameState.TIME_UP: self.draw_end_message,
            GameState.NO_MOVES: self.draw_end_message,
            GameState.GAME_CLEARED: self.draw_end_message,
            GameState.SCORE_DISPLAY: self.draw_score_display,
            GameState.HIGH_SCORE_DISPLAY: self.draw_high_score_display,
        }
    
        # 該当ステートの描画メソッドを呼び出し
        if self.state in draw_methods:
            draw_methods[self.state]()
    
        # パーティクルとスコアポップアップの描画
        self.draw_particles()
        for popup in self.score_popups:
            popup.draw()

    def draw_opening(self):
        game_title = translations["titles"]["game_title"][self.current_language]
        for y, text, color in game_title:
            self.draw_text(y, text, color, align="center", border_color=pyxel.COLOR_DARK_BLUE)
    
        instruction_data = translations["instructions"]["intro"][self.current_language]
        base_y = instruction_data["base_y"]
        line_spacing = instruction_data["line_spacing"]
    
        for index, line_data in enumerate(instruction_data["lines"]):
            y = base_y + index * line_spacing
            text = line_data["line"]
            color = line_data["color"]
            self.draw_text(y, text, color, align="left", x_offset=50, border_color=pyxel.COLOR_DARK_BLUE)
    
        is_hovered = self.language_button.is_hovered(pyxel.mouse_x, pyxel.mouse_y)
        self.language_button.draw(is_hovered, draw_text_func=self.draw_text, font=self.font_small)

    def calculate_shake_offset(self):
        if self.shake_timer > 0:
            # 残りタイマーに基づいて非線形減衰を計算
            normalized_timer = self.shake_timer / 20  # 0〜1に正規化
            # 減衰を緩やかに（直線減衰や平方根を使用）
            current_magnitude = self.shake_magnitude * (normalized_timer ** 0.5)  # 緩やかな減衰
            # ランダム性を強化（ノイズのような動きを追加）
            shake_x = random.uniform(-current_magnitude, current_magnitude) + math.sin(pyxel.frame_count * 0.1) * current_magnitude * 0.2
            shake_y = random.uniform(-current_magnitude, current_magnitude) + math.cos(pyxel.frame_count * 0.1) * current_magnitude * 0.2
        else:
            shake_x = 0
            shake_y = 0

        # 結果を返す
        return shake_x, shake_y

    def draw_opening(self):
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
        self.language_button.draw(is_hovered, draw_text_func=self.draw_text, font=self.font_small)

    def draw_difficulty_selection(self):
        """難易度選択画面のタイトルを描画"""
        difficulty_data = translations["titles"]["difficulty_selection"][self.current_language]
    
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

    def draw_board_generation(self):
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

    def draw_gameplay(self):
        # 盤面とボタン・ステータスを描画
        self.draw_game_buttons()
        self.draw_difficulty_label()
        self.draw_grid()
        self.draw_score_and_time()

    def draw_end_message(self):
        self.draw_difficulty_label()
        self.draw_grid()
        self.draw_score_and_time()

        # トランジションが終了した場合のみメッセージを描画
        if self.show_message:
#            # ゲーム状態に応じたメッセージ
#            messages = translations["game_state_messages"]

            if self.state == GameState.TIME_UP:
                # タイムアップ画面の描画
                time_up_msg = translations["game_state_messages"]["time_up"]
                self.draw_text(WINDOW_HEIGHT // 2 - 20, time_up_msg["title"][self.current_language], pyxel.COLOR_RED, align="center", border_color=pyxel.COLOR_DARK_BLUE)
                self.draw_text(WINDOW_HEIGHT // 2, time_up_msg["subtitle"][self.current_language], pyxel.COLOR_WHITE, align="center", border_color=pyxel.COLOR_DARK_BLUE)
            
            elif self.state == GameState.NO_MOVES:
                # 手詰まり画面の描画
                no_moves_msg = translations["game_state_messages"]["no_moves"]
                self.draw_text(WINDOW_HEIGHT // 2 - 20, no_moves_msg["title"][self.current_language], pyxel.COLOR_RED, align="center", border_color=pyxel.COLOR_DARK_BLUE)
                self.draw_text(WINDOW_HEIGHT // 2, no_moves_msg["subtitle"][self.current_language], pyxel.COLOR_WHITE, align="center", border_color=pyxel.COLOR_DARK_BLUE)
            
            elif self.state == GameState.GAME_CLEARED:
                # ゲームクリア画面の描画
                # 画面をクリア
                pyxel.cls(pyxel.COLOR_WHITE)

                cleared_msg = translations["game_state_messages"]["game_cleared"]
                self.draw_text(WINDOW_HEIGHT // 2 - 40, cleared_msg["title"][self.current_language], pyxel.COLOR_YELLOW, align="center", border_color=pyxel.COLOR_DARK_BLUE)
                self.draw_text(WINDOW_HEIGHT // 2 - 20, cleared_msg["subtitle"][self.current_language], pyxel.COLOR_WHITE, align="center", border_color=pyxel.COLOR_DARK_BLUE)
                bonus_text = cleared_msg["bonus"][self.current_language].format(bonus=int(self.score * 0.5))
                self.draw_text(WINDOW_HEIGHT // 2, bonus_text, pyxel.COLOR_YELLOW, align="center", border_color=pyxel.COLOR_DARK_BLUE)
                self.draw_text(WINDOW_HEIGHT // 2 + 20, cleared_msg["action"][self.current_language], pyxel.COLOR_WHITE, align="center", border_color=pyxel.COLOR_DARK_BLUE)

                self.draw_difficulty_label()
                self.draw_score_and_time()

    def draw_score_display(self):
        # 画面をクリア
        pyxel.cls(pyxel.COLOR_GRAY)
    
        # パーティクルをリセット
#        self.reset_particles()

        # スコアメッセージを描画
        score_msg = translations["game_state_messages"]["score_display"]
        self.draw_text(WINDOW_HEIGHT // 2 - 20, score_msg["title"][self.current_language], pyxel.COLOR_YELLOW, align="center", border_color=pyxel.COLOR_DARK_BLUE)
        self.draw_text(WINDOW_HEIGHT // 2, f"{int(self.score)}", pyxel.COLOR_YELLOW, align="center", border_color=pyxel.COLOR_DARK_BLUE)
        self.draw_text(WINDOW_HEIGHT // 2 + 20, score_msg["action"][self.current_language], pyxel.COLOR_WHITE, align="center", border_color=pyxel.COLOR_DARK_BLUE)

    def draw_high_score_display(self):
        # 画面をクリア
        pyxel.cls(pyxel.COLOR_GRAY)

        # ハイスコア表示画面の描画
        high_score_msg = translations["game_state_messages"]["high_score_display"]
        self.draw_text(35, high_score_msg["title"][self.current_language], pyxel.COLOR_YELLOW, align="center", border_color=pyxel.COLOR_DARK_BLUE)
        for i, score in enumerate(self.high_scores):
            rank = f"{i + 1:>2}"  # 順位を右詰めで整形
            text = f"{rank}: {score:>6}"  # スコアを右詰めで整形
            color = pyxel.COLOR_YELLOW if i == self.current_score_rank else pyxel.COLOR_WHITE
            self.draw_text(60 + i * 12, text, color, align="center", border_color=pyxel.COLOR_DARK_BLUE)
        self.draw_text(200, high_score_msg["action"][self.current_language], pyxel.COLOR_WHITE, align="center", border_color=pyxel.COLOR_DARK_BLUE)

    def draw_text(self, y, text, color, align="center", x_offset=0, font=None, border_color=None):
        """BDFフォントを使用してテキストを描画"""
        font = font or self.font_small  # デフォルトで self.font_small を使用
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

    def draw_grid(self):
        cell_size, grid_x_start, grid_y_start = self.get_grid_layout()
    
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                block = self.grid[row][col]
                if block is not None:
                    # block.draw(...) メソッドを呼ぶ形に変更
#                    block.draw(grid_x_start, grid_y_start, cell_size)
                    block.draw()

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
