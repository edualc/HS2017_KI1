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
move_count = 0
coeff = [-1, 3, -1, 3, -1]
log_elastic = False
log_csv = False

'''========================================================================================
    Methods used directly by 2048.py
========================================================================================'''
def find_best_move(board):
    global move_count
    global coeff
    global score

    '''Which moves are possible? 1 for possible, 0 for not possible'''
    possible_moves_array = util.build_possible_moves_list(board)
    if console_logging:  
        print(f'possible_moves_array: {possible_moves_array}')

    '''What are the scores for each move?'''
    heuristic_array = build_heuristic_array(possible_moves_array, board)
        
    '''Choose the best move out of all possible'''
    best_move = util.index_min(heuristic_array)

    handle_logging(board, util.execute_move(best_move, board), best_move, heuristic_array)

    move_count += + 1
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
                
    # return combineable_tiles_count
    return util.round_nearest(combineable_tiles_count/7, 0.01)

def heuristics_empty_cells_count(board):
    # return util.cell_of_type_count(0, board)
    return util.round_nearest(util.cell_of_type_count(0, board) / 15, 0.01)

def heuristics_highest_tile_in_corner(board, board_to_check):
    # htic = 100
    htic = 1

    if util.get_position_of_highest_tile(board_to_check) == [0, 0]:
        htic = 0

    # return htic
    return util.round_nearest(htic, 0.01)

def heuristics_monotonous_row(board):
    # return sum(sum(board * goal))
    return util.round_nearest(sum(sum(board * goal)), 0.01)

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
    # return heuristic_score
    return util.round_nearest(heuristic_score / 41, 0.01)

'''========================================================================================
    Helper methods connected to heuristics used
    (general helper methods can be found in util.py)
========================================================================================'''

def handle_logging(board, best_board, best_move, heuristic_array):
    global file_writer

    if not log_elastic and not log_csv:
        return

    content = {
        'ai_id': ai_id,
        'move_count': move_count,
        'heuristics_empty_cells_count': heuristics_empty_cells_count(best_board),
        'heuristics_neighbour_difference': heuristics_neighbour_difference(best_board),
        'highest_tile': int(util.highest_tile(best_board)),
        'heuristics_highest_tile_in_corner': heuristics_highest_tile_in_corner(board, best_board),
        'heuristics_monotonous_row': int(util.round_nearest(heuristics_monotonous_row(best_board)/(heuristics_monotonous_row(board)), 0.01)),
        'best_move': best_move,
        'score': score,
        'heuristics_combineable_cells_count': heuristics_combineable_cells_count(best_move, board),
        'heuristics_total': heuristic_array[best_move],
        'coefficient_0_act': coeff[0],
        'coefficient_1_ndh': coeff[1],
        'coefficient_2_ecc': coeff[2],
        'coefficient_3_htic': coeff[3],
        'coefficient_4_morow': coeff[4]
    }

    if log_elastic:
        log.elastic_post(content)

    if log_csv:
        log_list = []
        for key, value in content.items():
            log_list.append(value)

        file_writer.writerow(log_list)

def build_heuristic_array(move_possible_array, board):
    heuristic_array = util.build_list(math.inf, 4)
    
    for i in range(4):
        if move_possible_array[i] > 0:
            board_to_check = util.execute_move(i, board)
            
            act = heuristics_combineable_cells_count(i, board)
            ndh = heuristics_neighbour_difference(board_to_check)
            ecc = heuristics_empty_cells_count(board_to_check)
            htic = heuristics_highest_tile_in_corner(board, board_to_check)
                
            # heuristic_array[i] = coeff[0] * act/7 + coeff[1] * (ndh/41) + coeff[2] * (ecc/15) + coeff[3] * htic + coeff[4] * (heuristics_monotonous_row(board_to_check) / heuristics_monotonous_row(board))
            heuristic_array[i] = coeff[0] * act + coeff[1] * ndh + coeff[2] * ecc + coeff[3] * htic + coeff[4] * (heuristics_monotonous_row(board_to_check) / heuristics_monotonous_row(board))

            # add heuristics together
            # heuristic_array[i] = (-2*act) + (4*ndh) - ecc - 50 * (heuristics_monotonous_row(board_to_check) / heuristics_monotonous_row(board)) # (1)
            # heuristic_array[i] = - (act/7) + 3*(ndh/41) - (ecc/15) + htic - heuristics_monotonous_row(board_to_check) / heuristics_monotonous_row(board) # (2) weighted
            # heuristic_array[i] = - 2*(act/7) + (ndh/41) - 4*(ecc/15) + htic - heuristics_monotonous_row(board_to_check) / heuristics_monotonous_row(board) # (3) weighted2
            # heuristic_array[i] = - (act/7) + 2*(ndh/41) - (ecc/15) + htic - 2 * heuristics_monotonous_row(board_to_check) / heuristics_monotonous_row(board) # (4) weighted3
            # heuristic_array[i] = 2*(ndh/41) + htic - 2 * heuristics_monotonous_row(board_to_check) / heuristics_monotonous_row(board) # (5) weighted4
            # heuristic_array[i] = (-2*act) + (4*ndh) - ecc - 100 * (heuristics_monotonous_row(board_to_check) / heuristics_monotonous_row(board)) # (6) weighted5

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

def print_csv_header(file_writer):
    file_writer.writerow([
        'ai_id',
        'move_count',
        'heuristics_empty_cells_count',
        'heuristics_neighbour_difference',
        'highest_tile',
        'heuristics_highest_tile_in_corner',
        'heuristics_monotonous_row',
        'best_move',
        'score',
        'heuristics_combineable_cells_count',
        'heuristics_total',
        'coefficient_0_act',
        'coefficient_1_ndh',
        'coefficient_2_ecc',
        'coefficient_3_htic',
        'coefficient_4_morow'
    ])