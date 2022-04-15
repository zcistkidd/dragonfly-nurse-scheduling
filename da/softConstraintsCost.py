import csv

import pandas as pd
from sklearn import preprocessing
#TODO coordinate with Chi to finalise all csv files to use numerized values
df_cover = pd.read_csv("data/SECTION_COVER.csv")# soft
df_shift_off = pd.read_csv("data/SECTION_SHIFT_OFF_REQUESTS.csv")# soft
df_shift_on = pd.read_csv("data/SECTION_SHIFT_ON_REQUESTS.csv")# soft
# df_nurse_schedule = pd.read_csv("data/nurse_schedule.csv");

  #   D1 D2 D3 D4 D5 ... D14
  # 1  0  1 2  0  2       1
  # 2  1  2 1  1  2       0
  # 3
  # 4
  # 5
  # 6


def costCalculator(df_nurse_schedule):
    cost = cover() + shiftOffRequest() + shiftOnRequest();
    return cost;

def cover(df_nurse_schedule):
    cover_cost_total = 0;
    cover_cost_each_vector = []
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
            cover_cost_total = cover_cost_total + 1
            cover_cost_each_vector.append(1)
        if count < row['Requirement']: # not enough nurse
            cover_cost_total = cover_cost_total + 100
            cover_cost_each_vector.append(100)
    #TODO return a pandas series to represnet each nurse's cost
    return pd.Series(cover_cost_each_vector), cover_cost_total


def shiftOffRequest(df_nurse_schedule):
    shift_off_cost_total = 0
    shift_off_cost_each_vector= []
    shift_off_reader = csv.DictReader(df_shift_off)
    for row in shift_off_reader:
        employee = row['EmployeeID_num']
        day = row['Day']
        shift = row['ShiftID_num']

        # check with nurse schedule to see if there is a day off as requested
        nurse = df_nurse_schedule[employee] # 1 row, 14 columns
        if nurse[day] == shift:
            shift_off_cost_total= shift_off_cost_total + 1
            shift_off_cost_each_vector.append(1)
    return pd.Series(shift_off_cost_each_vector), shift_off_cost_total


def shiftOnRequest(df_nurse_schedule):
    shift_on_cost_total = 0;
    shift_on_cost_each_vector = []
    shift_on_reader = csv.DictReader(df_shift_on)
    for row in shift_on_reader:
        employee = row['EmployeeID_num']
        day = row['Day']
        shift = row['ShiftID_num']

        # check with nurse schedule to see if there is a shift as requested
        nurse = df_nurse_schedule[employee]  # 1 row, 14 columns
        if nurse[day] != shift: # nurse['day']?? how to get the specified column
            shift_on_cost_total = shift_on_cost_total + 1
            shift_on_cost_each_vector.append(1)

    return pd.Series(shift_on_cost_each_vector), shift_on_cost_total


def main():
    

if __name__ == "__main__":
    main()
