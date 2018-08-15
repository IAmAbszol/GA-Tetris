# Due to pygame not accepting for a multiple instances of the TetrisApp
# I decided to create my own Tetris game that's a simplified hacked up
# version of the tetris.py Tetris game.
# Display can be enabled for simple testing
# but is advised to disable it during
# training to maximize throughput

import random
from math import e
from copy import deepcopy

cols = 10
rows = 22
sleep = 500 # ms?

tetris_shapes = [
    [[1, 1, 1],
     [0, 1, 0]],

    [[0, 2, 2],
     [2, 2, 0]],

    [[3, 3, 0],
     [0, 3, 3]],

    [[4, 0, 0],
     [4, 4, 4]],

    [[0, 0, 5],
     [5, 5, 5]],

    [[6, 6, 6, 6]],

    [[7, 7],
     [7, 7]]
]

# build a deck of 1000 pieces, all going to be the same for every game created (better testing for now)
deck = [tetris_shapes[random.randrange(len(tetris_shapes))] for i in range(10000)]

def rotate_clockwise(shape):
    return [[shape[y][x]
             for y in range(len(shape))]
            for x in range(len(shape[0]) - 1, -1, -1)]


def check_collision(board, shape, offset):
    off_x, off_y = offset
    for cy, row in enumerate(shape):
        for cx, cell in enumerate(row):
            try:
                if cell and board[cy + off_y][cx + off_x]:
                    return True
            except IndexError:
                return True
    return False

def remove_row(board, row):
    del board[row]
    return [[0 for i in range(cols)]] + board


def join_matrixes(mat1, mat2, mat2_off):
    off_x, off_y = mat2_off
    for cy, row in enumerate(mat2):
        for cx, val in enumerate(row):
            mat1[cy + off_y - 1][cx + off_x] += val
    return mat1


def new_board():
    board = [[0 for x in range(cols)]
             for y in range(rows)]
    # creates row of just 1's, helps find floor from collision
    board += [[1 for x in range(cols)]]
    return board

class TetrisGame():
    def __init__(self, caller, display=False):
        self.deck = deepcopy(deck)
        self.next_stone = self.draw()
        self.display = display
        self.caller = caller
        self.init_game()

    def draw(self):
        if not self.deck:
            print("Game has concluded")
            return self.score
        return self.deck.pop(0)

    def new_stone(self):
        self.stone = self.next_stone[:]
        self.next_stone = self.draw()
        self.stone_x = int(cols/2 - len(self.stone[0]) /2)
        self.stone_y = 0

        if check_collision(self.board,
                           self.stone,
                           (self.stone_x, self.stone_y)):
            self.gameover = True

    def init_game(self):
        self.board = new_board()
        self.level = 1
        self.score = 0
        self.lines = 0

    def display_board(self, board):
        if self.display:
            print("Displaying {}".format(self.caller))
            for r in range(len(board)):
                for c in range(len(board[r])):
                    print("{} ".format(board[r][c]), end="")
                print("")

    def add_cl_lines(self, n):
        linescores = [0, 40, 100, 300, 1200]
        self.lines += n
        self.score += linescores[n] * self.level
        if self.lines >= self.level * 6:
            self.level += 1

    def move(self, delta_x):
        if not self.gameover:
            new_x = self.stone_x + delta_x
            if new_x < 0:
                new_x = 0
            if new_x > cols - len(self.stone[0]):
                new_x = cols - len(self.stone[0])
            if not check_collision(self.board,
                                   self.stone,
                                   (new_x, self.stone_y)):
                self.stone_x = new_x

    def drop(self, manual, evaluating=False):
        if not self.gameover:
            self.score += 1 if manual else 0
            self.stone_y += 1
            if check_collision(self.board,
                               self.stone,
                               (self.stone_x, self.stone_y)):
                self.board = join_matrixes(self.board,
                                           self.stone,
                                           (self.stone_x, self.stone_y))
                self.new_stone()
                cleared_rows = 0
                while True:
                    for i, row in enumerate(self.board[:-1]):
                        if 0 not in row:
                            self.board = remove_row(self.board, i)
                            cleared_rows += 1
                            break
                    else:
                        break
                if not evaluating:
                    self.add_cl_lines(cleared_rows)
                return True
        return False

    def insta_drop(self):
        if not self.gameover:
            while (not self.drop(True)):
                pass

    def rotate_stone(self):
        if not self.gameover:
            new_stone = rotate_clockwise(self.stone)
            if not check_collision(self.board,
                                   new_stone,
                                   (self.stone_x, self.stone_y)):
                self.stone = new_stone

    def run(self, genes, draw):
        # AI will not actually use keyboard presses
        key_actions = {
            'LEFT': lambda : self.move(-1),
            'RIGHT': lambda : self.move(1),
            'UP': lambda : self.rotate_stone,
            'RETURN': lambda : self.insta_drop
        }

        self.gameover = False
        self.new_stone()
        while True:
            if self.gameover:
                return self.score
            else:
                self.analyze_board(genes)

                draw(self.caller, self.board, genes, self.score)

    # taken from my previous attempt, its pretty solid =D
    def analyze_board(self, genes):
        # copy info for eval
        save_board = deepcopy(self.board)
        save_score = deepcopy(self.score)
        save_lines = deepcopy(self.lines)
        save_level = deepcopy(self.level)
        eval_x = self.stone_x
        eval_y = self.stone_y
        instructions = []
        best = {'rotation': 0, 'index': 0, 'score': 0}
        for i in range(cols):
            self.move(-1)
        for rotation in range(4):
            for movement in range(cols):
                new_score = self.evaluate_decision(self.board, genes)
                if new_score > int(best['score']):
                    best['rotation'] = int(rotation)
                    best['index'] = int(movement)
                    best['score'] = new_score
                # order of operations, stone wasn't moving due to already colliding with bottom before reset
                self.stone_y = eval_y
                self.move(1)
            for i in range(cols):
                self.move(-1)
            self.rotate_stone()
        instructions.append(best['rotation'])
        instructions.append(best['index'])
        self.board = deepcopy(save_board)
        self.score = deepcopy(save_score)
        self.lines = deepcopy(save_lines)
        self.level = deepcopy(save_level)
        self.gameover = False
        self.stone_x = eval_x
        self.position_and_drop(instructions)

    @staticmethod
    def level_value_assignment(row):
        return rows * e ** -row

    # evaluation function focuses on
    # 0. Line clear potential --> Evaluating based on number of holes left after succession and how close
    #    it is to clearing. Idea to use for evaluation is a histogram
    # 1. Number of holes --> Evaluating ONLY ON LINES WITH BLOCKS the number of holes, more = bad.
    #    Uses level evaluation equation to score appropriately
    # 2. Cumulative height --> Taking sum difference of heights based on histogram representation of figure.
    # Testing revision: Restrict values [Decimal -> (positive, negative)]
    # 3. Reward min gap coverage based on where the piece is to be evaluated
    def evaluate_decision(self, board, genes):
        score = 0
        shadow_board = deepcopy(board)
        for i in range(0, rows):
            if not check_collision(shadow_board, self.stone, (self.stone_x, self.stone_y)):
                self.stone_y += 1
            else:
                join_matrixes(shadow_board, self.stone, (self.stone_x, self.stone_y))

        row_histogram = [0] * rows
        hole_score = 0
        for i in range((rows-1), -1, -1):
            # constraint 0
            # start at rows, iterate to 0 (n-1)-->(n-(-1)) = n+1 where n was 0, -1 to decrement third parameter
            if sum(1 for x in shadow_board[i] if x > 0) > 0:
                row_histogram[i] = sum(1 for x in shadow_board[i] if x > 0)
            # constraint 1
            # sum all holes on rows with blocks in them
            if sum(1 for x in shadow_board[i] if x > 0) > 0:
                hole_score += sum(1 for x in shadow_board[i] if x == 0) * \
                              genes[1] if genes[1] <= 0 else -genes[1] * self.level_value_assignment(i)
        score += max(row_histogram) * genes[0] if genes[0] >= 0 else -genes[0] + hole_score
        # constraint 2
        height_histogram = [0] * cols
        for r in range(rows):
            for c in range(cols):
                if shadow_board[r][c] > 0:
                    if height_histogram[c] == 0:
                        height_histogram[c] = (rows - r)
        score += max(height_histogram) * genes[2] if genes[2] <= 0 else -genes[2]
        # constraint 3
        # test to see if row(s) found have the desired evaluation block
        '''
        desired_rows = [int(i) for i in range((self.stone_y - 1), (self.stone_y + len(self.stone) - 1))]
        gap_scores = [0] * len(desired_rows)
        id = max(max(self.stone))
        begin_reading = False
        for index, row in enumerate(desired_rows):
            if sum(1 for x in shadow_board[row] if x > 0 and x != id) > 0:
                print("")
            else:
                # empty row besides our stone
                # calculate favored side
                what_side = int(cols - self.stone_x)
                print("Right Side" if what_side < (cols / 2) else "Left Side")
                if what_side < cols / 2:
                    for x in shadow_board[row]:
                        if x == id and not begin_reading:
                            begin_reading = True
                            continue
                        if x != id and begin_reading:
                            gap_scores[index] += 1
                else:
                    for x in shadow_board[row]:
                        if x != id:
                            gap_scores[index] += 1
                        else:
                            break

        score += (cols - sum(gap_scores))
        '''
        #self.display_board(shadow_board)
        #print("Scored : {}".format(score))
        #print("Stone_x: {}\tStone_y: {}\tStone_height?: {}".format(self.stone_x, self.stone_y, len(self.stone)))
        return score

    def position_and_drop(self, instructions):
        # piece should be at neutral position
        for i in range(int(instructions[0])):
            self.rotate_stone()
        requiredMoves = int(instructions[1]) - self.stone_x
        if requiredMoves < 0:
            while requiredMoves is not 0:
                self.move(-1)
                requiredMoves += 1
        elif requiredMoves > 0:
            while requiredMoves is not 0:
                self.move(1)
                requiredMoves -= 1
        self.insta_drop()

'''
if __name__ == '__main__':
    App = TetrisGame("Hello", display=True)
    App.run([5, -1, -4, 3])
'''