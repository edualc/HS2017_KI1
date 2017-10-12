import random
import game
import sys
import time
import math
import csv

# Author:				chrn (original by nneonneo)
# Date:				11.11.2016
# Description:			The logic of the AI to beat the game.

UP, DOWN, LEFT, RIGHT = 0, 1, 2, 3

file_writer = None
ai_id = 0

def find_best_move(board):
    bestmove = -1    
	
	# TODO:
	# Build a heuristic agent on your own that is much better than the random agent.
	# Your own agent don't have to beat the game.
    bestmove = find_best_move_random_agent(board)
    return bestmove

'''
1) play 'randomly' with adjusted weight values, one move direction is prohibited
2) when space gets crowded, try to see which move keeps your board cleanest => which move keeps the crowdedness lowest
3) get a heuristic for "crowdedness" => how many spaces are empty
4) get a heuristic for "difference in sizes" => how much is the difference to the closest neighbouring tile
5) get a heuristic for "amount of tiles possibly combined"
6) try combining as much as possible
    
7) Heuristic: the bigger the tile, the more important it is to keep it close to higher tiles
8) don't move corner once highest tile is inside a corner
9) todo: echo stats as csv/log?
'''
def find_best_move_random_agent(board):
    print(' *** ')
    
    print_board(board)
    
    print(' * ')
    ecc = empty_cells_count(board)
    print(f'Empty Cells Count   \t {ecc} => ',
          'PANIC!' if ecc < 4 else 'normal')
    ndh = neighbour_difference_heuristic(board)
    print(f'Neighbour Difference\t {ndh}')
    ht = highest_tile(board)
    print(f'Highest Tile        \t {ht}')
    htich = highest_tile_in_corner_heuristic(board)
    print(f'Highest in Corner   \t {htich}')
    
    '''
    Which moves are possible? 1 for possible, 0 for not possible
    '''
    move_possible_array = [0, 0, 0, 0]
    
    for i in range(0,4):
        if move_possible(i, board):
            move_possible_array[i] = 1
            
    print(move_possible_array)
            
    '''
    What are the scores for each move?
    '''
    heuristic_array = [999, 999, 999, 999]
    
    for i in range(0,4):
        if move_possible_array[i] > 0:
            board_to_check = execute_move(i, board)
            
            htic = 100
            
            act = amount_of_combineable_tiles(i, board)
            ndh = neighbour_difference_heuristic(board_to_check)
            ecc = empty_cells_count(board_to_check)
            if keep_highest_tile_in_corner(i, board):
                htic = 0
                
            # add heuristics together
            heuristic_array[i] = (-2*act) + (4*ndh) - ecc + htic
        
    '''
    Choose the best move out of all possible
    '''
    best_move = 0
    for i in range(0,4):
        if heuristic_array[i] < heuristic_array[best_move]:
            best_move = i
            
    _log([ai_id, ecc, ndh, ht, htich, move_possible_array, heuristic_array, best_move, to_score(board)]) # logging
            
    
    return best_move
        
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

def print_board(board):
    for row in board:
        for cell in row:
            print('%8d' % cell, end=' ')
        print()

def _to_val(cell):
    if cell == 0: return 0
    return cell

def to_val(board):
    return [[_to_val(cell) for cell in row] for row in board]

def _to_score(cell):
    if cell <= 1:
        return 0
    return (cell-1) * (2**cell)

def to_score(board):
    return [[_to_score(cell) for cell in row] for row in board]

    '''
    #=============
    # Own Methods
    #=============
    '''
def empty_cells_count(board):
    count = 0
    for row in board:
        for cell in row:
            if _to_val(cell) == 0:
                count += 1
    return count

def move_possible(move, board):
    return not board_equals(execute_move(move, board), board)

def cell_of_type_count(cell_val, board):
    cell_count = 0
    for row in board:
        for cell in row:
            if (_to_val(cell) == cell_val):
                cell_count += 1
    return cell_count

def amount_of_combineable_tiles(move, board):
    new_board = execute_move(move, board)
    
    combineable_tiles_count = 0
    
    '''
    Check Directions
    '''
    if (move == 0) or (move == 1):
        '''
        0,1 = UP, DOWN
        '''
        for y in range(0,4):
            if (new_board[0][y] == new_board[1][y]):
                if (new_board[1][y] == new_board[2][y]) and (new_board[2][y] == new_board[3][y]):
                    # xxxx
                    combineable_tiles_count += 2
                else:
                    # xxab. xxxa
                    combineable_tiles_count += 1
            elif (new_board[1][y] == new_board[2][y]):
                # axxx, axxb
                combineable_tiles_count += 1
            elif (new_board[2][y] == new_board[3][y]):
                # abxx
                combineable_tiles_count += 1
    else:
        '''
        2,3 = LEFT, RIGHT
        '''
        for x in range(0,4):
            if (new_board[x][0] == new_board[x][1]):
                if (new_board[x][1] == new_board[x][2]) and (new_board[x][2] == new_board[x][3]):
                    # xxxx
                    combineable_tiles_count += 2
                else:
                    # xxab. xxxa
                    combineable_tiles_count += 1
            elif (new_board[x][1] == new_board[x][2]):
                # axxx, axxb
                combineable_tiles_count += 1
            elif (new_board[x][2] == new_board[x][3]):
                # abxx
                combineable_tiles_count += 1
                
    return combineable_tiles_count

def neighbour_difference_heuristic(board):
    heuristic_score = 0 # initialize score
    heuristics_board = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    
    for x in range(0,4):
        for y in range(0,4):
            current_tile = board[x][y]
            current_tile_score = 1000 # initialize too big
            
            # check top neighbour
            if (y-1) in range(0,4):
                top_score = _evaluate_tile_ratio(current_tile, board[x][y-1])
                if top_score < current_tile_score:
                    current_tile_score = top_score
            
            # check right neighbour
            if (x+1) in range(0,4):
                right_score = _evaluate_tile_ratio(current_tile, board[x+1][y])
                if right_score < current_tile_score:
                    current_tile_score = right_score
            
            # check bottom neighbour
            if (y+1) in range(0,4):
                bottom_score = _evaluate_tile_ratio(current_tile, board[x][y+1])
                if bottom_score < current_tile_score:
                    current_tile_score = bottom_score
            
            # check left neighbour
            if (x-1) in range(0,4):
                left_score = _evaluate_tile_ratio(current_tile, board[x-1][y])
                if left_score < current_tile_score:
                    current_tile_score = left_score
            
            heuristic_score += current_tile_score
            heuristics_board[x][y] = current_tile_score
            
#    print_board(heuristics_board)
    return heuristic_score

def highest_tile_in_corner_heuristic(board):
    highest_cell = highest_tile(board)
    if (_to_val(board[0][0]) >= highest_cell) or (_to_val(board[0][3]) >= highest_cell) or (_to_val(board[3][0]) >= highest_cell) or (_to_val(board[3][3]) >= highest_cell):
        return 0
    return 5
    
def highest_tile(board):
    highest_cell = 2;
    for row in board:
        for cell in row:
            if _to_val(cell) > highest_cell:
                highest_cell = _to_val(cell)
    return highest_cell

def keep_highest_tile_in_corner(move, board):
    highest_cell = highest_tile(board)
    new_board = execute_move(move, board)
    result = False
    
    if (_to_val(new_board[0][0]) >= highest_cell) or (_to_val(new_board[0][3]) >= highest_cell) or (_to_val(new_board[3][0]) >= highest_cell) or (_to_val(new_board[3][3]) >= highest_cell):
        result = True
    #print(f'move: {move} // {result}')   
    return result

def _evaluate_tile_ratio(cell, neighbour_cell):
    '''
    Compares two cells and returns their difference in exponent
    '''
    current_tile_exp = math.frexp(_to_val(cell))[1]
    neighbour_tile_exp = math.frexp(_to_val(neighbour_cell))[1]
    
    if neighbour_tile_exp == 0:
        return current_tile_exp
    
    ratio = current_tile_exp - neighbour_tile_exp

    if ratio == 0:
        return ratio

    if ratio < 1:
        ratio = -1 * ratio

    return ratio

def _log(line):
    if file_writer is None:
        return
    
    file_writer.writerow(line)
    