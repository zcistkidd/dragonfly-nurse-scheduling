import csv

import pandas as pd
from numpy import array
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


# Check if the approved day-off is scheduled with shift for each nurse
def days_off_validation():
    days_off__reader = csv.DictReader(df_days_off)
    for row in days_off__reader:
        employee = row['EmployeeID_num']
        day_off = row['DayIndexes(startatzero)']

        # check with nurse schedule
        nurse = df_nurse_schedule[employee]  # 1 row, 14 columns
        if nurse[day_off] != 3:
            return False
    return True


# Check
def staff_validation:
    off_in_2_weeks = 0
    if array[0] == 3:
        off_in_2_weeks += 1

    for i in range(0, n - 1):
        # round to int?
        array[i + 1] = round(array[i + 1])
        prev = array[i]
        current = array[i + 1]

        # Circular? E-1 D-2 L-3 O-4?
        if current < 1:
            current = 4 - abs(current) % 4
        elif current > 4:
            current = current % 4

        if current == 4:
            off_in_2_weeks += 1
            if (i + 1) % 7 == 0:
                # min/max of shifts per week required??
                if off_in_2_weeks < 7 or off_in_2_weeks > 7:
                    return False

                off_in_2_weeks = 0

            # Min consecutive day off 2??
            if prev != 4:
                counter = count_consec(array, i + 1, 4)
                if counter < 2 or counter > 5:
                    return False
        else:
            # L cannot be followed by anything other than O, D not followed by E
            if (prev == 3 and current != 4) or (prev == 2 and current == 1):
                return False

            # Max consecutive shifts 5, min 2
            if prev == 4 and current != 4:
                counter = count_consec(array, i + 1, 1)
                if counter < 2 or counter > 5:
                    return False

def count_consec(array, start, sign):
    index = start
    counter = 0
    if sign == 4:
        while array[index] == 4:
            counter += 1
            index += 1
    else:
        while array[index] != 4:
            counter += 1
            index += 1

    return counter

def shift_validation():
    return True


# def cover(df_nurse_schedule):
#     cover_cost_total = 0;
#     cover_cost_each_vector = []
#
#     for _, row in df_cover.iterrows():
#         day = row['Day']  # get day and shiftID from constraint
#         shift = row['ShiftID_num']
#         # schedule_reader = csv.DictReader(df_nurse_schedule) # check with nurse schedule matrix
#         schedule = df_nurse_schedule[:, [day]] # select specified day column, 1 columns, number of nurses = rows
#         [rows, cols] = schedule.shape
#         count = 0
#
#         for i in range(rows):
#             for j in range(cols):
#                 if schedule[i,j] == shift:
#                     count = count + 1
#
#         if count > row['Requirement']: # more nurse than we needed
#             cover_cost_total = cover_cost_total + 1
#             cover_cost_each_vector.append(1)
#         if count < row['Requirement']: # not enough nurse
#             cover_cost_total = cover_cost_total + 100
#             cover_cost_each_vector.append(100)
#     return pd.Series(cover_cost_each_vector), cover_cost_total
