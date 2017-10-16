import random
import game
import sys

import util
import log

# Author:      chrn (original by nneonneo)
# Date:        11.11.2016
# Copyright:   Algorithm from https://github.com/nneonneo/2048-ai
# Description: The logic to beat the game. Based on expectimax algorithm.

UP, DOWN, LEFT, RIGHT = 0, 1, 2, 3
move_args = [UP,DOWN,LEFT,RIGHT]
lookup_depth = 3

def find_best_move(board):
    best_move = -1    
    result = [score_toplevel_move(i, board) for i in range(len(move_args))]
    best_move = result.index(max(result))
    # for m in move_args:
    #     print(m)
    #     print(result[m])
    
    return best_move
    
def score_toplevel_move(move, board):
    """Entry Point to score the first move."""
    new_board = util.execute_move(move, board)

    if util.board_equals(board, new_board):
        return 0

    potential_outcomes = build_potential_outcomes(new_board)

	# TODO:
	# Implement the Expectimax Algorithm.
	# 1.) Start the recursion until it reach a certain depth
	# 2.) When you don't reach the last depth, get all possible board states and 
	#		calculate their scores dependence of the probability this will occur. (recursively)
	# 3.) When you reach the leaf calculate the board score with your heuristic.
    return random.randint(1,1000)

def build_potential_outcomes(board):
    return []
