import csv
import re
import pandas as pd
import numpy as np
import os
import xlsxwriter

src = "D:\\game\\steamapps\\common\\14 Minesweeper Variants 2\\MineVar\\puzzle\\all_puzzles_dedup.txt"

csv = "stats.csv"

xlsx = "stats.xlsx"

'''
statistics of 
- maximum number of clues used for a single step,
- total number of clues used,
- starting clues,
- starting clues on sub board,
- final clues
per level type
'''

LHS = ["H", "C", "S", "G", "F", "B", "T"]
LHS_BONUS = ["Z", "G'"]
RHS = ["X", "D", "P", "E", "M", "A", "L"]
RHS_BONUS = ["X'", "I"]
MAINPAGE = ["V", *LHS, *RHS]
# ATTACH = ["EX", "LD", "LM", "EA", "LX", "ED", "LP"]
ATTACH = ["E-X", "L-D", "L-M", "E-A", "L-X", "E-D", "L-P"]
ATTACH_BONUS = ["E'", "E^", "L'"]
# COMBO_ALT = ["GH", "CH", "CG", "FG", "FH", "CF", "BH", "GR"]
COMBO_ALT = ["G-H", "C-H", "C-G", "F-G", "F-H", "C-F", "B-H", "G-R"]
RHS_CLUE = ["X", "D", "P", "M", "A"]
RHS_BOARD = ["E", "L"]
PAGES = ["F", "!", "+'", "&'", "?", "5", "6", "7", "8", "!!", "+'!", "&'!", "?!", "5!", "6!", "7!", "8!"]
GALLERY_COLUMNS = ["V", *RHS, *RHS_BONUS, "E-#", "L-#", *ATTACH]
GALLERY_ROWS = ['', *LHS, *LHS_BONUS]

FIELDS = ['id', 'type', 'dimension', 'difficulty', 'max_clues', 'workload', 'starting_clues', 'starting_questions', 'number_clues']
KEYS = FIELDS[4:]

def get_type(level_type):
    '''
    [2B][2X'][@c] -> ("B", "X'")
    [V] -> ("V",)
    [2E][2#] -> ("E", "#")
    [2G][R+] -> ("G", "R+")
    '''
    pattern = re.compile(r'\[\d?([A-Za-z^\'#]+)\+?\]')
    matches = pattern.findall(level_type)
    return tuple(matches)

def get_difficulty(level_type):
    # number of !
    return level_type.count('!')

def is_starting_clue(clue):
    # contains capital letters and numbers
    return any([c.isupper() for c in clue]) and any([c.isdigit() for c in clue])

def is_number_clue(clue):
    # contains numbers
    return any([c.isdigit() for c in clue])

def is_starting_question(clue):
    return clue == 'Q'

def is_starting_sub_question(clue):
    return clue == 'Qprior'

def read_file(in_file, out_file):
    # remove, create, write header
    if os.path.exists(out_file):
        os.remove(out_file)
    
    with open(out_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDS)
        writer.writeheader()

        with open(in_file, 'r') as f:
            lines = f.readlines()[1:]
            '''
            [2A]!!5x5-10-(V;5x1,2x1,1x5)-6457	q 2a2 f f q 2a2 2A0 2a2 2a8 f f 2a2 2a0 q f f q q f f q q 2A6 f f
            [2B][2E][2#][@c]!5x10-10-(4x1,3x3,2x7,1x16;L4R1)-1781	f 2e4 q 2m0 f f q q q q 2EA1 f f f 2EA1 q q q f q 2ea3 Q 2ed4 2p1 2EA0 q q f q q f q f f q q q q q f q f 2M0 2ex23 f q f q q q
            [2T][2P]!5x5-12-(1x6,-4x1;L4R0)-1672	2P1 f f 2p2 q f f Q q f f q q f f 2P1 Q f Q 2P1 f f q q f
            '''

            for line in lines:
                parts = line.split('\t')

                level_id = parts[0]
                # [2A]!!5x5-10-(V;5x1,2x1,1x5)-6457 -> [2A]!!5x5-10-6457
                ingame_id = re.sub(r'\(.*\)-', '', level_id)
                level_type = level_id.split('-')[0]
                r = re.search(r'(\d+)x(\d+)', level_type)
                row = int(r.group(1))
                col = int(r.group(2))

                # get the ( ) part
                no_of_clues = level_id.split('(')[1].split(')')[0]
                # get all %dx%d pairs
                clues = re.findall(r'(\d+)x(\d+)', no_of_clues)
                clue_pairs = [(int(clue[0]), int(clue[1])) for clue in clues]
                clue_pairs.sort(key=lambda x: -x[0])
                max_clues = clue_pairs[0][0]
                workload = sum([(clue[0] - 1) * clue[1] for clue in clue_pairs])

                grids = parts[1].strip().split(' ')
                if col > row:
                    # the grids is row x col, the main board is row x row
                    # i.e. grids[0:row], [col:col+row], [2*col:2*col+row], ..
                    main_board = [grids[i*col:i*col+row] for i in range(row)]
                    mb = [grid for row in main_board for grid in row]
                    sub_board = [grids[i*col+row:(i+1)*col] for i in range(row)]
                    sb = [grid for row in sub_board for grid in row]
                    starting_questions = len([clue for clue in sb if is_starting_sub_question(clue)])
                else:
                    mb = grids
                    starting_questions = 0
                
                starting_clues = len([clue for clue in mb if is_starting_clue(clue)])
                starting_questions = starting_questions + len([clue for clue in mb if is_starting_question(clue)])
                number_clues = len([clue for clue in mb if is_number_clue(clue)])
                
                writer.writerow({
                    'id': ingame_id,
                    'type': '-'.join(get_type(level_type)),
                    'dimension': row,
                    'difficulty': get_difficulty(level_type),
                    'max_clues': max_clues,
                    'workload': workload,
                    'starting_clues': starting_clues,
                    'starting_questions': starting_questions,
                    'number_clues': number_clues
                })

def get_mean(df, filters, key):
    for k, v in filters.items():
        df = df[df[k] == v]
    return df[key].mean()

def display_type(csv_type, diff, dim=None):
    return ''.join([
        *csv_type.split('-'),
        '!' * diff,
        str(dim) if dim else ''
    ])

def is_gray_row(row_name):
    return row_name in LHS_BONUS

def is_gray_col(col_name):
    return col_name in RHS_BONUS or col_name in ATTACH

def is_gray_cell(row_name, col_name):
    return is_gray_row(row_name) or is_gray_col(col_name)

def analyze(in_file, out_file):
    df = pd.read_csv(in_file)
    workbook = xlsxwriter.Workbook(out_file)
    center_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter'
    })
    text_format = workbook.add_format({
        'border': 1,
        'align': 'center',
        'valign': 'vcenter'
    })
    gray_text_format = workbook.add_format({
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'color': '#666666'
    })
    number_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'num_format': '0.000'
    })
    gray_number_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'num_format': '0.000',
        'color': '#666666'
    })

    def row_desc(worksheet, x, y):
        worksheet.write(x+1, y, 'Max Clues', center_format)
        worksheet.write(x+2, y, 'Workload', center_format)
        worksheet.write(x+3, y, 'Starting Clues', center_format)
        worksheet.write(x+4, y, 'Starting ?s', center_format)
        worksheet.write(x+5, y, 'Number Clues', center_format)

    for page_id, page in enumerate(PAGES):
        diff = page.count('!')
        if page[0].isdigit():
            worksheet = workbook.add_worksheet(page)
            dim = int(page[0])
            x, y = 1, 1
            
            worksheet.set_column(0, 0, 14)

            for row, row_name in enumerate(GALLERY_ROWS):
                row_desc(worksheet, x, 0)

                for col, col_name in enumerate(GALLERY_COLUMNS):
                    cell_name = '-'.join([row_name, col_name]) if (row > 0 and col > 0) else col_name

                    worksheet.write(x, y, display_type(cell_name, diff, dim), gray_text_format if is_gray_cell(row_name, col_name) else text_format)

                    for key_id, key in enumerate(KEYS):
                        filters = {'type': cell_name, 'difficulty': diff, 'dimension': dim}
                        mean = get_mean(df, filters, key)
                        # print(f'{cell_name} {display_type(cell_name, diff, dim)} {key} {mean}')
                        worksheet.write(x+1+key_id, y, mean, gray_number_format if is_gray_cell(row_name, col_name) else number_format)

                    y += 1

                    if col_name == "I":
                        y += 1
                
                x += 6
                y = 1
    
    workbook.close()

def main():
    # read_file(src, csv)
    analyze(csv, xlsx)

if __name__ == "__main__":
    main()