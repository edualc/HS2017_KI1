import random
import game
import sys
import time
import math
import numpy as np

UP, DOWN, LEFT, RIGHT = 0, 1, 2, 3

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

def build_list_2d(content, x, y):
    return [[content for y_coord in range(y)] for x_coord in range(x)]

def build_list(content, x):
    return [content for x_coord in range(x)]


def cell_of_type_count(cell_val, board):
    cell_count = 0

    for row in board:
        for cell in row:
            if cell == cell_val:
                cell_count += 1

    return cell_count

def move_possible(move, board):
    return not board_equals(execute_move(move, board), board)

def build_possible_moves_list(board):
    possible_moves_array = build_list(0, 4)
    
    for i in range(4):
        if move_possible(i, board):
            possible_moves_array[i] = 1
            
    return possible_moves_array   

def highest_tile(board):
    return np.amax(np.array(board))

def is_highest_tile_in_corner(board):
    position = get_position_of_highest_tile(board)
    corner_positions = [[0,0], [3,0], [0,3], [3,3]]

    for c_pos in corner_positions:
        if position == c_pos:
            return True
    
    return False

def get_position_of_highest_tile(board):
    '''returns the position of the given highest tile, checking corners first to ensure
    a duplicate highest cell does return a corner position if at least one is in a corner'''
    max_tile = highest_tile(board)

    if board[0, 0] == max_tile:
        return [0, 0]
    elif board[3, 0] == max_tile:
        return [3, 0]
    elif board[0, 3] == max_tile:
        return [0, 3]
    elif board[3, 3] == max_tile:
        return [3, 3]
    else:
        return None
