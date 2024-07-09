# 14 Minesweeper Variants 2
# Save Progress Tracker
# By: Mojimoon

import os
import json
import re

# C:\Users\USERNAME\AppData\Roaming\Godot\app_userdata\Minesweeper Variants 2\{0,1,2,3}\minevar_v2.save

save_path = os.path.join(os.getenv('APPDATA'), 'Godot', 'app_userdata', 'Minesweeper Variants 2')

V = ("V", )
TAG = ("2#", )
LHS = ("2H", "2C", "2S", "2G", "2F", "2B", "2T")
RHS_CLUE = ("2X", "2D", "2P", "2M", "2A")
RHS_SUB = ("2E", "2L")
RHS = RHS_CLUE + RHS_SUB
MAIN = V + LHS + RHS
LHS_BONUS = ("2Z", "2G'")
RHS_BONUS = ("2X'", "2I")
BONUS = LHS_BONUS + RHS_BONUS
LHS_FULL = LHS + LHS_BONUS
RHS_FULL = RHS + RHS_BONUS
ATTACHMENT_BONUS = ("2E'", "2E^", "2L'")
EXCL_ATTACHMENTS = (
    ("2E", "2P"), ("2E", "2M"), ("2L", "2A")
)

CATEGORY = {
    "F": (0, 0),
    "!": (1, 0),
    "!!": (2, 0),
    "+'": (0, 1),
    "+'!": (1, 1),
    "&'": (0, 2),
    "&'!": (1, 2),
    "?": (0, 3),
    "?!": (1, 3),
    5: (0, 4),
    "5!": (1, 4),
    6: (0, 5),
    "6!": (1, 5),
    7: (0, 6),
    "7!": (1, 6),
    8: (0, 7),
    "8!": (1, 7)
}

COUNTER = (
    (53492, 3200, 6253, 1600, 18994, 19000, 17741, 18950),
    (49422, 2923, 6219, 1454, 16559, 17348, 17878, 18090),
    (3634, 0, 0, 0, 0, 0, 0, 0),
)

TOTAL = 159709

def get_bangs(problem):
    for i in range(0, len(problem)):
        if problem[i] == '!':
            if i < len(problem) - 1 and problem[i+1] == '!':
                return 2
            return 1
    return 0

def get_size(problem):
    # get "5x?", "6x?", "7x?", "8x?" but discard the second number
    return int(re.search(r'[5-8]x\d', problem).group()[0])

def get_brackets(problem):
    # return re.findall(r'\[(\w+)\]', problem)
    ret = re.findall(r'\[(.*?)\]', problem)
    if ret[-1] == '@c':
        return ret[:-1]
    return ret

def is_combination(brackets):
    # LHS_FULL + RHS_FULL
    return len(brackets) == 2 and brackets[0] in LHS_FULL and brackets[1] in RHS_FULL

def is_main_combination(brackets):
    # LHS + RHS
    return len(brackets) == 2 and brackets[0] in LHS and brackets[1] in RHS

def is_attachment(brackets):
    # RHS_SUB + RHS_CLUE
    return len(brackets) == 2 and brackets[0] in RHS_SUB and brackets[1] in RHS_CLUE

def is_main_attchement(brackets):
    # RHS_SUB + RHS_CLUE, not in EXCL_ATTACHMENTS
    return is_attachment(brackets) and (brackets[0], brackets[1]) not in EXCL_ATTACHMENTS

def is_attachment_combination(brackets):
    # LHS_FULL + attachment
    return len(brackets) == 3 and brackets[0] in LHS_FULL and is_attachment(brackets[1:])

def is_main_attachment_combination(brackets):
    # LHS + main attachment
    return len(brackets) == 3 and brackets[0] in LHS and is_main_attchement(brackets[1:])

def is_tag(brackets):
    # RHS_SUB + TAG
    return len(brackets) == 2 and brackets[1] == TAG[0]

def is_combination_tag(brackets):
    # LHS_FULL + tag
    return len(brackets) == 3 and brackets[0] in LHS_FULL and is_tag(brackets[1:])

def is_main_combination_tag(brackets):
    # LHS + tag
    return len(brackets) == 3 and brackets[0] in LHS and is_tag(brackets[1:])

def is_main_variants(brackets):
    return len(brackets) == 1 and brackets[0] in MAIN

def is_bonus_variants(brackets):
    return len(brackets) == 1 and brackets[0] in BONUS

def is_attachment_alt(brackets):
    return (len(brackets) == 1 and brackets[0] in ATTACHMENT_BONUS) \
        or (len(brackets) == 2 and brackets[0] == '2E' and brackets[1] == '2L')

def is_combination_alt(brackets):
    # LHS + LHS
    return len(brackets) == 2 and ((brackets[0] in LHS and brackets[1] in LHS) \
        or (brackets[0] == '2G' and brackets[1] == 'R+'))

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

                '''
                {"Puzzles":{"[2H]5x5-10-725":5,"[2H]5x5-10-322":2,"[2H]5x5-10-550":5, ...}}
                '''

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
                        # F and gallery
                        update(progress, 'F', bangs, ult)
                        update(progress, size, bangs, ult)
                    
                    if is_bonus_variants(brackets):
                        # ? and gallery
                        update(progress, '?', bangs, ult)
                        update(progress, size, bangs, ult)
                    
                    if is_combination(brackets):
                        # main: F and gallery
                        # side: gallery
                        update(progress, size, bangs, ult)
                        if is_main_combination(brackets):
                            update(progress, 'F', bangs, ult)
                    
                    if is_attachment(brackets):
                        # main: F, &' and gallery
                        # side: &'
                        update(progress, '&\'', bangs, ult)
                        if is_main_attchement(brackets):
                            update(progress, 'F', bangs, ult)
                            update(progress, size, bangs, ult)

                    if is_attachment_combination(brackets):
                        # main: F, gallery
                        # side: gallery
                        update(progress, size, bangs, ult)
                        if is_main_attachment_combination(brackets):
                            update(progress, 'F', bangs, ult)
                    
                    if is_tag(brackets):
                        # F, &', gallery
                        update(progress, size, bangs, ult)
                        update(progress, 'F', bangs, ult)
                        update(progress, '&\'', bangs, ult)
                    
                    if is_combination_tag(brackets):
                        # main: F, gallery
                        # side: gallery
                        update(progress, size, bangs, ult)
                        if is_main_combination_tag(brackets):
                            update(progress, 'F', bangs, ult)
                    
                    if is_combination_alt(brackets):
                        # +'
                        update(progress, '+\'', bangs, ult)
                    
                    if is_attachment_alt(brackets):
                        # &'
                        update(progress, '&\'', bangs, ult)
            
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
