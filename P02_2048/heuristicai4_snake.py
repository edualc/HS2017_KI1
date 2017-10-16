import csv
import math
import random
import sys
import time

import game
import util
import log
import numpy as np

# Author:				edualc (original by nneonneo, edited by chrn)
# Date:				10.10.2017
# Description:		The logic of the AI to beat the game.

'''
- Crowdedness: How many spaces are empty?           => heuristics_empty_cells_count
- Difference in sizes: Nearest upgrade neighbour?   => heuristics_neighbour_difference
- Possible merges: How many can be merged?          => heuristics_combineable_cells_count
- Corner strategy: Is the max. tile in a corner?    => heuristics_highest_tile_in_corner
- Monotonous rows: Prepare easy upgrade path        => heuristics_monotonous_row
'''

UP, DOWN, LEFT, RIGHT = 0, 1, 2, 3

ai_id = 0
console_logging = False
file_writer = None
goal = np.array([[65536, 32768, 16384, 8192], [512, 1024, 2048, 4096], [256, 128, 64, 32], [2, 4, 8, 16]])
score = 0

'''========================================================================================
    Methods used directly by 2048.py
========================================================================================'''
def find_best_move(board):
    '''Which moves are possible? 1 for possible, 0 for not possible'''
    possible_moves_array = util.build_possible_moves_list(board)
    if console_logging:  
        print(f'possible_moves_array: {possible_moves_array}')

    '''What are the scores for each move?'''
    heuristic_array = build_heuristic_array(possible_moves_array, board)
        
    '''Choose the best move out of all possible'''
    best_move = util.index_min(heuristic_array)
    
    log.log(file_writer, [ai_id, heuristics_empty_cells_count(board), heuristics_neighbour_difference(board), util.highest_tile(board), heuristics_highest_tile_in_corner(board, util.execute_move(best_move, board)), best_move, score, heuristics_combineable_cells_count(best_move, board), possible_moves_array, heuristic_array]) # logging
    return best_move

'''========================================================================================
    Different heuristics calculations
========================================================================================'''
def heuristics_combineable_cells_count(move, board):
    new_board = util.execute_move(move, board)
    combineable_tiles_count = 0
    
    '''Check Directions'''
    if (move == UP) or (move == DOWN):
        '''0,1 = UP, DOWN'''
        for y in range(4):
            if (new_board[0][y] == new_board[1][y]) and (new_board[0][y] != 0):
                if (new_board[1][y] == new_board[2][y]) and (new_board[2][y] == new_board[3][y]):
                    # xxxx
                    combineable_tiles_count += 2
                else:
                    # xxab. xxxa
                    combineable_tiles_count += 1
            elif (new_board[1][y] == new_board[2][y]) and (new_board[1][y] != 0):
                # axxx, axxb
                combineable_tiles_count += 1
            elif (new_board[2][y] == new_board[3][y]) and (new_board[2][y] != 0):
                # abxx
                combineable_tiles_count += 1
    else:
        '''2,3 = LEFT, RIGHT'''
        for x in range(4):
            if (new_board[x][0] == new_board[x][1]) and (new_board[x][0] != 0):
                if (new_board[x][1] == new_board[x][2]) and (new_board[x][2] == new_board[x][3]):
                    # xxxx
                    combineable_tiles_count += 2
                else:
                    # xxab. xxxa
                    combineable_tiles_count += 1
            elif (new_board[x][1] == new_board[x][2]) and (new_board[x][1] != 0):
                # axxx, axxb
                combineable_tiles_count += 1
            elif (new_board[x][2] == new_board[x][3]) and (new_board[x][2] != 0):
                # abxx
                combineable_tiles_count += 1
                
    return combineable_tiles_count

def heuristics_empty_cells_count(board):
    return util.cell_of_type_count(0, board)

def heuristics_highest_tile_in_corner(board, board_to_check):
    htic = 100

    if util.get_position_of_highest_tile(board_to_check) == [0, 0]:
        htic = 0

    return htic

def heuristics_monotonous_row(board):
    return sum(sum(board * goal))

def heuristics_neighbour_difference(board):
    heuristic_score = 0 # initialize score
    neighbour_difference_board = util.build_list_2d(0, 4, 4)
    
    for x in range(4):
        for y in range(4):
            current_tile = board[x][y]
            current_tile_score = math.inf
            
            # check left neighbour
            if y - 1 in range(4):
                top_score = _evaluate_tile_ratio(current_tile, board[x][y-1])
                if top_score < current_tile_score:
                    current_tile_score = top_score
            
            # check top neighbour
            if x + 1 in range(4):
                right_score = _evaluate_tile_ratio(current_tile, board[x+1][y])
                if right_score < current_tile_score:
                    current_tile_score = right_score
            
            # check right neighbour
            if y + 1 in range(4):
                bottom_score = _evaluate_tile_ratio(current_tile, board[x][y+1])
                if bottom_score < current_tile_score:
                    current_tile_score = bottom_score
            
            # check bottom neighbour
            if x - 1 in range(4):
                left_score = _evaluate_tile_ratio(current_tile, board[x-1][y])
                if left_score < current_tile_score:
                    current_tile_score = left_score
            
            heuristic_score += current_tile_score
            neighbour_difference_board[x][y] = current_tile_score
    
    if console_logging:
        print(f'neighbour_difference_board: {neighbour_difference_board}')
    return heuristic_score

'''========================================================================================
    Helper methods connected to heuristics used
    (general helper methods can be found in util.py)
========================================================================================'''

def build_heuristic_array(move_possible_array, board):
    heuristic_array = util.build_list(math.inf, 4)
    
    for i in range(4):
        if move_possible_array[i] > 0:
            board_to_check = util.execute_move(i, board)
            
            act = heuristics_combineable_cells_count(i, board)
            ndh = heuristics_neighbour_difference(board_to_check)
            ecc = heuristics_empty_cells_count(board_to_check)
            htic = heuristics_highest_tile_in_corner(board, board_to_check)
                
            # add heuristics together
            # heuristic_array[i] = (-2*act) + (4*ndh) - ecc - 50 * (heuristics_monotonous_row(board_to_check) / heuristics_monotonous_row(board)) # (1)
            # heuristic_array[i] = - (act/7) + 3*(ndh/41) - (ecc/15) + htic - heuristics_monotonous_row(board_to_check) / heuristics_monotonous_row(board) # (2) weighted
            # heuristic_array[i] = - 2*(act/7) + (ndh/41) - 4*(ecc/15) + htic - heuristics_monotonous_row(board_to_check) / heuristics_monotonous_row(board) # (3) weighted2
            # heuristic_array[i] = - (act/7) + 2*(ndh/41) - (ecc/15) + htic - 2 * heuristics_monotonous_row(board_to_check) / heuristics_monotonous_row(board) # (4) weighted3
            # heuristic_array[i] = 2*(ndh/41) + htic - 2 * heuristics_monotonous_row(board_to_check) / heuristics_monotonous_row(board) # (5) weighted4
            heuristic_array[i] = (-2*act) + (4*ndh) - ecc - 100 * (heuristics_monotonous_row(board_to_check) / heuristics_monotonous_row(board)) # (6) weighted5

            # TODO!
            # ==============================
            # - each heuristic on its own with the monotonous row
            # ==============================

    return heuristic_array

def _evaluate_tile_ratio(cell, neighbour_cell):
    '''Compares two cells and returns their absolute difference in exponent'''
    current_tile_exp = math.frexp(util._to_val(cell))[1]
    neighbour_tile_exp = math.frexp(util._to_val(neighbour_cell))[1]
    
    if neighbour_tile_exp == 0:
        return current_tile_exp
    
    ratio = current_tile_exp - neighbour_tile_exp

    return math.fabs(ratio)
