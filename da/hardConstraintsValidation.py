import csv

import pandas as pd
from sklearn import preprocessing

df_days_off = pd.read_csv("data/SECTION_DAYS_OFF.csv")
df_shift = pd.read_csv("data/SECTION_SHIFTS.csv")
df_staff = pd.read_csv("data/SECTION_STAFF.csv")
df_nurse_schedule = pd.read_csv("data/nurse_schedule.csv");


#   D1 D2 D3 D4 D5 ... D14
# 1  0  1 2  0  2       1
# 2  1  2 1  1  2       0
# 3
# 4
# 5
# 6


def days_off_validation():
    days_off__reader = csv.DictReader(df_days_off)
    for row in days_off__reader:
        employee = row['EmployeeID_num']
        day_off = row['DayIndexes(startatzero)']

        # check with nurse schedule
        nurse = df_nurse_schedule[employee]  # 1 row, 14 columns
        if nurse[day_off] != -1:
            return 0
    return 1

def


def staff_validation():
    return 1


def shift_validation():
    return 0
