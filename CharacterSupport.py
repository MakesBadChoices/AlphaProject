# Generic Imports
import numpy.random as rand

#  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
# THis function reads a dice string and outputs a valid roll for it. A die string reads as follows:
# 2d4 + 1 indicates roll 2 dice with 4 sides each, and then add 1 to the result.
# Note: The only valid symbols are [d, +, -, *, /]. They are read left to right.
def dice_reader(die_string):

    die_string = die_string.replace(' ', '')
    eval_chunks = die_string.split('d')
    num_dice = int(eval_chunks[0])
    die_faces = int(eval_chunks[1])

    total = 0
    for die in xrange(0, num_dice):
        total += rand.randint(die_faces) + 1
    return total

#  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
def dice_reader_plus(string, splitters=None):

    if splitters is None: splitters = ['d', '+', '-']

    string = string.replace(' ', '')
    index_list = []
    operation_dictionary = {}
    for i, char in enumerate(string):
        if char in splitters:
            index_list.append(i)
            operation_dictionary[i] = char
    index_list.sort()

    # Go through and compress the die statements
    new_string = ''
    for i, entry in enumerate(index_list):

        # Esscape clause for single entries
        if len(index_list) == 1:
            die_roll = dice_reader(string)
            return die_roll


        if operation_dictionary[entry] == 'd':

            # Go and take characters starting from the previous and up to the next
            if i != 0 and i != len(index_list)-1:
                extract_string = string[index_list[i-1]+1:index_list[i+1]]
            elif i == 0:
                extract_string = string[0:index_list[i+1]]
            elif i == len(index_list)-1:
                extract_string = string[index_list[i-1]+1:]

            die_roll = dice_reader(extract_string)
            new_string += str(die_roll)
            operation_dictionary[entry] = die_roll

        elif i == 0:
            new_string += string[0:index_list[i]]
        elif i == len(index_list)-1:
            new_string += operation_dictionary[entry] + string[index_list[i]+1:]
        else:
            new_string += operation_dictionary[entry]

    # Now that the die statements are compressed, let's finish the job...
    index_list = []
    operation_dictionary = {}
    for i, char in enumerate(new_string):
        if char in splitters:
            index_list.append(i)
            operation_dictionary[i] = char
    index_list.sort()

    grand_total = 0
    for i, entry in enumerate(index_list):

        # First check to see if there is only one or NO operations...
        if len(index_list) == 1:
            num1 = int(new_string[0:index_list[i]])
            num2 = int(new_string[index_list[i]+1:])

            if operation_dictionary[entry] == '+': grand_total = num1 + num2
            if operation_dictionary[entry] == '-': grand_total = num1 - num2

        elif len(index_list) == 0:

            grand_total = int(new_string)

        # First operation has special rules
        elif i == 0:
            num1 = int(new_string[0:index_list[i]])
            num2 = int(new_string[index_list[i]+1:index_list[i+1]])

            if operation_dictionary[entry] == '+': grand_total = num1 + num2
            if operation_dictionary[entry] == '-': grand_total = num1 - num2

        # Subsequent operations add to the grand total
        else:

            if i == len(index_list) - 1:
                num2 = int(new_string[index_list[i]+1:])
            else:
                num2 = int(new_string[index_list[i]+1:index_list[i+1]])

            if operation_dictionary[entry] == '+': grand_total += num2
            if operation_dictionary[entry] == '-': grand_total -= num2

    return grand_total

#  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
# Various tables and things ...
bonus_table = {
    1: -5,
    2: -4,
    3: -4,
    4: -3,
    5: -3,
    6: -2,
    7: -2,
    8: -1,
    9: -1,
    10: 0,
    11: 0,
    12: 1,
    13: 1,
    14: 2,
    15: 2,
    16: 3,
    17: 3,
    18: 4,
    19: 4,
    20: 5,
    21: 5,
    22: 6,
    23: 6,
    24: 7,
    25: 7,
    26: 8,
    27: 8,
    28: 9,
    29: 9,
    30: 10
}

#  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
level_bonus_table = {
    1: 3,
    2: 3,
    3: 3,
    4: 3,
    5: 4,
    6: 4,
    7: 4,
    8: 4,
    9: 5,
    10: 5,
    11: 5,
    12: 5,
    13: 5,
    14: 6,
    15: 6,
    16: 6,
    17: 6,
    18: 6,
    19: 6,
    20: 7
}
#  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -