import random
import game
import sys

# Author:				edualc (original by nneonneo, edited by chrn)
# Date:				10.10.2017
# Description:		The logic of the AI to beat the game.

UP, DOWN, LEFT, RIGHT = 0, 1, 2, 3

def find_best_move(board):
    bestmove = -1    
	
	# TODO:
	# Build a heuristic agent on your own that is much better than the random agent.
	# Your own agent don't have to beat the game.
    bestmove = find_best_move_random_agent(board)
    return bestmove

def find_best_move_random_agent(board):

    # return a board that simulates a certain move
    try_right = execute_move(RIGHT, board)
    try_left = execute_move(LEFT, board)
    try_up = execute_move(UP, board)

    # return if a certain move is a valid move
    right_possible = not board_equals(try_right, board)
    left_possible = not board_equals(try_left, board)
    up_possible = not board_equals(try_up, board)

    only_down_possible = board_equals(board, try_right) and board_equals(try_right, try_left) and board_equals(try_left, try_up)
    
    if only_down_possible:
        return DOWN
    else:
        if up_possible:
            return UP
        else:
            if left_possible:
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