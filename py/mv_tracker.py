# 14 Minesweeper Variants
# Save Progress Tracker
# By: Mojimoon

import os
import json
import re

# C:\Users\USERNAME\AppData\Roaming\Godot\app_userdata\Minesweeper Variants\{0,1,2,3}\minevar.save

save_path = os.path.join(os.getenv('APPDATA'), 'Godot', 'app_userdata', 'Minesweeper Variants')

V = ("V", )
TAG = ("#", "#'")
LHS = ("Q", "C", "T", "O", "D", "S", "B")
RHS = ("M", "L", "W", "N", "X", "P", "E")
MAIN = V + LHS + RHS
LHS_BONUS = ("T'", "D'", "A", "H")
RHS_BONUS = ("X'", "K", "W'", "E'")
BONUS = LHS_BONUS + RHS_BONUS
LHS_FULL = LHS + LHS_BONUS
RHS_FULL = RHS + RHS_BONUS

CATEGORY = {
    "F": (0, 0),
    "!": (1, 0),
    "!!": (2, 0),
    "+'": (0, 1),
    "+'!": (1, 1),
    "?": (0, 2),
    "?!": (1, 2),
    5: (0, 3),
    "5!": (1, 3),
    6: (0, 4),
    "6!": (1, 4),
    7: (0, 5),
    "7!": (1, 5),
    8: (0, 6),
    "8!": (1, 6)
}

COUNTER = (
    (53892, 3200, 5453, 1600, 19294, 19300, 18063, 19250),
    (49654, 2923, 5419, 1454, 16843, 17581, 18132, 18351),
    (3634, 0, 0, 0, 0, 0, 0, 0)
)

TOTAL = 159731

def get_bangs(problem):
    for i in range(0, len(problem)):
        if problem[i] == '!':
            if i < len(problem) - 1 and problem[i+1] == '!':
                return 2
            return 1
    return 0

def get_size(problem):
    return int(re.search(r'[5-8]x\d', problem).group()[0])

def get_brackets(problem):
    ret = re.findall(r'\[(.*?)\]', problem)
    if ret[-1] == '@c':
        return ret[:-1]
    return ret

def is_combination(brackets):
    return len(brackets) == 2 and brackets[0] in LHS_FULL and brackets[1] in RHS_FULL

def is_main_combination(brackets):
    return len(brackets) == 2 and brackets[0] in LHS and brackets[1] in RHS

def is_tag(brackets):
    return len(brackets) == 1 and brackets[0] in TAG

def is_main_tag(brackets):
    return len(brackets) == 1 and brackets[0] == TAG[0]

def is_combination_tag(brackets):
    return len(brackets) == 2 and brackets[0] in LHS_FULL and brackets[1] in TAG

def is_main_combination_tag(brackets):
    return len(brackets) == 2 and brackets[0] in LHS and brackets[1] == TAG[0]

def is_main_variants(brackets):
    return len(brackets) == 1 and brackets[0] in MAIN

def is_bonus_variants(brackets):
    return len(brackets) == 1 and brackets[0] in BONUS

def is_combination_alt(brackets):
    return len(brackets) == 2 and (
        (brackets[0] in LHS and brackets[1] in LHS) or
        (brackets[0] in RHS and brackets[1] in RHS) or
        (brackets[0] == 'U' and brackets[1] == 'W')
    )

def update(progress, category, bangs, ult=False):
    progress[0][bangs][CATEGORY[category][1]] += 1
    if ult:
        progress[1][bangs][CATEGORY[category][1]] += 1

def main():
    has_save = False
    for i in range(0, 4):
        if os.path.exists(os.path.join(save_path, f'{i}', 'minevar_v2.save')):
            has_save = True
            progress = [[[0 for _ in range(8)] for _ in range(3)] for _ in range(2)]
            total = 0
            total_ult = 0

            print(f'Save {i+1}')
            with open(os.path.join(save_path, f'{i}', 'minevar_v2.save'), 'r') as f:
                data = json.load(f)
            
                for problem, count in data['Puzzles'].items():
                    if count % 8 != 5:
                        continue
                    brackets = get_brackets(problem)
                    bangs = get_bangs(problem)
                    size = get_size(problem)
                    ult = (count > 64)
                    total += 1
                    if ult:
                        total_ult += 1
                    
                    if is_main_variants(brackets):
                        update(progress, 'F', bangs, ult)
                        update(progress, size, bangs, ult)
                    
                    if is_bonus_variants(brackets):
                        update(progress, '?', bangs, ult)
                        update(progress, size, bangs, ult)
                    
                    if is_combination(brackets):
                        update(progress, size, bangs, ult)
                        if is_main_combination(brackets):
                            update(progress, 'F', bangs, ult)
                        
                    if is_tag(brackets):
                        update(progress, size, bangs, ult)
                        if is_main_tag(brackets):
                            update(progress, 'F', bangs, ult)
                    
                    if is_combination_tag(brackets):
                        update(progress, size, bangs, ult)
                        if is_main_combination_tag(brackets):
                            update(progress, 'F', bangs, ult)
                    
                    if is_combination_alt(brackets):
                        update(progress, '+\'', bangs, ult)
            
            print_progress(progress, [total, total_ult])

    if not has_save:
        print('Data save not found.')
        print(f'Check {save_path} for save files.')

def print_progress(progress, total):
    lens = [
        len(str(total[0])),
        min(len(str(TOTAL)), 1 + len(str(total[1]))),
        len(str(TOTAL))
    ]
    fmt = '{0:<4}{1:>%d} /{2:>%d} ({3:.2%%})' % (lens[0], lens[2])

    if total[1] > 0:
        fmt = '{0:<4}{1:>%d} +{2:>%d} /{3:>%d} ({4:.2%%})' % (lens[0], lens[1], lens[2])
        for k, v in CATEGORY.items():
            print(fmt.format(k, progress[0][v[0]][v[1]], progress[1][v[0]][v[1]], COUNTER[v[0]][v[1]], progress[0][v[0]][v[1]]/COUNTER[v[0]][v[1]]))
        print(fmt.format('==', total[0], total[1], TOTAL, total[0]/TOTAL))
    else:
        for k, v in CATEGORY.items():
            print(fmt.format(k, progress[0][v[0]][v[1]], COUNTER[v[0]][v[1]], progress[0][v[0]][v[1]]/COUNTER[v[0]][v[1]]))
        print(fmt.format('==', total[0], TOTAL, total[0]/TOTAL))

if __name__ == '__main__':
    main()
