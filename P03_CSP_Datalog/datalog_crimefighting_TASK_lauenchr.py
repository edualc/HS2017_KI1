#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 14:38:21 2017

@author: tugg
"""
import sys
import pandas as pa
from pyDatalog import pyDatalog

# ---------------------------------------------------------------------------
# Social graph analysis:
# work through this code from top to bottom (in the way you would use a R or Jupyter notebook as well...) and write datalog clauses and python code in order to solve the respective tasks. Overall, there are 7 tasks.
# ---------------------------------------------------------------------------
calls = pa.read_csv('calls.csv', sep='\t', encoding='utf-8')
texts = pa.read_csv('texts.csv', sep='\t', encoding='utf-8')

suspect = 'Quandt Katarina'
company_Board = ['Soltau Kristine', 'Eder Eva', 'Michael Jill']

pyDatalog.create_terms('X', 'Y', 'Z')
pyDatalog.create_terms('knows','has_link')
pyDatalog.clear()

# First treat calls simply as social links (denoted knows), which have no date
for i in range(50):
    +knows(calls.iloc[i,1], calls.iloc[i,2])

# -----------------------------------------------------------------------------------
# Task 1: Knowing someone is a bi-directional relationship -> define the predicate accordingly
knows(X, Y) <= knows(Y, X)

# -----------------------------------------------------------------------------------
# Task 2: Define the predicate has_link in a way that it is true if there exists some connection (path of people knowing the next link) in the social graph
# Hints:
#   check if your predictate works: at least 1 of the following asserts should be true (2 if you read in all 150 communcation records)
#   assert (has_link('Quandt Katarina', company_Board[0]))
#   assert (has_link('Quandt Katarina', company_Board[1]))
#   assert (has_link('Quandt Katarina', company_Board[2]))

has_link(X, Z) <= knows(Y, Z) & has_link(X, Y) & (X != Z)
has_link(X, Y) <= knows(X, Y) 

#assert (has_link('Quandt Katarina', company_Board[1]))
#assert (has_link('Quandt Katarina', company_Board[2]))
#sys.exit()

# -----------------------------------------------------------------------------------
# Task 3: You already know that a connection exists; now give the concrete paths between the board members and the suspect
# Hints:
#   if a knows b, there is a path between a and b
#   (X._not_in(P2)) is used to check wether x is not in path P2
#   (P==P2+[Z]) declares P as a new path containing P2 and Z

pyDatalog.create_terms('P', 'P2', 'path')

path(X, Z, P) <= knows(Y, Z) & path(X, Y, P2) & (X != Z) & (Y._not_in(P2)) & (P == P2 + [Y])
path(X, Y, P) <= knows(X, Y) & (P == [])

#print(path(company_Board[1], suspect, P))
#sys.exit()

# -----------------------------------------------------------------------------------
# Task 4: There are so many path, therefore we are only interested in short pahts.
# find all the paths between the suspect and the company board, which contain five poeple or less
pyDatalog.create_terms('path_with_max_cost', 'path_with_cost', 'C', 'C2')

path_with_cost(X, Z, P, C) <= knows(Y, Z) & path_with_cost(X, Y, P2, C2) & (X != Z) & (Y._not_in(P2)) & (P == P2+[Y]) & (C == C2+1)
path_with_cost(X, Y, P, C) <= knows(X, Y) & (P == []) & (C == 0)
path_with_max_cost(X, Y, P, C) <= path_with_cost(X, Y, P, C2) & (C >= C2)

#for cp in company_Board:
#    print(cp)
#    print(path_with_max_cost(cp, suspect, P, 5))
#    print('----------------------------------------------------------')

#sys.exit()

# -----------------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Call-Data analysis:
# Now we use the text and the calls data together their corresponding dates
# ---------------------------------------------------------------------------
date_board_decision = '12.2.2017'
date_shares_bought = '23.2.2017'
pyDatalog.create_terms('called,texted')
pyDatalog.create_terms('T', 'T2', 'path_with_cost_time', 'connection')
pyDatalog.clear()

for i in range(150): # calls
    +called(calls.iloc[i,1], calls.iloc[i,2],calls.iloc[i,3])

for i in range(150): # texts
    +texted(texts.iloc[i,1], texts.iloc[i,2],texts.iloc[i,3])

called(X,Y,Z) <= called(Y,X,Z) # calls are bi-directional

# -----------------------------------------------------------------------------------
# Task 5: we are are again interested in links, but this time a connection only valid the links are descending in date 
# find out who could have actually sent an information, when imposing this new restriction
# Hints:
#   You are allowed to naively compare the dates lexicographically using ">" and "<"; it works in this example of concrete dates (but is of course evil in general)

connection(X, Y, Z) <= called(X, Y, Z)
connection(X, Y, Z) <= texted(X, Y, Z) # commented out since this kills the performance

has_link(X, Z, T) <= connection(Y, Z, T) & has_link(X, Y, T2) & (X != Z) & (T > T2)
has_link(X, Y, T) <= connection(X, Y, T)

#print(has_link(company_Board[1], suspect, T))
#print(has_link(company_Board[2], suspect, T))
#sys.exit()

# -----------------------------------------------------------------------------------
# Task 6: at last find all the communication paths which lead to the suspect, again with the restriction that the dates have to be ordered correctly
path_with_cost_time(X, Z, P, C, T) <= connection(Y, Z, T) & path_with_cost_time(X, Y, P2, C2, T2) & (X != Z) & (Y._not_in(P2)) & (P == P2+[Y]) & (C == C2+1) & (T > T2) & (C2 < 6) # hardcap at length 6, directly in recursion to improve performance
path_with_cost_time(X, Y, P, C, T) <= connection(X, Y, T) & (P == []) & (C == 0)

for cp in company_Board:
    print(cp)
    print(path_with_cost_time(cp, suspect, P, C, T))
    print()
    
#sys.exit()

# -----------------------------------------------------------------------------------
# Final task: after seeing this information, who, if anybody, do you think has given a tipp to the suspect?

print('-----------------------------------------------------------------------')
print(company_Board[1], 'is most likely to have talked since it is the only one with communication corresponding to the date ordering filter.')


# General hint (only use on last resort!): 
#   if nothing else helped, have a look at https://github.com/pcarbonn/pyDatalog/blob/master/pyDatalog/examples/graph.py