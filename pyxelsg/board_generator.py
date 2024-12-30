import random

class BoardGenerator:
    def generate_filled_solvable_board(self, rows, cols, colors):
        """
        正方形または長方形の盤面を完全に埋めて解けるように逆生成
        """
        board = [[0 for _ in range(cols)] for _ in range(rows)]
        steps = []

        while not self.is_board_filled(board):
            x = random.randint(0, cols - 1)
            y = random.randint(0, rows - 1)
            group = self.generate_random_shape(x, y, rows, cols)
#            color = random.randint(1, colors)
            color = random.randint(0, colors-1)

            for gx, gy in group:
                if board[gy][gx] == 0:
                    board[gy][gx] = color
                    steps.append((gx, gy, color))

        for x, y, color in reversed(steps):
            board[y][x] = color

        return board

    def is_board_filled(self, board):
        """
        盤面が完全に埋まっているかを確認
        """
        return all(0 not in row for row in board)

    def generate_random_shape(self, x, y, rows, cols):
        """
        ランダムな形状を生成（境界チェックと特定形状を優先）
        """
        predefined_shapes = [
            [(0, 0), (1, 0), (0, 1), (1, 1)],
            [(0, 0), (1, 0), (2, 0), (1, 1)],
            [(0, 0), (1, 0), (1, 1)],
            [(0, 0), (1, 0), (0, 1)],
        ]

        if random.random() < 0.25:
            shape_offsets = random.choice(predefined_shapes)
        else:
            shape_offsets = [(0, 0)]
#            for _ in range(random.randint(2, 5)):
#            for _ in range(random.randint(2, max(rows, cols))):
            for _ in range(random.randint(2, min(rows, cols))):
                dx, dy = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])
                nx, ny = shape_offsets[-1][0] + dx, shape_offsets[-1][1] + dy
                if (nx, ny) not in shape_offsets and 0 <= x + nx < cols and 0 <= y + ny < rows:
                    shape_offsets.append((nx, ny))

        return [(x + dx, y + dy) for dx, dy in shape_offsets if 0 <= x + dx < cols and 0 <= y + dy < rows]

    def print_board(board):
        """
        盤面を整形して表示
        """
        for row in board:
            print(" ".join(str(cell) if cell != 0 else "." for cell in row))

