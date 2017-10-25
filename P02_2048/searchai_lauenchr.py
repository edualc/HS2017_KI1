import random
import copy
import game
import sys

# Author:      chrn (original by nneonneo)
# Date:        11.11.2016
# Copyright:   Algorithm from https://github.com/nneonneo/2048-ai
# Description: The logic to beat the game. Based on expectimax algorithm.

UP, DOWN, LEFT, RIGHT = 0, 1, 2, 3
move_args = [UP,DOWN,LEFT,RIGHT]

def find_best_move(board):
    """
    find the best move for the next turn.
    It will split the workload in 4 process for each move.
    """
    bestmove = -1    
    
    result = [score_toplevel_move(i, board) for i in range(len(move_args))]
    
    bestmove = result.index(max(result))
    
    #for m in move_args:
    #    print(m)
    #   print(result[m])
    
    return bestmove
    
def score_toplevel_move(move, board):
    """
    Entry Point to score the first move.
    """
    newboard = execute_move(move, board)

    if board_equals(board,newboard):
        return 0
	# TODO:
	# Implement the Expectimax Algorithm.
	# 1.) Start the recursion until it reach a certain depth
	# 2.) When you don't reach the last depth, get all possible board states and 
	#		calculate their scores dependence of the probability this will occur. (recursively)
	# 3.) When you reach the leaf calculate the board score with your heuristic.
    return expectimax_calc(0, newboard, 0);
    
    #return random.randint(1,1000)

def expectimax_calc(depth, board, isChance):
    maxDepth = 3
    
    if depth == maxDepth:
        return heuristic_value(board)
    
    if isChance == 1:
        avg = 0
        chance_2 = 0.9
        chance_4 = 0.1
        chance_sel = 1 / empty_cells_count(board)
        
        for x in range(4):
            for y in range(4):
                if board[x][y] == 0:
                    board[x][y] = 2
                    avg += chance_sel * chance_2 * expectimax_calc(depth + 1, board, 0)
                    board[x][y] = 4
                    avg += chance_sel * chance_4 * expectimax_calc(depth + 1, board, 0)
                    board[x][y] = 0
                    
        return avg
    else:
        results = []
        for m in move_args:
            results.append(expectimax_calc(depth + 1, execute_move(m, board), 1))
            
        return max(results)

def heuristic_value(board):    
    weightingHtiC = 12
    weightingFreeTile = 1
    
    val = 0
    val += weightingHtiC * highest_tile_in_corner(board)
    val += weightingFreeTile * empty_cells_count(board)
    return val

def highest_tile(board):
    highest_cell = 2
    for row in board:
        for cell in row:
            if cell > highest_cell:
                highest_cell = cell
    
    return highest_cell

def highest_tile_in_corner(board):
    ht = highest_tile(board)
    if (board[0][0] == ht):
        return 1
    else:
        return 0

def empty_cells_count(board):
    count = 0
    
    for row in board:
        for cell in row:
            if cell == 0:
                count += 1
    
    return count

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
