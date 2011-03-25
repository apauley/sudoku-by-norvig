#!/usr/bin/env python

# A sudoku solver by Peter Norvig
# http://norvig.com/sudoku.html

import sys, os, time

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

class Puzzle(dict):
    "A dict with a counter"
    def __init__(self, tuples, count=0):
        self.count = count
        super(Puzzle, self).__init__(tuples)

    def copy(self):
        return Puzzle(self.items(), self.count)

def has_failed(puzzle):
    return not puzzle

def failed(puzzle):
    "Return a failed puzzle"
    return Puzzle([], puzzle.count)

def parse_grid(grid):
    """Convert grid to a puzzle of possible values, {square: digits}, or
    return a failed puzzle if a contradiction is detected."""
    ## To start, every square can be any digit; then assign values from the grid.
    puzzle = Puzzle((square, digits) for square in squares)
    for square, digit in grid_puzzle(grid).items():
        if digit in digits and not assign(puzzle, square, digit):
            return failed(puzzle) ## (Fail if we can't assign d to square s.)
    return puzzle

def grid_puzzle(grid):
    "Convert grid into a dict of {square: char} with '0' or '.' for empties."
    chars = [c for c in grid if c in digits or c in '0.']
    assert len(chars) == 81
    return Puzzle(zip(squares, chars))

def assign(puzzle, square, digit):
    """Eliminate all the other values (except digit) from puzzle[square]
    and propagate.
    Return puzzle, except return failed if a contradiction is detected."""
    other_values = puzzle[square].replace(digit, '')
    if all(eliminate(puzzle, square, digit2) for digit2 in other_values):
        return puzzle
    else:
        return failed(puzzle)

def eliminate(puzzle, square, digit):
    """Eliminate digit from puzzle[square];
    propagate when values or places <= 2.
    Return puzzle, except return failed if a contradiction is detected."""
    if digit not in puzzle[square]:
        return puzzle ## Already eliminated
    puzzle[square] = puzzle[square].replace(digit, '')
    if len(puzzle[square]) == 0:
        return failed(puzzle) ## Contradiction: removed last value

    puzzle.count += 1
    puzzle = peer_eliminate(puzzle, square)
    if has_failed(puzzle):
        return failed(puzzle)

    puzzle = assign_unique_place(puzzle, square, digit)
    if has_failed(puzzle):
        return failed(puzzle)

    return puzzle

def peer_eliminate(puzzle, square):
    ## (1) If a square is reduced to one value, then eliminate it from the peers.
    if len(puzzle[square]) == 1:
        digit = puzzle[square]
        if not all(eliminate(puzzle, s2, digit) for s2 in peers[square]):
            return failed(puzzle)
    return puzzle

def assign_unique_place(puzzle, square, digit):
    ## (2) If a unit is reduced to only one place for a digit, then put it there
    for u in units[square]:
        digit_places = [square2 for square2 in u if digit in puzzle[square2]]
        if len(digit_places) == 0:
            return failed(puzzle) ## Contradiction: no place for this value
        elif len(digit_places) == 1:
            # digit can only be in one place in unit; assign it there
            if not assign(puzzle, digit_places[0], digit):
                return failed(puzzle)
    return puzzle

def solve(grid):
    return search(parse_grid(grid))

def search(puzzle):
    "Using depth-first search and propagation, try all possible values."
    if has_failed(puzzle):
        return failed(puzzle) ## Failed earlier
    if is_solved(puzzle):
        return puzzle
    ## Choose the unfilled square s with the fewest possibilities
    possibilities, square = min((len(puzzle[s]), s)
                                for s in squares if len(puzzle[s]) > 1)
    return first_valid_result(puzzle, square, puzzle[square])

def first_valid_result(puzzle, square, values):
    if len(values) == 0:
        return failed(puzzle)
    new_puzzle = search(assign(puzzle.copy(), square, values[0]))
    if new_puzzle:
        return new_puzzle
    diff = new_puzzle.count - puzzle.count
    puzzle.count += diff
    return first_valid_result(puzzle, square, values[1:])

def solve_all(grids, name=''):
    """Attempt to solve a sequence of grids. Report results."""
    def time_solve(grid):
        start = time.clock()
        puzzle = solve(grid)
        t = time.clock()-start
        return (t, is_solved(puzzle), puzzle)
    times, results, puzzles = zip(*[time_solve(grid) for grid in grids])
    eliminations = [puzzle.count for puzzle in puzzles]

    N = len(grids)
    if N >= 1:
        hz = N/sum(times)
        print "Solved %d of %d puzzles from %s in %.6f secs (%d Hz)" % (
            sum(results), N, name, sum(times), hz)

        [total_elims, avg_elims, max_elims, min_elims] = stats(eliminations)
        print "  (%d total eliminations, avg %.2f, max %d, min %d)." % (
            total_elims, avg_elims, max_elims, min_elims)
    return puzzles

def stats(lst):
    total = sum(lst)
    avg = total/len(lst)
    return [total, avg, max(lst), min(lst)]

def is_solved(puzzle):
    "A puzzle is solved if each unit is a permutation of the digits 1 to 9."
    def unitsolved(unit): return set(puzzle[s] for s in unit) == set(digits)
    return (not has_failed(puzzle)) and all(unitsolved(unit) for unit in unitlist)

def to_string(puzzle):
    return ''.join([value_or_dot(puzzle[s]) for s in squares])

def value_or_dot(value):
    return (value if (len(value) == 1) else '.')

def from_file(filename, sep='\n'):
    "Parse a file into a list of strings, separated by sep."
    return file(filename).read().strip().split(sep)

def to_file(outfile, solutions):
    grids = [to_string(s)+'\n' for s in solutions]
    fp = file(outfile, 'w')
    try:
        fp.writelines(grids)
    finally:
        fp.close()

def solve_file(filename, sep='\n'):
    solutions = solve_all(from_file(filename, sep), filename)
    outfile = os.path.splitext(filename)[0] + '.out'
    to_file(outfile, solutions)

def solve_files(*filenames):
    [solve_file(filename) for filename in filenames]

def test():
    "A set of tests that must pass."
    assert len(squares) == 81
    assert len(unitlist) == 27
    assert all(len(units[s]) == 3 for s in squares)
    assert all(len(peers[s]) == 20 for s in squares)
    assert units['C2'] == [['A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2', 'I2'],
                           ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9'],
                           ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3']]
    assert peers['C2'] == set(['A2', 'B2', 'D2', 'E2', 'F2', 'G2', 'H2', 'I2',
                               'C1', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9',
                               'A1', 'A3', 'B1', 'B3'])
    print 'All tests pass.'

if __name__ == '__main__':
    test()
    if len(sys.argv) > 1:
        solve_files(*sys.argv[1:])
    else:
        solve_files("easy50.txt", "top95.txt", "hardest.txt")
