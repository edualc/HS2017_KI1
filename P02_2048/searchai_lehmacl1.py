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
import copy

# Author:       lauenchr & lehmacl1 (original by nneonneo)
# Date:		    23.10.2017
# Copyright:    Algorithm from https://github.com/nneonneo/2048-ai
# Description:  The logic to beat the game. Based on expectimax algorithm.

UP, DOWN, LEFT, RIGHT = 0, 1, 2, 3
move_args = [UP,DOWN,LEFT,RIGHT]
MAX_DEPTH = 3
CHANCE_2 = 0.9
CHANCE_4 = 0.1

'''
TODO: "Gewichtete" Heuristik ACT (grosse tiles mergbar priorisieren!)

Evaluation =
    128 (Constant)
    + (Number of Spaces x 128)
    + Sum of faces adjacent to a space { (1/face) x 4096 }
    + Sum of other faces { log(face) x 4 }
    + (Number of possible next moves x 256)
    + (Number of aligned values x 2)
Evaluation Details

128 (Constant)
This is a constant, used as a base-line and for other uses like testing.

+ (Number of Spaces x 128)
More spaces makes the state more flexible, we multiply by 128 (which is the median) since a grid filled with 128 faces is an optimal impossible state.

+ Sum of faces adjacent to a space { (1/face) x 4096 }
Here we evaluate faces that have the possibility to getting to merge, by evaluating them backwardly, tile 2 become of value 2048, while tile 2048 is evaluated 2.

+ Sum of other faces { log(face) x 4 }
In here we still need to check for stacked values, but in a lesser way that doesn't interrupt the flexibility parameters, so we have the sum of { x in [4,44] }.

+ (Number of possible next moves x 256)
A state is more flexible if it has more freedom of possible transitions.

+ (Number of aligned values x 2)
This is a simplified check of the possibility of having merges within that state, without making a look-ahead.

Note: The constants can be tweaked..
'''

goal = np.array([[65536, 32768, 16384, 8192], [512, 1024, 2048, 4096], [256, 128, 64, 32], [2, 4, 8, 16]])
# goal_flat = np.array([
#   [20, 18, 16, 14],
#   [ 8,  9, 10, 12],
#   [ 6,  5,  1,  1],
#   [ 4,  3,  1,  1]
# ]).flatten()
# goal = np.array([
#     (8, 5, 3, 1),
#     (4, 3, 1, 0),
#     (2, 1, 0, -1),
#     (1, 0, -1, -3)
# ])

goal_flat = goal.flatten()

Nb = np.array([
        (-1, 0),
        (0, -1),
        (0, 1),
        (1, 0)
    ])

low_goal_flat = np.array([
  [64,32,16, 4],
  [32,16, 8, 0],
  [16, 8, 0, 0],
  [ 4, 0, 0, 0]
]).flatten()

score = 0
move_count = 0

ai_id = 0

console_logging = False
file_writer = None
log_elastic = False
log_csv = False

def find_best_move(board):
  global move_count

  """find the best move for the next turn.
  It will split the workload in 4 process for each move."""
  bestmove = 0  
  result = [score_toplevel_move(i, board) for i in range(len(move_args))]

  bestmove = result.index(max(result))

  if console_logging:
    print(np.around(result,decimals=2))
    time.sleep(5)
  # time.sleep(move_count / 1000)

  handle_logging(util.execute_move(bestmove, board), bestmove)
  move_count += 1

  return bestmove
    
def score_toplevel_move(move, board):
  """Entry Point to score the first move."""
  board_to_check = util.execute_move(move, board)

  if util.board_equals(board, board_to_check):
    return -1

  htic = heuristics_highest_tile_in_corner(board_to_check)
  expectimax_score = expectimax_calc(0, board, 0, 0) + htic

  return expectimax_score
    
def expectimax_calc(move, old_board, depth, isChance):
  board_to_check = util.execute_move(move, old_board)

  if depth == MAX_DEPTH:
    return heuristic_value(move, board_to_check, old_board)
  
  if isChance == 1:
    avg = 0
    ecc = util.cell_of_type_count(0, board_to_check)
    if ecc == 0:
      possibility_multiplier = 1
    else:
      possibility_multiplier = 1 / ecc

    for x in range(4):
      for y in range(4):
        if board_to_check[x][y] == 0:
          board_to_check[x][y] = 2
          avg += possibility_multiplier * CHANCE_2 * expectimax_calc(move, old_board, depth + 1, 0)
          board_to_check[x][y] = 4
          avg += possibility_multiplier * CHANCE_4 * expectimax_calc(move, old_board, depth + 1, 0)
          board_to_check[x][y] = 0

    return avg
  else:
    results = []
    for m in move_args:
      check_board = util.execute_move(m, board_to_check)
      if util.board_equals(check_board, board_to_check):
        results.append(0)
      else:
        results.append(expectimax_calc(m, board_to_check, depth + 1, 1))
        
    return max(results)

'''========================================================================================
  Different heuristics calculations
========================================================================================'''

def heuristic_gradient_weighted(board_to_check, old_board):
  '''
  Multiplies each element of the given board with a predefined 
  goal board. The goal board has a monotonous gradient towards
  the top left position.
  The calculated value is divided by the value of the board
  before to keep the return value around 1.
  '''

  return 1
  board_gradient = heuristic_gradient(board_to_check)
  old_board_gradient = heuristic_gradient(old_board)

  if old_board_gradient == 0:
    old_board_gradient = board_gradient

  return board_gradient / old_board_gradient

def heuristic_gradient(board_to_check):
  return sum([b*g for b,g in zip(board_to_check.flatten(), goal_flat)])

def heuristic_weighted_merge(move, board):
  '''
  Checks all possible tile-merges with the given move and
  board and returns the score that is gained.
  '''

  score = 0.01

  if move < 2:
    '''UP/DOWN'''
    for y in range(4):
      if (board[0][y] == board[1][y]) and (util._to_val(board[0][y]) != 0):
        '''merge in top spots, nonzero => XX??'''
        score += board[0][y]

        if (board[2][y] == board[3][y]) and (util._to_val(board[2][y]) != 0):
          '''merge in whole row, nonzero => XXYY'''
          score += board[2][y]

      elif (board[1][y] == board[2][y]) and (util._to_val(board[1][y]) != 0):
        '''merge in middle spots, nonzero => AXX?'''
        score += board[1][y]

      elif (board[2][y] == board[3][y]) and (util._to_val(board[2][y]) != 0):
        '''merge in bottom spots, nonzero => ABXX'''
        score += board[2][y]
      
  else:
    '''LEFT/RIGHT'''
    for x in range(4):
      if (board[x][0] == board[x][1]) and (util._to_val(board[x][0]) != 0):
        '''merge in left spots, nonzero => XX??'''
        score += board[x][0]

        if (board[x][2] == board[x][3]) and (util._to_val(board[x][2]) != 0):
          '''merge in whole column, nonzero => XXYY'''
          score += board[x][2]

      elif (board[x][1] == board[x][2]) and (util._to_val(board[x][1]) != 0):
        '''merge in middle spots, nonzero => AXX?'''
        score += board[x][1]

      elif (board[x][2] == board[x][3]) and (util._to_val(board[x][2]) != 0):
        '''merge in right spots, nonzero => ABXX'''
        score += board[x][2]

  '''x2 to match the resulting tile value instead of source tile values'''
  return 2 * score

def heuristic_merge_count(move, board):
  '''
  TODO
  '''

  merges = 0

  if move < 2:
    '''UP/DOWN'''
    for y in range(4):
      if (board[0][y] == board[1][y]) and (util._to_val(board[0][y]) != 0):
        '''merge in top spots, nonzero => XX??'''
        merges += 1

        if (board[2][y] == board[3][y]) and (util._to_val(board[2][y]) != 0):
          '''merge in whole row, nonzero => XXYY'''
          merges += 1

      elif (board[1][y] == board[2][y]) and (util._to_val(board[1][y]) != 0):
        '''merge in middle spots, nonzero => AXX?'''
        merges += 1

      elif (board[2][y] == board[3][y]) and (util._to_val(board[2][y]) != 0):
        '''merge in bottom spots, nonzero => ABXX'''
        merges += 1
      
  else:
    '''LEFT/RIGHT'''
    for x in range(4):
      if (board[x][0] == board[x][1]) and (util._to_val(board[x][0]) != 0):
        '''merge in left spots, nonzero => XX??'''
        merges += 1

        if (board[x][2] == board[x][3]) and (util._to_val(board[x][2]) != 0):
          '''merge in whole column, nonzero => XXYY'''
          merges += 1

      elif (board[x][1] == board[x][2]) and (util._to_val(board[x][1]) != 0):
        '''merge in middle spots, nonzero => AXX?'''
        merges += 1

      elif (board[x][2] == board[x][3]) and (util._to_val(board[x][2]) != 0):
        '''merge in right spots, nonzero => ABXX'''
        merges += 1

  '''x2 to match the resulting tile value instead of source tile values'''
  return merges

def heuristic_empty_tiles(board):
  '''
  Returns the amount of empty tiles in the given board, weighted
  to have a value between 0 (no spaces) and 1 (1 being an empty board)
  '''

  empty_tiles_count_weighted = util.cell_of_type_count(0, board) / 15
  return util.round_nearest(empty_tiles_count_weighted, 0.01)

def heuristics_highest_tile_in_corner(board_to_check):
    htic = 0

    if util.get_position_of_highest_tile(board_to_check) == [0, 0]:
      htic = 1000000000

    return htic

'''========================================================================================
  Helper methods connected to heuristics used
  (general helper methods can be found in util.py)
========================================================================================'''

def heuristic_value(move, board_to_check, old_board):
  weighted_merge = heuristic_weighted_merge(move, board_to_check)
  empty_tiles_multiplier = (heuristic_empty_tiles(board_to_check) + 0.5)
  gradient = heuristic_gradient(board_to_check)

  return (gradient + weighted_merge)

def handle_logging(best_board, best_move):
  if log_elastic:
    content = {
      'ai_id': ai_id,
      'ai_type': __name__,
      'move_count': move_count,
      'highest_tile': int(util.highest_tile(best_board)),
      'best_move': best_move,
      'score': score
    }

    log.elastic_post(content)

def _empty_cells_weighted(board):
  '''
  only used for expectimax calc
  '''
  count = util.cell_of_type_count(0, board)

  if count == 0:
    return 1

  return count

'''========================================================================================
  Unused heuristics
========================================================================================'''

def heuristic_low_tiles(board):
  '''
  Returns the amount of 2 and 4 tiles on the given board.
  '''

  return (util.cell_of_type_count(2, board) + util.cell_of_type_count(4, board)) / 8 + 0.1

def heuristic_low_tiles_gradient(board, old_board):
  '''
  Similar to :heuritic_gradient, we check for 2 and 4 tiles in the
  given board and gradient-weight them depending on their position
  and the importance of them being there.
  The value is divided by the value of the old board and stays around 1. 
  '''

  low_board = board.copy()
  for row in low_board:
    for cell in row:
      if util._to_val(cell) > 4:
        cell = 0

  low_old_board = old_board.copy()
  for row in low_old_board:
    for cell in row:
      if util._to_val(cell) > 4:
        cell = 0

  board_low_gradient = sum([b*g for b,g in zip(low_board.flatten(), low_goal_flat)])
  old_board_low_gradient = sum([o*g for o,g in zip(low_old_board.flatten(), low_goal_flat)])

  if (board_low_gradient == 0) or (old_board_low_gradient == 0):
    return 1

  return board_low_gradient / old_board_low_gradient

def heuristic_exponent_difference(board_to_check):
  score = 0
  
  for x in range(4):
    for y in range(4):
      score += (goal[x][y] * board_to_check[x][y])

      for mod in range(4):
        xN = x + Nb[mod][0]
        yN = y + Nb[mod][1]
    
        if xN < 4 and xN >= 0 and yN < 4 and yN >= 0:
          xPot = math.frexp(board_to_check[x][y])[1] - 1
          xNPot = math.frexp(board_to_check[xN][yN])[1] - 1
          diffPot = abs(xPot - xNPot)
          
          if diffPot == 0:
            score += board_to_check[x][y]
          else:
            score += (1 / diffPot * board_to_check[x][y]) / 2
  
  return score