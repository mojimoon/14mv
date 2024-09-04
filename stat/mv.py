import csv
import re
import pandas as pd
import numpy as np
import os
import xlsxwriter

in1 = "D:\\game\\steamapps\\common\\14 Minesweeper Variants\\MineVar\\puzzle\\all_puzzles_dedup.txt"

out1 = "stats.csv"

out2 = "stats_mean.xlsx"

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