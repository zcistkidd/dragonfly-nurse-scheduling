# # take in an array??
# from numpy import array
#
#
# def check_schedule:
#     if array[0] == 4:
#         off_in_2_weeks += 1
#
#     for i in range(0, n - 1):
#         # round to int?
#         array[i + 1] = round(array[i + 1])
#         prev = array[i]
#         current = array[i + 1]
#
#         # Circular? E-1 D-2 L-3 O-4?
#         if current < 1:
#             current = 4 - abs(current) % 4
#         elif current > 4:
#             current = current % 4
#
#         if current == 4:
#             off_in_2_weeks += 1
#             if (i + 1) % 7 == 0:
#                 # min/max of shifts per week required??
#                 if off_in_2_weeks < 7 or off_in_2_weeks > 7:
#                     return False
#
#                 off_in_2_weeks = 0
#
#             # Min consecutive day off 2??
#             if prev != 4:
#                 counter = count_consec(array, i + 1, 4)
#                 if counter < 2 or counter > 5:
#                     return False
#         else:
#             # L cannot be followed by anything other than O, D not followed by E
#             if (prev == 3 and current != 4) or (prev == 2 and current == 1):
#                 return False
#
#             # Max consecutive shifts 5, min 2
#             if prev == 4 and current != 4:
#                 counter = count_consec(array, i + 1, 1)
#                 if counter < 2 or counter > 5:
#                     return False
#
#
# def count_consec(array, start, sign):
#     index = start
#     counter = 0
#     if sign == 4:
#         while array[index] == 4:
#             counter += 1
#             index += 1
#     else:
#         while array[index] != 4:
#             counter += 1
#             index += 1
#
#     return counter
