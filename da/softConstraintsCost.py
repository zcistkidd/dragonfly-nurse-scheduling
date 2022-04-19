import csv

import numpy as np
import pandas as pd
from sklearn import preprocessing

# TODO coordinate with Chi to finalise all csv files to use numerized values
df_cover = pd.read_csv("data/SECTION_COVER.csv")  # soft
df_shift_off = pd.read_csv("./data/SECTION_SHIFT_OFF_REQUESTS.csv")  # soft
df_shift_on = pd.read_csv("data/SECTION_SHIFT_ON_REQUESTS.csv")  # soft


#   D1 D2 D3 D4 D5 ... D14
# 1  0  1 2  0  2       1
# 2  1  2 1  1  2       0
# 3
# 4
# 5
# 6


def costCalculator(df_nurse_schedule):
    # cost = cover(df_nurse_schedule) \
    #        + shiftOffRequest(df_nurse_schedule) \
    #        + shiftOnRequest(df_nurse_schedule)

    number_of_nurses = len(df_nurse_schedule)
    number_of_days = len(df_nurse_schedule[0])
    # cost matrix
    # nurse_cost = np.arange(number_of_days * number_of_nurses).reshape((number_of_nurses, number_of_days))
    nurse_cost = [[0 for i in range(number_of_days)] for j in range(number_of_nurses)]
    # offcost,totaloffcost = shiftOffRequest(df_nurse_schedule, nurse_cost)
    # oncost, totaloncost = shiftOnRequest(df_nurse_schedule, nurse_cost)
    total_cost = shiftOffRequest(df_nurse_schedule, nurse_cost) + \
                 shiftOnRequest(df_nurse_schedule, nurse_cost)
    # cost =  offcost.add(oncost)
    cost = convertNurseCost(nurse_cost)
    return cost,total_cost;


def convertNurseCost(nurse_cost):
    cost = []

    for i in range(len(nurse_cost)):
        temp = 0
        for j in range(len(nurse_cost[0])):
            temp = temp + nurse_cost[i][j]
        cost.append(temp)

    return cost


def shiftOffRequest(df_nurse_schedule, nurse_cost):
    shift_off_cost_total = 0
    shift_off_cost_each_vector = []
    shift_off_reader = csv.DictReader(df_shift_off)
    for _, row in df_shift_off.iterrows():
        employee = row['EmployeeID_num']
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


def shiftOnRequest(df_nurse_schedule, nurse_cost):
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
