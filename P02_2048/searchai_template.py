import random
import game
import sys
import numpy as np
import copy
import csv
import math
import time

import util
import log

# Author:       lauenchr & lehmacl1 (original by nneonneo)
# Date:		    23.10.2017
# Copyright:    Algorithm from https://github.com/nneonneo/2048-ai
# Description:  The logic to beat the game. Based on expectimax algorithm.

UP, DOWN, LEFT, RIGHT = 0, 1, 2, 3
move_args = [UP,DOWN,LEFT,RIGHT]
MAX_DEPTH = 2
CHANCE_2 = 0.9
CHANCE_4 = 0.1

'''
TODO: "Gewichtete" Heuristik ACT (grosse tiles mergbar priorisieren!)
'''

goal = np.array([[2, 4, 8, 16], [256, 128, 64, 32], [512, 1024, 2048, 4096], [65536, 32768, 16384, 8192]])
score = 0
move_count = 0

ai_id = 0
# coeff = [1, 8, 7, 10, 0] # act / ndh / ecc / htic / morow

console_logging = False
file_writer = None
log_elastic = False
log_csv = False

def find_best_move(board):
    """find the best move for the next turn.
    It will split the workload in 4 process for each move."""
    bestmove = -1    
    result = [score_toplevel_move(i, board) for i in range(len(move_args))]

    bestmove = result.index(max(result))

    if console_logging:
        print(np.around(result,decimals=2))
        # time.sleep(5)

    return bestmove
    
def score_toplevel_move(move, board):
    """Entry Point to score the first move."""
    board_to_check = util.execute_move(move, board)

    if util.board_equals(board, board_to_check):
        return 0

    expectimax_score = expectimax_calc(board_to_check, board, 0, 0)

    return expectimax_score
    
def expectimax_calc(board_to_check, old_board, depth, isChance):
    # TODO: kann man bei der Suche abbrechen, :higest_tile aus der Ecke getrieben wird?
    # => welchen Einfluss hat dies auf Anfangsszenarien?

    if depth == MAX_DEPTH:
        return heuristic_value(board_to_check, old_board)
    
    if isChance == 1:
        avg = 0
        
        empty_cells_count = util.cell_of_type_count(0, board_to_check)
        if empty_cells_count == 0:
            moves_to_check_count = 0
            return 0
        else:
            possibility_multiplier = 1 / empty_cells_count

        for x in range(4):
            for y in range(4):
                if board_to_check[x][y] == 0:
                    board_to_check[x][y] = 2
                    avg += possibility_multiplier * CHANCE_2 * expectimax_calc(board_to_check, old_board, depth + 1, 0)
                    board_to_check[x][y] = 4
                    avg += possibility_multiplier * CHANCE_4 * expectimax_calc(board_to_check, old_board, depth + 1, 0)
                    board_to_check[x][y] = 0
                    
        return avg
    else:
        results = []
        for m in move_args:
            results.append(expectimax_calc(util.execute_move(m, board_to_check), board_to_check, depth + 1, 1))
            
        return max(results)

'''========================================================================================
    Different heuristics calculations
========================================================================================'''

# TODO: Add heuristic calculations

'''========================================================================================
    Helper methods connected to heuristics used
    (general helper methods can be found in util.py)
========================================================================================'''

def heuristic_value(board_to_check, old_board):
    return 1;
