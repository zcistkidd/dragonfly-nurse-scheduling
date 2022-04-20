import pandas as pd
# from numpy import array
import numpy as np

df_days_off = pd.read_csv("./data/SECTION_DAYS_OFF.csv")
df_shift = pd.read_csv("./data/SECTION_SHIFTS.csv")
df_staff = pd.read_csv("./data/SECTION_STAFF.csv")
df_cover = pd.read_csv("./data/SECTION_COVER.csv")  # soft

def schedule_validation(nurse_schedule, nurseID):
    if days_off_validation(nurse_schedule, nurseID) and staff_validation(nurse_schedule, nurseID):
        return True
    else:
        return False

def days_off_validation(nurse_schedule, nurseID):
    # days_off
    for _, row in df_days_off.iterrows():
        employee = row['EmployeeID_num']
        day_off = row['DayIndexes(startatzero)']

        # check with nurse schedule
        if employee == nurseID:
            if nurse_schedule[nurseID][day_off] != 3:
                return False
    return True

# Check min/max minutes, weekends, shifts, consecutive days off and working days
def staff_validation(nurse_schedule, nurseID):
    number_of_days = len(nurse_schedule[0])  # number of days

    nurse = nurse_schedule
    max_total_minutes = df_staff.at[nurseID, 'MaxTotalMinutes']
    min_total_minutes = df_staff.at[nurseID, 'MinTotalMinutes']
    max_consecutive_shifts = df_staff.at[nurseID, 'MaxConsecutiveShifts']
    min_consecutive_shifts = df_staff.at[nurseID, 'MinConsecutiveShifts']
    min_consecutive_days_off = df_staff.at[nurseID, 'MinConsecutiveDaysOff']
    max_weekends = df_staff.at[nurseID, 'MaxWeekends']
    max_evening_shift = df_staff.at[nurseID, 'MaxShifts_1']
    max_day_shift = df_staff.at[nurseID, 'MaxShifts_0']
    max_late_shift = df_staff.at[nurseID, 'MaxShifts_2']
    for i in range(0, number_of_days - 1):
        # round to int?
        # nurse[i + 1] = round(nurse[i + 1])
        prev = nurse[0][i]
        current = nurse[0][i + 1]

        # D-0 E-1 L-2 O-3
        # Check if min consecutive day off <= 2
        if min_consecutive_days_off == 2:
            if current == 3:
                if prev != 3:
                    # counter = count_consec(array, i + 1, 4)
                    if current == number_of_days - 1:
                        return False
                    if nurse[0][current + 1] != 3:
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


def count_consecutive_working_days(array, start):
    index = start  # current day index
    counter = 0
    while array[0][index - 1] != 3:
        counter += 1
        index += 1
    return counter
