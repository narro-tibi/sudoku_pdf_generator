# import sudoku
from Generator.sudoku_solver import SudokuGrid, SudokuSolver, SudokuRater
import random
# from defaults import *

class SudokuGenerator:

    """A class to generate new Sudoku Puzzles."""

    def __init__(self, start_grid=None, clues=30, group_size=9):
        self.generated = []
        self.clues = clues
        self.all_coords = []
        self.group_size = group_size
        for x in range(self.group_size):
            for y in range(self.group_size):
                self.all_coords.append((x, y))
        if start_grid:
            self.start_grid = SudokuGrid(grid)
        else:
            try:
                self.start_grid = self.generate_grid()
            except:
                self.start_grid = self.generate_grid()
        self.puzzles = []
        self.rated_puzzles = []

    def get_board_sizes(self):
        sudoku_board_sizes = [3, 3, self.group_size]
        return sudoku_board_sizes

    def average_difficulty(self):
        difficulties = [i[1].value for i in self.rated_puzzles]
        if difficulties:
            return sum(difficulties)/len(difficulties)

    def generate_grid(self):
        self.start_grid = SudokuSolver(
            verbose=False, group_size=self.group_size)
        self.start_grid.solve()
        return self.start_grid

    def reflect(self, x, y, axis=1):
        # downward sloping
        upper = self.group_size - 1
        # reflect once...
        x, y = upper - y, upper-x
        # reflect twice...
        return y, x

    def make_symmetric_puzzle(self):
        nclues = self.clues/2
        # coff = [i * nclues for i in self.all_coords]
        buckshot = set(random.sample(self.all_coords, int(nclues)))
        new_puzzle = SudokuGrid(
            verbose=False, group_size=self.group_size)
        reflections = set()
        for x, y in buckshot:
            reflection = self.reflect(x, y)
            if reflection:
                nclues += 1
                reflections.add(reflection)
        buckshot = buckshot | reflections  # unite our sets
        remaining_coords = set(self.all_coords) - set(buckshot)
        while len(buckshot) < self.clues:
            coord = random.sample(remaining_coords, 1)[0]
            buckshot.add(coord)
            reflection = self.reflect(*coord)
            if reflection:
                buckshot.add(reflection)
            remaining_coords = remaining_coords - buckshot
        return self.make_puzzle_from_coords(buckshot)

    def make_puzzle(self):
        buckshot = random.sample(self.all_coords, self.clues)
        while buckshot in self.generated:
            buckshot = random.sample(self.all_coords, self.clues)
        return self.make_puzzle_from_coords(buckshot)

    def make_puzzle_from_coords(self, buckshot):
        new_puzzle = SudokuGrid(
            verbose=False, group_size=self.group_size)
        self.generated.append(set(buckshot))
        for x, y in buckshot:
            new_puzzle.add(x, y, self.start_grid._get_(x, y))
        self.puzzles.append(new_puzzle)
        return new_puzzle

    def make_puzzle_by_boxes(self,
                             skew_by=0.0,
                             max_squares=None,):
        """Make a puzzle paying attention to evenness of clue
        distribution.

        If skew_by is 0, we distribute our clues as evenly as possible
        across boxes.  If skew by is 1.0, we make the distribution of
        clues as uneven as possible. In other words, if we had 27
        boxes for a 9x9 grid, a skew_by of 0 would put exactly 3 clues
        in each 3x3 grid whereas a skew_by of 1.0 would completely
        fill 3 3x3 grids with clues.

        We believe this skewing may have something to do with how
        difficult a puzzle is to solve. By toying with the ratios,
        this method may make it considerably easier to generate
        difficult or easy puzzles.
        """
        # Number of total boxes
        nboxes = len(self.start_grid.boxes)
        # If no max is given, we calculate one based on our skew_by --
        # a skew_by of 1 will always produce full squares, 0 will
        # produce the minimum fullness, and between between in
        # proportion to its betweenness.
        if not max_squares:
            max_squares = self.clues / nboxes
            max_squares += int((nboxes-max_squares)*skew_by)
        clued = 0
        # nclues will be a list of the number of clues we want per
        # box.
        nclues = []
        for n in range(nboxes):
            # Make sure we'll have enough clues to fill our target
            # number, regardless of our calculation of the current max
            minimum = (self.clues-clued)/(nboxes-n)
            if max_squares < minimum:
                cls = minimum
            else:
                cls = int(max_squares)
            clues = max_squares
            if clues > (self.clues - clued):
                clues = self.clues - clued
            nclues.append(int(clues))
            clued += clues
            if skew_by:
                # Reduce our number of squares proportionally to
                # skewiness.
                max_squares = round(max_squares * skew_by)
        # shuffle ourselves...
        random.shuffle(nclues)
        buckshot = []
        for i in range(nboxes):
            if nclues[i]:
                buckshot.extend(
                    random.sample(self.start_grid.box_coords[i],
                                  nclues[i])
                )
        return self.make_puzzle_from_coords(buckshot)

    def assess_difficulty(self, sudoku_grid):
        solver = None
        try:
            solver = SudokuRater(
                sudoku_grid, verbose=False, group_size=self.group_size)
            d = solver.difficulty()
            self.rated_puzzles.append((sudoku_grid, d))
            return d
        except:
            print('Impossible!')
            print('Puzzle was:')
            if solver:
                print((solver.virgin))
            print(('Solution: '), end=' ')
            print((self.start_grid))
            print(('Puzzle foobared in following state:'), end=' ')
            if solver:
                print(solver)
            raise

    def is_unique(self, sudoku_grid):
        """If puzzle is unique, return its difficulty.

        Otherwise, return None."""
        solver = SudokuRater(
            sudoku_grid, verbose=False, group_size=self.group_size)
        if solver.has_unique_solution():
            return solver.difficulty()
        else:
            return None

    def generate_puzzle_for_difficulty(self,
                                       lower_target=0.3,
                                       upper_target=0.5,
                                       max_tries=100,
                                       by_box=False,
                                       by_box_kwargs={}):
        for i in range(max_tries):
            if by_box:
                puz = self.make_puzzle_by_boxes(**by_box_kwargs)
            else:
                puz = self.make_puzzle()
            d = self.assess_difficulty(puz.grid)
            if (d and (not lower_target or d.value > lower_target) and
               (not upper_target or
                    d.value < upper_target)):
                return puz, d
        else:
            return None, None

    def make_unique_puzzles(self, n=10, ugargs={}):
        ug = self.unique_generator(**ugargs)
        ret = []
        for i in range(n):
            print('Working on puzzle ')
            ret.append(next(ug))
            # print('Got one!')
        return ret

    def unique_generator(self, symmetrical=True,
                         by_box=False, by_box_kwargs={}):
        while 1:
            if symmetrical:
                puz = self.make_symmetric_puzzle()
            elif by_box:
                puz = self.make_puzzle_by_boxes(**by_box_kwargs)
            else:
                puz = self.make_puzzle()
            diff = self.is_unique(puz.grid)
            if diff:
                yield puz, diff

    def generate_puzzles(self, n=10,
                         symmetrical=True,
                         by_box=False,
                         by_box_kwargs={}):
        ret = []
        for i in range(n):
            print(('Generating puzzle '), i)
            if symmetrical:
                puz = self.make_symmetric_puzzle()
            elif by_box:
                puz = self.make_puzzle_by_boxes(**by_box_kwargs)
            else:
                puz = self.make_puzzle()
            # print 'Assessing puzzle ',puz
            try:
                d = self.assess_difficulty(puz.grid)
            except:
                raise
            if d:
                ret.append((puz, d))
        # ret.sort(lambda a, b: a[1].value >
        #          b[1].value and 1 or a[1].value < b[1].value and -1 or 0)
        return ret


class InterruptibleSudokuGenerator (SudokuGenerator):
    pass


def generate_puzzles_by_difficulty(difficulty='Any', grid_size=9):
    g = SudokuGenerator(None, int((grid_size*0.608)**2), grid_size)
    while 1:
        puzzles = g.make_unique_puzzles(1)
        # puzzle = g.generate_puzzle_for_difficulty(0.5, 0.6)
        puz, d = puzzles[0]
        if difficulty == 'Any' or d.value_string() == difficulty:
            print("Found the correct difficulty!", difficulty)
            break
    return puz, d


def make_puzzles(num, difficulty, square_size):
    grid_size = square_size * square_size
    puzzles = []
    for i in range(int(num)):
        puzzles.append(generate_puzzles_by_difficulty(difficulty, grid_size))

    return puzzles


# if __name__ == '__main__':
#     import optparse
#
#     parser = optparse.OptionParser(usage='usage: %prog [options] output-file')
#     parser.add_option("-n", "--number", default=3, action="store", type="int", help="Number of puzzles to generate")
#     parser.add_option("-d", "--difficulty", default='Any', help="Difficulty level.  Can be 'Any', 'Easy', 'Medium', 'Hard', 'Very hard'")
#     (options, args) = parser.parse_args()
#
#     sg = SudokuGenerator()
#     puzzles = sg.generate_puzzle_for_difficulty(0.5, 0.6)
# #
#     print("PUZZLES", puzzles)
#
#     print("MAIN symmetrical", sg.make_symmetric_puzzle())
#     # generatePuzzle('Hard')
#
#     go(options.number, options.difficulty)

    # unique_maker = sg.unique_generator()
    # unique = []
    # for n in range(3):
    #     unique.append(next(unique_maker))
    # print('Generated Unique...', unique)
    # unique_puzzles = filter(lambda x: SudokuSolver(x[0].grid,verbose=False).has_unique_solution(),puzzles)
    # print("unique", unique_puzzles)

    # uniq_puzzles = sg.make_unique_puzzles(3)
    # for puz, d in uniq_puzzles:
    #     print("UNIQUE PUZZLE", d.value_string(), d.value, puz)
