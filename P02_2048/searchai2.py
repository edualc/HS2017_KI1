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

ai_id = 0
console_logging = False
file_writer = None
goal = np.array([[65536, 32768, 16384, 8192], [512, 1024, 2048, 4096], [256, 128, 64, 32], [2, 4, 8, 16]])
score = 0
move_count = 0
coeff = [-1, 3, -1, 0, -1]
log_elastic = False
log_csv = False

def find_best_move(board):
    best_move = -1    
    best_move = a_very_lauenchr_expectimax_calc(0, board, 0, None)

    possible_moves = util.build_possible_moves_list(board)
    heuristic_array = [0 for x in range(4)]

    for m in move_args:
        if possible_moves[m] > 0:
            heuristic_array[m] = a_very_lauenchr_expectimax_calc(0, util.execute_move(move_args[m], board), 0, board)

    best_move = move_args[heuristic_array.index(max(heuristic_array))]
    return best_move

def a_very_lauenchr_expectimax_calc(depth, new_board, isChance, old_board):
    if depth == MAX_DEPTH:
        return heuristic_value(new_board, old_board)
    
    if isChance == 1:
        avg = 0
        chance_2 = 0.9
        chance_4 = 0.1

        ecc = heuristics_empty_cells_count(new_board)
        if ecc == 0:
            chance_cel = 0
        else:
            chance_sel = 1 / heuristics_empty_cells_count(new_board)
        
        for x in range(4):
            for y in range(4):
                if new_board[x][y] == 0:
                    new_board[x][y] = 2
                    avg += chance_sel * chance_2 * a_very_lauenchr_expectimax_calc(depth + 1, new_board, 0, old_board)
                    new_board[x][y] = 4
                    avg += chance_sel * chance_4 * a_very_lauenchr_expectimax_calc(depth + 1, new_board, 0, old_board)
                    new_board[x][y] = 0
                    
        return avg
    else:
        results = []
        for m in move_args:
            results.append(a_very_lauenchr_expectimax_calc(depth + 1, util.execute_move(m, new_board), 1, new_board))
            
        return max(results)

def heuristic_value(board_to_check, old_board):
    act = heuristics_combineable_cells_count(board_to_check, old_board)
    ndh = heuristics_neighbour_difference(board_to_check)
    ecc = heuristics_empty_cells_count(board_to_check)
    htic = heuristics_highest_tile_in_corner(board_to_check)
        
    return coeff[0] * act + coeff[1] * ndh + coeff[2] * ecc + coeff[3] * htic + coeff[4] * (heuristics_monotonous_row(board_to_check) / heuristics_monotonous_row(old_board))

'''========================================================================================
    Different heuristics calculations
========================================================================================'''

def heuristics_combineable_cells_count(new_board, old_board):
    '''
    Clunky evaluation: what was the last move? UP/DOWN or LEFT/RIGHT?
    TODO: Refactoring
    '''
    if util.board_equals(util.execute_move(UP, old_board), old_board):
        move = UP
    elif util.board_equals(util.execute_move(DOWN, old_board), old_board):
        move = DOWN
    elif util.board_equals(util.execute_move(LEFT, old_board), old_board):
        move = LEFT
    else:
        move = RIGHT

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

def heuristics_highest_tile_in_corner(board_to_check):
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