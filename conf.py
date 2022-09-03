import json
import math
import os
import sys
from reportlab.lib.units import mm, inch

ROOT_DIR = os.path.abspath(os.curdir)

# helper functions
def nextnonexistent(file):
    """create and increment new file next to sibling"""
    fnew = file
    root, ext = os.path.splitext(file)
    i = 0
    while os.path.exists(fnew):
        i += 1
        fnew = '%s_%i%s' % (root, i, ext)
    return fnew

def get_din_size(pagesize):
    """return din sizes of paper (based on 72dpi per page)"""
    w, h = pagesize
    din_width = w / 2.835
    din_height = h / 2.835

    return math.ceil(din_width), math.ceil(din_height)


with open('settings.json') as f:
    json_data = json.load(f)

# set pdf folder path
folder = ROOT_DIR + os.sep + 'pdfs'

# get PDF page size settings and reportlab tuples by multiplication with mm
# reference: A4 = (210*mm,297*mm)
PAGE_SIZE = tuple(mm * elem for elem in eval(json_data["PDF_PAGE_SIZE"]))

# for attr, value in pdf_sizes.items():
#     if (json_data['PDF_PAGE_SIZE'] == attr):
#         PAGE_SIZE = value

# get file name and create new files
pdf_file_name = json_data['PDF_FILE_NAME']
pdf_file_path = str(folder + os.sep + pdf_file_name + '.pdf')

pdf_file_path = nextnonexistent(pdf_file_path)

# get desired amount of puzzles
amount = json_data['SUDOKU_AMOUNT']
if len(sys.argv) > 1:
    amount = sys.argv[1]

# get desired amount of puzzles displayed per page
amount_per_page = json_data['SUDOKUS_PER_PAGE']