#!/usr/bin/env python

# A sudoku solver by Peter Norvig
# http://norvig.com/sudoku.html

import time

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

def solve(grid):
    return search(parse_grid(grid))

def search(values):
    "Using depth-first search and propagation, try all possible values."
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in squares):
        return values ## Solved!
    ## Choose the unfilled square s with the fewest possibilities
    possibilities, square = min((len(values[s]), s)
                                for s in squares if len(values[s]) > 1)
    return some(search(assign(values.copy(), square, digit))
                for digit in values[square])

def some(seq):
    "Return some element of seq that is true."
    for e in seq:
        if e: return e
    return False

def solve_all(grids, name='', showif=0.0):
    """Attempt to solve a sequence of grids. Report results.
    When showif is a number of seconds, display puzzles that take longer.
    When showif is None, don't display any puzzles."""
    def time_solve(grid):
        start = time.clock()
        values = solve(grid)
        t = time.clock()-start
        ## Display puzzles that take long enough
        if showif is not None and t > showif:
            display(grid_values(grid))
            if values: display(values)
            print '(%.2f seconds)\n' % t
        return (t, solved(values), values)
    times, results, valuedicts = zip(*[time_solve(grid) for grid in grids])
    N = len(grids)
    if N > 1:
        print "Solved %d of %d puzzles from %s (avg %.2f secs (%d Hz), max %.2f secs)." % (
            sum(results), N, name, sum(times)/N, N/sum(times), max(times))
    return valuedicts

def solved(values):
    "A puzzle is solved if each unit is a permutation of the digits 1 to 9."
    def unitsolved(unit): return set(values[s] for s in unit) == set(digits)
    return values is not False and all(unitsolved(unit) for unit in unitlist)

def to_string(values):
    return ''.join([value_or_dot(values[s]) for s in squares])

def value_or_dot(value):
    return (value if (len(value) == 1) else '.')

def display(values):
    "Display these values as a 2-D grid."
    width = 1+max(len(values[s]) for s in squares)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print ''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols)
        if r in 'CF': print line
    print

def from_file(filename, sep='\n'):
    "Parse a file into a list of strings, separated by sep."
    return file(filename).read().strip().split(sep)

def solve_file(filename, sep='\n'):
    return solve_all(from_file(filename, sep), filename, None)

if __name__ == '__main__':
    solve_file("easy50.txt", '========')
    solve_file("top95.txt")
    solve_file("hardest.txt")
