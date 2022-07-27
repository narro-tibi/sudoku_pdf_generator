import math
import os
import json
from conf import ROOT_DIR, font
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
# Custom Font Warning: if glyphs are missing, suppress warnings = 0, don't supress warnings = 1
import reportlab.rl_config
reportlab.rl_config.warnOnMissingFontGlyphs = 0

with open('settings.json') as f:
    json_data = json.load(f)

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


def generate_single_pdf(sizes, page, pagenum, amount, puzzle):
    # page data
    inch = 72
    size = PAGE_WIDTH - 72
    top = PAGE_HEIGHT - 72 * 2
    left = 36

    selfsizes = sizes

    # print current progress
    print("Currently working on drawing a puzzle on page " + str(pagenum) + "...")

    draw_board(page, pagenum, top, left, size, puzzle, selfsizes, json_data['FONT_SIZE_SINGLE_PAGE'], pagenum)


def generate_four_pdf(page, pagenum, puzzles):
    inch = 72
    top = PAGE_HEIGHT
    left = 36
    size = (PAGE_WIDTH - inch * 1.5) / 2
    right = left + size
    bottom = top - size

    # todo: get data per puzzle
    board_size = [3,3,9]
    for i, puzzle in enumerate(puzzles):
        board_size = puzzle.get_board_sizes()

    box_height = size / board_size[2]

    font_size = 24
    if board_size[0] > 3:
        font_size = font_size - (board_size[0] * 2)

    selfsizes = board_size
    page_data = [top, left, right, bottom, box_height, font_size]

    coords = [
        (top - inch * 1, left),
        (top - inch * 1, left + size + inch * .5),
        (top - inch * 1 - size - inch, left),
        (top - inch * 1 - size - inch, left + size + inch * .5),
    ]

    # print current progress
    print("Currently working on drawing a puzzle on page " + str(pagenum) + "...")

    for i, puzzle in enumerate(puzzles):
        sudoku_index = pagenum * 4 - 3 + i

        draw_board(page, sudoku_index, coords[i][0], coords[i][1], size, puzzle, selfsizes, json_data['FONT_SIZE_4_PAGE'], pagenum)


def generate_six_pdf(page, pagenum, puzzles):
    inch = 72
    top = PAGE_HEIGHT
    left = 36
    size = (PAGE_WIDTH - inch * 1.5) / 2.5
    right = left + size
    bottom = top - size

    # todo: get data per puzzle
    board_size = [3,3,9]
    for i, puzzle in enumerate(puzzles):
        board_size = puzzle.get_board_sizes()

    box_height = size / board_size[2]

    font_size = 24
    if board_size[0] > 3:
        font_size = font_size - (board_size[0] * 2)

    selfsizes = board_size
    page_data = [top, left, right, bottom, box_height, font_size]

    col = row = 0
    i = 0
    for p, puzzle in enumerate(puzzles):
        sudoku_index = pagenum * 6 - 5 + i
        i += 1

        # print current progress
        print("Currently working on puzzle solutions... " + str(p + 1))

        # todo: get previous last page number, then count page number from there (e.g. 300 sudoku pages, then solutions 301+)
        # todo: center position of solutions
        draw_board(page, sudoku_index, PAGE_HEIGHT - 54 - row * 72 * 3.25, 72 + col * 72 * 3.5, 72 * 2.75, puzzle,
                   selfsizes, json_data['FONT_SIZE_6_PAGE'], pagenum)
        col += 1
        if col == 2:
            col = 0
            row += 1
            if row == 3:
                col = row = 0
                # if showFooter:
                #     generateFooter(page)
                # page.showPage()

    # print current progress
    print("Currently working on drawing a puzzle on page " + str(pagenum) + "...")


def draw_board(page, sudoku_number, top, left, size, puzzle, selfsizes, font_size = 24, page_count=1, is_solution = False):
    gridwidth, gridheight, gridsize = selfsizes
    right = left + size
    bottom = top - size

    thin_line = 1
    thick_line = 4
    box_height = size / gridsize

    # change line thickness for board sizes
    if json_data['SUDOKUS_PER_PAGE'] == 4:
        thin_line = 0.8
        thick_line = 2.75
    if json_data['SUDOKUS_PER_PAGE'] == 6:
        thin_line = 0.4
        thick_line = 2
    if is_solution and json_data['SUDOKUS_PER_PAGE'] == 1:
        thin_line = 0.4
        thick_line = 2
    if is_solution and json_data['SUDOKUS_PER_PAGE'] != 1:
        thin_line = 0.25
        thick_line = 1.5

    if gridwidth > 3:
        font_size = font_size - (gridwidth * 2)

    page_data = [top, left, right, bottom, box_height, font_size]

    # custom text above sudoku
    sudoku_index = str(sudoku_number).capitalize()

    # todo: make a check for text positioning and font size
    # set font and font size for custom text per sudoku
    page.setFont(font, font_size)
    # page.drawString(left, PAGE_HEIGHT - 72 * 1.5, json_data['CUSTOM_TEXT'] + sudoku_index)
    page.drawString(left, top + (font_size / 1.5), json_data['CUSTOM_TEXT'] + sudoku_index)

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

    # position numbers inside cells
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


def generateSolutions(page, puzzles, doc_page_number):
    board_size = [3, 3, 9]
    selfsizes = board_size

    # 9 grid display values for a page
    col_limit = 3
    top_offset = 72
    top_multiplier = 2.5
    left_offset = 36
    left_multiplier = 2.5
    size_multiplier = 2
    modulo_value = 9

    # 6 grid display values for a page
    if json_data['SUDOKUS_PER_PAGE'] == 1:
        col_limit = 2
        top_offset = 54
        top_multiplier = 3.25
        left_offset = 72
        left_multiplier = 3.5
        size_multiplier = 2.75
        modulo_value = 6

    col = row = 0
    i = 0
    j = 1
    page_num = doc_page_number + j
    for puz, d in enumerate(puzzles):
        i += 1
        solver = d.solve()
        difficulty_rating = d.show_difficulty()

        # print current progress
        print("Currently working on puzzle solutions... " + str(puz + 1))

        # todo: get previous last page number, then count page number from there (e.g. 300 sudoku pages, then solutions 301+)
        # todo: center position of solutions
        draw_board(page, i, PAGE_HEIGHT - top_offset - row * 72 * top_multiplier, left_offset + col * 72 * left_multiplier, 72 * size_multiplier, solver,
                   selfsizes, json_data['FONT_SIZE_SOLUTIONS'], page_num, is_solution=True)
        col += 1
        if col == col_limit:
            col = 0
            row += 1
            if row == 3:
                col = row = 0
                # if showFooter:
                #     generateFooter(page)
                page.showPage()
        if ((puz + 1) % modulo_value == 0):
            j += 1
            page_num = doc_page_number + j