import datetime
import math
import random
import unittest
from itertools import chain

import genetic


def get_fitness(genes, grid):
    score = 0
    for i in range(0, (grid[0] * grid[1])):
        if i > 0 and genes[i - 1] == 1 and genes[i] == 1:
            score += 10
        else:
            score -= (i * 2.5)
        p, n = countPositivesAndNegatives(genes, i, grid)
        score += (3 * p)
        score += (-2 * n)

    for i in range(0, grid[1]):
        score += sum(1 for _ in range((grid[0] * i), (grid[0] * i) + (grid[0] - 1)) if genes[i] == 1) * assignment(i)
        score -= sum(1 for _ in range((grid[0] * i), (grid[0] * i) + (grid[0] - 1)) if genes[i] == 0) * assignment(i)

    return Fitness(score)


def display(candidate, grid, startTime):
    timeDiff = datetime.datetime.now() - startTime
    board = Board(candidate.Genes, grid)
    board.print()
    print("{}\t{}\t{}".format(candidate.Fitness, candidate.Strategy, timeDiff))


# use window to restrict region where its selecting genes
def mutate(genes, grid, window):
    if random.randrange(0,2) == 0:
        # shift dir
        row, column, duration = random.randrange(0, grid[1]), random.randrange(0, grid[1]), grid[1]
        fitness = get_fitness(genes, grid)
        if random.randrange(0, 2) == 0:
            # up
            while duration > 0:
                # grab at the bottom
                cur = genes[column]
                prev = cur
                for a in range(0, grid[1]):
                    cur = genes[(a * grid[0]) + column]
                    genes[(a * grid[0]) + column] = prev
                    prev = cur
                genes[column] = prev
                if get_fitness(genes, grid) > fitness:
                    return
                duration -= 1
        else:
            # down
            while duration > 0:
                # grab at the top
                cur = genes[((grid[1] - 1) * grid[0]) + column]
                prev = cur
                for a in range((grid[1] - 2), -1, -1):
                    # start one below from the top
                    cur = genes[(a * grid[0]) + column]
                    genes[(a * grid[0]) + column] = prev
                    prev = cur
                # now apply the change back to the top
                genes[((grid[1] - 1) * grid[0]) + column] = prev
                if get_fitness(genes, grid) > fitness:
                    return
                duration -= 1
        return

    while True:
        index = random.randrange(0, len(genes))
        if genes[index] == 1 or (index + grid[0]) >= (grid[0] * grid[1]) or genes[index + grid[0]] == 1:
            continue

        genes[index], genes[index + grid[0]] = 1, 1
        window.slide()
        return


def crossover(parentGenes, donorGenes, fnGetFitness):
    pairs = {Pair(donorGenes[0], donorGenes[-1]): 0}
    for i in range(len(donorGenes) - 1):
        pairs[Pair(donorGenes[i], donorGenes[i + 1])] = 0

    tempGenes = parentGenes[:]
    if Pair(parentGenes[0], parentGenes[-1]) in pairs:
        # find a discontinuity
        found = False
        for i in range(len(parentGenes) - 1):
            if Pair(parentGenes[i], parentGenes[i + 1]) in pairs:
                continue
            tempGenes = parentGenes[i + 1:] + parentGenes[:i + 1]
            found = True
            break
        if not found:
            return None

    runs = [[tempGenes[0]]]
    for i in range(len(tempGenes) - 1):
        if Pair(tempGenes[i], tempGenes[i + 1]) in pairs:
            runs[-1].append(tempGenes[i + 1])
            continue
        runs.append([tempGenes[i + 1]])

    initialFitness = fnGetFitness(parentGenes)
    count = random.randint(2, 20)
    runIndexes = range(len(runs))
    while count > 0:
        count -= 1
        for i in runIndexes:
            if len(runs[i]) == 1:
                continue
            if random.randint(0, len(runs)) == 0:
                runs[i] = [n for n in reversed(runs[i])]

        if len(runIndexes) < 2:
            return parentGenes
        indexA, indexB = random.sample(runIndexes, 2)
        runs[indexA], runs[indexB] = runs[indexB], runs[indexA]
        childGenes = list(chain.from_iterable(runs))
        if fnGetFitness(childGenes) > initialFitness:
            return childGenes
    return childGenes


class Tetris(unittest.TestCase):
    '''
    def test_single_block(self):
        self.solve([10, 24])
    '''

    def test_double_block(self):
        self.solveDouble([4, 4])

    def solveDouble(self, grid):
        geneset = [0, 1]

        def fnDisplay(candidate):
            display(candidate, grid, startTime)

        def fnGetFitness(genes):
            return get_fitness(genes, grid)

        def fnCreate():
            return [random.randrange(0, 1) for _ in range((grid[0] * grid[1]))]

        def fnCustomMutate(genes):
            mutate(genes, grid, window)

        def fnCrossover(parent, donor):
            return crossover(parent, donor, fnGetFitness)

        window = Window(0, (grid[0] * grid[1]), (grid[0] * 2))
        optimalFitness = get_fitness(list(1 for _ in range(grid[0] * grid[1])), grid)
        startTime = datetime.datetime.now()
        best = genetic.get_best(fnGetFitness, None, optimalFitness, geneset, fnDisplay, custom_mutate=fnCustomMutate, custom_create=fnCreate)
        self.assertTrue(not optimalFitness > best.Fitness)

    def solve(self, grid):
        geneset = [0, 1]

        def fnDisplay(candidate):
            display(candidate, grid, startTime)

        def fnGetFitness(genes):
            return get_fitness(genes, grid)

        optimalFitness = Fitness(get_fitness(list([1 for _ in range((grid[0] * grid[1]))]), grid), 0)
        startTime = datetime.datetime.now()
        best = genetic.get_best(fnGetFitness, optimalFitness, optimalFitness, geneset, fnDisplay, maxAge=5, maxSeconds=10)

        self.assertTrue(not optimalFitness > best.Fitness)


'''
    def test_benchmark(self):
        genetic.Benchmark.run(lambda: self.solve([10,24]))
'''

def assignment(height):
    return (100/math.exp(height))

def countPositivesAndNegatives(genes, index, grid):
    # was going to 1 liner but nah
    positives = 0
    negatives = 0
    if genes[index] == 1:
        # right side
        if (index + 1) % grid[0] == 0:
            positives += 1
        if (index + 1) < len(genes):
            if genes[(index + 1)] == 1:
                positives += 1
            else:
                negatives += 1

        # left
        if (index - 1) % grid[0] == 0 or (index - 1) < 0:
            positives += 1
        if (index - 1) >= 0:
            if genes[index - 1] == 1:
                positives += 1
            else:
                negatives += 1

        # up
        if (index + grid[0]) < len(genes):
            if genes[index + grid[0]] == 1:
                positives += 1
            else:
                negatives += 1
        else:
            positives += 1

        # down
        if (index - grid[0]) < 0:
            if genes[index - grid[0]] == 1:
                positives += 1
            else:
                negatives += 1
        else:
            positives += 1

    else:
        if (index + grid[0]) < len(genes):
            if genes[index + grid[0]] == 0:
                positives += 2
            else:
                negatives += 2
        if (index - grid[0]) >= 0:
            if genes[index - grid[0]] == 0:
                positives += 2
            else:
                negatives += 2

    return positives, negatives


class Board:
    def __init__(self, genes, grid):
        self.board = [['0'] * grid[0] for _ in range(grid[1])]
        for row in range(grid[1]):
            for col in range(grid[0]):
                self.board[row][col] = genes[row * grid[0] + col]

    def getRow(self, index):
        return self.board[index]

    def print(self):
        for i in reversed(range(len(self.board))):
            print(' '.join(map(str, self.board[i])))


class Pair:
    def __init__(self, node, adjacent):
        if node < adjacent:
            node, adjacent = adjacent, node
        self.Node = node
        self.Adjacent = adjacent

    def __eq__(self, other):
        return self.Node == other.Node and self.Adjacent == other.Adjacent

    def __hash__(self):
        return hash(self.Node) * 397 ^ hash(self.Adjacent)


class Window:
    def __init__(self, minimum, maximum, size):
        self.Min = minimum
        self.Max = maximum
        self.Size = size
        self.Position = 0

    def slide(self):
        self.Position = (self.Position - self.Size) if (self.Position - self.Size) > 0 else (self.Max - self.Position)

    def __str__(self):
        return str(self.Min) + " " + str(self.Max) + " " + self.Size


class Fitness:
    def __init__(self, score):
        self.Score = score

    def __gt__(self, other):
        return self.Score > other.Score

    def __str__(self):
        return "{} Fitness".format(self.Score)


if __name__ == '__main__':
    unittest.main()
