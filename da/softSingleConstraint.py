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


#   D1 D2 D3 D4 D5 ... D14
# 1  0  1 2  0  2       1
# 2  1  2 1  1  2       0
# 3
# 4
# 5
# 6


def costCalculator(df_nurse_schedule, idx):
    number_of_days = len(df_nurse_schedule[0])
    number_of_agent = len(df_nurse_schedule)
    # cost matrix
    nurse_cost = [[0 for i in range(number_of_days)] for j in range(number_of_agent)]
    off_cost = shiftOffRequest(df_nurse_schedule, nurse_cost, 0)
    on_cost = shiftOnRequest(df_nurse_schedule, nurse_cost, 0)
    hard_constraints_validation(df_nurse_schedule, nurse_cost)
    cost = convertNurseCost(nurse_cost)
    return cost


def shiftOffRequest(df_nurse_schedule, nurse_idx):
    # df_nurse_schedule 14*20
    shift_off_cost_total = 0
    shift_off_cost_each_vector = np.zeros(len(df_nurse_schedule))
    # Only keep cost associated with current nurse_idx
    cur_off_request = df_shift_off[df_shift_off['EmployeeID_num'] == nurse_idx]

    for _, row in cur_off_request.iterrows():
        day = row['Day']
        shift = row['ShiftID_num']
        weight = row['Weight']
        #Filtered out the n th day col
        cur_day_col = df_nurse_schedule[:,day]
        #Get a bolean vector indicating if thats day's shift is the cost shift
        pos_with_cost = cur_day_col == shift
        #Added weight to the result vector
        shift_off_cost_each_vector += (pos_with_cost * weight)

    return shift_off_cost_each_vector


def shiftOnRequest(df_nurse_schedule, nurse_idx):
    shift_on_cost_each_vector = np.zeros(len(df_nurse_schedule))
    cur_on_request = df_shift_off[df_shift_off['EmployeeID_num'] == nurse_idx]

    for _, row in cur_on_request.iterrows():
        day = row['Day']
        shift = row['ShiftID_num']
        weight = row['Weight']
        #Filtered out the n th day col
        cur_day_col = df_nurse_schedule[:,day]
        #Get a bolean vector indicating if thats day's shift is the cost shift
        pos_with_cost = cur_day_col == shift
        #Added weight to the result vector
        shift_on_cost_each_vector += (pos_with_cost * weight)

    return shift_on_cost_each_vector


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
def days_off_validation(nurse_schedule, nurse_idx):
    days_off_cost_each_vector = np.zeros(len(nurse_schedule))
    cur_off_constraint = df_days_off[df_days_off['EmployeeID_num'] == nurse_idx]
    for _, row in cur_off_constraint.iterrows():
        day = row['DayIndexes(startatzero)']
        cur_day_col = nurse_schedule[:, day]
        pos_with_cost = cur_day_col != 3
        days_off_cost_each_vector += (pos_with_cost * 99999999)
    return days_off_cost_each_vector


def shifts_cost(nurse_schedule):
    m,n = len(nurse_schedule),len(nurse_schedule[0])
    shift_on_cost_each_vector = np.zeros(m)
    for i in range(m):
        for j in range(n-1):
            cur = nurse_schedule[i][j]
            nxt = nurse_schedule[i][j+1]
            if (cur,nxt) in [(0,1),(2,0),(2,1)]:
                shift_on_cost_each_vector[i] += 99999999
    return shift_on_cost_each_vector


def total_minutes_cost(nurse_schdule, nurse_idx):
    shift_on_cost_total_minutes = np.zeros(len(nurse_schdule))
    cur_on_request = df_shift_off[df_shift_off['ID_num'] == nurse_idx]


    MaxTotalMinutes = cur_on_request['MaxTotalMinutes']
    MinTotalMinutes = cur_on_request['MinTotalMinutes']

    total_minutes = ((nurse_schdule < 3).sum())*480
    max_violation = total_minutes > MaxTotalMinutes
    min_violation = total_minutes < MinTotalMinutes

    shift_on_cost_total_minutes += (max_violation * 99999999 + min_violation * 99999999)

    return shift_on_cost_total_minutes



def total_shifts_cost(nurse_schdule, nurse_idx):
    cost_total_shifts = np.zeros(len(nurse_schdule))
    cur_on_request = df_shift_off[df_shift_off['ID_num'] == nurse_idx]

    MaxShifts_0 = cur_on_request['MaxShifts_0']
    MaxShifts_1 = cur_on_request['MaxShifts_1']
    MaxShifts_2 = cur_on_request['MaxShifts_2']


    count_0 = (nurse_schdule == 0).sum()
    count_1 = (nurse_schdule == 1).sum()
    count_2 = (nurse_schdule == 2).sum()

    vol_0 = count_0 > MaxShifts_0
    vol_1 = count_1 > MaxShifts_1
    vol_2 = count_2 > MaxShifts_2

    cost_total_shifts += (vol_0 * 99999999 + vol_1 * 99999999 + vol_2 * 99999999)

    return cost_total_shifts





















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
    res = np.array([[0, 1, 0, 1, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
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
    # cost = costCalculator(res, 0)
    res_on = shiftOnRequest(res,0)
    res_off = shiftOffRequest(res,0)
    res_shifts = shifts_cost(res)
    print(res_on)
    print(res_off)



if __name__ == "__main__":
    main()
