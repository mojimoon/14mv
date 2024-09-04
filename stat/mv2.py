import csv
import re
import pandas as pd
import numpy as np
import os

in_file = "D:\\game\\steamapps\\common\\14 Minesweeper Variants 2\\MineVar\\puzzle\\all_puzzles_dedup.txt"

out_file = "stats.csv"

'''
statistics of 
- maximum number of clues used for a single step,
- total number of clues used,
- starting clues,
- starting clues on sub board,
- final clues
per level type
'''

def write_to_csv(outputfile, data):
    file_exists = os.path.isfile(outputfile)
    with open(outputfile, 'a', newline='') as csvfile:
        fieldnames = ['level', 'type', 'dimension', 'difficulty', 'max_clues', 'total_clues', 'starting_clues', 'starting_clues_sub', 'final_clues']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

def get_type(level_type):
    # all capital letters
    return ''.join([c for c in level_type if c.isupper()])

def get_difficulty(level_type):
    # number of !
    return level_type.count('!')

def read_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()[1:]
        '''
        [2A]!!5x5-10-(V;5x1,2x1,1x5)-6457	q 2a2 f f q 2a2 2A0 2a2 2a8 f f 2a2 2a0 q f f q q f f q q 2A6 f f
        [2B][2E][2#][@c]!5x10-10-(4x1,3x3,2x7,1x16;L4R1)-1781	f 2e4 q 2m0 f f q q q q 2EA1 f f f 2EA1 q q q f q 2ea3 Q 2ed4 2p1 2EA0 q q f q q f q f f q q q q q f q f 2M0 2ex23 f q f q q q
        [2T][2P]!5x5-12-(1x6,-4x1;L4R0)-1672	2P1 f f 2p2 q f f Q q f f q q f f 2P1 Q f Q 2P1 f f q q f
        '''

        for line in lines:
            parts = line.split('\t')

            level_id = parts[0]
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
            total_clues = sum([clue[0] * clue[1] for clue in clue_pairs])

            grids = parts[1].strip().split(' ')
            # the grids is row x col, the main board is row x row
            # i.e. grids[0:row], [col:col+row], [2*col:2*col+row], ..

            if col > row:
                main_board = [grids[i*col:i*col+row] for i in range(row)]
                mb = [grid for row in main_board for grid in row]
                sub_board = [grids[i*col+row:(i+1)*col] for i in range(row)]
                sb = [grid for row in sub_board for grid in row]
            else:
                mb = grids

            # a grid containing capital letter is a starting clue
            starting_clues = [grid for grid in mb if any([c.isupper() for c in grid])]
            # a grid containing number is a final clue (flags and questions are not counted)
            final_clues = [grid for grid in mb if grid.isdigit()]

            if col > row:
                starting_sub_clues = [grid for grid in sb if grid.isupper()]
            
            write_to_csv(out_file, {
                'level': level_id,
                'type': get_type(level_type),
                'dimension': row,
                'difficulty': get_difficulty(level_type),
                'max_clues': max_clues,
                'total_clues': total_clues,
                'starting_clues': len(starting_clues),
                'starting_clues_sub': len(starting_sub_clues) if col > row else 0,
                'final_clues': len(final_clues)
            })

read_file(in_file)
