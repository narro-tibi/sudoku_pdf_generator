import os
import sys
ROOT_DIR = os.path.abspath(os.curdir)

# getting optional custom font
font = 'Helvetica'
if len(sys.argv) > 4:
    font = sys.argv[4]