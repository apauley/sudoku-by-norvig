#!/usr/bin/env python

def cross(A, B):
    return [a+b for a in A for b in B]

digits = '123456789'
rows = 'ABCDEFGHI'
cols = digits
squares = cross(rows, cols)

column_squares = [cross(rows, c) for c in cols]
row_squares    = [cross(r, cols) for r in rows]
box_squares    = [cross(rs, cs)
                  for rs in ('ABC','DEF','GHI')
                  for cs in ('123','456','789')]

unitlist = (column_squares +
            row_squares +
            box_squares)

units = dict((s, [u for u in unitlist if s in u])
             for s in squares)
peers = dict((s, set(s2 for u in units[s] for s2 in u if s2 != s))
             for s in squares)
