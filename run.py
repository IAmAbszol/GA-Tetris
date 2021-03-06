import datetime
import random
import os
import subprocess
import numpy as np
import sys
import array
import signal
from bisect import bisect_left
from math import exp
from fractions import Fraction
from threading import Thread
from py4j.java_gateway import JavaGateway

import my_tetris

desired_score = 1000000
restricted_genes = []

# alternative is https://stackoverflow.com/questions/6893968/how-to-get-the-return-value-from-a-thread-in-python
# users asynchronous calls and can pull results from return, though not clarified join operator
# due to asynchronous nature. Currently only using thread
def get_fitness(participant, pool, index, fnDraw):
    app = my_tetris.TetrisGame(index)
    participant.Fitness = app.run(participant.Genes, fnDraw, desired_score)
    pool[index] = participant


def display(candidate, startTime):
    timeDiff = datetime.datetime.now() - startTime
    file = open("log.txt", "a")
    file.write("{}\t{}\tStrategy: {} - {}\n".format(candidate.Genes,
                             candidate.Fitness,
                             candidate.Strategy,
                             timeDiff))
    file.close()

def mutate(participant, players, geneset, fnDraw):
    threads = [None] * players
    pool = [None] * players
    for index in range(players):
        tmpGenes = childGenes = participant.Genes[:]
        for gene in range(len(tmpGenes)):
            tmpGenes[gene] = geneset[random.randrange(0, len(geneset))]
        for i in range(0, len(tmpGenes)):
            if random.uniform(0, 1) > 0.6:
                childGenes[i] = tmpGenes[i]
        while childGenes in restricted_genes:
            tmpGenes = childGenes = participant.Genes[:]
            for gene in range(len(tmpGenes)):
                tmpGenes[gene] = geneset[random.randrange(0, len(geneset))]
            for i in range(0, len(tmpGenes)):
                if random.uniform(0, 1) > 0.6:
                    childGenes[i] = tmpGenes[i]
        threads[index] = Thread(target=get_fitness, args=(Chromosome(childGenes, 0, "Mutate"), pool, index, fnDraw))
        threads[index].start()
    for thread in threads:
        thread.join()
    return pool

def crossover(participantA, participantB, players, geneset, fnDraw):
    threads = [None] * players
    pool = [None] * players
    window = Window(0, 2, len(participantA.Genes))
    for index in range(players):
        childGenes = []
        for i in range(len(participantA.Genes)):
            if random.uniform(0, 1) > 0.5:
                childGenes.append(participantB.Genes[i])
            else:
                childGenes.append(participantA.Genes[i])
        while childGenes in restricted_genes:
            for i in range(len(participantA.Genes)):
                if random.uniform(0, 1) > 0.5:
                    childGenes[random.randrange(0, len(childGenes))] = (participantB.Genes[i])
                else:
                    childGenes[random.randrange(0, len(childGenes))] = (participantA.Genes[i])
        threads[index] = Thread(target=get_fitness, args=(Chromosome(childGenes, 0, "Crossover"), pool, index, fnDraw))
        threads[index].start()
    for thread in threads:
        thread.join()
    return pool

def create_children(players, evaluation_length, geneset, fnDraw):
    participants = [Chromosome([0 for x in range(evaluation_length)], 0, "Create") for i in range(players)]
    threads = [None] * players
    pool = [None] * players
    for index, participant in enumerate(participants):
        genes = participant.Genes
        for gene in range(len(genes)):
            genes[gene] = geneset[random.randrange(0, len(geneset))]
        #participant.Genes = [ 1.6, -2.31, -0.59, 3.97, 6.52, -2, -3.78]
        while genes in restricted_genes:
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

        evaluation_genes = 7
        goal = Chromosome([0] * evaluation_genes, desired_score, None)
        number_of_players = 10
        best_score = Chromosome([0] * evaluation_genes, 0, None)
        maxAge = None

        generange = [i for i in range(-100, 100)]
        geneset = [i for i in set(Fraction(d, e) for d in generange for e in generange if e != 0)]
        strategy_pool = []
        #geneset = [i for i in generange]

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
        # create kill point for safe exit of JVM
        # capture interupt signal to kill quickly
        def signal_handler(sig, frame):
            pythongui.stop()
            sys.exit(0)
        # setup interrupt handler
        signal.signal(signal.SIGINT, signal_handler)
        # setup initial gui
        pythongui.setup(number_of_players, my_tetris.cols, my_tetris.rows, 20, 8)

        # clear log
        if os.path.exists("log.txt"):
            os.remove("log.txt")

        def fnDraw(id, board, genes, score, waiting=False):
            '''
            if not waiting:
                # convert 2d matrix to byte array and pass to Java
                np_board = np.array(board)
                header_board = array.array('i', list(np_board.shape))
                body_board = array.array('i', np_board.flatten().tolist());
                if sys.byteorder != 'big':
                    header_board.byteswap()
                    body_board.byteswap()
                buf_board = bytearray(header_board.tostring() + body_board.tostring())
            else:
                pythongui.getBoard(int(id)).drawText("Game has completed. Score: {}".format(score))
                return

            np_genes = np.array([ int(i) for i in genes])
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
            '''

        startTime = datetime.datetime.now()

        # create initial participants - measures fitness as well by playing Tetris
        participants = create_children(number_of_players, evaluation_genes, geneset, fnDraw)
        sorted_participants = sorted(participants, reverse=True)
        parent = bestParent = sorted_participants[0]
        strategy_pool.append(parent.Strategy)
        strategy_pool.append("Crossover")
        strategy_pool.append("Mutate")
        historicalFitnesses = [bestParent.Fitness]
        crossover_pool = [bestParent]
        while True:
            #participants = mutate(parent, number_of_players, geneset, fnDraw)
            selected = random.choice(strategy_pool)
            participants = None
            if selected == "Create":
                participants = create_children(number_of_players, evaluation_genes, geneset, fnDraw)
            elif selected == "Mutate":
                participants = mutate(parent, number_of_players, geneset, fnDraw)
            elif selected == "Crossover":
                sorted_participants = sorted(crossover_pool, reverse=True)
                if len(sorted_participants) == 1:
                    participants = crossover(sorted_participants[0], sorted_participants[0], number_of_players, geneset, fnDraw)
                elif len(sorted_participants) > 1:
                    participants = crossover(sorted_participants[random.randrange(0, len(sorted_participants))],
                                             sorted_participants[random.randrange(0, len(sorted_participants))],
                                             number_of_players,
                                             geneset,
                                             fnDraw)
                else:
                    participants = None
            sorted_participants = sorted(participants, reverse=True)
            child = sorted_participants[0]
            if parent.Fitness > child.Fitness:
                parent.Age += 1
                if maxAge is None:
                    continue
                if maxAge > parent.Age:
                    continue
                index = bisect_left(historicalFitnesses, child.Fitness, 0,
                                len(historicalFitnesses))
                difference = len(historicalFitnesses) - index
                proportionSimilar = difference / len(historicalFitnesses)
                if random.random() < exp(-proportionSimilar):
                    parent = child
                    continue
                bestParent.Age = 0
                parent = bestParent
                continue
            if not child.Fitness > parent.Fitness:
                child.Age = parent.Age + 1
                parent = child
                strategy_pool.append(child.Strategy)
                crossover_pool.append(child)
                #display(child, startTime)
                continue
            child.Age = 0
            parent = child
            if child.Fitness > bestParent.Fitness:
                bestParent = child
                historicalFitnesses.append(bestParent.Fitness)
                strategy_pool.append(bestParent.Strategy)
                crossover_pool.append(bestParent)
                restricted_genes.append(bestParent.Genes)
                display(child, startTime)
            if bestParent.Fitness >= goal.Fitness:
                display(sorted_participants[0], startTime)
                exit(0)

class Chromosome:
    def __init__(self, genes, fitness, strat):
        self.Genes = genes
        self.Fitness = fitness
        self.Age = 0
        self.Strategy = strat

    def __gt__(self, other):
        return self.Fitness > other.Fitness

    def __str__(self):
        return "Genes : {} - Fitness : {}.".format(self.Genes, self.Fitness)

class Window:
    def __init__(self, minimum, maximum, size):
        self.Min = minimum
        self.Max = maximum
        self.Size = size

    def slide(self):
        self.Size = self.Size - 1 if self.Size > self.Min else self.Max

if __name__ == '__main__':
    App = RunTetris()
    App.test_participants()
