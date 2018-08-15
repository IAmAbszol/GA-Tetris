# Genetic Algorithm developed using Python & Java

# Completely overhauled the original project

Thanks to Github user 'Silvasur' for the incredibly simple Tetris game.

I ended up reworking it from using Pygame to a simple text based board since
Pygame wouldn't allow for multiple players to be spawned. This is from Pygame's
"hook" to the Python Interpreter and possibly the kernel in an effort to lock
multiple threads from being created of that game instance.

Link to simple tetris: https://gist.github.com/silvasur/565419

# Description

The Tetris Genetic Algorithm is responsible for playing Tetris at it's best given the proper genes to complete
the evaluation phase of its programming when playing.

Utilizing Python3 as it's back-end and Java 1.8 as its front-end, the program can spawn as many players as need be
while allowing the user to maniupulate the front-end to their desire.

# Prerequisites

Java >= 1.7

Python >= 3.5 (Comes pre-installed with pip)

# Installation

Simple, run ```pip install -r requirements.txt``` for all the requirements needed by Py4j

# Running

```
python run.py
```

# Customization :)

The code to customize the PythonGUI further can be found at: https://github.com/IAmAbszol/Dynamic-Multiplayer-Text-Board 

Detailed documentation in terms of how the methods work are provided though code examples are yet to be added. This
will probably come later when I'll need this outside of Python.