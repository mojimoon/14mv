# 14 Minesweeper Variants 2
# Problem Counter
# By: Mojimoon

import os
import json
import re
from mv2_tracker import *

src = "D:/game/steamapps/common/14 Minesweeper Variants 2/MineVar/puzzle/all_puzzles_dedup.txt"

def main():
    with open(src, "r") as f:
        problems = f.readlines()
        problems = problems[1:]

        count = [[[0 for _ in range(8)] for _ in range(3)]]
        total = 0

        for line in problems:
            problem = line.split("\t")[0]
            brackets = get_brackets(problem)
            bangs = get_bangs(problem)
            size = get_size(problem)
            total += 1

            if is_main_variants(brackets):
                update(count, 'F', bangs)
                update(count, size, bangs)
            
            if is_bonus_variants(brackets):
                update(count, '?', bangs)
                update(count, size, bangs)
            
            if is_combination(brackets):
                update(count, size, bangs)
                if is_main_combination(brackets):
                    update(count, 'F', bangs)
            
            if is_attachment(brackets):
                update(count, '&\'', bangs)
                if is_main_attchement(brackets):
                    update(count, 'F', bangs)
                    update(count, size, bangs)
            
            if is_attachment_combination(brackets):
                update(count, size, bangs)
                if is_main_attachment_combination(brackets):
                    update(count, 'F', bangs)
            
            if is_tag(brackets):
                update(count, size, bangs)
                if is_main_combination_tag(brackets):
                    update(count, 'F', bangs)
            
            if is_combination_tag(brackets):
                update(count, size, bangs)
                if is_main_combination_tag(brackets):
                    update(count, 'F', bangs)
            
            if is_combination_alt(brackets):
                update(count, '+\'', bangs)
            
            if is_attachment_alt(brackets):
                update(count, '&\'', bangs)
        
        print_progress(count, [total, 0])

if __name__ == "__main__":
    main()
