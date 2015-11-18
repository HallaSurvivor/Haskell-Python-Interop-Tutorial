# Haskell to Python Interop Tutorial
A Tic Tac Toe game to teach the basics of passing Python lists to Haskell code.

I made this because I found that there aren't many tutorials, and arguably no easy to follow tutorials, that
explain how to pass python arrays to Haskell.

That said, I went out and tried things until it worked, and this is a product of that.
Hopefully it can help somebody else progress faster :)

# How it works
The graphics are handled in python, and the logic is handled in Haskell
This immitates a real-world project, but with a trivial example (Tic Tac Toe)

Compiling will also create certain extraneous files, such as main.hi, main.o, and main_stub.h
These are related to running main.hs as a program, or in the case of main_stub.h, 
calling the code from an intermediate c layer. 

All of these can be deleted safely

# How to run

First compile main.hs into a .so file (shared library) to be called from inside run.py

Do this with the command:
ghc -dynamic -shared -fPIC -lHSrts-ghc7.6.3 -o main.so main.hs

This command is broken down in further detail inside of main.hs
(I'm sorry the description is so bad, I don't 100% understand some of the flags myself)

The python code is written in 2.7 and requires pygame, because I'm better with it than Tkinter

Finally, run the command
python run.py
