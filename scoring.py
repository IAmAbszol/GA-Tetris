import random
from math import e

import copy

# global params
# params:
# data - (board, rows, cols)
# board - Passed in as shadow_board
# stone - (stone, stone_x, stone_y)
# gene - constant passed in

class Scoring:
    def __init__(self, data):
        self.board = data[0]
        self.rows = data[1]
        self.cols = data[2]

    def get_score(self, stone, genes):
        heights = self.get_heights()
        return self.line_clear_score(stone, genes[0]) + self.hole_count_score(stone, genes[1]) + \
                self.blocking_score(stone, genes[2]) + self.touching_score(stone, genes[3], genes[4]) + \
                self.bumpiness(heights, genes[5]) + self.deepest_pit(heights, genes[6])


    def get_heights(self):
        heights = [0] * self.cols
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] > 0:
                    if heights[c] == 0:
                        heights[c] = (self.rows - r)
        return heights


    def line_clear_score(self, stone, gene):
        desired_rows = [int(i) for i in range((stone[2] - 1), (stone[2] + len(stone[0]) - 1))]
        row_histogram = [0] * len(desired_rows)
        for index, row in enumerate(desired_rows):
            row_histogram[index] = sum(1 for x in self.board[row] if x > 0)
        return gene * max(row_histogram)


    def hole_count_score(self, stone, gene):
        hole_score = 0
        for row in range(self.rows):
            if sum(1 for x in self.board[row] if x > 0) > 0:
                hole_score += sum(1 for x in self.board[row] if x == 0)
        return gene * hole_score

    def blocking_score(self, stone, gene):
        score = 0
        desired_rows = [int(i) for i in range((stone[2] - 1), (stone[2] + len(stone[0]) - 1))]
        id = max(max(stone[0]))
        for rindex, row in enumerate(desired_rows):
            for cindex, col in enumerate(self.board[row]):
                if self.board[row][cindex] == id:
                    eval_row = row
                    while not eval_row == 21:
                        eval_row += 1
                        if self.board[eval_row][cindex] == id:
                            break
                        if self.board[eval_row][cindex] == 0:
                            score += 1
        return gene * score

    def bumpiness(self, heights_histogram, gene):
        bumpiness_histogram = []
        for index in range(0, len(heights_histogram) - 1):
            bumpiness_histogram.append(abs(heights_histogram[index] - heights_histogram[index+1]))
        return gene * sum(bumpiness_histogram)

    def touching_score(self, stone, geneBlock, geneBorder):
        desired_rows = [int(i) for i in range((stone[2] - 1), (stone[2] + len(stone[0]) - 1))]
        id = max(max(stone[0]))
        touch_score = 0
        border_score = 0
        for index, row in enumerate(desired_rows):
            for idx, col in enumerate(self.board[row]):
                if col == id:
                    # eval LRD
                    eval_idx = idx
                    if idx > 0:
                        eval_idx -= 1
                        if self.board[row][eval_idx] > 0 and not self.board[row][eval_idx] == id:
                            touch_score += 1
                    else:
                        border_score += 1

                    eval_idx = idx
                    if idx < (self.cols - 1):
                        eval_idx += 1
                        if self.board[row][eval_idx] > 0 and not self.board[row][eval_idx] == id:
                            touch_score += 1
                    else:
                        border_score += 1

                    if not row == 21:
                        eval_row = (row + 1)
                        if self.board[eval_row][idx] > 0 and not self.board[eval_row][idx] == id:
                            touch_score += 1
                    else:
                        border_score += 1
        return geneBlock * touch_score + geneBorder * border_score

    def deepest_pit(self, heights_histogram, gene):
        return gene * (max(heights_histogram) - min(heights_histogram))