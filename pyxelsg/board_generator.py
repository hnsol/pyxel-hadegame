import random
from collections import deque
import time

class BoardGenerator:
    def __init__(self, max_tries=1000):
        """
        max_tries: ランダム生成→判定を繰り返す最大回数
        """
        self.max_tries = max_tries
        self.EMPTY = -1  # 空セルの表現

    def generate_filled_solvable_board(self, rows, cols, colors, timeout=3):
        """
        1) 大きめブロックを意図的に作る方式で盤面をランダム生成
        2) 解ソルバでチェック
        3) 解けたら返す
        """
        start_time = time.time()  # 処理開始時刻
        last_board = None  # 最後に生成した盤面

        for i in range(self.max_tries):
            if time.time() - start_time > timeout:  # タイムアウトチェック
                print(f"Debug: Timeout reached after {timeout} seconds.")
                return last_board
            if i % 1 == 0:
                print(f"Debug: Attempt {i}")
#                print(f"Debug: rows min max {rows} {round(rows/5)} {int(rows/2)}")
                print(f"Debug: rows min max {rows} {round(rows/7)} {int(rows/2)}")
            board = self._generate_blocky_board(
                rows, cols, colors,
#                min_block_size=round(rows / 5),
#                min_block_size=1,
                min_block_size=round(rows / 7),
#                max_block_size=int(rows / 1.8)
                max_block_size=min(2, int(rows / 2))
            )
            last_board = board

            if self._is_solvable(board, start_time, timeout):  # タイムアウト対応版
                return board
    
        print("Debug: Max tries reached.")
        return last_board

    def _generate_blocky_board(self, rows, cols, colors,
                               min_block_size=3, max_block_size=8):
        """
        「大きめブロックを意図的に作る」ランダム生成。
        盤面をすべて埋めて返す。
        """
        # まずは空ボードを作る
        board = [[self.EMPTY for _ in range(cols)] for _ in range(rows)]

        # 空セルがある限り、大きめブロックを作って埋めていく
        while True:
            empty_cells = [(r, c) for r in range(rows) for c in range(cols)
                           if board[r][c] == self.EMPTY]

            if not empty_cells:
                # 全部埋まったら終了
                break

            start_r, start_c = random.choice(empty_cells)

            # ブロックサイズをランダムに決める
            block_size = random.randint(min_block_size, max_block_size)

            # 同色ブロックを形成するための「候補セル」一覧を生成
            # BFSやランダムウォークなどで block_size 個をなるべく確保
            group = self._make_random_block(board, start_r, start_c,
                                            block_size, rows, cols)

            # 実際に生成された group が 1 個 (最小) の場合もある
            # → group のサイズがあまりに小さければ適宜補う or そのまま
            color = random.randint(0, colors - 1)

            # groupのセルを同色で塗る
            for (r, c) in group:
                board[r][c] = color

        return board

    def _make_random_block(self, board, start_r, start_c,
                           desired_size, rows, cols):
        """
        空きセルから連続する領域をなるべく desired_size 個確保する。
        BFS/DFS の変形で「拡張候補をランダムに加える」イメージ。
        """
        # 既に埋まっている場所はスキップ
        if board[start_r][start_c] != self.EMPTY:
            return [(start_r, start_c)]

        group = [(start_r, start_c)]
        visited = set(group)
        queue = deque([ (start_r, start_c) ])

        while queue and len(group) < desired_size:
            r, c = queue.popleft()
            # 上下左右からランダムに選んで順番を変える
            directions = [(1,0),(-1,0),(0,1),(0,-1)]
            random.shuffle(directions)

            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    if board[nr][nc] == self.EMPTY:
                        if (nr, nc) not in visited:
                            visited.add((nr, nc))
                            group.append((nr, nc))
                            queue.append((nr, nc))
                            # 必要な数になったら終了
                            if len(group) >= desired_size:
                                break

        return group

    # --------------------------------------------------
    #  以下は「ソルバ (クリア可能性チェック)」のロジック
    #  大きい盤面だと時間がかかるので、メモ化など工夫が推奨
    # --------------------------------------------------

    def _is_solvable(self, board, start_time, timeout):
        """
        この盤面が最後まで消せるかどうかを判定する（簡易版）。
        必要に応じてメモ化を入れると高速化できます。
        """
        # すぐ済む軽いケース向けの簡易実装。
        # 大きいサイズ・色数5などでは計算量が跳ね上がるため注意。
        memo = {}
        board_key = self._board_to_key(board)
        return self._is_solvable_impl(board, memo, board_key, start_time, timeout)

#    def _is_solvable_impl(self, board, memo, board_key):
#        if self._is_all_empty(board):
#            return True
#        if board_key in memo:
#            return memo[board_key]
#
#        groups = self._find_groups(board)
#        if not groups:
#            # 消せる塊がないのに空でない → 解けない
#            memo[board_key] = False
#            return False
#
#        for group in groups:
#            new_board = self._remove_group(board, group)
#            self._apply_gravity(new_board)
#            self._apply_compression(new_board)
#            new_key = self._board_to_key(new_board)
#            if self._is_solvable_impl(new_board, memo, new_key):
#                memo[board_key] = True
#                return True
#
#        memo[board_key] = False
#        return False

    def _is_solvable_impl(self, board, memo, board_key, start_time, timeout, timeout_flag=[False]):
        if time.time() - start_time > timeout:  # タイムアウトチェック
            if not timeout_flag[0]:  # 初めてタイムアウトが発生した場合のみプリント
                print("Debug: Timeout reached inside _is_solvable_impl.")
                timeout_flag[0] = True  # フラグを立てる
            return False
    
        if self._is_all_empty(board):  # 盤面が空かチェック
            return True
    
        if board_key in memo:  # メモ化チェック
            return memo[board_key]
    
        groups = self._find_groups(board)
        if not groups:
            memo[board_key] = False
            return False
    
        for group in groups:
            new_board = self._remove_group(board, group)
            self._apply_gravity(new_board)
            self._apply_compression(new_board)
            new_key = self._board_to_key(new_board)
            if self._is_solvable_impl(new_board, memo, new_key, start_time, timeout):
                memo[board_key] = True
                return True

        memo[board_key] = False
        return False

    def _board_to_key(self, board):
        """
        盤面をタプルに変換して辞書キー化。
        """
        return tuple(tuple(row) for row in board)

    def _find_groups(self, board):
        """
        2つ以上の同色連結塊を一覧で返す。
        """
        rows = len(board)
        cols = len(board[0])
        visited = [[False]*cols for _ in range(rows)]
        groups = []

        for r in range(rows):
            for c in range(cols):
                color = board[r][c]
                if color == self.EMPTY or visited[r][c]:
                    continue
                # BFS/DFSで連結成分を探す
                group = []
                queue = deque([(r, c)])
                visited[r][c] = True

                while queue:
                    rr, cc = queue.popleft()
                    group.append((rr, cc))
                    for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
                        nr, nc = rr+dr, cc+dc
                        if 0 <= nr < rows and 0 <= nc < cols:
                            if not visited[nr][nc] and board[nr][nc] == color:
                                visited[nr][nc] = True
                                queue.append((nr, nc))

                if len(group) >= 2:
                    groups.append(group)

        return groups

    def _remove_group(self, board, group):
        """
        groupのセルを消去した新しい盤面を返す。
        """
        import copy
        new_board = copy.deepcopy(board)
        for (r, c) in group:
            new_board[r][c] = self.EMPTY
        return new_board

    def _apply_gravity(self, board):
        rows = len(board)
        cols = len(board[0])
        for c in range(cols):
            stack = []
            for r in range(rows-1, -1, -1):
                if board[r][c] != self.EMPTY:
                    stack.append(board[r][c])
            for r in range(rows-1, -1, -1):
                if stack:
                    board[r][c] = stack.pop(0)
                else:
                    board[r][c] = self.EMPTY

    def _apply_compression(self, board):
        rows = len(board)
        cols = len(board[0])
        write_col = 0
        for read_col in range(cols):
            col_empty = True
            for r in range(rows):
                if board[r][read_col] != self.EMPTY:
                    col_empty = False
                    break
            if not col_empty:
                if write_col != read_col:
                    for r in range(rows):
                        board[r][write_col] = board[r][read_col]
                write_col += 1

        # 残りを空列に
        for col in range(write_col, cols):
            for r in range(rows):
                board[r][col] = self.EMPTY

    def _is_all_empty(self, board):
        for row in board:
            for cell in row:
                if cell != self.EMPTY:
                    return False
        return True

    @staticmethod
    def print_board(board):
        """
        簡易表示用。EMPTY は '.' などで表示。
        """
        for row in board:
            print(" ".join('.' if cell < 0 else str(cell) for cell in row))
        print()


if __name__ == "__main__":
#    rows, cols, colors = 6, 8, 5
#    rows, cols, colors = 5, 5, 3
#    rows, cols, colors = 6, 10, 4
#    rows, cols, colors = 8, 12, 5
    rows, cols, colors = 9, 15, 5
#    rows, cols, colors = 10, 18, 5
    generator = SameGameBoardGenerator(max_tries=200)
    board = generator.generate_filled_solvable_board(rows, cols, colors)

    if board is not None:
        print("Generated solvable board:")
        generator.print_board(board)
    else:
        print("No solvable board found within max_tries.")
