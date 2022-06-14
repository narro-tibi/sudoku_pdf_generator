import os
import sys
import time

from reportlab.lib.pagesizes import A4

from Generator.sudoku import Sudoku, generate_pdf2
from conf import ROOT_DIR
from reportlab.pdfgen import canvas

# set pdf folder path
folder = ROOT_DIR + os.sep + 'pdfs'

# getting file name based on difficulty rating
pdf_file_name = str(folder + os.sep + sys.argv[1] + ".pdf")

# getting desired amount of puzzles
amount = 1
if len(sys.argv) > 1:
    amount = sys.argv[2]

# get desired difficulty level
# todo: randomize between values depending on text setting, e.g. "hard": 0.65-0.75
difficulty_level = 0.8

# get desired amount of puzzles displayed per page
amount_per_page = 1

# create pdf canvas
doc = canvas.Canvas(filename=pdf_file_name, pagesize=A4)

# Grab Currrent Time Before Running the Code
start = time.time()

# Initializes a Sudoku puzzle with n x m grid of a certain difficulty (percentage of numbers removed)
objs = list()
for i in range(int(amount)):
    objs.append(Sudoku(3, puzzlenum=i+1).difficulty(float(difficulty_level)))

for i, puzzle in enumerate(objs):
    # print("Printing to PDF. Puzzle No." + str(i))
    puzzle.generate_pdf(doc, amount_per_page, i+1, difficulty_level)
    doc.showPage()

    # pdf_file_name = pdf_file_name + str(i) + ".pdf"
    # print(pdf_file_name)
    # doc = canvas.Canvas(filename=pdf_file_name, pagesize=A4)

doc.save()

# Grab Currrent Time After Running the Code
end = time.time()
total_time = end - start
print("Total time:\n" + str(total_time) + " seconds.")
