import random
import game
import sys
import time

# Author:				chrn (original by nneonneo)
# Date:				11.11.2016
# Description:			The logic of the AI to beat the game.

UP, DOWN, LEFT, RIGHT = 0, 1, 2, 3

def find_best_move(board):
    bestmove = -1    
	
	# TODO:
	# Build a heuristic agent on your own that is much better than the random agent.
	# Your own agent don't have to beat the game.
    bestmove = find_best_move_random_agent(board)
    return bestmove

'''
1) play 'randomly' with adjusted weight values, one move direction is prohibited
2) when space gets crowded, try to see which move keeps your board cleanest
3) get a heuristic for "crowdedness"
4) get a heuristic for "difference in sizes"
5) try combining as much as possible
'''
def find_best_move_random_agent(board):
    print(' *** ')
    ecc = empty_cells_count(board)
    print(f'Empty Cells Count   \t {ecc} => ',
          'PANIC!' if ecc < 4 else 'normal')
    bcph = bad_chess_pattern_heuristic(board)
    print(f'Bad Chess Pattern   \t {bcph}')
    ndh = neighbour_difference_heuristic(board)
    print(f'Neighbour Difference\t {ndh}')
    ht = highest_tile(board)
    print(f'Highest Tile        \t {ht}')
    htich = highest_tile_in_corner_heuristic(board)
    print(f'Highest in Corner   \t {htich}')
    
    

    
    '''
    print_board(board)
    print()
    print(to_val(board))
    print()
    time.sleep(1)
    '''
    
    only_down_possible = (not move_possible(UP, board)) and (not move_possible(LEFT, board)) and (not move_possible(RIGHT, board))
    
    if only_down_possible:
        keep_highest_tile_in_corner(DOWN, board)
        return DOWN
    else:
        if move_possible(UP, board):
            keep_highest_tile_in_corner(UP, board)
            return UP
        else:
            if move_possible(LEFT, board):
                keep_highest_tile_in_corner(LEFT, board)
                return LEFT
            else:
                keep_highest_tile_in_corner(RIGHT, board)
                return RIGHT    
    
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
    return  (newboard == board).all()  

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

    '''
    #=============
    # Own Methods
    #=============
    '''
def empty_cells_count(board):
    count = 0
    for row in board:
        for cell in row:
            if _to_val(cell) == 0:
                count += 1
    return count

def move_possible(move, board):
    return not board_equals(execute_move(move, board), board)

def cell_of_type_count(cell_val, board):
    cell_count = 0
    for row in board:
        for cell in row:
            if (_to_val(cell) == cell_val):
                cell_count += 1
    return cell_count

# TODO
def bad_chess_pattern_heuristic(board):
    return 0

# TODO
def neighbour_difference_heuristic(board):
    return 0

def highest_tile_in_corner_heuristic(board):
    highest_cell = highest_tile(board)
    if (_to_val(board[0][0]) >= highest_cell) or (_to_val(board[0][3]) >= highest_cell) or (_to_val(board[3][0]) >= highest_cell) or (_to_val(board[3][3]) >= highest_cell):
        return 0
    return 1
    
def highest_tile(board):
    highest_cell = 2;
    for row in board:
        for cell in row:
            if _to_val(cell) > highest_cell:
                highest_cell = _to_val(cell)
    return highest_cell

def keep_highest_tile_in_corner(move, board):
    highest_cell = highest_tile(board)
    new_board = execute_move(move, board)
    result = False
    
    if (_to_val(new_board[0][0]) >= highest_cell) or (_to_val(new_board[0][3]) >= highest_cell) or (_to_val(new_board[3][0]) >= highest_cell) or (_to_val(new_board[3][3]) >= highest_cell):
        result = True
    #print(f'move: {move} // {result}')   
    return result