import functools
import random
import math
import numpy as np
import re

GROUP_SIZE = 9

TYPE_ROW = 0
TYPE_COLUMN = 1
TYPE_BOX = 2

digit_set = list(range(1, GROUP_SIZE+1))
# random.shuffle(digit_set)
sets = [digit_set] * 9

class UnsolvablePuzzle (TypeError):
    pass


class ConflictError (ValueError):

    def __init__(self, conflict_type, coordinates, value):
        self.args = conflict_type, coordinates, value
        self.type = conflict_type
        self.coordinates = coordinates
        self.x = coordinates[0]
        self.y = coordinates[1]
        self.value = value


class AlreadySetError (ValueError):
    pass

class SudokuGrid:
    def __init__(self, grid=None, verbose=False, group_size=9):
        self.grid = []
        self.cols = []
        self.rows = []
        self.boxes = []
        self.group_size = int(group_size) # grid size as number
        self.verbose = False
        self.gen_set = set(range(1, self.group_size+1))
        for n in range(self.group_size):
            self.cols.append(set())
            self.rows.append(set())
            self.boxes.append(set())
            self.grid.append([0]*self.group_size)
        self.grid = np.array(self.grid, dtype='b')
        self.box_by_coords = {}
        self.box_coords = {}
        self.calculate_box_coords()  # sets box_coords and box_by_coords
        self.row_coords = {}
        for n, row in enumerate([[(x, y) for x in range(self.group_size)] for y in range(self.group_size)]):
            self.row_coords[n] = row
        self.col_coords = {}
        for n, col in enumerate([[(x, y) for y in range(self.group_size)] for x in range(self.group_size)]):
            self.col_coords[n] = col
        if grid is not None and type(grid) is not bool:
            if type(grid) == str:
                g = re.split("\s+", grid)
                side = int(math.sqrt(len(g)))
                grid = []
                for row in range(side):
                    start = row*int(side)
                    grid.append([int(i) for i in g[start:start+side]])
            # print 'populating from grid->',
            # print grid
            self.populate_from_grid(grid)
        self.verbose = verbose
        # print("GRID", self.group_size)

    def calculate_box_coords(self):
        width = int(math.sqrt(self.group_size))
        box_coordinates = [[n*width,
                            (n+1)*width] for n in range(width)]
        box_num = 0
        for xx in box_coordinates:
            for yy in box_coordinates:
                self.box_coords[box_num] = []
                for x in range(*xx):
                    for y in range(*yy):
                        self.box_by_coords[(x, y)] = box_num
                        self.box_coords[box_num].append((x, y))
                box_num += 1

    def add(self, x, y, val, force=False):
        if not val:
            pass
        if self._get_(x, y):
            if force:
                try:
                    self.remove(x, y)
                except:
                    print('Strange')
            else:
                raise AlreadySetError
                # print 'Value already set'
                # self.remove(x,y)
        if val in self.rows[y]:
            raise ConflictError(TYPE_ROW, (x, y), val)
        if val in self.cols[x]:
            raise ConflictError(TYPE_COLUMN, (x, y), val)
        box = self.box_by_coords[(x, y)]
        if val in self.boxes[box]:
            raise ConflictError(TYPE_BOX, (x, y), val)
        # do the actual adding
        self.rows[y].add(val)
        self.cols[x].add(val)
        self.boxes[box].add(val)
        if self.verbose:
            print(('Set ', x, ',', y, '=', val))
        self._set_(x, y, val)
        # if self.verbose: print self

    def remove(self, x, y):
        # print 'Removing ',x,y
        val = self._get_(x, y)
        self.rows[y].remove(val)
        self.cols[x].remove(val)
        self.boxes[self.box_by_coords[(x, y)]].remove(val)
        self._set_(x, y, 0)

    def _get_(self, x, y): return self.grid[y][x]

    def _set_(self, x, y, val): self.grid[y][x] = val

    def possible_values(self, x, y):
        return self.gen_set - self.rows[y] - self.cols[x] - self.boxes[self.box_by_coords[(x, y)]]

    def pretty_print(self):
        print('SUDOKU')
        for r in self.grid:
            for i in r:
                print((i), end=' ')
            print()
        print()

    def populate_from_grid(self, grid):
        if grid is not None:
            for y, row in enumerate(grid):
                for x, cell in enumerate(row):
                    # print("cell", x, cell)
                    if cell:
                        self.add(x, y, cell)

    def __repr__(self):
        s = "<Grid\n       "
        grid = []
        for r in self.grid:
            grid.append(" ".join([str(i) for i in r]))
        s += "\n       ".join(grid)
        return s

    def calculate_open_squares(self):
        possibilities = {}
        for x in range(self.group_size):
            for y in range(self.group_size):
                if not self._get_(x, y):
                    possibilities[(x, y)] = self.possible_values(x, y)
        return possibilities

    def find_conflict(self, x, y, val, conflict_type):
        if conflict_type == TYPE_ROW:
            coords = self.row_coords[y]
        elif conflict_type == TYPE_COLUMN:
            coords = self.col_coords[x]
        elif conflict_type == TYPE_BOX:
            coords = self.box_coords[self.box_by_coords[(x, y)]]
        for x, y in coords:
            if self._get_(x, y) == val:
                return x, y

    def to_string(self):
        """Output our grid as a string."""
        return " ".join([" ".join([str(x) for x in row]) for row in self.grid])

class SudokuSolver (SudokuGrid):
    """A SudokuGrid that can solve itself."""

    def __init__(self, grid=False, verbose=False, group_size=9):
        self.current_guess = None
        self.initialized = False
        SudokuGrid.__init__(self, grid, verbose=verbose, group_size=group_size)
        self.virgin = SudokuGrid(grid, False, group_size)
        self.guesses = GuessList()
        self.breadcrumbs = BreadcrumbTrail()
        self.backtraces = 0
        self.initialized = True
        self.solved = False
        self.trail = []
        #self.complete_crumbs = BreadcrumbTrail()

    def auto_fill(self):
        changed = []
        try:
            change = self.fill_must_fills()
        except UnsolvablePuzzle:
            return changed
        while change:
            changed.extend(change)
            try:
                change = self.fill_must_fills()
            except:
                return changed
            try:
                change.extend(self.fill_deterministically())
            except:
                return changed + change
        return changed

    def fill_must_fills(self):
        changed = []
        for label, coord_dic, filled_dic in [('Column', self.col_coords, self.cols),
                                             ('Row', self.row_coords, self.rows),
                                             ('Box', self.box_coords, self.boxes)]:
            for n, coord_set in list(coord_dic.items()):
                needs = dict([(n, False) for n in range(1, self.group_size+1)])
                for coord in coord_set:
                    val = self._get_(*coord)
                    if val:
                        # We already have this value set...
                        del needs[val]
                    else:
                        # Otherwise, register ourselves as possible
                        # for each number we could be
                        for v in self.possible_values(*coord):
                            # if we don't yet have a possible number, plug ourselves in
                            if v in needs:
                                if not needs[v]:
                                    needs[v] = coord
                                else:
                                    del needs[v]
                for n, coords in list(needs.items()):
                    if not coords:
                        raise UnsolvablePuzzle(
                            'Missing a %s in %s' % (n, label))
                    else:
                        try:
                            self.add(coords[0], coords[1], n)
                            changed.append((coords, n))
                        except AlreadySetError:
                            raise UnsolvablePuzzle(
                                "%s,%s must be two values at once!" % (coords)
                            )
        return changed

    def fill_must_fills_2(self):
        changed = []
        for label, coord_dic, filled_dic in [('Column', self.col_coords, self.cols),
                                             ('Row', self.row_coords, self.rows),
                                             ('Box', self.box_coords, self.boxes)]:
            for n, coord_set in list(coord_dic.items()):
                needs = dict([(n, []) for n in range(1, self.group_size+1)])
                for coord in coord_set:
                    val = self._get_(*coord)
                    if val:
                        del needs[val]
                    else:
                        for v in self.possible_values(*coord):
                            needs[v].append(coord)
                for n, coords in list(needs.items()):
                    if len(coords) == 0:
                        raise UnsolvablePuzzle(
                            'Missing a %s in %s' % (n, label))
                    elif len(coords) == 1:
                        try:
                            self.add(coords[0][0], coords[0][1], n)
                            changed.append((coords[0], n))
                        except AlreadySetError:
                            raise UnsolvablePuzzle(
                                "%s,%s must be two values at once!" % (
                                    coords[0])
                            )
        return changed

    def fill_must_fills_old(self):
        """If we have a row where only one column can be a 3, it must be a 3.

        We raise an error if we discover an impossible situation.
        We return a list of what we've changed
        """
        has_changed = []
        for label, coord_dic, filled_dic in [('Column', self.col_coords, self.cols),
                                             ('Row', self.row_coords, self.rows),
                                             ('Box', self.box_coords, self.boxes)]:
            for n, coord_set in list(coord_dic.items()):
                # get set of filled in values for our column
                values = filled_dic[n]
                needed = self.gen_set - values
                # A dictionary to track who can fill our various needs...
                needed_dic = {}
                for c in needed:
                    needed_dic[c] = []
                # just work on the open squares
                coord_set = [coords for coords in coord_set if not self._get_(*coords)]
                for xy, poss_set in [(c, self.possible_values(*c)) for c in coord_set]:
                    # print 'Looking at ',coords
                    # print 'Possible vals: ',poss_set
                    # our set of values we can fill is now greater...
                    values = values | poss_set
                    # track who can fill our needs...
                    for v in poss_set:
                        needed_dic[v].append(xy)
                # check if our set of fillable values is sufficient
                # print 'Needed dic: ',needed_dic
                if values != self.gen_set:
                    # if self.verbose: print 'PROBLEM in ',label,' ',n
                    # print 'Initial puzzle was: ',self.virgin
                    raise UnsolvablePuzzle(
                        "Impossible to solve! We are missing %s in %s" % (self.gen_set-values, label))
                # Check if there are any values for which only one cell will suffice
                needed_filled_by = list(needed_dic.items())
                values_only_one_can_fill = [x for x in needed_filled_by if len(x[1]) == 1]
                for v, coords in values_only_one_can_fill:
                    coords = coords[0]
                    if self.verbose:
                        print(('Setting ', coords, v, ' by necessity!'))
                    if self.verbose:
                        print(('(No other item in this ',
                              label, ' can be a ', v, ')'))
                    has_changed.append([(coords[0], coords[1]), v])
                    try:
                        self.add(coords[0], coords[1], v)
                    except AlreadySetError:
                        if self._get_(coords[0], coords[1]) == v:
                            pass
                        else:
                            raise UnsolvablePuzzle(
                                "Impossible to solve! %s,%s must be two values at once!" % (
                                    coords)
                            )
        if self.verbose:
            print(('fill_must_fills returning ', has_changed))
        # print 'fill_must_fills returning ',has_changed
        return has_changed

    def scan_must_fills(self):
        """Scan to find how many fill_must_fills we could fill in with
        100% positivity based on the grid as it currently stands (not
        using the *cumulative* results"""
        # we do this by temporarily disabling the add call
        self.fake_add = True
        self.fake_added = []
        self.fill_must_fills()

    def fill_deterministically(self):
        poss = list(self.calculate_open_squares().items())
        one_choice = [x for x in poss if len(x[1]) == 1]
        retval = []
        for coords, choices in one_choice:
            if self.verbose:
                print(('Deterministically adding ', coords, choices))
            val = choices.pop()
            self.add(coords[0], coords[1], val)
            retval.append([(coords[0], coords[1]), val])
        if self.verbose:
            print(('deterministically returning ', retval))
        # print 'deterministically filled ',retval
        return retval

    def solve(self):
        self.auto_fill()
        while not self.guess_least_open_square():
            1
        if self.verbose:
            print(('Solved!\n', self))
        self.solved = True

    def solution_finder(self):
        self.auto_fill()
        while not self.guess_least_open_square():
            1
        self.solved = True
        yield tuple([tuple(r) for r in self.grid[0:]])
        while self.breadcrumbs:
            # print self.breadcrumbs
            self.unwrap_guess(self.breadcrumbs[-1])
            try:
                while not self.guess_least_open_square():
                    1
            except UnsolvablePuzzle:
                break
            else:
                yield tuple([tuple(r) for r in self.grid[0:]])
        yield None

    def has_unique_solution(self):
        sf = self.solution_finder()
        next(sf)
        if next(sf):
            return False
        else:
            return True

    def find_all_solutions(self):
        solutions = set([])
        sf = self.solution_finder()
        sol = next(sf)
        while sol:
            solutions.add(sol)
            sol = next(sf)
        return solutions

    def guess_least_open_square(self):
        # get open squares and check them
        poss = list(self.calculate_open_squares().items())
        # if there are no open squares, we're done!
        if not poss:
            if self.verbose:
                print('Solved!')
            return True
        # otherwise, find the possibility with the least possibilities
        # key = lambda x: getattr(x, 'duration')
        poss.sort(key=functools.cmp_to_key(lambda a, b: len(a[1]) > len(b[1]) and 1 or len(a[1]) < len(b[1]) and -1 or
                  a[0] > b[0] and 1 or a[1] < b[1] and -1 or 0))
        least = poss[0]
        # remove anything we've already guessed
        possible_values = least[1] - self.guesses.guesses_for_coord(*least[0])
        if not possible_values:
            if self.breadcrumbs:
                self.backtraces += 1
                # print self.breadcrumbs
                #raw_input('Hit return to back up...')
                self.unwrap_guess(self.breadcrumbs[-1])
                return self.guess_least_open_square()
            else:
                raise UnsolvablePuzzle("Unsolvable %s.\n \
                Out of guesses for %s. Already guessed\n \
                %s (other guesses are %s)" % (self,
                                              least[0],
                                              self.guesses.guesses_for_coord(
                                                  *least[0]),
                                              self.guesses))
        guess = random.choice(list(possible_values))
        # print 'Our trail so far: ',self.breadcrumbs
        # print 'Guessing ',guess,' from ',possible_values,' for ',least[0]
        # raw_input('Continue...')
        # If we have a trail, we mark our parent
        #if self.breadcrumbs: parent=self.breadcrumbs[-1]
        # else: parent=None
        # Create guess object
        guess_obj = Guess(least[0][0], least[0][1], guess)
        if self.breadcrumbs:
            self.breadcrumbs[-1].children.append(guess_obj)
        # print 'Guessing ',guess_obj
        # print 'adding guess ',least[0],guess
        self.current_guess = None  # reset (we're tracked via guess.child)
        self.add(least[0][0], least[0][1], guess)
        self.current_guess = guess_obj  # (All deterministic additions
        # get added to our
        # consequences)
        self.guesses.append(guess_obj)
        self.trail.append(('+', guess_obj))
        self.breadcrumbs.append(guess_obj)
        try:
            filled = self.auto_fill()
            # print 'filled :',filled
            # print 'Done with guess.'
        except NotImplementedError:
            # print 'Bad Guess!!!'
            # print self
            self.trail.append('Problem filling coordinates after guess')
            #raw_input('Hit return to unwrap %s'%guess_obj)
            self.unwrap_guess(guess_obj)
            return self.guess_least_open_square()
            # print self
        if set([]) in list(self.calculate_open_squares().values()):
            # print 'BAD GUESS!!!'
            # print self
            self.trail.append('Guess leaves us with impossible squares.')
            #raw_input('Hit return to unwrap %s'%guess_obj)
            self.unwrap_guess(guess_obj)
            return self.guess_least_open_square()
            # print self

    def unwrap_guess(self, guess):
        # print 'Unwrapping guess ',guess
        # print self
        # raw_input('Unwrap...')
        # print 'Before:'
        # print self
        self.trail.append(('-', guess))
        if self._get_(guess.x, guess.y):
            self.remove(guess.x, guess.y)
        for consequence in list(guess.consequences.keys()):
            if self._get_(*consequence):
                self.remove(*consequence)
        # for d in self.guesses.remove_children(guess):
        for child in guess.children:
            # if self._get_(d.x,d.y):
            # print 'remove descendant ',child.x,child.y
            self.unwrap_guess(child)
            if child in self.guesses:
                self.guesses.remove(child)
        # print 'removing %s from breadcrumbs (%s)'%(guess,self.breadcrumbs)
        if guess in self.breadcrumbs:
            self.breadcrumbs.remove(guess)
        # print 'Remaining crumbs: ',self.breadcrumbs
        # print 'Remaining guesses: ',self.guesses
        # print 'New unwrapped self:'
        # print self
        # print 'After:'
        # print self

    def print_possibilities(self):
        poss = self.calculate_open_squares()
        poss_list = list(poss.items())
        poss_list.sort(lambda a, b: len(a[1]) > len(
            b[1]) and 1 or len(a[1]) < len(b[1]) and -1 or 0)
        most_poss = len(poss_list[-1][1])
        for y in range(len(self.cols)):
            for x in range(len(self.rows)):
                if self.grid[y][x]:
                    val = self.grid[y][x]
                else:
                    val = "".join([str(s) for s in poss[(x, y)]])
                print((self.pad(val, most_poss+2)), end=' ')
            for n in range(most_poss + 2):
                print()

    def pad(self, n, pad_to):
        n = str(n)
        padding = int(pad_to) - len(n)
        second_half = padding / 2
        first_half = second_half + padding % 2
        return " "*first_half + n + " "*second_half

    def add(self, x, y, val, *args, **kwargs):
        if self.current_guess:
            self.current_guess.add_consequence(x, y, val)
        SudokuGrid.add(self, x, y, val, *args, **kwargs)
    #    if self.initialized:
    #        stack = traceback.extract_stack()
    #        print ":".join(str(x) for x in stack[-5][1:-1]),
    #        print ":".join(str(x) for x in stack[-4][1:-1]),
    #        print ":".join(str(x) for x in stack[-3][1:-1]),
    #        print ': adding ',x,y,val
    #
    #    SudokuGrid.add(self,x,y,val,*args,**kwargs)

    # def remove (self, x, y):
    #    #if self.initialized: self.complete_crumbs.remove_guesses_for_coord(x,y)
    #    SudokuGrid.remove(self,x,y)

class DifficultyRating:
    def __init__(self,
                 fill_must_fillables,
                 elimination_fillables,
                 guesses,
                 backtraces,
                 squares_filled):
        self.fill_must_fillables = fill_must_fillables
        self.elimination_fillables = elimination_fillables
        self.guesses = guesses
        self.backtraces = backtraces
        self.squares_filled = squares_filled
        if self.fill_must_fillables:
            self.instant_fill_fillable = float(
                len(self.fill_must_fillables[0]))
        else:
            self.instant_fill_fillable = 0.0
        if self.elimination_fillables:
            self.instant_elimination_fillable = float(
                len(self.elimination_fillables[0]))
        else:
            self.instant_elimination_fillable = 0.0

        self.proportion_instant_elimination_fillable = self.instant_elimination_fillable / \
            self.squares_filled
        # some more numbers that may be crazy...
        self.proportion_instant_fill_fillable = self.instant_fill_fillable/self.squares_filled
        self.elimination_ease = add_with_diminishing_importance(
            self.count_values(self.elimination_fillables)
        )
        self.fillable_ease = add_with_diminishing_importance(
            self.count_values(self.fill_must_fillables)
        )
        self.value = self.calculate()

    def count_values(self, dct):
        kk = list(dct.keys())
        kk.sort()
        return [len(dct[k]) for k in kk]

    def calculate(self):
        return 1 - float(self.fillable_ease)/self.squares_filled \
                 - float(self.elimination_ease)/self.squares_filled \
            + len(self.guesses)/self.squares_filled \
            + self.backtraces/self.squares_filled

    def __repr__(self): return '<DifficultyRating %s>' % self.value

    def pretty_print(self):
        for name, stat in [('Number of moves instantly fillable by elimination',
                           self.instant_elimination_fillable),
                           ('Percentage of moves instantly fillable by elimination',
                           self.proportion_instant_elimination_fillable*100),
                           ('Number of moves instantly fillable by filling',
                           self.instant_fill_fillable),
                           ('Percentage of moves instantly fillable by filling',
                           self.proportion_instant_fill_fillable*100),
                           ('Number of guesses made',
                           len(self.guesses)),
                           ('Number of backtraces', self.backtraces),
                           ('Ease by filling', self.fillable_ease),
                           ('Ease by elimination', self.elimination_ease),
                           ('Calculated difficulty', self.value)
                           ]:
            print((name, ': ', stat))

    def value_string(self):
        if self.value > 0.75:
            return "Very hard"
        if self.value >= 0.59:
            return "Hard"
        elif self.value > 0.45:
            return "Medium"
        # elif self.value > 0.3: return "Medium"
        else:
            return "Easy"


class SudokuRater (SudokuSolver):

    def __init__(self, grid=False, verbose=False, group_size=9):
        self.initialized = False
        self.guessing = False
        self.fake_add = False
        self.fake_additions = []
        self.filled = set([])
        self.fill_must_fillables = {}
        self.elimination_fillables = {}
        self.tier = 0
        SudokuSolver.__init__(self, grid, verbose, group_size)

    def add(self, *args, **kwargs):
        if not self.fake_add:
            if self.initialized and not self.guessing:
                # print 'Scanning fillables'
                self.scan_fillables()
                # print 'Done scanning fillables'
                for delayed_args in self.add_me_queue:
                    coords = (delayed_args[0], delayed_args[1])
                    if not self._get_(*coords):
                        # print 'Adding scanned fillable:'
                        SudokuSolver.add(self, *delayed_args)
                if not self._get_(args[0], args[1]):
                    SudokuSolver.add(self, *args)
                self.tier += 1
            else:
                SudokuSolver.add(self, *args, **kwargs)
        else:
            self.fake_additions.append(args)

    def scan_fillables(self):
        self.fake_add = True
        # this will now tell us how many squares at current
        # difficulty could be filled at this moment.
        self.fake_additions = []
        try:
            self.fill_must_fills()
        except:
            pass
        self.fill_must_fillables[self.tier] = set(
            self.fake_additions[:])-self.filled
        self.add_me_queue = self.fake_additions[:]
        self.fake_additions = []
        try:
            self.fill_deterministically()
        except:
            pass
        self.elimination_fillables[self.tier] = set(
            self.fake_additions[:])-self.filled
        self.filled = self.filled | self.fill_must_fillables[
            self.tier] | self.elimination_fillables[self.tier]
        self.add_me_queue.extend(self.fake_additions[:])
        self.fake_add = False

    def guess_least_open_square(self):
        # print 'guessing'
        self.guessing = True
        return SudokuSolver.guess_least_open_square(self)

    def difficulty(self):
        if not self.solved:
            self.solve()
        self.clues = 0
        # Add up the number of our initial clues through some nifty mapping calls
        list(map(lambda r: [setattr(self, 'clues', self.clues.__add__(i and 1 or 0)) for i in r],
            self.virgin.grid))
        self.numbers_added = self.group_size**2 - self.clues
        # self.auto_fill()
        rating = DifficultyRating(self.fill_must_fillables,
                                  self.elimination_fillables,
                                  self.guesses,
                                  self.backtraces,
                                  self.numbers_added)
        return rating

class GuessList (list):
    def __init__(self, *guesses):
        list.__init__(self, *guesses)

    def guesses_for_coord(self, x, y):
        return set([guess.val for guess in [guess for guess in self if guess.x == x and guess.y == y]])

    def remove_children(self, guess):
        removed = []
        for g in guess.children:
            # print 'removing descendant of ',guess,':',g
            if g in self:
                removed.append(g)
                self.remove(g)
                # print 'recursion from ',g,'->'
                # removed.extend(self.remove_descendants(g))
        return removed

    def remove_guesses_for_coord(self, x, y):
        nuking = False
        nuked = []
        for i in range(len(self)-1):
            g = self[i-len(nuked)]
            if g.x == x and g.y == y:
                nuking = True
            if nuking:
                # print 'nuking ',g
                self.remove(g)
                nuked += [g]
        return nuked


class BreadcrumbTrail (GuessList):
    def append(self, guess):
        # Raise an error if we add something to ourselves twice
        if self.guesses_for_coord(guess.x, guess.y):
            raise ValueError("We already have crumbs on %s,%s" %
                             (guess.x, guess.y))
        else:
            list.append(self, guess)


class Guess:
    def __init__(self, x, y, val):
        self.x = x
        self.y = y
        self.children = []
        self.val = val
        self.consequences = {}

    def add_consequence(self, x, y, val):
        # print 'Guess: adding consequence ',x,y,val
        self.consequences[(x, y)] = val

    def __repr__(self):
        s = "<Guess (%s,%s)=%s" % (self.x, self.y, self.val)
        if self.consequences:
            s += " implies: "
            s += ", ".join(["%s->%s" % (k, v)
                           for k, v in list(self.consequences.items())])
        s += ">"
        return s

def add_with_diminishing_importance(lst, diminish_by=lambda x: x+1):
    sum = 0
    for i, n in enumerate(lst):
        sum += float(n) / diminish_by(i)
    return sum


if __name__ == '__main__':
    #sgs = {}
    # for n in range(20):
    #    sg=SudokuGenerator()
    #    sg.generate_puzzles(20)
    #    sgs[sg]=sg.average_difficulty()

    pass