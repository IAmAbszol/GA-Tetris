import datetime
import random
import os
import subprocess
import numpy as np
import sys
import array
from fractions import Fraction
from threading import Thread
from py4j.java_gateway import JavaGateway

import my_tetris

# alternative is https://stackoverflow.com/questions/6893968/how-to-get-the-return-value-from-a-thread-in-python
# users asynchronous calls and can pull results from return, though not clarified join operator
# due to asynchronous nature. Currently only using thread
def get_fitness(participant, pool, index, fnDraw):
    app = my_tetris.TetrisGame(index)
    app.run(participant.Genes, fnDraw)
    participant.Fitness = 0
    pool[index] = participant


def display(candidate, startTime):
    timeDiff = datetime.datetime.now() - startTime
    print("{}\t{} - {}".format(candidate.Genes,
                             candidate.Fitness,
                             timeDiff))

def mutate(participant, players, geneset, fnDraw):
    # now create multiple children/offspring from this participant who was most successful
    threads = [None] * players
    pool = [None] * players
    for index in range(players):
        childGenes = participant.Genes[:]
        idx = random.randrange(0, len(participant.Genes))
        newGene, alternate = random.sample(geneset, 2)
        childGenes[idx] = alternate if newGene == childGenes[idx] else newGene

        threads[index] = Thread(target=get_fitness, args=(Chromosome(childGenes, 0), pool, index, fnDraw))
        threads[index].start()
    for thread in threads:
        thread.join()
    return pool


def create_children(players, evaluation_length, geneset, fnDraw):
    participants = [Chromosome([0 for x in range(evaluation_length)], 0) for i in range(players)]
    threads = [None] * players
    pool = [None] * players
    for index, participant in enumerate(participants):
        genes = participant.Genes
        for gene in range(len(genes)):
            genes[gene] = geneset[random.randrange(0, len(geneset))]
        participant.Genes = genes
        threads[index] = Thread(target=get_fitness, args=(participant, pool, index, fnDraw))
        threads[index].start()
    for thread in threads:
        thread.join()
    return pool

class RunTetris:
    def test_participants(self):

        def create_pythongui():
            subprocess.run(["java", "-jar", "PythonGUI.jar"])

        number_of_players = 1
        evaluation_genes = 3
        goal = 100000
        best_score = 0

        generange = [i for i in range(-100, 100)]
        #geneset = [i for i in set(Fraction(d, e) for d in geneRange for e in geneRange if e != 0)]
        geneset = [i for i in generange]

        # call pythongui.jar
        if not os.path.isfile("PythonGUI.jar"):
            print("PythonGUI.jar has been renamed or missing from this current working directory!")
            exit(1)

        def call_jvm():
            subprocess.run(["java", "-jar", "PythonGUI.jar"])

        # call jvm in a separate thread to prevent halting
        jvm_thread = Thread(target=call_jvm)
        jvm_thread.start()

        # link python to jvm
        gateway = JavaGateway()
        pythongui = gateway.entry_point
        # setup initial gui
        pythongui.setup(number_of_players, my_tetris.cols, my_tetris.rows, 15, 10)

        def fnDraw(id, board, genes, score):
            # convert 2d matrix to byte array and pass to Java
            np_board = np.array(board)
            header_board = array.array('i', list(np_board.shape))
            body_board = array.array('i', np_board.flatten().tolist());
            if sys.byteorder != 'big':
                header_board.byteswap()
                body_board.byteswap()
            buf_board = bytearray(header_board.tostring() + body_board.tostring())

            np_genes = np.array(genes)
            size = [len(np_genes)]
            header_genes = array.array('i', size)
            body_genes = array.array('i', np_genes.flatten().tolist())
            if sys.byteorder != 'big':
                header_genes.byteswap()
                body_genes.byteswap()
            buf_genes = bytearray(header_genes.tostring() + body_genes.tostring())

            # pass converted matrices byte array to java
            pythongui.getBoard(int(id)).draw(pythongui.getBoard(int(id)).convertToIntegerMatrix2D(buf_board),
                                             pythongui.getBoard(int(id)).convertToIntegerMatrix1D(buf_genes),
                                             score)

        startTime = datetime.datetime.now()

        # create initial participants - measures fitness as well by playing Tetris
        participants = create_children(number_of_players, evaluation_genes, geneset, fnDraw)

        while True:
            sorted_participants = sorted(participants, reverse=True)
            if sorted_participants[0].Fitness > best_score:
                best_score = sorted_participants[0].Fitness
                display(sorted_participants[0], startTime)
            if best_score >= goal:
                exit(0)
            else:
                participants = mutate(sorted_participants[0], number_of_players, geneset, fnDraw)

class Chromosome:
    def __init__(self, genes, fitness):
        self.Genes = genes
        self.Fitness = fitness
        self.Age = 0

    def __gt__(self, other):
        return self.Fitness > other.Fitness

    def __str__(self):
        return "Genes : {} - Fitness : {}.".format(self.Genes, self.Fitness)

if __name__ == '__main__':
    App = RunTetris()
    App.test_participants()