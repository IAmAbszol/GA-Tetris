Thanks to https://github.com/epai/tetris-terminal-game
Main framework for the Tetris game along with an impressive
backend that allows for code manipulation of the game to be quite easy
for adapting this algorithm

Steps for Tetris AI
AI geneset will only be 0, 0.01, 0.02 ... .99, 1, ..... 10
Thus any decimals of length 2 up to 10

Fitness will evaluate positioning of the pieces and using the genes
to calculate the "reward"

Mutation will alter the genes


How this will all work

Each genetic algorithm occurs when the best fitness is found from running
n iterations through 4 rotations each, thus 4n.

The GA parent is determined by the highest score, thus resulting parents
target will be measured by score.



So
* Mutation
- Changes genes that target how fitness works

* Fitness
- Evaluates the best place to put that object given the simulated positions
--> Send the 4n iterations through a loop to yield best fitness


The technical

Flowchart

get_fitness(genes):
0. Game start
1. Run
    a. Using only "fitness" --> (Calculate BEST piece position by using fitness "score" parameters)
    b. Move piece n directions then drop when complete
    c. Loop
2. Game ends, take score. (Initial collection only) else compare new parent score vs this. Replace

Thus could fitness play tetris to measure it? I think so
Fitness will be a score, wanting score for optimal can be 1000000...
Run tetris on fitness

Functions to use and documentation to what it needs
All required functions are within the Game class/__game__.py

Functions
    - dropPiece() : Will be used once piece has been observed to be placed in the correct position
    - doMove(int) : Requires [ 1, -1 ] as its only parameter, -1 to move left else 1 for right else return

Fields
    - simulateLanded : Prints the board of the landing position. 
        * Implementation may not be needed as a direct approach of calculation can be used. * Look into it though
    - grabs ahold of current board schema

Rig game start into the get_fitness function
Rig game end as a return with the score attached for fitness to use.

Parameters (Genes)
indecies
0 - Evaluate clear line reward
1 - Fill up line reward
2 - Penalize gap
3 - Penalize height

Utilizing doMove appropriately
I don't wish to access the Game object if not needed, so the only access from it
will be the currPiece.topLeft.column field value that changes as the piece moves.
This will prove useful for black box testing the number of columns, rather than count
and calculate, a simple check will be used
doMove(-1)
if prevColumn == getCurrPiece().topLeft.column:
    start moving to the right.

The program will act like a 3D printer, adjust to 0,0 and move from left to right.
Then it re-initializes at n,0 and continues.

After each iteration, rotatePiece() is called to rotate and re-evaluate
The coordinates and rotation number is calculated and stored for the highest fitness

Next the program will take the desired coordinate and rotation.
The steps
0. Rotate once (After iterating, the ending rotation should be 3 of 4, 4 being reset so calling rotate will/should be back in reset position)
1. Calcuate number of moves from current (getCurrPiece().topLeft.column) position
2. Iterate through from position to coordinate. Use difference, if negative then left else right
3. dropPiece()
