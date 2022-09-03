import math
import sys
import time
import json
from conf import pdf_file_path, PAGE_SIZE, amount_per_page
from reportlab.pdfgen import canvas
from Generator.sudoku_maker import make_puzzles
from Generator.printpuzzles import generate_single_pdf, generate_four_pdf, generateSolutions, generate_six_pdf

with open('settings.json') as f:
    json_data = json.load(f)

# create pdf canvas
doc = canvas.Canvas(filename=pdf_file_path, pagesize=PAGE_SIZE)

# grab current time before running the code
start = time.time()


def createPDF(output_file, puzzles, perPage = 1, showSolutions = json_data['SHOW_SOLUTIONS']):
    # doc = canvas.Canvas(filename=output_file, pagesize=PAGE_SIZE)
    doc_page_number = 1

    if perPage == 1:
        i = 0
        for puzzle in puzzles:
            # print("PUZZLE CREATE PDF", puzzle)
            i += 1
            doc_page_number = doc.getPageNumber()
            # TODO: update for dynamic grid size
            nine_puz_grid_size = [3, 3, puzzle[0].group_size]
            boardsize = nine_puz_grid_size
            # generate_single_pdf(boardsize, doc, i, i + 1, puzzle)
            generate_single_pdf(puzzle, boardsize, doc, i)
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


if __name__ == '__main__':
    puzzles = make_puzzles(json_data['SUDOKU_AMOUNT'], json_data['DIFFICULTY_LEVEL'], json_data['SORT_BY_DIFFICULTY'], json_data['SUDOKU_SQUARE_SIZE'])
    createPDF(pdf_file_path, puzzles, amount_per_page)

# grab current time after running the code
end = time.time()
total_time = end - start
print("Total time:\n" + str(total_time) + " seconds.")

