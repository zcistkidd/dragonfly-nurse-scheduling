import csv

import pandas as pd
from sklearn import preprocessing

df_cover = pd.read_csv("data/SECTION_COVER.csv")# soft
df_shift_off = pd.read_csv("data/SECTION_SHIFT_OFF_REQUESTS.csv")# soft
df_shift_on = pd.read_csv("data/SECTION_SHIFT_ON_REQUESTS.csv")# soft
df_nurse_schedule = pd.read_csv("data/nurse_schedule.csv");

  #   D1 D2 D3 D4 D5 ... D14
  # 1  0  1 2  0  2       1
  # 2  1  2 1  1  2       0
  # 3
  # 4
  # 5
  # 6


def costCalculator():
    cost = cover() + shiftOffRequest()  + shiftOnRequest();
    return cost;

def cover():
    cover_cost = 0;
    cover_reader = csv.DictReader(df_cover)
    for row in cover_reader:
        day = row['Day']  # get day and shiftID from constraint
        shift = row['ShiftID_num']
        # schedule_reader = csv.DictReader(df_nurse_schedule) # check with nurse schedule matrix
        schedule = df_nurse_schedule[:, [day]] # select specified day column, 1 columns, number of nurses = rows
        [rows, cols] = schedule.shape
        print(rows, cols)
        count = 0

        for i in range(rows):
            for j in range(cols):
                if schedule[i,j] == shift:
                    count = count + 1

        if count > row['Requirement']: # more nurse than we needed
            cover_cost = cover_cost + count - row['Requirement']
            # cover_cost = cover_cost + 1
        if count < row['Requirement']: # not enough nurse
            cover_cost = cover_cost + (row['Requirement'] - count) * 100
            # cover_cost = cover_cost + 100

    return cover_cost;


def shiftOffRequest():
    shift_off_cost = 0;
    shift_off_reader = csv.DictReader(df_shift_off)
    for row in shift_off_reader:
        employee = row['EmployeeID_num']
        day = row['Day']
        shift = row['ShiftID_num']

        # check with nurse schedule to see if there is a day off as requested
        nurse = df_nurse_schedule[employee] # 1 row, 14 columns
        if nurse[day] == shift:
            shift_off_cost = shift_off_cost + 1

    return shift_off_cost;


def shiftOnRequest():
    shift_on_cost = 0;
    shift_on_reader = csv.DictReader(df_shift_on)
    for row in shift_on_reader:
        employee = row['EmployeeID_num']
        day = row['Day']
        shift = row['ShiftID_num']

        # check with nurse schedule to see if there is a day off as requested
        nurse = df_nurse_schedule[employee]  # 1 row, 14 columns
        if nurse[day] != shift:
            shift_on_cost = shift_on_cost + 1

    return shift_on_cost;
