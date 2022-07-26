import os
from pickletools import float8
from random import shuffle, seed as random_seed, randrange
import sys
from typing import Iterable, List, Optional, Tuple, Union, cast
from conf import ROOT_DIR, font
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Custom Font Warning: if glyphs are missing, suppress warnings = 0, don't supress warnings = 1
import reportlab.rl_config
reportlab.rl_config.warnOnMissingFontGlyphs = 0

# Custom fonts folder
folder = ROOT_DIR + os.sep + 'fonts'

# Check if custom font exists, then register it
if font != 'Helvetica':
        fontRegular = os.path.join(folder, font + '.ttf')
        if (os.path.exists(fontRegular)):
            pdfmetrics.registerFont(TTFont(font, fontRegular))
        else:
            print("Font File doesn't exist. Fallback to default font.")
            font = 'Helvetica'

# PDF page size settings
PAGE_WIDTH, PAGE_HEIGHT=A4

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

class UnsolvableSudoku(Exception):
    pass


class _SudokuSolver:
    def __init__(self, sudoku: 'Sudoku'):
        self.width = sudoku.width
        self.height = sudoku.height
        self.size = sudoku.size
        self.sudoku = sudoku

    def _solve(self, puzzlenum) -> Optional['Sudoku']:
        blanks = self.__get_blanks()
        blank_count = len(blanks)
        are_blanks_filled = [False for _ in range(blank_count)]
        blank_fillers = self.__calculate_blank_cell_fillers(blanks)
        solution_board = self.__get_solution(
            Sudoku._copy_board(self.sudoku.board), blanks, blank_fillers, are_blanks_filled)
        solution_difficulty = 0
        if not solution_board:
            return None
        return Sudoku(self.width, self.height, board=solution_board, difficulty=solution_difficulty)

    def __calculate_blank_cell_fillers(self, blanks: List[Tuple[int, int]]) -> List[List[List[bool]]]:
        sudoku = self.sudoku
        valid_fillers = [[[True for _ in range(self.size)] for _ in range(
            self.size)] for _ in range(self.size)]
        for row, col in blanks:
            for i in range(self.size):
                same_row = sudoku.board[row][i]
                same_col = sudoku.board[i][col]
                if same_row and i != col:
                    valid_fillers[row][col][same_row - 1] = False
                if same_col and i != row:
                    valid_fillers[row][col][same_col - 1] = False
            grid_row, grid_col = row // sudoku.height, col // sudoku.width
            grid_row_start = grid_row * sudoku.height
            grid_col_start = grid_col * sudoku.width
            for y_offset in range(sudoku.height):
                for x_offset in range(sudoku.width):
                    if grid_row_start + y_offset == row and grid_col_start + x_offset == col:
                        continue
                    cell = sudoku.board[grid_row_start +
                                        y_offset][grid_col_start + x_offset]
                    if cell:
                        valid_fillers[row][col][cell - 1] = False
        return valid_fillers

    def __get_blanks(self) -> List[Tuple[int, int]]:
        blanks = []
        for i, row in enumerate(self.sudoku.board):
            for j, cell in enumerate(row):
                if cell == Sudoku._empty_cell_value:
                    blanks += [(i, j)]
        return blanks

    def __is_neighbor(self, blank1: Tuple[int, int], blank2: Tuple[int, int]) -> bool:
        row1, col1 = blank1
        row2, col2 = blank2
        if row1 == row2 or col1 == col2:
            return True
        grid_row1, grid_col1 = row1 // self.height, col1 // self.width
        grid_row2, grid_col2 = row2 // self.height, col2 // self.width
        return grid_row1 == grid_row2 and grid_col1 == grid_col2

    # Optimized version of above
    def __get_solution(self, board: List[List[Union[int, None]]], blanks: List[Tuple[int, int]], blank_fillers: List[List[List[bool]]], are_blanks_filled: List[bool]) -> Optional[List[List[int]]]:
        min_filler_count = None
        chosen_blank = None
        for i, blank in enumerate(blanks):
            x, y = blank
            if are_blanks_filled[i]:
                continue
            valid_filler_count = sum(blank_fillers[x][y])
            if valid_filler_count == 0:
                # Blank cannot be filled with any number, no solution
                return None
            if not min_filler_count or valid_filler_count < min_filler_count:
                min_filler_count = valid_filler_count
                chosen_blank = blank
                chosen_blank_index = i

        if not chosen_blank:
            # All blanks have been filled with valid values, return this board as the solution
            return cast(List[List[int]], board)

        row, col = chosen_blank

        # Declare chosen blank as filled
        are_blanks_filled[chosen_blank_index] = True

        # Save list of neighbors affected by the filling of current cell
        revert_list = [False for _ in range(len(blanks))]

        for number in range(self.size):
            # Only try filling this cell with numbers its neighbors aren't already filled with
            if not blank_fillers[row][col][number]:
                continue

            # Test number in this cell, number + 1 is used because number is zero-indexed
            board[row][col] = number + 1

            for i, blank in enumerate(blanks):
                blank_row, blank_col = blank
                if blank == chosen_blank:
                    continue
                if self.__is_neighbor(blank, chosen_blank) and blank_fillers[blank_row][blank_col][number]:
                    blank_fillers[blank_row][blank_col][number] = False
                    revert_list[i] = True
                else:
                    revert_list[i] = False
            solution_board = self.__get_solution(
                board, blanks, blank_fillers, are_blanks_filled)

            if solution_board:
                return solution_board

            # No solution found by having tested number in this cell
            # So we reallow neighbor cells to have this number filled in them
            for i, blank in enumerate(blanks):
                if revert_list[i]:
                    blank_row, blank_col = blank
                    blank_fillers[blank_row][blank_col][number] = True

        # If this point is reached, there is no solution with the initial board state,
        # a mistake must have been made in earlier steps

        # Declare chosen cell as empty once again
        are_blanks_filled[chosen_blank_index] = False
        board[row][col] = Sudoku._empty_cell_value

        return None


class Sudoku:
    _empty_cell_value = None

    def __init__(self, width: int = 3, height: Optional[int] = None, board: Optional[Iterable[Iterable[Union[int, None]]]] = None, difficulty: Optional[float] = None, puzzlenum=1):
        self.width = width
        self.height = height if height else width
        self.size = self.width * self.height
        self.__difficulty: float
        self.puzzlenum = puzzlenum

        assert self.width > 0, 'Width cannot be less than 1'
        assert self.height > 0, 'Height cannot be less than 1'
        assert self.size > 1, 'Board size cannot be 1 x 1'

        if difficulty is not None:
            self.__difficulty = difficulty

        if board:
            blank_count = 0
            self.board: List[List[Union[int, None]]] = [
                [cell for cell in row] for row in board]
            for row in self.board:
                for i in range(len(row)):
                    if not row[i] in range(1, self.size + 1):
                        row[i] = Sudoku._empty_cell_value
                        blank_count += 1
            if difficulty == None:
                if self.validate():
                    self.__difficulty = blank_count / \
                        (self.size * self.size)
                else:
                    self.__difficulty = -2
        else:
            positions = list(range(self.size))
            # random_seed(seed)
            shuffle(positions)
            self.board = [[(i + 1) if i == positions[j]
                           else Sudoku._empty_cell_value for i in range(self.size)] for j in range(self.size)]

    def solve(self, raising: bool = False) -> 'Sudoku':
        solution = _SudokuSolver(self)._solve(self.puzzlenum) if self.validate() else None
        if solution:
            return solution
        elif raising:
            raise Exception('No solution found')
        else:
            solution_board = Sudoku.empty(self.width, self.height).board
            solution_difficulty = -2
            return Sudoku(board=solution_board, difficulty=solution_difficulty)

    def validate(self) -> bool:
        row_numbers = [[False for _ in range(self.size)]
                       for _ in range(self.size)]
        col_numbers = [[False for _ in range(self.size)]
                       for _ in range(self.size)]
        box_numbers = [[False for _ in range(self.size)]
                       for _ in range(self.size)]

        for row in range(self.size):
            for col in range(self.size):
                cell = self.board[row][col]
                box = (row // self.height) * self.height + (col // self.width)
                if cell == Sudoku._empty_cell_value:
                    continue
                elif isinstance(cell, int):
                    if row_numbers[row][cell - 1]:
                        return False
                    elif col_numbers[col][cell - 1]:
                        return False
                    elif box_numbers[box][cell - 1]:
                        return False
                    row_numbers[row][cell - 1] = True
                    col_numbers[col][cell - 1] = True
                    box_numbers[box][cell - 1] = True
        return True

    @ staticmethod
    def _copy_board(board: Iterable[Iterable[Union[int, None]]]) -> List[List[Union[int, None]]]:
        return [[cell for cell in row] for row in board]

    @ staticmethod
    def empty(width: int, height: int):
        size = width * height
        board = [[Sudoku._empty_cell_value] * size] * size
        return Sudoku(width, height, board, 0)

    def difficulty(self, difficulty: float) -> 'Sudoku':
        assert 0 < difficulty < 1, 'Difficulty must be between 0 and 1'
        indices = list(range(self.size * self.size))
        shuffle(indices)
        problem_board = self.solve().board
        for index in indices[:int(difficulty * self.size * self.size)]:
            row_index = index // self.size
            col_index = index % self.size
            problem_board[row_index][col_index] = Sudoku._empty_cell_value
        return Sudoku(self.width, self.height, problem_board, difficulty)

    def show_difficulty(self) -> float:
        if self.__difficulty is not None:
            return self.__difficulty

    def show(self) -> None:
        if self.__difficulty == -2:
            print('Puzzle has no solution')
        if self.__difficulty == -1:
            print('Invalid puzzle. Please solve the puzzle (puzzle.solve()), or set a difficulty (puzzle.difficulty())')
        if not self.board:
            print('No solution')
        print(self.__format_board_ascii())

    def show_full(self) -> None:
        print(self.__str__())

    def get_board_sizes(self) -> None:
        selfsizes = [self.width, self.height, self.size]
        return selfsizes

    def __format_board_ascii(self) -> str:
        table = ''
        cell_length = len(str(self.size))
        format_int = '{0:0' + str(cell_length) + 'd}'
        for i, row in enumerate(self.board):
            if i == 0:
                table += ('+-' + '-' * (cell_length + 1) *
                          self.width) * self.height + '+' + '\n'
            table += (('| ' + '{} ' * self.width) * self.height + '|').format(*[format_int.format(
                x) if x != Sudoku._empty_cell_value else ' ' * cell_length for x in row]) + '\n'
            if i == self.size - 1 or i % self.height == self.height - 1:
                table += ('+-' + '-' * (cell_length + 1) *
                          self.width) * self.height + '+' + '\n'
        return table

    def generate_pdf(self, page, amount_per_page, amount, difficulty, puzzles):
        page_count = 1
        # page data
        inch = 72
        size = PAGE_WIDTH - 72
        top = PAGE_HEIGHT - 72 * 2
        left = 36

        selfsizes = [self.width, self.height, self.size]

        draw_board(page, difficulty, top, left, size, puzzles, selfsizes, amount)

    def generate_four_pdf(self, page, amount, difficulty, puzzles):
        amount_per_page = 4
        inch = 72
        size = PAGE_WIDTH - 72
        top = PAGE_HEIGHT - 72 * 2
        left = 36
        right = left + size
        bottom = top - size

        box_height = size / self.size

        font_size = 24
        if self.width > 3:
            font_size = font_size - (self.width * 2)

        selfsizes = [self.width, self.height, self.size]
        page_data = [top, left, right, bottom, box_height, font_size]

        if amount_per_page == 4:
            top = PAGE_HEIGHT
            left = 36
            size = (PAGE_WIDTH - inch * 1.5) / 2
            coords = [
                (top - inch * 1, left),
                (top - inch * 1, left + size + inch * .5),
                (top - inch * 1 - size - inch, left),
                (top - inch * 1 - size - inch, left + size + inch * .5),
            ]

            firstFour = puzzles[0:amount_per_page]

            # mylist[::2]
            for p, puzzle in enumerate(firstFour):
                if (p == 0):
                    for b, puz in enumerate(puzzle):
                        # print("Sfsdfds", b, puz, puzzle)

                        page_data = [coords[0][0], coords[0][1], right, bottom, box_height, font_size]
                        # print("PRE", page_data)
                        page_count = 1
                        # self.draw_board(page, difficulty, coords[i][0], coords[i][1], size, puzzleboard, page_count)
                        # TODO: separate drawing of grid and positioning of numbers
                        draw_board(page, difficulty, coords[b][0], coords[b][1], size, puzzle, selfsizes, page_count)
                        # print("POST", page_data)
                        # position_numbers(page, puzzle[0].board, selfsizes, page_data)

    def __str__(self) -> str:
        if self.__difficulty == -2:
            difficulty_str = 'INVALID PUZZLE (GIVEN PUZZLE HAS NO SOLUTION)'
        elif self.__difficulty == -1:
            difficulty_str = 'INVALID PUZZLE'
        elif self.__difficulty == 0:
            difficulty_str = 'SOLVED'
        else:
            difficulty_str = '{:.2f}'.format(self.__difficulty)
        return '''
---------------------------
{}x{} ({}x{}) SUDOKU PUZZLE
Difficulty: {}
---------------------------
{}
        '''.format(self.size, self.size, self.width, self.height, difficulty_str, self.__format_board_ascii())

def generate_pdf2(doc, puzzles, amount_per_page, pages, difficu):
    Sudoku().generate_pdf(doc, puzzles, amount_per_page, pages, difficu)

def draw_board(page, difficulty, top, left, size, puzzles, selfsizes, page_count=1):
        gridwidth, gridheight, gridsize = selfsizes
        right = left + size
        bottom = top - size

        thin_line = 1
        thick_line = 4
        box_height = size / gridsize

        font_size = 24
        if gridwidth > 3:
            font_size = font_size - (gridwidth * 2)

        page_data = [top, left, right, bottom, box_height, font_size]

        # custom text above sudoku
        text_above_sudoku = str(difficulty).capitalize()

        # set font and font size for custom text
        page.setFont(font, 16)
        page.drawString(left, PAGE_HEIGHT - 72 * 1.5, "Schwierigkeitsgrad: " + text_above_sudoku)

        # draw page number
        page_number_font_size = 20
        page.setFont("Helvetica", page_number_font_size)
        page.drawString(PAGE_WIDTH / 2 - font_size / 4, 62, str(page_count))

        # draw sudoku board based on dynamic size
        for i in range(0, gridsize + 1):
            squared_grid_size = i % gridwidth

            if squared_grid_size == 0:
                page.setLineWidth(thick_line)
            else:
                page.setLineWidth(thin_line)
            page.line(left, top - i * box_height, right, top - i * box_height)
            page.line(left + i * box_height, top, left + i * box_height, bottom)

        # set font and font size for Sudoku Board
        page.setFont("Helvetica", font_size)

        print(puzzles)
        # position numbers inside cells
        if type(puzzles) == Sudoku:
            position_numbers(page, puzzles.board, selfsizes, page_data)
        else:
            for p, puzzle in enumerate(list(puzzles)):
                # if p % 4:
                # print("p puzzle", p, puzzle)

                # for puz in puzzle:
                    # print("puz", puz)
                position_numbers(page, puzzle.board, selfsizes, page_data)

def position_numbers(page, board, selfsizes, pagedata):
    gridwidth, gridheight, gridsize = selfsizes
    top, left, right, bottom, box_height, font_size = pagedata

    for i, row in enumerate(board):
        for j, col in enumerate(row):
            if col != None:  # TODO: better if condition
                # adjust position for double digit numbers
                if col not in range(10, gridsize + 1):
                    page.drawString(left + j * box_height + box_height * 0.38,
                                    top - i * box_height - box_height * 0.65, str(col))
                else:
                    page.drawString(
                        left - (font_size / gridwidth + (
                                gridwidth / 2)) + j * box_height + box_height * 0.38,
                        top - i * box_height - box_height * 0.65, str(col))
