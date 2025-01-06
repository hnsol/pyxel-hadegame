# title: 8bit BGM Generator (Refactored)
# author: frenchbread (Refactored by hann-solo)
# desc: A refactored version of the Pyxel music auto-generation tool with reusable class structure
# site: https://github.com/shiromofufactory/8bit-bgm-generator
# license: MIT
# version: 0.1

import pyxel as px
import json
from . import bgm_sounds
import os
import logging

logging.basicConfig(level=logging.INFO)

# パラメータ設定一覧
# language: 0 (Japanese), 1 (English)
#    **言語設定**。未使用
# 
# preset: 0, 1, 2, ..., 7
#    **プリセット番号**。事前定義された楽曲のスタイルや設定をまとめたもの。
#
# transpose: -12 ～ +12
#    **転調（半音単位）**。元のキーから上下にどれだけ音を移動させるか。
#
# instrumentation: [0, 1, 2, 3]
#    **編成の種類**。どの楽器を使うかを決定。
#    0: メロディ（reverv） + ベース
#    1: メロディ + ベース + ドラム
#    2: メロディ + ベース + サブ音色
#    3: フル編成（メロディ + ベース + サブ音色 + ドラム）
#
# speed: [360, 312, 276, 240, 216, 192, 168, 156]
#    **テンポ（速度）**。BPMに対応し、値が小さいほどテンポが速くなります。
#    80, 92, 104, 120, 133, 150, 171, 184に相当
#
# chord: 0, 1, 2, ..., 7
#    **コード進行番号**。選択するコード進行の種類を指定（JSONで定義された値）。
#    I-VIIb,     IV-V/IV, I-V-VIb-VIIb, IVM7-IIIM7-VI7-I, 
#    VIm-V-IV-V, VIm-V-I, VIm-II,     , IIIm7-IVM7-V6-VIm9
#
# base: 0, 1, 2, ..., 7
#    **ベースパターン番号**。選択するベースパターンの種類を指定（JSONで定義された値）。
#
# base_highest_note: 26 (固定)
#    **ベースの最高音**。ベース音の許容範囲の最高音を MIDI ノート番号26に固定。
#
# base_quantize: [12, 13, 14, 15]
#    **ベースのクオンタイズ**。音符の長さを何%で演奏するかを指定。
#    75%, 81%, 87%, 93%
#
# drums: 0 (No Drums), 1, 2, ..., 7
#    **ドラムパターン番号**。選択するドラムパターンの種類を指定。
#
# melo_tone: [0, 1, 2, 3, 4, 5]
#    **メロディ音色番号**。メロディチャンネルに使用する音色を指定。
#    Pulse solid, Pulse thin, Pulse soft, Square solid, Square thin (Harp), Square soft (Flute)
#
# sub_tone: [0, 1, 2, 3, 4, 5]
#    **サブ音色番号**。サブチャンネル（和音やハーモニー）に使用する音色を指定。
#
# melo_lowest_note: [28, 29, 30, 31, 32, 33]
#    **メロディの最低音**。メロディ音の許容範囲の最低音を MIDI ノート番号で指定。
#    E2, F2, F#2, G2, G#2, A2
#
# melo_density: [0 (less), 2 (normal), 4 (more)]
#    **メロディの密度**。音符の量（少ない/普通/多い）を設定。
#
# melo_use16: [True, False]
#    **16分音符を使用するか**。`True`で使用する、`False`で使用しない。


SUBMELODY_DIFF = 0
SUB_RHYTHM = [0, None, 0, None, 0, None, 0, None, 0, None, 0, None, 0, None, 0, None]

# 生成する曲の小節数（8固定）
BARS_NUMBERS = 8

# アプリ
class BGMGenerator:
#    BASE_DIR = "assets/bgm_data"  # デフォルトのディレクトリを定義
    BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../assets/bgm_data")

#    def __init__(self, tones_path="assets/bgm_data/tones.json", patterns_path="assets/bgm_data/patterns.json",
#                 generator_path="assets/bgm_data/generator.json", rhythm_path="assets/bgm_data/rhythm.json"):
#        # JSONデータの読み込み
#        self.tones = self._load_json(tones_path)
#        self.patterns = self._load_json(patterns_path)
#        self.generator = self._load_json(generator_path)
#        self.melo_rhythm = self._load_json(rhythm_path)
    def __init__(self, tones_path=None, patterns_path=None, generator_path=None, rhythm_path=None):
        # デフォルトパスを適用
        self.tones_path = tones_path or os.path.join(self.BASE_DIR, "tones.json")
        self.patterns_path = patterns_path or os.path.join(self.BASE_DIR, "patterns.json")
        self.generator_path = generator_path or os.path.join(self.BASE_DIR, "generator.json")
        self.rhythm_path = rhythm_path or os.path.join(self.BASE_DIR, "rhythm.json")

        # デバッグ用ログ
        print(f"Base directory: {self.BASE_DIR}")
        print(f"Tones path: {self.tones_path}")
        print(f"Patterns path: {self.patterns_path}")
        print(f"Generator path: {self.generator_path}")
        print(f"Rhythm path: {self.rhythm_path}")

        # JSONデータの読み込み
        self.tones = self._load_json(self.tones_path)
        self.patterns = self._load_json(self.patterns_path)
        self.generator = self._load_json(self.generator_path)
        self.melo_rhythm = self._load_json(self.rhythm_path)

        # デフォルトパラメータの設定 based on preset 2
        self.default_parm = {
            "preset": 2,
            "transpose": 0,
            "language": 1,
            "base_highest_note": 26, # fix
            "melo_density": 2,
            "speed": 312,
            "chord": 2,
            "base": 1,
            "base_quantize": 15,
            "drums": 0,
            "melo_tone": 5,
            "sub_tone": 5,
            "melo_lowest_note": 30,
            "melo_use16": False,
            "instrumentation": 0,
        }

        self.list_tones = [
            (11, "Pulse solid"),
            (8, "Pulse thin"),
            (2, "Pulse soft"),
            (10, "Square solid"),
            (6, "Square thin (Harp)"),
            (4, "Square soft (Flute)"),
        ]
        self.parm = self.default_parm.copy()  # 呼び出し側で設定可能に
        self.music = None

    @property
    def total_len(self):
        return BARS_NUMBERS * 16

    @property
    def with_submelody(self):
        return self.parm["instrumentation"] in (2, 3)

    @property
    def with_drum(self):
        return self.parm["instrumentation"] in (1, 3)

    def _load_json(self, path):
        """JSONデータをロード"""
        # 基準ディレクトリを取得
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        # フルパスを生成
        full_path = os.path.join(base_path, path)
        
        try:
            with open(full_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
#            print(f"Error: File not found: {full_path}")
            logging.error(f"Error: File not found: {full_path}")
            return {}  # デフォルト値として空の辞書を返す
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {full_path}: {e}")
            return {}  # 不正なJSONデータの場合も空の辞書を返す

    def get_default_parm(self):
        """デフォルトのparmを取得"""
        return self.default_parm.copy()

    def set_parm(self, custom_parm):
        """呼び出し側からparmを設定"""
        self.parm.update(custom_parm)

    def play(self, loop=True):
        """生成済みのBGMを再生"""
        if not self.music:
            print("No music to play. Please generate music first.")
            return
        for ch, sound in enumerate(self.music):
            px.sounds[ch].set(*sound)
            px.play(ch, ch, loop=loop)
        print("Playing music.")

    def stop(self):
        """BGMの再生を停止"""
        px.stop()
        print("Music stopped.")

    def generate_music(self, make_melody=True):
        px.stop()
        parm = self.parm
        print(f"parm: {parm}")
        base = self.generator["base"][parm["base"]]
        drums = self.generator["drums"][parm["drums"]]
        # コードリスト準備
        self.set_chord_lists()
        # バッキング生成
        items = []
        self.base_notes = []
        self.cur_chord_idx = -1
        for loc in range(self.total_len):
            items.append([None for _ in range(19)])
            (chord_idx, _) = self.get_chord(loc)
            if chord_idx > self.cur_chord_idx:
                chord_list = self.chord_lists[chord_idx]
                self.cur_chord_idx = chord_idx
                self.cur_chord_loc = loc
            item = items[loc]
            tick = loc % 16  # 拍(0-15)
            if loc == 0:  # 最初の行（セットアップ）
                item[0] = parm["speed"]  # テンポ
                item[1] = 48  # 4/4拍子
                item[2] = 3  # 16分音符
                item[3] = self.list_tones[parm["melo_tone"]][0]  # メロディ音色
                item[4] = 6  # メロディ音量
                item[5] = 14  # メロディ音長
                item[7] = 7  # ベース音色
                item[8] = 7  # ベース音量
                item[9] = parm["base_quantize"]  # ベース音長
                if self.with_submelody:
                    item[11] = self.list_tones[parm["sub_tone"]][0]
                    item[12] = 4
                    item[13] = 15
                    if self.with_drum:
                        item[15] = 15
                        item[16] = 5
                        item[17] = 15
                elif self.with_drum:
                    item[11] = 15
                    item[12] = 5
                    item[13] = 15
                else:  # リバーブ
                    item[11] = item[3]
                    item[12] = 2
                    item[13] = item[5]

            # ベース音設定
            if not chord_list["repeat"] is None:
                repeat_loc = self.chord_lists[chord_list["repeat"]]["loc"]
                target_loc = repeat_loc + loc - self.cur_chord_loc
                item[10] = items[target_loc][10]
            else:
                pattern = "basic" if loc // 16 < 7 else "final"
                base_str = base[pattern][tick]
                if base_str == ".":
                    base_note = None
                elif base_str == "0":
                    base_note = -1
                else:
                    highest = parm["base_highest_note"]
                    pattern = "basic" if loc // 16 < 7 else "final"
                    base_root = 12 + parm["transpose"] + chord_list["base"]
                    while base_root + 24 > highest:
                        base_root -= 12
                    notes = chord_list["notes_origin"]
                    adjust_list = [0, -1, 1, -2, 2, -3, 3]
                    adjust_idx = 0
                    base_add = {"1": 7, "2": 12, "3": 19, "4": 24}[base_str]
                    while notes:
                        adjust = adjust_list[adjust_idx]
                        base_note = base_root + base_add + adjust
                        tmp = (base_note + parm["transpose"]) % 12
                        # print(notes, tmp, notes[tmp])
                        if notes[(base_note + parm["transpose"]) % 12] in [1, 2, 3]:
                            break
                        adjust_idx += 1
                item[10] = base_note
            self.base_notes.append(base_note)
            # ドラム音設定
            if self.with_drum:
                pattern = "basic" if (loc // 16) % 4 < 3 else "final"
                idx = 18 if self.with_submelody else 14
                drum_str = drums[pattern][tick]
                if drum_str == "0":
                    item[idx] = None
                else:
                    item[idx] = ":" + drum_str
        # メロディー生成
        failure_cnt = 0
        while make_melody:
            self.generate_melody()
            if self.check_melody():
                break
            failure_cnt += 1
            self.set_chord_lists()
            # print("--------失敗---------")
        # print("失敗回数", failure_cnt)
        # メロディ・サブとリバーブの音符を設定
        for loc in range(self.total_len):
            item = items[loc]
            item[6] = self.melody_notes[loc]
            if self.with_submelody:
                item[14] = self.submelody_notes[loc]
            elif not self.with_drum:  # リバーブ
                item[14] = self.melody_notes[
                    (loc + self.total_len - 1) % self.total_len
                ]
        # 完了処理
        self.music = bgm_sounds.compile(items, self.tones, self.patterns)
        self.items = items

    # self.chord_listsを生成
    def set_chord_lists(self):
        chord = self.generator["chords"][self.parm["chord"]]
        self.chord_lists = []
        for progression in chord["progression"]:
            chord_list = {
                "loc": progression["loc"],
                "base": 0,
                "no_root": False,
                "notes": [],
                "notes_origin": [],
                "repeat": progression["repeat"] if "repeat" in progression else None,
            }
            if "repeat" in progression:
                chord_list["base"] = self.chord_lists[progression["repeat"]]["base"]
            if "notes" in progression:
                notes = [int(s) for s in progression["notes"]]
                chord_list["notes_origin"] = notes
                note_chord_cnt = 0
                # ベース音設定
                for idx in range(12):
                    if notes[idx] == 2:
                        chord_list["base"] = idx
                    if notes[idx] in [1, 2, 3]:
                        note_chord_cnt += 1
                chord_list["no_root"] = note_chord_cnt > 3
                # レンジを決める
                if self.with_submelody:
                    chord_list["notes"] = self.make_chord_notes(notes, SUBMELODY_DIFF)
                else:
                    chord_list["notes"] = self.make_chord_notes(notes)
            self.chord_lists.append(chord_list)

    # コードリストの音域設定
    def make_chord_notes(self, notes, tone_up=0):
        parm = self.parm
        note_highest = None
        idx = 0
        results = []
        while True:
            note_type = int(notes[idx % 12])
            note = 12 + idx + parm["transpose"]
            if note >= parm["melo_lowest_note"] + tone_up:
                if note_type in [1, 2, 3, 9]:
                    results.append((note, note_type))
                    if note_highest is None:
                        note_highest = note + 15
            if note_highest and note >= note_highest:
                break
            idx += 1
        return results

    # メロディ生成
    def generate_melody(self):
        self.melody_notes = [-2 for _ in range(self.total_len)]
        self.submelody_notes = [-2 for _ in range(self.total_len)]
        # メインメロディ
        # print("=== MAIN START ===")
        rhythm_main_list = []
        for _ in range(5):
            rhythm_main_list.append(self.get_rhythm_set())
        rhythm_main_list.sort(key=len)
        rhythm_main = rhythm_main_list[self.parm["melo_density"]]
        for loc in range(self.total_len):
            # すでに埋まっていたらスキップ
            if self.melody_notes[loc] != -2:
                continue
            # 1セットの音を追加
            notesets = self.get_next_notes(rhythm_main, loc)
            if notesets is None:  # repeat
                repeat_loc = self.chord_lists[self.chord_list["repeat"]]["loc"]
                target_loc = repeat_loc + loc - self.cur_chord_loc
                repeat_note = self.melody_notes[target_loc]
                self.put_melody(loc, repeat_note, 1)
                repeat_subnote = self.submelody_notes[target_loc]
                self.submelody_notes[loc] = repeat_subnote
            else:
                notesets_len = 0
                for noteset in notesets:
                    self.put_melody(noteset[0], noteset[1], noteset[2])
                    notesets_len += noteset[2]
                self.put_submelody(loc, -2, notesets_len)
        # サブメロディ
        # print("=== SUB START ===")
        rhythm_sub = self.get_rhythm_set(True)
        prev_note_loc = -1
        for loc in range(self.total_len):
            note = self.submelody_notes[loc]
            if not note is None and note >= 0:
                prev_note_loc = loc
                self.prev_note = note
            elif loc - prev_note_loc >= 4 and loc % 4 == 0:
                notesets = self.get_next_notes(rhythm_sub, loc, True)
                if not notesets is None:
                    for noteset in notesets:
                        self.put_submelody(noteset[0], noteset[1], noteset[2])
                    prev_note_loc = loc

    # メロディのリズムを取得
    def get_rhythm_set(self, is_sub=False):
        self.cur_chord_idx = -1  # 現在のコード（self.chord_listsのインデックス）
        self.cur_chord_loc = -1  # 現在のコードの開始位置
        self.is_repeat = False  # リピートモード
        self.chord_list = []
        self.prev_note = -1  # 直前のメロディー音
        self.first_in_chord = True  # コード切り替え後の最初のノート
        results = []
        used16 = False
        while True:
            for bar in range(BARS_NUMBERS):
                if is_sub:
                    pat_line = SUB_RHYTHM
                else:
                    while True:
                        pat_line = self.melo_rhythm[
                            px.rndi(0, len(self.melo_rhythm) - 1)
                        ]
                        # 16分音符回避設定
                        if self.has_16th_note(pat_line):
                            if not self.parm["melo_use16"]:
                                continue
                            used16 = True
                        # 先頭が持続音のものは避ける（暫定）
                        if not pat_line[0] is None:
                            break
                for idx, pat_one in enumerate(pat_line):
                    loc = bar * 16 + idx
                    if not pat_one is None:
                        results.append((loc, pat_one))
            if is_sub or not self.parm["melo_use16"] or used16:
                break
        for _ in range(2):
            results.append((self.total_len, -1))
        return results

    # 16分音符が含まれるか
    def has_16th_note(self, line):
        prev_str = None
        for i in line:
            if i == 0 and prev_str == 0:
                return True
            prev_str = i
        return False

    def get_next_notes(self, rhythm_set, loc, is_sub=False):
        pat = None
        for pat_idx, rhythm in enumerate(rhythm_set):
            if loc == rhythm[0]:
                pat = rhythm[1]
                break
            elif loc < rhythm[0]:
                break
        note_len = rhythm_set[pat_idx + 1][0] - loc
        # コード切替判定
        change_code = False
        premonitory = False
        (next_chord_idx, next_chord_loc) = self.get_chord(loc)
        if next_chord_idx > self.cur_chord_idx:
            change_code = True
        elif not self.is_repeat and loc + note_len > next_chord_loc:
            (next_chord_idx, next_chord_loc) = self.get_chord(loc + note_len)
            change_code = True
            premonitory = True
            # print(loc, note_len, "先取音発生")
        if change_code:
            self.chord_list = self.chord_lists[next_chord_idx]
            self.cur_chord_idx = next_chord_idx
            self.cur_chord_loc = loc
            self.first_in_chord = True
            self.is_repeat = not self.chord_list["repeat"] is None
        # 小節単位の繰り返し
        if self.is_repeat:
            # print(loc, "repeat")
            return [] if premonitory else None
        if pat == -1:  # 休符
            # print(loc, "休符")
            return [(loc, -1, note_len)]
        # 初期処理
        self.chord_notes = self.chord_list["notes"]
        next_idx = self.get_target_note(is_sub, loc)
        # 連続音を何個置けるか（コード維持＆４分音符以下）
        following = []
        prev_loc = loc
        while True:
            pat_loc = rhythm_set[pat_idx + 1 + len(following)][0]
            no_next = pat_loc >= next_chord_loc or pat_loc - prev_loc > 4
            if not following or not no_next:
                following.append((prev_loc, pat_loc - prev_loc))
            if no_next:
                break
            prev_loc = pat_loc
        loc, note_len = following[0]
        # 直前のメロディーのインデックスを今のコードリストと照合(構成音から外れていたらNone)
        cur_idx = None
        if not premonitory:
            for idx, note in enumerate(self.chord_notes):
                if self.prev_note == note[0]:
                    cur_idx = idx
                    break
        # 初音（直前が休符 or コード構成音から外れた場合は、コード構成音を取得）
        if self.prev_note < 0 or cur_idx is None:
            # print(loc, "初音")
            note = self.chord_notes[next_idx][0]
            return [(loc, note, note_len)]
        # 各種変数準備
        results = []
        diff = abs(next_idx - cur_idx)
        direction = 1 if next_idx > cur_idx else -1
        # 刺繍音/同音
        if diff == 0:
            cnt = len(following) // 2
            if cnt and px.rndi(0, 1) and not is_sub:
                # print(loc, "刺繍音", cnt * 2)
                for i in range(cnt):
                    while next_idx == cur_idx:
                        next_idx = self.get_target_note()
                    direction = 1 if next_idx > cur_idx else -1
                    # print(cur_idx, next_idx, self.chord_notes)
                    note = self.chord_notes[cur_idx + direction][0]
                    prev_note = self.prev_note
                    note_follow = following[i * 2]
                    results.append((note_follow[0], note, note_follow[1]))
                    note_follow = following[i * 2 + 1]
                    results.append((note_follow[0], prev_note, note_follow[1]))
                return results
            else:
                # print(loc, "同音")
                return [(loc, self.prev_note, note_len)]
        # ステップに必要な長さが足りない/跳躍量が大きい/割合で跳躍音採用
        if abs(next_idx - cur_idx) > len(following):
            note = self.chord_notes[next_idx][0]
            # print(loc, "跳躍")
            return [(loc, note, note_len)]
        # ステップ
        # print(loc, "ステップ", abs(next_idx - cur_idx))
        i = 0
        while next_idx != cur_idx:
            cur_idx += direction
            note = self.chord_notes[cur_idx][0]
            note_follow = following[i]
            results.append((note_follow[0], note, note_follow[1]))
            i += 1
        return results

    # メロディ検査（コード中の重要構成音が入っているか）
    def check_melody(self):
        cur_chord_idx = -1
        need_notes_list = []
        for loc in range(self.total_len):
            (next_chord_idx, _) = self.get_chord(loc)
            if next_chord_idx > cur_chord_idx:
                # need_notes_listが残っている＝重要構成音が満たされていない
                if len(need_notes_list) > 0:
                    return False
                cur_chord_idx = next_chord_idx
                notes_list = self.chord_lists[cur_chord_idx]["notes"]
                need_notes_list = []
                for chord in notes_list:
                    note = chord[0] % 12
                    if chord[1] == 1 and not note in need_notes_list:
                        need_notes_list.append(note)
            note = self.melody_notes[loc]
            if not note is None and note >= 0 and note % 12 in need_notes_list:
                need_notes_list.remove(note % 12)
            if self.with_submelody:
                note = self.submelody_notes[loc]
                if not note is None and note >= 0 and note % 12 in need_notes_list:
                    need_notes_list.remove(note % 12)
        return True

    # コードリスト取得（locがchords_listsの何番目のコードか、次のコードの開始位置を返す）
    def get_chord(self, loc):
        chord_lists_cnt = len(self.chord_lists)
        next_chord_loc = 16 * BARS_NUMBERS
        for rev_idx in range(chord_lists_cnt):
            idx = chord_lists_cnt - rev_idx - 1
            if loc >= self.chord_lists[idx]["loc"]:
                break
            else:
                next_chord_loc = self.chord_lists[idx]["loc"]
        return idx, next_chord_loc

    # 跳躍音の跳躍先を決定
    def get_target_note(self, is_sub=False, loc=None):
        no_root = self.first_in_chord or self.chord_list["no_root"]
        allowed_types = [1, 3] if no_root else [1, 2, 3]
        notes = self.get_subnotes(loc) if is_sub else self.chord_list["notes"]
        # 跳躍先候補が1オクターブ超のみの場合、最低音を選択
        hightest_note = 0
        hightest_idx = 0
        for idx, noteset in enumerate(notes):
            if noteset[0] > hightest_note and noteset[1] in allowed_types:
                hightest_note = noteset[0]
                hightest_idx = idx
        if self.prev_note - hightest_note > 12:
            return hightest_idx
        while True:
            idx = px.rndi(0, len(notes) - 1)
            if not notes[idx][1] in allowed_types:
                continue
            note = notes[idx][0]
            if self.prev_note >= 0:
                diff = abs(self.prev_note - note)
                if diff > 12:
                    continue
                factor = diff if diff != 12 else diff - 6
                # 近い音ほど出やすい（オクターブ差は補正、サブはそうではない）
                if px.rndi(0, 15) < factor and not is_sub:
                    continue
            return idx

    # メロディのトーンを配置
    def put_melody(self, loc, note, note_len=1):
        for idx in range(note_len):
            self.melody_notes[loc + idx] = note if idx == 0 else None
        if note is not None:
            self.prev_note = note
            self.first_in_chord = False

    # サブメロディのトーンを配置
    def put_submelody(self, loc, note, note_len=1):
        master_note = None
        subnote = note
        master_loc = loc
        while master_loc >= 0:
            master_note = self.melody_notes[master_loc]
            if not master_note is None and master_note >= 0:
                prev_note = master_note if note == -2 else note
                subnote = self.search_downer_note(prev_note, master_note, master_loc)
                break
            master_loc -= 1
        prev_subnote = None
        for idx in range(note_len):
            if (
                not self.melody_notes[loc + idx] is None
                and self.melody_notes[loc + idx] >= 0
            ):
                master_note = self.melody_notes[loc + idx]
            duplicate = (
                not master_note is None
                and not subnote is None
                and (abs(subnote > master_note) < 3)
            )
            if duplicate:
                subnote = self.search_downer_note(subnote, master_note, loc + idx)
            self.submelody_notes[loc + idx] = (
                subnote if subnote != prev_subnote else None
            )
            prev_subnote = subnote

    # メロの下ハモを探す
    def search_downer_note(self, prev_note, master_note, loc):
        if self.with_submelody and master_note >= 0:
            notes = self.get_subnotes(loc)
            if not prev_note is None and abs(prev_note - master_note) >= 3:
                return prev_note
            cur_note = master_note - 3
            while cur_note >= self.parm["melo_lowest_note"]:
                for n in notes:
                    if n[0] == cur_note and n[1] in [1, 2, 3]:
                        return cur_note
                cur_note -= 1
        return -1

    # サブパートの許容音域を取得
    def get_subnotes(self, start_loc):
        master_note = None
        base_note = None
        loc = start_loc
        while master_note is None or base_note is None:
            if master_note is None and self.melody_notes[loc] != -1:
                master_note = self.melody_notes[loc]
            if base_note is None and self.base_notes[loc] != -1:
                base_note = self.base_notes[loc]
            loc = (loc + self.total_len - 1) % self.total_len
        notes = self.chord_list["notes_origin"].copy()
        results = []
        has_important_tone = False
        idx = 0
        while notes:
            note_type = notes[idx % 12]
            if note_type in [1, 2, 3, 9]:
                note = 12 + idx + self.parm["transpose"]
                # ベース+3〜メイン-3までを許可する
                if note > master_note - 3 and has_important_tone:
                    break
                if note >= base_note + 3:
                    results.append((note, note_type))
                    if note_type in [1, 3]:
                        has_important_tone = True
            idx += 1
        self.chord_notes = results
        return results

