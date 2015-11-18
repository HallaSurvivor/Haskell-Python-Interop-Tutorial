"""
A simple tic tac toe game meant to illustrate InterOp between Haskell and Python

There are inline comments scattered throughout the code in order to
explain what everything important does.

Python handles the graphics
Haskell handles the logic

python 2.7
"""

import ctypes as c  
# We need to use C types since Haskell
# knows how to interface with C, but
# not with python directly.


import pygame
# We use pygame to handle the graphics
# because I'm better with pygame than
# TKinter. 


SCREENSIZE = 300
BGCOLOR    = (200, 200, 200)
TEXTCOLOR  = (255, 255, 204)
LINECOLOR  = (0,   0,   0)
# Set up some general constants for use later


pygame.init()  
# Initialize pygame


lib = c.cdll.LoadLibrary("./main.so")  
# Import the Haskell library
# make sure you've compiled it.
# as an .so file, not the default.
# The instructions for doing so 
# are in main.hs


lib.hs_init(0,0) 
# Initialize Haskell
# The arguments, 0 and 0,
# correpsond to NULLs
# in the background, and
# are required.

font = pygame.font.SysFont(None, 48)

def convertToC(board):
    """
    Take a python list and turn it into a C array

    note: while the *board notation 
    is convenient, it does not 
    represent a pointer to the board.
    It is python *args unpacking in the
    same way as any other *args, **kwargs
    function.
    """
    return (c.c_int * len(board))(*board)


class gamestate(object):
    """
    A gamestate for handling all the graphics.

    I don't go into much detail, as this guide
    is meant for Haskell-Python InterOp, not
    pygame. That said, I try to include some
    information in case you've never seen
    pygame before.
    """
    def __init__(self):
        self.player = 1  # The current player
        self.board  = None
        self.done   = False
        self.state  = 0
        # The gamestate.
        # 0  -> game is ongoing
        # 1  -> player 1 won
        # 2  -> player 2 won
        # -1 -> tie game

        self.screen = pygame.display.set_mode((SCREENSIZE, SCREENSIZE))
        pygame.display.set_caption('TicTacToe')
        self.clock  = pygame.time.Clock()

    def draw_x(self, center):
        """
        draw an X to a given square
        """

        centerx, centery = center
        offset = SCREENSIZE/6

        Left   = centerx - offset
        Right  = centerx + offset
        Top    = centery - offset
        Bottom = centery + offset
        
        pygame.draw.line(self.screen, LINECOLOR, (Left, Top), (Right, Bottom), 3)
        pygame.draw.line(self.screen, LINECOLOR, (Left, Bottom), (Right, Top), 3)

    def draw_o(self, center):
        """
        draw an O to a given square
        """

        pygame.draw.circle(self.screen, LINECOLOR, center, SCREENSIZE/6, 2)

    def draw_board(self):
        """
        draw the board.
        
        * fill screen with BGCOLOR
        * draw the grid
        * draw the Xs and Os
        """

        self.screen.fill(BGCOLOR)
        
        # Draw the grid
        for i in xrange(3):
            pygame.draw.line(self.screen, LINECOLOR, (SCREENSIZE*i/3, 0), (SCREENSIZE*i/3, SCREENSIZE), 1)
            pygame.draw.line(self.screen, LINECOLOR, (0, SCREENSIZE*i/3), (SCREENSIZE, SCREENSIZE*i/3), 1)
        
        # Draw the Xs and Os
        for index, tile in enumerate(self.board):
            x = index % 3
            y = index / 3
            
            x *= SCREENSIZE / 3
            y *= SCREENSIZE / 3

            x += SCREENSIZE/6
            y += SCREENSIZE/6

            center = (x, y)
            if tile == 1:
               self.draw_x(center) 

            elif tile == 2:
                self.draw_o(center)

    def draw_win_screen(self):
        """
        Draw the screen for a tie/win
        """

        self.screen.fill(BGCOLOR)
        
        # Create either win text or tie text
        # The Haskell code returns a -1 on a tie.
        if self.state != -1:  
            winText = font.render('Player {0} won!'.format(self.state), True, TEXTCOLOR)
        
        else:
            winText = font.render('Tie game!', True, TEXTCOLOR)
        
        winTextRect = winText.get_rect()
        winTextRect.center = self.screen.get_rect().center
        
        # Create the replay text
        replayText = font.render('Click to replay', True, TEXTCOLOR)
        replayTextRect = replayText.get_rect()
        replayTextRect.centerx = self.screen.get_rect().centerx
        replayTextRect.centery = self.screen.get_rect().centery + SCREENSIZE/6
        
        # Draw the win text and replay text to the screen
        self.screen.blit(winText, winTextRect)
        self.screen.blit(replayText, replayTextRect)
    
    def switch_player(self):
        """
        Take turns
        """
        if self.player == 1:
            self.player = 2
        else:
            self.player = 1
    
    def draw(self):
        """
        Draw the appropriate screen.

        If the game is ongoing:
          draw the board
        Otherwise:
          draw the win/tie screen
        """

        if self.state == 0:
            self.draw_board()
        else:
            self.draw_win_screen()

    def click(self, x, y):
        """
        Handle clicks.

        If the game is ongoing:
          * If you click in a tile
          * and that tile is not taken
            * modify the board
            * swap the player

        Otherwise:
          * If you click anywhere
            * restart the game
        """

        if self.state == 0:
            for i in xrange(3):
                for j in xrange(3):
                    left   = i * SCREENSIZE / 3
                    right  = (i+1) * SCREENSIZE / 3
                    top    = j * SCREENSIZE / 3
                    bottom = (j+1) * SCREENSIZE / 3
                
                    if left < x < right and top < y < bottom:
                        if lib.checkValid(cBoard, 3*j+i):                        
                            # Call into Haskell to see if 
                            # a move is valid. The function
                            # takes a cBoard and an integer
                            # corresponding to the position
                            # to add a new tile.
                            # It returns True if the move is
                            # legal,
                            # i.e. if nobody has played there yet.

                            self.board[3*j+i] = self.player
                            self.switch_player()

        else: 
            # If you're on the win/tie screen
            self.board  = None
            self.player = 1
            self.state  = 0



game = gamestate()

while not game.done:
    game.clock.tick(120)  # Max at 120 fps.

    if game.board is None: game.board = [0] * 9
    
    cBoard = convertToC(game.board)
    winner = lib.checkWin(cBoard)
    # Here's another Haskell call.
    # Note we just call it from the c dll
    # that we compiled it into, and use it
    # like any other imported function.

    if winner:
        game.state = winner
    
    game.draw()
    # draw the gamestate to the screen,
    # either the current board or
    # the win/tie end screen.

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # Close the window if you click the X
            game.done = True
    
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            # run the click method when you click.
            game.click(x, y)
                
    pygame.display.flip()
    # update the drawn window

lib.hs_exit()  
# Close Haskell

pygame.quit()  
# Close Pygame
