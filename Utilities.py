# Generic Imports
from copy import copy

# Project Specific Imports

def merge_dictionaries(dict1, dict2):
    dict3 = dict1.copy()
    dict3.update(dict2)
    return dict3


# ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~
def movement_cost_compute(min_x, max_x, min_y, max_y, origin, tile_grid):

    x_matrix = [99999] * len(tile_grid[0])
    cost_matrix = [copy(x_matrix) for i in xrange(0, len(tile_grid))]
    cost_matrix[origin[1]][origin[0]] = 0

    tile_buffer = [(origin[0], origin[1])]

    # Keep doing this until the buffer is empty
    while len(tile_buffer) > 0:

        current_coords = tile_buffer.pop()
        curr_x = current_coords[0]
        curr_y = current_coords[1]

        # Look at the tile north of the current
        if curr_y - 1 >= min_y:
            if tile_grid[curr_y-1][curr_x].difficult: new_cost = cost_matrix[curr_y][curr_x] + 10
            else: new_cost = cost_matrix[curr_y][curr_x] + 5
            if cost_matrix[curr_y-1][curr_x] > new_cost:
                cost_matrix[curr_y-1][curr_x] = new_cost
                tile_buffer.append((curr_x, curr_y-1))

        # Look at the tile to the right of the current
        if curr_x + 1 <= max_x:
            if tile_grid[curr_y][curr_x+1].difficult: new_cost = cost_matrix[curr_y][curr_x] + 10
            else: new_cost = cost_matrix[curr_y][curr_x] + 5
            if cost_matrix[curr_y][curr_x+1] > new_cost:
                cost_matrix[curr_y][curr_x+1] = new_cost
                tile_buffer.append((curr_x+1, curr_y))

        # Look at the tile below current
        if curr_y + 1 <= max_y:
            if tile_grid[curr_y+1][curr_x].difficult: new_cost = cost_matrix[curr_y][curr_x] + 10
            else: new_cost = cost_matrix[curr_y][curr_x] + 5
            if cost_matrix[curr_y+1][curr_x] > new_cost:
                cost_matrix[curr_y+1][curr_x] = new_cost
                tile_buffer.append((curr_x, curr_y+1))

        # Look at the tile to the left of the current
        if curr_x - 1 >= min_x:
            if tile_grid[curr_y][curr_x-1].difficult: new_cost = cost_matrix[curr_y][curr_x] + 10
            else: new_cost = cost_matrix[curr_y][curr_x] + 5
            if cost_matrix[curr_y][curr_x-1] > new_cost:
                cost_matrix[curr_y][curr_x-1] = new_cost
                tile_buffer.append((curr_x-1, curr_y))

    return cost_matrix


# ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~
# This computes cost matrices of stuff. I dunno
def a_star(matrix_dimensions, origin, passable_matrix, cost_matrix):
    pass



# ==================================================================================================================== #
#  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  - #
# ==================================================================================================================== #
#  DEBUG ZONE     DEBUG ZONE     DEBUG ZONE     DEBUG ZONE     DEBUG ZONE     DEBUG ZONE     DEBUG ZONE     DEBUG ZONE #
# ==================================================================================================================== #
#  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  - #
# ==================================================================================================================== #

if __name__ == "__main__":

    movement_cost_compute((3, 3), (0, 0), None)

