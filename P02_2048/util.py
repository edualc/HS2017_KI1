import random
import game
import sys
import time
import math


def execute_move(move, board):
    """
    move and return the grid without a new random tile 
	It won't affect the state of the game in the browser.
    """

    if move == UP:
        return game.merge_up(board)
    elif move == DOWN:
        return game.merge_down(board)
    elif move == LEFT:
        return game.merge_left(board)
    elif move == RIGHT:
        return game.merge_right(board)
    else:
        sys.exit("No valid move")

def board_equals(board, newboard):
    """
    Check if two boards are equal
    """
    return (newboard == board).all()  

def print_board(board):
    for row in board:
        for cell in row:
            print('%8d' % cell, end=' ')
        print()

def _to_val(cell):
    if cell == 0: return 0
    return cell

def to_val(board):
    return [[_to_val(cell) for cell in row] for row in board]

def _to_score(cell):
    if cell <= 1:
        return 0
    return (cell-1) * (2**cell)

def to_score(board):
    return [[_to_score(cell) for cell in row] for row in board]

def index_min(list):
    return list.index(min(list))

def index_max(list):
    return list.index(max(list))