#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author:      chrn (original by nneonneo)
# Date:        11.11.2016
# Copyright:   https://github.com/nneonneo/2048-ai
# Description: Helps the user achieve a high score in a real game of 2048 by using a move searcher.
#              This Script initialize the AI and controls the game flow.


from __future__ import print_function

import time
import datetime
import os
import searchai_lehmacl1    #for task 3
import searchai_lauenchr2    #for task 3
import searchai    #for task 3
import heuristicai2 #for task 2
import heuristicai2_weighted #for task 2
import heuristicai4_snake #for task 2
import csv

games_played = []

'''========================================================================================
    AI Configuration & Logging Behaviour
========================================================================================'''
current_ai = searchai_lauenchr2
games_to_be_played = 10
log_each_game_as_csv = False
log_totals_as_csv = False
log_elastic = True

def print_board(m):
    for row in m:
        for c in row:
            print('%8d' % c, end=' ')
        print()

def _to_val(c):
    if c == 0: return 0
    return c

def to_val(m):
    return [[_to_val(c) for c in row] for row in m]

def _to_score(c):
    if c <= 1:
        return 0
    return (c-1) * (2**c)

def to_score(m):
    return [[_to_score(c) for c in row] for row in m]

def find_best_move(board):
    return current_ai.find_best_move(board)

def movename(move):
    return ['up', 'down', 'left', 'right'][move]

def play_game(gamectrl):
    moveno = 0
    start = time.time()
    while 1:
        state = gamectrl.get_status()
        if state == 'ended':
            break
        elif state == 'won':
            time.sleep(0.75)
            gamectrl.continue_game()

        moveno += 1
        board = gamectrl.get_board()
        move = find_best_move(board)
        if move < 0:
            break
        # print("%010.6f: Score %d, Move %d: %s" % (time.time() - start, gamectrl.get_score(), moveno, movename(move)))
        current_ai.score = gamectrl.get_score()
        gamectrl.execute_move(move)

    score = gamectrl.get_score()
    board = gamectrl.get_board()
    maxval = max(max(row) for row in to_val(board))
    print("Game over. Final score %d; highest tile %d." % (score, maxval))
    games_played.append([score, maxval])

def parse_args(argv):
    import argparse

    parser = argparse.ArgumentParser(description="Use the AI to play 2048 via browser control")
    parser.add_argument('-p', '--port', help="Port number to control on (default: 32000 for Firefox, 9222 for Chrome)", type=int)
    parser.add_argument('-b', '--browser', help="Browser you're using. Only Firefox with the Remote Control extension, and Chrome with remote debugging, are supported right now.", default='firefox', choices=('firefox', 'chrome'))
    parser.add_argument('-k', '--ctrlmode', help="Control mode to use. If the browser control doesn't seem to work, try changing this.", default='fast', choices=('keyboard', 'fast', 'hybrid'))

    return parser.parse_args(argv)

def main(argv):
    args = parse_args(argv)

    if args.browser == 'firefox':
        from ffctrl import FirefoxRemoteControl
        if args.port is None:
            args.port = 32000
        ctrl = FirefoxRemoteControl(args.port)
    elif args.browser == 'chrome':
        from chromectrl import ChromeDebuggerControl
        if args.port is None:
            args.port = 9222
        ctrl = ChromeDebuggerControl(args.port)

    if args.ctrlmode == 'keyboard':
        from gamectrl import Keyboard2048Control
        gamectrl = Keyboard2048Control(ctrl)
    elif args.ctrlmode == 'fast':
        from gamectrl import Fast2048Control
        gamectrl = Fast2048Control(ctrl)
    elif args.ctrlmode == 'hybrid':
        from gamectrl import Hybrid2048Control
        gamectrl = Hybrid2048Control(ctrl)

    if gamectrl.get_status() == 'ended':
        gamectrl.restart_game()

    '''========================================================================================
        Start playing 2048
    ========================================================================================'''

    for i in range(games_to_be_played):
        if log_each_game_as_csv:
            '''Log Each Game'''
            file_name = 'log/' + timestamp() + '_' + current_ai.__name__ +'.csv'
            with open(file_name, 'w', newline='') as csv_file:
                file_writer = csv.writer(csv_file)
                current_ai.print_csv_header(file_writer)

                '''Initialize global variables for current_ai'''
                initialize_current_ai_globals(file_writer)

                '''Play full game and reset'''
                play_game(gamectrl)
                gamectrl.restart_game()

        else:
            '''Initialize global variables for current_ai'''
            initialize_current_ai_globals(None)

            '''Play full game and reset'''
            play_game(gamectrl)
            gamectrl.restart_game()

    '''Log Totals'''
    if log_totals_as_csv:
        file_name = 'log/' + timestamp() + '_' + current_ai.__name__ + '_totals.csv'
        with open(file_name, 'w', newline='') as csv_file2:
            csv_writer2 = csv.writer(csv_file2)
            for line in games_played:
                csv_writer2.writerow(line)

def initialize_current_ai_globals(file_writer):
    if current_ai.__name__ == 'searchai':
        current_ai.ai_id = 'expectimax_' + timestamp()
    else:
        current_ai.ai_id = 'heuristic_' + timestamp() # identify for logging
    current_ai.move_count = 0
    current_ai.score = 0

    current_ai.file_writer = file_writer

    current_ai.log_csv = log_each_game_as_csv
    current_ai.log_elastic = log_elastic

def timestamp():
    return datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d_%H%M%S')

if __name__ == '__main__':
    import sys
    exit(main(sys.argv[1:]))
