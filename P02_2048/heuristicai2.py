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
    empty_count = empty_cells_count(board)
    print('Empty Cells Count: ', 
          empty_count, 
          ' => ', 
          'PANIC!' if empty_count < 4 else 'GO HAM!')
    
    # return a board that simulates a certain move
    #try_right = execute_move(RIGHT, board)
    #try_left = execute_move(LEFT, board)
    #try_up = execute_move(UP, board)

    '''
    print_board(board)
    print()
    print(to_val(board))
    print()
    time.sleep(1)
    '''
    # return if a certain move is a valid move
    #right_possible = not board_equals(try_right, board)
    #left_possible = not board_equals(try_left, board)
    #up_possible = not board_equals(try_up, board)

    #only_down_possible = board_equals(board, try_right) and board_equals(try_right, try_left) and board_equals(try_left, try_up)
    
    only_down_possible = (not move_possible(UP, board)) and (not move_possible(LEFT, board)) and (not move_possible(RIGHT, board))
    
    if only_down_possible:
        return DOWN
    else:
        if move_possible(UP, board):
            return UP
        else:
            if move_possible(LEFT, board):
                return LEFT
            else:
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

def print_board(m):
    for row in m:
        for c in row:
            print('%8d' % c, end=' ')
        print()

def _to_val(c):
    if c == 0: return 0
    return c

def to_val(m):
    return [[_to_val(c) for c in row] for row in m]

def _to_score(c):
    if c <= 1:
        return 0
    return (c-1) * (2**c)

def to_score(m):
    return [[_to_score(c) for c in row] for row in m]

def empty_cells_count(m):
    count = 0
    for row in m:
        for c in row:
            if _to_val(c) == 0:
                count += 1
    return count

def move_possible(move, board):
    return not board_equals(execute_move(move, board), board)
