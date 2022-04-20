import csv

import pandas as pd
# from numpy import array
import numpy as np
from sklearn import preprocessing

df_days_off = pd.read_csv("./data/SECTION_DAYS_OFF.csv")
df_shift = pd.read_csv("./data/SECTION_SHIFTS.csv")
df_staff = pd.read_csv("./data/SECTION_STAFF.csv")
df_cover = pd.read_csv("./data/SECTION_COVER.csv")  # soft



def hard_constraints_validation(nurse_schedule):
    # nurse_schedule: matrix
    # if days_off_validation(nurse_schedule) and staff_validation(nurse_schedule) and cover_validation(nurse_schedule):
    if days_off_validation(nurse_schedule) and staff_validation(nurse_schedule):
        return True
    else:
        return False

# Check if the approved day-off is scheduled with shift for each nurse
def days_off_validation(nurse_schedule):
    for _, row in df_days_off.iterrows():
        employee = row['EmployeeID_num']
        day_off = row['DayIndexes(startatzero)']

        # check with nurse schedule
        nurse = nurse_schedule[employee]  # 1 row, 14 columns
        if nurse[day_off] != 3:
            return False
    return True

# Check min/max minutes, weekends, shifts, consecutive days off and working days
def staff_validation(nurse_schedule):
    number_of_days = len(nurse_schedule[0])  # number of days

    for j in range(0, len(nurse_schedule)):
        nurse = nurse_schedule[j]
        max_total_minutes = df_staff.at[j, 'MaxTotalMinutes']
        # max_total_minutes = df_staff[j]['MaxTotalMinutes']
        min_total_minutes = df_staff.at[j, 'MinTotalMinutes']
        max_consecutive_shifts = df_staff.at[j, 'MaxConsecutiveShifts']
        min_consecutive_shifts = df_staff.at[j, 'MinConsecutiveShifts']
        min_consecutive_days_off = df_staff.at[j, 'MinConsecutiveDaysOff']
        max_weekends = df_staff.at[j, 'MaxWeekends']
        max_evening_shift = df_staff.at[j, 'MaxShifts_1']
        max_day_shift = df_staff.at[j, 'MaxShifts_0']
        max_late_shift = df_staff.at[j, 'MaxShifts_2']
        for i in range(0, number_of_days - 1):
            # round to int?
            # nurse[i + 1] = round(nurse[i + 1])
            prev = nurse[i]
            current = nurse[i + 1]

            # D-0 E-1 L-2 O-3
            # Check if min consecutive day off <= 2
            if min_consecutive_days_off == 2:
                if current == 3:
                    if prev != 3:
                        # counter = count_consec(array, i + 1, 4)
                        if current == number_of_days - 1:
                            return False
                        if nurse[current + 1] != 3:
                            return False
                        # if counter < 2:
                        #     return False

            # Check L cannot be followed by anything other than O,
            # Check D not followed by E
            if (prev == 2 and current != 3) or (prev == 0 and current == 1):
                return False

            # Check Max consecutive shifts >= 2 && <= 5
            if prev == 3 and current != 3:
                counter = count_consecutive_working_days(nurse, i + 1)
                if counter < min_consecutive_shifts \
                        or counter > max_consecutive_shifts:
                    return False

        # Check working minutes
        total_working_time = 0
        for i in range(0, number_of_days):
            if nurse[i] != 3:
                total_working_time += 720

        if total_working_time < min_total_minutes:
            return False
        if total_working_time > max_total_minutes:
            return False

        # Check max number of shifts
        count_day = 0
        count_evening = 0
        count_late = 0
        # D-0 E-1 L-2 O-3
        for i in range(0, number_of_days):
            if nurse[i] == 0:
                count_day += 1
                if count_day > max_day_shift:
                    return False
            if nurse[i] == 1:
                count_evening += 1
                if count_evening > max_evening_shift:
                    return False
            if nurse[i] == 2:
                count_late += 1
                if count_late > max_late_shift:
                    return False

        # Check max weekends
        # index 5&6, 12&13,19&21, at least we have 7 days in matrix
        current_Satuarday_index = 5
        current_Sunday_index = 6
        count_weekend = 0
        while current_Sunday_index <= number_of_days - 1:
            if nurse[current_Satuarday_index] != 3 \
                    or nurse[current_Sunday_index] != 3:
                count_weekend += 1
            if count_weekend > max_weekends:
                return False
            current_Satuarday_index += 7
            current_Sunday_index += 7
    return True


# calculate consecutive working days
def count_consecutive_working_days(array, start):
    index = start  # current day index
    counter = 0
    while array[index] != 3:
        counter += 1
        index += 1
    return counter


# def cover_validation(nurse_schedule):
#     for _, row in df_cover.iterrows():
#         day = row['Day']  # get day and shiftID from constraint
#         shift = row['ShiftID_num']
#         schedule = nurse_schedule[:, [day]]  # select specified day column, 1 columns, number of nurses = rows
#         count = 0
#         for i in range(len(schedule)):
#             if schedule[i][0] == shift:
#                 count = count + 1
#
#         if count <= row['Requirement']:  # not enough nurse
#             return False
#     return True


def main():
    nurse_schedule = np.array([[3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
                               [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
                               [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
                               [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
                               [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
                               [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
                               [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
                               [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
                               [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
                               [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
                               [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
                               [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
                               [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
                               [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
                               [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
                               [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
                               [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
                               [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
                               [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
                               [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]])
    if hard_constraints_validation(nurse_schedule) == True:
        print("True")
    else:
        print("False")


if __name__ == "__main__":
    main()
# def cover(df_nurse_schedule):
#     cover_cost_total = 0;
#     cover_cost_each_vector = []
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
#         if count > row['Requirement']: # more nurse than we needed
#             cover_cost_total = cover_cost_total + 1
#             cover_cost_each_vector.append(1)
#         if count < row['Requirement']: # not enough nurse
#             cover_cost_total = cover_cost_total + 100
#             cover_cost_each_vector.append(100)
#     return pd.Series(cover_cost_each_vector), cover_cost_total
