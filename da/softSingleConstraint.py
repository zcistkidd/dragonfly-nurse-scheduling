import csv
from collections import defaultdict

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
    res_on = shiftOnRequest(df_nurse_schedule, idx)
    res_off = shiftOffRequest(df_nurse_schedule, idx)
    res_shifts = shifts_cost(df_nurse_schedule)
    total_shifts = total_shifts_cost(df_nurse_schedule, idx)
    total_mins = total_minutes_cost(df_nurse_schedule, idx)
    days_off_cost = days_off_validation(df_nurse_schedule, idx)
    weekend = weekend_cost(df_nurse_schedule, idx)
    con_off_cost = consective_off_cost(df_nurse_schedule, idx)
    con_on_cost = consective_shifts_cost(df_nurse_schedule, idx)

    cost = res_on + res_off + res_shifts + total_shifts + total_mins + days_off_cost + weekend + con_off_cost + con_on_cost
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
    cur_on_request = df_staff[df_staff['ID_num'] == nurse_idx]


    MaxTotalMinutes = np.repeat(cur_on_request['MaxTotalMinutes'],len(nurse_schdule))
    MinTotalMinutes = np.repeat(cur_on_request['MinTotalMinutes'],len(nurse_schdule))

    total_minutes = ((nurse_schdule < 3).sum(axis = 1))*480
    max_violation = total_minutes > MaxTotalMinutes
    min_violation = total_minutes < MinTotalMinutes

    shift_on_cost_total_minutes += (max_violation * 99999999 + min_violation * 99999999)

    return shift_on_cost_total_minutes



def total_shifts_cost(nurse_schdule, nurse_idx):
    cost_total_shifts = np.zeros(len(nurse_schdule))
    cur_on_request = df_staff[df_staff['ID_num'] == nurse_idx]

    MaxShifts_0 = np.repeat(cur_on_request['MaxShifts_0'],len(nurse_schdule))
    MaxShifts_1 = np.repeat(cur_on_request['MaxShifts_1'],len(nurse_schdule))
    MaxShifts_2 = np.repeat(cur_on_request['MaxShifts_2'],len(nurse_schdule))


    count_0 = (nurse_schdule == 0).sum(axis = 1)
    count_1 = (nurse_schdule == 1).sum(axis = 1)
    count_2 = (nurse_schdule == 2).sum(axis = 1)

    vol_0 = count_0 > MaxShifts_0[0]
    vol_1 = count_1 > MaxShifts_1[0]
    vol_2 = count_2 > MaxShifts_2[0]

    cost_total_shifts += (vol_0 * 99999999 + vol_1 * 99999999 + vol_2 * 99999999)

    return cost_total_shifts

def weekend_cost(nurse_schdule, nurse_idx,weekends = [5,6,12,13]):
    cost_weekend = np.zeros(len(nurse_schdule))
    cur_weekend = df_staff[df_staff['ID_num'] == nurse_idx]

    MaxShifts = np.repeat(cur_weekend['MaxWeekends'], len(nurse_schdule))



    cur_cnt,total_cnt = np.zeros(len(nurse_schdule)),np.zeros(len(nurse_schdule))
    for weekend in weekends:
        cur = nurse_schdule[:,weekend]
        cur_cnt =(cur < 3)
        total_cnt += cur_cnt
    cost_weekend = total_cnt*99999999

    return cost_weekend

def consective_shifts_cost(nurse_schedule, nurse_idx):
    cur = df_staff[df_staff['ID_num'] == nurse_idx]

    max_con_shifts = np.repeat(cur['MaxConsecutiveShifts'], len(nurse_schedule))
    min_con_shifts = np.repeat(cur['MinConsecutiveShifts'], len(nurse_schedule))

    m,n = len(nurse_schedule),len(nurse_schedule[0])
    cost = np.zeros(m)
    ocurrence = np.zeros(m)

    nurse_schedule = nurse_schedule < 3

    for i in range(m):
        ocurrence[i] = consective_counter(nurse_schedule[i],1)


    cost =(ocurrence > max_con_shifts) *99999999 + (ocurrence <min_con_shifts) *99999999

    return cost


def consective_off_cost(nurse_schedule, nurse_idx):
    cur = df_staff[df_staff['ID_num'] == nurse_idx]


    min_con_off = np.repeat(cur['MinConsecutiveDaysOff'], len(nurse_schedule))

    m, n = len(nurse_schedule), len(nurse_schedule[0])
    cost = np.zeros(m)
    ocurrence = np.zeros(m)

    nurse_schedule = nurse_schedule < 3

    for i in range(m):
        ocurrence[i] = consective_counter(nurse_schedule[i], 0)

    cost = (ocurrence < min_con_off) * 99999999

    return cost






def consective_counter(array,num):
    m = len(array)
    cnt = 0
    for i in range(m - 1):
        cur,nxt = array[i], array[i+1]
        if cur == nxt == num:
            cnt += 1
    return cnt






def main():
    # nurse schedule
    res = np.array([[0, 1, 0, 1, 3, 1, 3, 3, 3, 3, 3, 3, 3, 2],
                    [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]])
    cost = costCalculator(res, 0)
    # res_on = shiftOnRequest(res,0)
    # res_off = shiftOffRequest(res,0)
    # res_shifts = shifts_cost(res)
    # total_shifts = total_shifts_cost(res,0)
    # total_mins = total_minutes_cost(res,0)
    # days_off_cost = days_off_validation(res,0)
    # weekend = weekend_cost(res,0)
    # con_off_cost = consective_off_cost(res,0)
    # con_on_cost = consective_shifts_cost(res,0)

    print(cost)


if __name__ == "__main__":
    main()
