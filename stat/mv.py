import csv
import re
import pandas as pd
import numpy as np
import os
import xlsxwriter

in1 = "D:\\game\\steamapps\\common\\14 Minesweeper Variants\\MineVar\\puzzle\\all_puzzles_dedup.txt"

out1 = "mv/mv_stats.csv"

out2 = "mv/stats_mean.csv"

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

MAIN = ["V", *LHS, *RHS]
LHS_FULL = [*LHS, *LHS_BONUS]
RHS_FULL = [*RHS, *RHS_BONUS]
GALLERY_COLUMNS = ["V", *RHS, *RHS_BONUS, *TAG]
GALLERY_ROWS = ["", *LHS, *LHS_BONUS]

FIELDS = ['id', 'type', 'dimension', 'difficulty', 'max_clues', 'workload', 'starting_clues', 'starting_questions', 'number_clues', 'category']
KEYS = FIELDS[4:9]

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

def main():
    read_file(in1, out1)

if __name__ == "__main__":
    main()
