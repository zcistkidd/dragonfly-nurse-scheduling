import csv

import numpy as np
import pandas as pd
from sklearn import preprocessing

# TODO coordinate with Chi to finalise all csv files to use numerized values

df_shift_off = pd.read_csv("./data/SECTION_SHIFT_OFF_REQUESTS.csv")  # soft
df_shift_on = pd.read_csv("data/SECTION_SHIFT_ON_REQUESTS.csv")  # soft
df_cover = pd.read_csv("./data/SECTION_COVER.csv")  # soft
df_days_off = pd.read_csv("./data/SECTION_DAYS_OFF.csv")
df_shift = pd.read_csv("./data/SECTION_SHIFTS.csv")
df_staff = pd.read_csv("./data/SECTION_STAFF.csv")
df_cover = pd.read_csv("./data/SECTION_COVER.csv")  # soft


#   D1 D2 D3 D4 D5 ... D14
# 1  0  1 2  0  2       1
# 2  1  2 1  1  2       0
# 3
# 4
# 5
# 6


def costCalculator(df_nurse_schedule,idx):
    number_idx = len(df_nurse_schedule)
    number_of_days = len(df_nurse_schedule[0])
    # cost matrix
    # nurse_cost = np.arange(number_of_days * number_of_nurses).reshape((number_of_nurses, number_of_days))
    nurse_cost = [[0 for i in range(number_of_days)] for j in range(number_of_nurses)]
    total_cost = shiftOffRequest(df_nurse_schedule, nurse_cost) + \
                 shiftOnRequest(df_nurse_schedule, nurse_cost)
    hard_constraints_validation(df_nurse_schedule, nurse_cost)
    cost = convertNurseCost(nurse_cost)
    return cost




def shiftOffRequest(df_nurse_schedule, nurse_cost,nurse_idx):
    shift_off_cost_total = 0
    shift_off_cost_each_vector = []
    for _, row in df_shift_off.iterrows():
        employee = row['EmployeeID_num']
        if not nurse_idx == employee:
            continue
        day = row['Day']
        shift = row['ShiftID_num']

        # check with nurse schedule to see if there is a day off as requested
        nurse = df_nurse_schedule[employee]  # 1 row, 14 columns
        if nurse[day] == shift:
            shift_off_cost_total = shift_off_cost_total + 1
            nurse_cost[employee][day] = 1
            shift_off_cost_each_vector.append(1)
    # return pd.Series(shift_off_cost_each_vector), shift_off_cost_total
    return shift_off_cost_total


def shiftOnRequest(df_nurse_schedule, nurse_cost, nurse_idx):
    shift_on_cost_total = 0
    shift_on_cost_each_vector = []
    for _, row in df_shift_on.iterrows():
        employee = row['EmployeeID_num']
        day = row['Day']
        shift = row['ShiftID_num']
        if not nurse_idx == employee:
            continue
        # check with nurse schedule to see if there is a shift as requested
        nurse = df_nurse_schedule[employee]  # 1 row, 14 columns
        if nurse[day] != shift:  # nurse['day']?? how to get the specified column
            shift_on_cost_total = shift_on_cost_total + 1
            nurse_cost[employee][day] = 1
            shift_on_cost_each_vector.append(1)
    # return pd.Series(shift_on_cost_each_vector), shift_on_cost_total
    return shift_on_cost_total


def cover(df_nurse_schedule, nurse_cost):
    shift_on_cost_total = 0
    shift_on_cost_each_vector = []
    for _, row in df_shift_on.iterrows():
        employee = row['EmployeeID_num']
        day = row['Day']
        shift = row['ShiftID_num']

        # check with nurse schedule to see if there is a shift as requested
        nurse = df_nurse_schedule[employee]  # 1 row, 14 columns
        if nurse[day] != shift:  # nurse['day']?? how to get the specified column
            shift_on_cost_total = shift_on_cost_total + 1
            nurse_cost[employee][day] = 1
            shift_on_cost_each_vector.append(1)
    # return pd.Series(shift_on_cost_each_vector), shift_on_cost_total
    return shift_on_cost_total


def convertNurseCost(nurse_cost):
    cost = []

    for i in range(len(nurse_cost)):
        temp = 0
        for j in range(len(nurse_cost[0])):
            temp = temp + nurse_cost[i][j]
        cost.append(temp)

    return cost


def hard_constraints_validation(nurse_schedule, nurse_cost):
    # nurse_schedule: matrix
    # if days_off_validation(nurse_schedule) and staff_validation(nurse_schedule) and cover_validation(nurse_schedule):
    days_off_validation(nurse_schedule, nurse_cost)
    staff_validation(nurse_schedule, nurse_cost)
    # cover_hard(nurse_schedule, nurse_cost)


# Check if the approved day-off is scheduled with shift for each nurse
def days_off_validation(nurse_schedule, nurse_cost):
    for _, row in df_days_off.iterrows():
        employee = row['EmployeeID_num']
        day_off = row['DayIndexes(startatzero)']

        # check with nurse schedule
        nurse = nurse_schedule[employee]  # 1 row, 14 columns
        if nurse[day_off] != 3:
            nurse_cost[employee][day_off] += 99999999


def cover_hard(nurse_schedule, nurse_cost):
    for dayIndex in range(len(nurse_schedule[0])): # 0 -13
        day_schedule = nurse_schedule[:, [dayIndex]]
        day = 0
        evening = 0
        late = 0
        for i in day_schedule:
            if day_schedule[i][0] == 0:
                day += 1
            if day_schedule[i][0] == 1:
                evening += 1
            if day_schedule[i][0] == 2:
                late += 1
        if day == 0 or evening == 0 or late == 0:
            for j in range(len(nurse_cost)):
                if day_schedule[j] == 3:
                    nurse_cost[j][dayIndex] += 99999999


# Check min/max minutes, weekends, shifts, consecutive days off and working days
def staff_validation(nurse_schedule, nurse_cost):
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
        for i in range(0, number_of_days - 1):  # i: 0 - 12
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
                            nurse_cost[j][i] += 99999999
                        if nurse[current + 1] != 3:
                            nurse_cost[j][i] += 99999999
                        # if counter < 2:
                        #     return False

            # Check L cannot be followed by anything other than O,
            # Check D not followed by E
            if (prev == 2 and current != 3) or (prev == 0 and current == 1):
                nurse_cost[j][i] += 99999999

            # Check Max consecutive shifts >= 2 && <= 5
            if prev == 3 and current != 3:
                counter = count_consecutive_working_days(nurse, i + 1)
                if counter < min_consecutive_shifts \
                        or counter > max_consecutive_shifts:
                    nurse_cost[j][i] += 99999999

        # Check working minutes
        total_working_time = 0
        for i in range(0, number_of_days):
            if nurse[i] != 3:
                total_working_time += 720

        if total_working_time < min_total_minutes:
            nurse_cost[j][i] += 99999999
        if total_working_time > max_total_minutes:
            nurse_cost[j][i] += 99999999

        # Check max number of shifts
        count_day = 0
        count_evening = 0
        count_late = 0
        # D-0 E-1 L-2 O-3
        for i in range(0, number_of_days):
            if nurse[i] == 0:
                count_day += 1
                if count_day > max_day_shift:
                    nurse_cost[j][i] += 99999999
            if nurse[i] == 1:
                count_evening += 1
                if count_evening > max_evening_shift:
                    nurse_cost[j][i] += 99999999
            if nurse[i] == 2:
                count_late += 1
                if count_late > max_late_shift:
                    nurse_cost[j][i] += 99999999

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
                if nurse[current_Satuarday_index] != 3:
                    nurse_cost[j][current_Satuarday_index] += 99999999
                if nurse[current_Sunday_index] != 3:
                    nurse_cost[j][current_Sunday_index] += 99999999
            current_Satuarday_index += 7
            current_Sunday_index += 7


# calculate consecutive working days
def count_consecutive_working_days(array, start):
    index = start  # current day index
    counter = 0
    while array[index] != 3:
        if index == 13:
            break
        counter += 1
        index += 1

    return counter


def main():
    # nurse schedule
    res = np.array([[3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
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
    cost = costCalculator(res)
    print(cost)


if __name__ == "__main__":
    main()
