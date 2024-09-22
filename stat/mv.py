import csv
import re
import pandas as pd
import numpy as np
import os
import xlsxwriter

in1 = "D:\\game\\steamapps\\common\\14 Minesweeper Variants\\MineVar\\puzzle\\all_puzzles_dedup.txt"

out1 = "mv/mv_stats.csv"

out2 = "mv/mv_stats_mean.xlsx"

out3 = "mv/mv_stats_workload.xlsx"

LHS = ["Q", "C", "T", "O", "D", "S", "B"]
LHS_BONUS = ["D'", "A", "H", "T'"]
RHS = ["M", "L", "W", "N", "X", "P", "E"]
RHS_BONUS = ["X'", "K", "W'", "E'"]
# COMBO_ALT = [
#     "CD", "CQ", "CT", "OQ", "OT", "QT",
#     "LM", "MX", "MN", "NX", "UW"
# ]
COMBO_ALT = [
    ("C", "D"), ("C", "Q"), ("C", "T"), ("O", "Q"), ("O", "T"), ("Q", "T"),
    ("L", "M"), ("M", "X"), ("M", "N"), ("N", "X"), ("U", "W")
]
TAG = ["#", "#'"]
PAGES = ["F", "!", "+ʹ", "¿", "5", "6", "7", "8", "!!", "+ʹ!", "¿!", "5!", "6!", "7!", "8!"]

MAIN = ["V", *LHS, *RHS]
LHS_FULL = [*LHS, *LHS_BONUS]
RHS_FULL = [*RHS, *RHS_BONUS]
GALLERY_COLUMNS = ["V", *RHS, *RHS_BONUS, *TAG]
GALLERY_ROWS = ["", *LHS, *LHS_BONUS]

FIELDS = ['id', 'type', 'dimension', 'difficulty', 'max_clues', 'workload', 'starting_clues', 'starting_questions', 'number_clues', 'category']
KEYS = FIELDS[4:9]
KEY_DICT = {
    'max_clues': 'Max Clues',
    'workload': 'Workload',
    'starting_clues': 'Starting Clues',
    'starting_questions': 'Starting ?s',
    'number_clues': 'Number Clues'
}

FONT = 'Aptos'

def get_type(level_type):
    pattern = re.compile(r'\[\d?([A-Za-z^\'#]+)\+?\]')
    matches = pattern.findall(level_type)
    return tuple(matches)

def is_starting_clue(clue):
    return clue.isupper() and clue != 'Q'

def is_number_clue(clue):
    return clue.lower() != 'q' and clue.lower() != 'f'

def is_starting_question(clue):
    return clue == 'Q'

def get_category(types):
    if len(types) == 1:
        if types[0] in MAIN:
            return 'F'
        if types[0] == '#':
            return '#'
        if types[0] == '#\'':
            return '#?'
        return '?'
    if len(types) == 2:
        if types[0] in LHS_FULL and types[1] in RHS_FULL:
            if types[0] in LHS and types[1] in RHS:
                return '+'
            return '+?'
        if types[0] in LHS_FULL and types[1] in TAG:
            if types[0] in LHS and types[1] == '#':
                return '#+'
            return '#+?'
        if types in COMBO_ALT:
            return '+\''
    return '?1'

def read_file(in_file, out_file):
    if os.path.exists(out_file):
        os.remove(out_file)
    
    with open(out_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDS)
        writer.writeheader()

        with open(in_file, 'r') as f:
            lines = f.readlines()[1:]
            '''
            [C][T]7x7-20-10013	qfofqoqfqffofffqqqfoqoqoqfqOfoffoooqfqqffqqfqffof	4x3,3x3,2x5,1x9,-1x1,-3x1
            '''

            for line in lines:
                parts = line.split('\t')
                level_id = parts[0]
                dim = re.search(r'(\d+)x(\d+)', level_id).groups()
                dim = int(dim[0])

                no_of_clues = parts[2]
                clues = re.findall(r'(\d+)x(\d+)', no_of_clues)
                clue_pairs = [(int(clue[0]), int(clue[1])) for clue in clues]
                clue_pairs.sort(key=lambda x: -x[0])
                max_clues = clue_pairs[0][0]
                workload = sum([(clue[0] - 1) * clue[1] for clue in clue_pairs])

                grids = parts[1]
                starting_clues = len([c for c in grids if is_starting_clue(c)])
                starting_questions = len([c for c in grids if is_starting_question(c)])
                number_clues = len([c for c in grids if is_number_clue(c)])

                types = get_type(level_id)

                if max_clues >= 6 or (max_clues == 5 and dim <= 7):
                    diff = 2
                elif max_clues >= 4 or (max_clues == 3 and dim <= 5):
                    diff = 1
                else:
                    diff = 0

                writer.writerow({
                    'id': level_id,
                    'type': '-'.join(types),
                    'dimension': dim,
                    'difficulty': diff,
                    'max_clues': max_clues,
                    'workload': workload,
                    'starting_clues': starting_clues,
                    'starting_questions': starting_questions,
                    'number_clues': number_clues,
                    'category': get_category(types)
                })

def get(df, filters, key):
    for k, v in filters.items():
        df = df[df[k] == v]
    return df[key].mean()

def display_type(csv_type, diff, dim):
    return ''.join([
        *csv_type.split('-'),
        '!' * diff,
        str(dim)
    ])

def display_type_tuple(tuple_type, diff, dim):
    return ''.join([
        *tuple_type,
        '!' * diff,
        str(dim)
    ])

def is_gray_row(row_name):
    return row_name in LHS_BONUS

def is_gray_col(col_name):
    return col_name in RHS_BONUS or col_name == '#\''

def is_gray_cell(row_name, col_name):
    return is_gray_row(row_name) or is_gray_col(col_name)

def analyze(in_file, out_file, keys=KEYS, desc=True):
    df = pd.read_csv(in_file)
    workbook = xlsxwriter.Workbook(out_file)
    center_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'font_name': FONT
    })
    text_format = workbook.add_format({
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'font_name': FONT
    })
    gray_text_format = workbook.add_format({
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'color': '#666666',
        'font_name': FONT
    })
    number_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'num_format': '0.000',
        'font_name': FONT
    })
    gray_number_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'num_format': '0.000',
        'color': '#666666',
        'font_name': FONT
    })

    y_offset = len(keys) + 1

    def row_desc(worksheet, x, y):
        if desc:
            for i, key in enumerate(keys):
                worksheet.write(x+1+i, y, KEY_DICT[key], center_format)
    
    def create_worksheet(name):
        worksheet = workbook.add_worksheet(name)
        if desc:
            worksheet.set_column(0, 0, 14)
        return worksheet
    
    def cond_format(worksheet):
        # white to green color scale
        if not desc:
            worksheet.conditional_format(1, 1, 100, 100, {
                'type': '2_color_scale',
                'min_color': "#FFFFFF",
                'max_color': "#92D050"
            })
    
    for page_id, page in enumerate(PAGES):
        diff = page.count('!')

        if page_id < 2 or page_id == 8:
            worksheet = create_worksheet(page)
            x, y = 1, 1
            
            row_desc(worksheet, x, 0)
            y = 1
            for dim in [5, 6, 7, 8]:
                worksheet.write(x, y, display_type("V", diff, dim), text_format)
                for key_id, key in enumerate(keys):
                    filters = {'type': 'V', 'difficulty': diff, 'dimension': dim}
                    stat = get(df, filters, key)
                    worksheet.write(x+1+key_id, y, stat, number_format)
                y += 1
            x += y_offset
            x += 1 # empty row

            for row, l, r in zip(range(len(LHS)), LHS, RHS):
                row_desc(worksheet, x, 0)
                y = 1
                for dim in [5, 6, 7, 8]:
                    worksheet.write(x, y, display_type(l, diff, dim), text_format)
                    for key_id, key in enumerate(keys):
                        filters = {'type': l, 'difficulty': diff, 'dimension': dim}
                        stat = get(df, filters, key)
                        worksheet.write(x+1+key_id, y, stat, number_format)
                    y += 1
                y = 6
                for dim in [5, 6, 7, 8]:
                    worksheet.write(x, y, display_type(r, diff, dim), text_format)
                    for key_id, key in enumerate(keys):
                        filters = {'type': r, 'difficulty': diff, 'dimension': dim}
                        stat = get(df, filters, key)
                        worksheet.write(x+1+key_id, y, stat, number_format)
                    y += 1
                x += y_offset
            x += 1 # empty row

            if diff == 2:
                row_desc(worksheet, x, 0)
                y = 6
                for dim in [5, 6, 7, 8]:
                    worksheet.write(x, y, display_type("#", diff, dim), text_format)
                    for key_id, key in enumerate(keys):
                        filters = {'type': '#', 'difficulty': diff, 'dimension': dim}
                        stat = get(df, filters, key)
                        worksheet.write(x+1+key_id, y, stat, number_format)
                    y += 1
                
                cond_format(worksheet)
                continue
            
            row_desc(worksheet, x, 0)
            y = 1
            for dim in [5, 6, 7, 8]:
                worksheet.write(x, y, display_type("+", diff, dim), text_format)
                for key_id, key in enumerate(keys):
                    filters = {'category': '+', 'difficulty': diff, 'dimension': dim}
                    stat = get(df, filters, key)
                    worksheet.write(x+1+key_id, y, stat, number_format)
                y += 1
            y = 6
            for dim in [5, 6, 7, 8]:
                worksheet.write(x, y, display_type("#", diff, dim), text_format)
                for key_id, key in enumerate(keys):
                    filters = {'type': '#', 'difficulty': diff, 'dimension': dim}
                    stat = get(df, filters, key)
                    worksheet.write(x+1+key_id, y, stat, number_format)
                y += 1
            x += y_offset
        
            row_desc(worksheet, x, 0)
            y = 1
            for dim in [5, 6, 7, 8]:
                worksheet.write(x, y, display_type("#+", diff, dim), text_format)
                for key_id, key in enumerate(keys):
                    filters = {'category': '#+', 'difficulty': diff, 'dimension': dim}
                    stat = get(df, filters, key)
                    worksheet.write(x+1+key_id, y, stat, number_format)
                y += 1
            
            cond_format(worksheet)

        elif page.startswith('+'):
            worksheet = create_worksheet(page)
            x, y = 1, 1

            for row, cb in enumerate(COMBO_ALT):
                if cb[1] in LHS:
                    row_desc(worksheet, x, 0)

                    for col, dim in enumerate([5, 6, 7, 8]):
                        worksheet.write(x, y, display_type_tuple(cb, diff, dim), text_format)

                        for key_id, key in enumerate(keys):
                            filters = {'type': '-'.join(cb), 'difficulty': diff, 'dimension': dim}
                            stat = get(df, filters, key)
                            worksheet.write(x+1+key_id, y, stat, number_format)
                        y += 1
                    y = 1
                    x += y_offset
            
            x, y = 1, 6

            for row, cb in enumerate(COMBO_ALT):
                if cb[1] in RHS:
                    for col, dim in enumerate([5, 6, 7, 8]):
                        worksheet.write(x, y, display_type_tuple(cb, diff, dim), text_format)

                        for key_id, key in enumerate(keys):
                            filters = {'type': '-'.join(cb), 'difficulty': diff, 'dimension': dim}
                            stat = get(df, filters, key)
                            worksheet.write(x+1+key_id, y, stat, number_format)

                        y += 1
                    y = 6
                    x += y_offset
            
            cond_format(worksheet)
    
        elif page.startswith('¿'):
            # if page.endswith('¡'):
            #     diff = 1
            worksheet = create_worksheet(page)
            x, y = 1, 1

            for row, b in enumerate(LHS_BONUS):
                row_desc(worksheet, x, 0)
                for col, dim in enumerate([5, 6, 7, 8]):
                    worksheet.write(x, y, display_type(b, diff, dim), text_format)

                    for key_id, key in enumerate(keys):
                        filters = {'type': b, 'difficulty': diff, 'dimension': dim}
                        stat = get(df, filters, key)
                        worksheet.write(x+1+key_id, y, stat, number_format)
                    y += 1
                y = 1
                x += y_offset
            
            x, y = 1, 6

            for row, b in enumerate([*RHS_BONUS, '#\'']):
                if b == '#\'':
                    row_desc(worksheet, x, 0)
                for col, dim in enumerate([5, 6, 7, 8]):
                    worksheet.write(x, y, display_type(b, diff, dim), text_format)

                    for key_id, key in enumerate(keys):
                        filters = {'type': b, 'difficulty': diff, 'dimension': dim}
                        stat = get(df, filters, key)
                        worksheet.write(x+1+key_id, y, stat, number_format)
                    y += 1
                y = 6
                x += y_offset
            
            cond_format(worksheet)
        
        elif page[0].isdigit():
            worksheet = create_worksheet(page)
            x, y = 1, 1
            dim = int(page[0])

            for row, row_name in enumerate(GALLERY_ROWS):
                row_desc(worksheet, x, 0)

                for col, col_name in enumerate(GALLERY_COLUMNS):
                    if col_name == '#':
                        y += 1

                    if row == 0:
                        cell_name = col_name
                    elif col == 0:
                        cell_name = row_name
                    else:
                        cell_name = '-'.join([row_name, col_name])
                    
                    worksheet.write(x, y, display_type(cell_name, diff, dim), gray_text_format if is_gray_cell(row_name, col_name) else text_format)

                    for key_id, key in enumerate(keys):
                        filters = {'type': cell_name, 'difficulty': diff, 'dimension': dim}
                        stat = get(df, filters, key)
                        worksheet.write(x+1+key_id, y, stat, gray_number_format if is_gray_cell(row_name, col_name) else number_format)
                    y += 1
                x += y_offset
                y = 1
            
            cond_format(worksheet)
    
    workbook.close()

def main():
    # read_file(in1, out1)
    # analyze(out1, out2, keys=['max_clues', 'workload', 'starting_clues', 'number_clues'])
    analyze(out1, out3, keys=['workload'], desc=False)

if __name__ == "__main__":
    main()
