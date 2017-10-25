import game
import sys
import numpy
import math

import util
import log

# Author:      chrn (original by nneonneo)
# Date:        11.11.2016
# Copyright:   Algorithm from https://github.com/nneonneo/2048-ai
# Description: The logic to beat the game. Based on expectimax algorithm.

UP, DOWN, LEFT, RIGHT = 0, 1, 2, 3
move_args = [UP,DOWN,LEFT,RIGHT]

score = 0
move_count = 0

W = numpy.array([
        (8, 5, 3, 1),
        (4, 3, 1, 0),
        (2, 1, 0, -1),
        (1, 0, -1, -3)
    ])

Nb = numpy.array([
        (-1, 0),
        (0, -1),
        (0, 1),
        (1, 0)
    ])

def find_best_move(board):
    global move_count
    """
    find the best move for the next turn.
    It will split the workload in 4 process for each move.
    """
    bestmove = -1
    
    result = [score_toplevel_move(i, board) for i in range(len(move_args))]
    maxResult = max(result)
    
    if maxResult != 0:
        bestmove = result.index(maxResult)
        print(maxResult)
    
    #for m in move_args:
    #    print(m)
    #    print(result[m])
    
    handle_logging(util.execute_move(bestmove, board), bestmove)
    move_count += 1
    
    return bestmove
    
def score_toplevel_move(move, board):
    """
    Entry Point to score the first move.
    """
    newboard = execute_move(move, board)

    if board_equals(board, newboard):
        return 0
    
	# TODO:
	# Implement the Expectimax Algorithm.
	# 1.) Start the recursion until it reach a certain depth
	# 2.) When you don't reach the last depth, get all possible board states and 
	#		calculate their scores dependence of the probability this will occur. (recursively)
	# 3.) When you reach the leaf calculate the board score with your heuristic.
    maxDepth = 3
    minDepth = 2
    calcDepth = min(minDepth + (4 - (int)(empty_cells_count(board) / 4)), maxDepth)
    
    return expectimax_calc(0, newboard, 0, calcDepth, 0);
    
    #return random.randint(1,1000)

def expectimax_calc(depth, board, isChance, maxDepth, currScore):
    currScore += 1 / (depth + 1) * heuristic_value(board)
    
    if depth >= maxDepth:
        return currScore
    
    if isChance == 1:
        avg = 0
        chance_2 = 0.9
        chance_4 = 0.1
        empty_counter = 0
        
        for x in range(4):
            for y in range(4):
                if board[x][y] != 0:
                    continue
                
                empty_counter += 1
                
                board[x][y] = 2
                avg += chance_2 * expectimax_calc(depth + 1, board, 0, maxDepth, currScore)
                
                board[x][y] = 4
                avg += chance_4 * expectimax_calc(depth + 1, board, 0, maxDepth, currScore)
                
                board[x][y] = 0
                    
        return (avg / empty_counter)
    else:
        results = []
        for m in move_args:
            newboard = execute_move(m, board)
            if board_equals(board,newboard):
                results.append(0)
            else:
                results.append(expectimax_calc(depth + 1, newboard, 1, maxDepth, currScore))
            
        return max(results)

def empty_cells_count(board):
    count = 0
    
    for row in board:
        for cell in row:
            if cell == 0:
                count += 1
    
    return count

def heuristic_value(board):    
    score = 0
    
    for x in range(4):
        for y in range(4):
            score += (W[x][y] * board[x][y])
    
            for mod in range(4):
                xN = x + Nb[mod][0]
                yN = y + Nb[mod][1]
            
                if xN < 4 and xN >= 0 and yN < 4 and yN >= 0:
                    xPot = math.frexp(board[x][y])[1] - 1
                    xNPot = math.frexp(board[xN][yN])[1] - 1
                    diffPot = abs(xPot - xNPot)
                    
                    if diffPot == 0:
                        score += board[x][y]
                    else:
                        score += (1 / diffPot * board[x][y]) / 2
    
    return score

def execute_move(move, board):
    """
    move and return the grid without a new random tile 
	It won't affect the state of the game in the browser.
    """

    UP, DOWN, LEFT, RIGHT = 0, 1, 2, 3

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
