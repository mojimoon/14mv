import csv
import re
import pandas as pd
import numpy as np
import os
import xlsxwriter

in1 = "D:\\game\\steamapps\\common\\14 Minesweeper Variants 2\\MineVar\\puzzle\\all_puzzles_dedup.txt"
out1 = "mv2/mv2_stats_update1.csv"
out2 = "mv2/mv2_stats_mean_update1.xlsx"
out3 = "mv2/mv2_stats_workload_update1.xlsx"
stats1 = "mv/mv_stats.csv"

'''
statistics of 
- maximum number of clues used for a single step,
- total number of clues used,
- starting clues,
- starting clues on sub board,
- final clues
per level type
'''

LHS = ["2H", "2C", "2S", "2G", "2F", "2B", "2T"]
LHS_BONUS = ["2Z", "2G'"]
RHS = ["2X", "2D", "2P", "2E", "2M", "2A", "2L"]
RHS_BONUS = ["2X'", "2I"]
# ATTACH = ["EX", "LD", "LM", "EA", "LX", "ED", "LP"]
ATTACH = [("2E", "2X"), ("2L", "2D"), ("2L", "2M"), ("2E", "2A"), ("2L", "2X"), ("2E", "2D"), ("2L", "2P")]
ATTACH_BONUS = ["2E'", "2E^", "2L'"]
# COMBO_ALT = ["GH", "CH", "CG", "FG", "FH", "CF", "BH", "GR"]
COMBO_ALT = [("2G", "2H"), ("2C", "2H"), ("2C", "2G"), ("2F", "2G"), ("2F", "2H"), ("2C", "2F"), ("2B", "2H"), ("2G", "R+")]
RHS_CLUE = ["2X", "2D", "2P", "2M", "2A"]
RHS_BOARD = ["2E", "2L"]
TAGS = ["2E-2#", "2L-2#"]

# LHS = ["Q", "C", "T", "O", "D", "S", "B"]
# LHS_BONUS = ["D'", "A", "H", "T'"]
# RHS = ["M", "L", "W", "N", "X", "P", "E"]
# RHS_BONUS = ["X'", "K", "W'", "E'"]
LHS_1 = ["1Q", "1C", "1T", "1O", "1D", "1S", "1B"]
RHS_1 = ["1M", "1L", "1W", "1N", "1X", "1P", "1E"]

PAGES = ["F", "!", "+ʹ", "&ʹ", "¿", "5", "6", "7", "8", "!!", "+ʹ!", "&ʹ!", "¿!", "5!", "6!", "7!", "8!", "5+", "6+", "7+", "8+", "5+!", "6+!", "7+!", "8+!"]

ATTACH_ORDER = ['-'.join(a) for a in ATTACH]
MAINPAGE = ["V", *LHS, *RHS]
LHS_FULL = [*LHS, *LHS_BONUS]
RHS_FULL = [*RHS, *RHS_BONUS]
GALLERY_COLUMNS = ["V", *RHS, *RHS_BONUS, *TAGS, *ATTACH_ORDER]
GALLERY_ROWS = ['', *LHS, *LHS_BONUS]
CROSS_GALLERY_COLUMNS = ["1+2", *LHS, "2+1", *LHS_1]
CROSS_GALLERY_ROWS1 = ["", *RHS_1]
CROSS_GALLERY_ROWS2 = ["", *RHS]

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
    '''
    [2B][2X'][@c] -> ("2B", "2X'")
    [V] -> ("V",)
    [2E][2#] -> ("2E", "2#")
    [2G][R+] -> ("2G", "R+")
    '''
    pattern = re.compile(r'\[([\dA-Z^\'#\+]+)\+?\]')
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

def get_category(types):
    if len(types) == 1:
        if types[0] in MAINPAGE:
            return 'F' # main
        if types[0] in LHS_BONUS or types[0] in RHS_BONUS:
            return '?' # bonus
        if types[0] in ATTACH_BONUS:
            return '&\'' # attach bonus
        return '?1'
    if len(types) == 2:
        if types[0] in LHS_FULL and types[1] in RHS_FULL:
            if types[0] in LHS and types[1] in RHS:
                return '+' # combo
            return '+?' # combo (bonus)
        if types[0] in RHS_BOARD and types[1] in RHS_CLUE:
            if types in ATTACH:
                return '&' # attach
            return '&?' # attach (bonus)
        if types[0] in RHS_BOARD and types[1] == '2#':
            return '#' # tag
        if types in COMBO_ALT:
            return '+\'' # combo alt
        if (types[0] in LHS_1 and types[1] in RHS) or (types[0] in LHS and types[1] in RHS_1):
            return 'x' # crossover
        return '&\'' # attach bonus
    if types[0] in LHS:
        if types[2] == '2#':
            return '#+' # tag combo
        elif types[2] in RHS:
            return '&+' # attach combo
    elif types[0] in LHS_BONUS:
        if types[2] == '2#':
            return '#+?' # tag combo (bonus)
        elif types[2] in RHS:
            return '&+?' # attach combo (bonus)
    return '?3'

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

                type_tuples = get_type(level_type)
                
                writer.writerow({
                    'id': ingame_id,
                    'type': '-'.join(type_tuples),
                    'dimension': row,
                    'difficulty': get_difficulty(level_type),
                    'max_clues': max_clues,
                    'workload': workload,
                    'starting_clues': starting_clues,
                    'starting_questions': starting_questions,
                    'number_clues': number_clues,
                    'category': get_category(type_tuples)
                })

def get(df, filters, key):
    for k, v in filters.items():
        df = df[df[k] == v]
    return df[key].mean()

def remove2_at_start(s):
    return s[1:] if s.startswith('2') else s

def display_type(csv_type, diff, dim):
    types = map(remove2_at_start, csv_type.split('-'))
    return ''.join([
        *types,
        '!' * diff,
        str(dim)
    ])

def display_type_tuple(tuple_type, diff, dim):
    types = map(remove2_at_start, tuple_type)
    return ''.join([
        *types,
        '!' * diff,
        str(dim)
    ])

def display_type_full(csv_type, diff, dim):
    # if dim == 0:
    #     return ''.join([
    #         csv_type,
    #         '!' * diff
    #     ])
    return ''.join([
        *csv_type.split('-'),
        '!' * diff,
        str(dim)
    ])

def is_gray_row(row_name):
    return row_name in LHS_BONUS

def is_gray_col(col_name):
    return col_name in RHS_BONUS or col_name in ATTACH_ORDER

def is_gray_cell(row_name, col_name):
    return is_gray_row(row_name) or is_gray_col(col_name)

def analyze(in_file, out_file, keys=KEYS, desc=True):
    df = pd.read_csv(in_file)
    df1 = pd.read_csv(stats1)
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
            # worksheet.write(x+1, y, 'Max Clues', center_format)
            # worksheet.write(x+2, y, 'Workload', center_format)
            # worksheet.write(x+3, y, 'Starting Clues', center_format)
            # worksheet.write(x+4, y, 'Starting ?s', center_format)
            # worksheet.write(x+5, y, 'Number Clues', center_format)
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
        
        if page_id < 2 or page == '!!':
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
                cond_format(worksheet)
                continue
            
            for row, l, r in zip(range(2), ("+", "&+"), ("&", "#")):
                row_desc(worksheet, x, 0)
                y = 1
                for dim in [5, 6, 7, 8]:
                    worksheet.write(x, y, display_type(l, diff, dim), text_format)
                    for key_id, key in enumerate(keys):
                        filters = {'category': l, 'difficulty': diff, 'dimension': dim}
                        stat = get(df, filters, key)
                        worksheet.write(x+1+key_id, y, stat, number_format)
                    y += 1
                y = 6
                for dim in [5, 6, 7, 8]:
                    worksheet.write(x, y, display_type(r, diff, dim), text_format)
                    for key_id, key in enumerate(keys):
                        filters = {'category': r, 'difficulty': diff, 'dimension': dim}
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
            
            cond_format(worksheet)

        elif page.startswith('¿'):
            # if page.endswith('¡'):
            #     diff = 1
            worksheet = create_worksheet(page)
            x, y = 1, 1

            for row, b in enumerate([*LHS_BONUS, *RHS_BONUS]):
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
            
            cond_format(worksheet)
            
        elif page.startswith('&'):
            worksheet = create_worksheet(page)
            x, y = 1, 1

            for row, a in enumerate(RHS_CLUE):
                row_desc(worksheet, x, 0)

                for b in RHS_BOARD:
                    for col, dim in enumerate([5, 6, 7, 8]):
                        worksheet.write(x, y, display_type_tuple((b, a), diff, dim), text_format)

                        for key_id, key in enumerate(keys):
                            filters = {'type': '-'.join((b, a)), 'difficulty': diff, 'dimension': dim}
                            stat = get(df, filters, key)
                            worksheet.write(x+1+key_id, y, stat, number_format)

                        y += 1
                    y += 1 # empty column
                x += y_offset
                y = 1
            
            x += 1 # empty row

            row_desc(worksheet, x, 0)
            y = 1
            for col, dim in enumerate([5, 6, 7, 8]):
                worksheet.write(x, y, display_type("2E'", diff, dim), text_format)

                for key_id, key in enumerate(keys):
                    filters = {'type': "2E'", 'difficulty': diff, 'dimension': dim}
                    stat = get(df, filters, key)
                    worksheet.write(x+1+key_id, y, stat, number_format)

                y += 1
            y = 6
            for col, dim in enumerate([5, 6, 7, 8]):
                worksheet.write(x, y, display_type("2L'", diff, dim), text_format)

                for key_id, key in enumerate(keys):
                    filters = {'type': "2L'", 'difficulty': diff, 'dimension': dim}
                    stat = get(df, filters, key)
                    worksheet.write(x+1+key_id, y, stat, number_format)

                y += 1
            x += y_offset

            row_desc(worksheet, x, 0)
            y = 1
            for col, dim in enumerate([5, 6, 7, 8]):
                worksheet.write(x, y, display_type("2E^", diff, dim), text_format)

                for key_id, key in enumerate(keys):
                    filters = {'type': "2E^", 'difficulty': diff, 'dimension': dim}
                    stat = get(df, filters, key)
                    worksheet.write(x+1+key_id, y, stat, number_format)

                y += 1
            
            x += y_offset
            x += 1 # empty row

            row_desc(worksheet, x, 0)
            y = 1
            for col, dim in enumerate([5, 6, 7, 8]):
                worksheet.write(x, y, display_type_tuple(("2E", "2L"), diff, dim), text_format)

                for key_id, key in enumerate(keys):
                    filters = {'type': "2E-2L", 'difficulty': diff, 'dimension': dim}
                    stat = get(df, filters, key)
                    worksheet.write(x+1+key_id, y, stat, number_format)
                
                y += 1

            cond_format(worksheet)

        elif page[0].isdigit() and (len(page) == 1 or page[1] == '!'):
            worksheet = create_worksheet(page)
            dim = int(page[0])
            x, y = 1, 1

            for row, row_name in enumerate(GALLERY_ROWS):
                row_desc(worksheet, x, 0)

                for col, col_name in enumerate(GALLERY_COLUMNS):
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

                    if col_name == "2I":
                        y += 1
                
                x += y_offset
                y = 1
            
            cond_format(worksheet)
        
        elif page[0].isdigit() and len(page) > 1 and page[1] == '+':
            # if page == '5+':
            worksheet = create_worksheet(page)
            dim = int(page[0])
            x, y = 1, 1
            rows = CROSS_GALLERY_ROWS1
            y_base = 1

            for col, col_name in enumerate(CROSS_GALLERY_COLUMNS):
                row_desc(worksheet, x, 0)

                for row, row_name in enumerate(rows):
                    stat = 2
                    xx = x
                    yy = y
                    if col_name == "1+2":
                        if row == 0:
                            cell_name = ''
                            stat = 0
                        else:
                            cell_name = row_name
                            stat = 1
                    elif col_name == "2+1":
                        if row == 0:
                            cell_name = ''
                            stat = 0
                        else:
                            cell_name = row_name
                    elif '1' in col_name:
                        if row == 0:
                            cell_name = col_name
                            stat = 1
                        else:
                            cell_name = '-'.join([col_name, row_name])
                    else:
                        if row == 0:
                            cell_name = col_name
                        else:
                            cell_name = '-'.join([col_name, row_name])
                    
                    # print(f"x={x}, y={y}, row_name={row_name}, col_name={col_name}, cell_name={cell_name}, no_stat={no_stat}")
                    
                    if cell_name:
                        worksheet.write(x, y, display_type_full(cell_name, diff, dim), text_format if '-' in cell_name else gray_text_format)

                    if stat == 2:
                        for key_id, key in enumerate(keys):
                            filters = {'type': cell_name, 'difficulty': diff, 'dimension': dim}
                            stat = get(df, filters, key)
                            worksheet.write(x+1+key_id, y, stat, number_format if '-' in cell_name else gray_number_format)
                    elif stat == 1:
                        for key_id, key in enumerate(keys):
                            filters = {'type': cell_name[1:], 'difficulty': diff, 'dimension': dim}
                            stat = get(df1, filters, key)
                            worksheet.write(x+1+key_id, y, stat, gray_number_format)
                
                    y += 1
                
                if col_name == "2T":
                    x = 1
                    y_base = y + 1
                    y = y_base
                    rows = CROSS_GALLERY_ROWS2
                else:
                    x += y_offset
                    y = y_base
        
            cond_format(worksheet)
    
    workbook.close()

def main():
    # read_file(in1, out1)
    # analyze(out1, out2)
    analyze(out1, out3, keys=['workload'], desc=False)

if __name__ == "__main__":
    main()