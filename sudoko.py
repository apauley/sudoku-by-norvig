#!/usr/bin/env python

# A sudoku solver by Peter Norvig
# http://norvig.com/sudoku.html

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

def parse_grid(grid):
    """Convert grid to a dict of possible values, {square: digits}, or
    return False if a contradiction is detected."""
    ## To start, every square can be any digit; then assign values from the grid.
    values = dict((square, digits) for square in squares)
    for square, digit in grid_values(grid).items():
        if digit in digits and not assign(values, square, digit):
            return False ## (Fail if we can't assign d to square s.)
    return values

def grid_values(grid):
    "Convert grid into a dict of {square: char} with '0' or '.' for empties."
    chars = [c for c in grid if c in digits or c in '0.']
    assert len(chars) == 81
    return dict(zip(squares, chars))

def assign(values, square, digit):
    """Eliminate all the other values (except digit) from values[square]
    and propagate.
    Return values, except return False if a contradiction is detected."""
    other_values = values[square].replace(digit, '')
    if all(eliminate(values, square, digit2) for digit2 in other_values):
        return values
    else:
        return False

def eliminate(values, square, digit):
    """Eliminate digit from values[square];
    propagate when values or places <= 2.
    Return values, except return False if a contradiction is detected."""
    if digit not in values[square]:
        return values ## Already eliminated
    values[square] = values[square].replace(digit, '')
    ## (1) If a square is reduced to one value d2, then eliminate d2 from the peers.
    if len(values[square]) == 0:
        return False ## Contradiction: removed last value
    elif len(values[square]) == 1:
        d2 = values[square]
        if not all(eliminate(values, s2, d2) for s2 in peers[square]):
            return False
    ## (2) If a unit is reduced to only one place for a digit, then put it there
    for u in units[square]:
        digit_places = [square2 for square2 in u if digit in values[square2]]
        if len(digit_places) == 0:
            return False ## Contradiction: no place for this value
        elif len(digit_places) == 1:
            # d can only be in one place in unit; assign it there
            if not assign(values, digit_places[0], digit):
                return False
    return values

def display(values):
    "Display these values as a 2-D grid."
    width = 1+max(len(values[s]) for s in squares)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print ''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols)
        if r in 'CF': print line
    print

if __name__ == '__main__':
    grid = file('top95.txt').readlines()[0]
    display(parse_grid(grid))
