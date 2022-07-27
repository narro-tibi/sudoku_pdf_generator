import math
import os
import random
import sys
import time
import json
from conf import ROOT_DIR
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from Generator.sudoku import Sudoku
from Generator.printpuzzles import generate_single_pdf, generate_four_pdf, generateSolutions, generate_six_pdf

with open('settings.json') as f:
    json_data = json.load(f)

# set pdf folder path
folder = ROOT_DIR + os.sep + 'pdfs'

# get file name and create new files
pdf_file_name = json_data['PDF_FILE_NAME']
pdf_file_path = str(folder + os.sep + pdf_file_name + '.pdf')

def nextnonexistent(f):
    fnew = f
    root, ext = os.path.splitext(f)
    i = 0
    while os.path.exists(fnew):
        i += 1
        fnew = '%s_%i%s' % (root, i, ext)
    return fnew

pdf_file_path = nextnonexistent(pdf_file_path)

# get desired amount of puzzles
amount = json_data['SUDOKU_AMOUNT']
if len(sys.argv) > 1:
    amount = sys.argv[1]

# get desired amount of puzzles displayed per page
amount_per_page = json_data['SUDOKUS_PER_PAGE']

# create pdf canvas
doc = canvas.Canvas(filename=pdf_file_path, pagesize=A4)

# grab current time before running the code
start = time.time()

# Initializes a Sudoku puzzle with n x m grid of a certain difficulty (percentage of numbers removed)
puzzles = list()
for i in range(int(amount)):
    puzzles.append(Sudoku(json_data['SUDOKU_GRID_SIZE'], puzzlenum=i + 1).difficulty(random.uniform(json_data['MIN_DIFFICULTY_LEVEL'], json_data['MAX_DIFFICULTY_LEVEL'])))

def createPDF(output_file, puzzles, perPage = 1, showSolutions = json_data['SHOW_SOLUTIONS']):
    doc = canvas.Canvas(filename=output_file, pagesize=A4)
    doc_page_number = 1
    # todo: update solution solver for larger grid size
    # temporary solution: disable solution display on larger than 3x3 grids
    if json_data['SUDOKU_GRID_SIZE'] != 3:
        showSolutions = False

    if perPage == 1:
        i = 0
        for puzzle in puzzles:
            i += 1
            doc_page_number = doc.getPageNumber()
            boardsize = puzzle.get_board_sizes()
            generate_single_pdf(boardsize, doc, i, i + 1, puzzle)
            doc.showPage()
        if showSolutions:
            generateSolutions(doc, puzzles, doc_page_number)
            doc.showPage()
        doc.save()
    elif perPage == 4:
        for i in range(0, int(math.ceil(float(len(puzzles)) / 4))):
            doc_page_number = doc.getPageNumber()
            plist = puzzles[i*4:(i+1)*4]
            generate_four_pdf(doc, i + 1, plist)
            doc.showPage()
        if showSolutions:
            generateSolutions(doc, puzzles, doc_page_number)
            doc.showPage()
        doc.save()
    elif perPage == 6:
        for i in range(0, int(math.ceil(float(len(puzzles)) / 6))):
            doc_page_number = doc.getPageNumber()
            plist = puzzles[i * 6:(i + 1) * 6]
            generate_six_pdf(doc, i + 1, plist)
            doc.showPage()
        if showSolutions:
            generateSolutions(doc, puzzles, doc_page_number)
            doc.showPage()
        doc.save()

createPDF(pdf_file_path, puzzles, amount_per_page)

# grab current time after running the code
end = time.time()
total_time = end - start
print("Total time:\n" + str(total_time) + " seconds.")

