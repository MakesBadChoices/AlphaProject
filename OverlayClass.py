# Generic Imports
import pygame
from pygame.locals import *

# Project Specific Imports
from Config import *
from TileEngine import sprite_sheet
from Utilities import movement_cost_compute

# Set up some local resources we'll be using frequently within this module
arrow_sprites = sprite_sheet((TILESIZE, TILESIZE), str(os.path.join('CharacterGraphics', 'Arrow_resources.png')).strip())
HORZ_ARROW = arrow_sprites[0]
VERT_ARROW = arrow_sprites[1]
UPPER_LEFT = arrow_sprites[2]
UPPER_RIGHT = arrow_sprites[3]
BOTTOM_RIGHT = arrow_sprites[4]
BOTTOM_LEFT = arrow_sprites[5]
LEFT_ARROW = arrow_sprites[6]
DOWN_ARROW = arrow_sprites[7]
RIGHT_ARROW = arrow_sprites[8]
UP_ARROW = arrow_sprites[9]
ORIGIN_LEFT = arrow_sprites[10]
ORIGIN_DOWN = arrow_sprites[11]
ORIGIN_RIGHT = arrow_sprites[12]
ORIGIN_UP = arrow_sprites[13]

# ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~
class MovementOverlay(object):


    def __init__(self, master, character, navigable_tile_grid, scale=1):

        # First, establish who the big boss is
        self.master = master
        self.character = character
        self.navigable_tile_grid = navigable_tile_grid
        self.scale = scale

        # self.make_movement_square()
        self.sprite_list = []
        self.setup_movement_field()

        # Set up a space to record the arrow changes log
        self.arrow_sprite_list = []
        self.current_coords = (self.character.avatar.tile.gridx, self.character.avatar.tile.gridy)
        self.path_list = [[self.current_coords, 'NULL', character.movement]]

    # .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .
    def update(self):
        pass

    # .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .
    def setup_movement_field(self):

        # Query the targets current location
        origin_x = self.character.avatar.tile.gridx
        origin_y = self.character.avatar.tile.gridy

        # Determine the bounds of the search area...
        min_x = origin_x - (self.character.movement / MOVE_COST)
        max_x = origin_x + (self.character.movement / MOVE_COST)
        min_y = origin_y - (self.character.movement / MOVE_COST)
        max_y = origin_y + (self.character.movement / MOVE_COST)
        if min_x < 0: min_x = 0
        if min_y < 0: min_y = 0
        if max_x > len(self.navigable_tile_grid[0]) - 1: max_x = len(self.navigable_tile_grid[0]) - 1
        if max_y > len(self.navigable_tile_grid) - 1: max_y = len(self.navigable_tile_grid) - 1

        matrix_dimensions = (max_x - min_x, max_y - min_y)
        movement_cost_matrix = movement_cost_compute(min_x, max_x, min_y, max_y, (origin_x, origin_y), self.navigable_tile_grid)

        # Set up a group for drawing purposes
        self.sprite_list = []

        # Make tiles if we have an appropriately costed block
        print len(movement_cost_matrix)
        print movement_cost_matrix

        for j, row in enumerate(movement_cost_matrix):
            for i, column in enumerate(row):
                if movement_cost_matrix[j][i] <= self.master.current_creature.movement:
                    self.sprite_list.append(MovementSquare(self.navigable_tile_grid[j][i].rect.center, self.navigable_tile_grid[j][i].rect, movement_cost_matrix[j][i]))

        # Finally, now that we've filled out the sprite list, let the battleground know about it
        self.master.change_sprites(self.sprite_list, 'overlay_sprites', add=True, layer=0)
        self.movement_cost_matrix = movement_cost_matrix

    # .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .
    def process_input(self, incoming_event):

        print incoming_event
        if incoming_event.type == KEYDOWN:

            # Left Arrow
            if incoming_event.key == 276:

                if self.current_coords[0] - 1 < 0: return

                # Draw the arrow for debug mode
                destination_tile = self.navigable_tile_grid[self.current_coords[1]][self.current_coords[0]-1]
                center_coords = destination_tile.rect.center

                # Check to see if this is erasing old input
                if self.path_list[-1][1] == 'RIGHT':
                    self.master.change_sprites([self.arrow_sprite_list[-1]], 'overlay_sprites', add=False, layer=0)
                    self.arrow_sprite_list.pop()
                    self.path_list.pop()
                    self.current_coords = (self.current_coords[0]-1, self.current_coords[1])
                    self.draw_arrow()
                    return

                # If not, make sure movement is left and the tile is navigable
                if destination_tile.passable:
                    remaining_movement = self.path_list[-1][2]
                    move_cost = MOVE_COST
                    if destination_tile.difficult: move_cost *= 2
                    if remaining_movement - move_cost >= 0:
                        self.path_list.append([(self.current_coords[0]-1, self.current_coords[1]), 'LEFT', remaining_movement-move_cost])
                        print self.path_list
                        self.current_coords = (self.current_coords[0]-1, self.current_coords[1])
                        self.draw_arrow()

            # Up Arrow
            if incoming_event.key == 273:

                if self.current_coords[1] - 1 < 0: return

                # Draw the arrow for debug mode
                destination_tile = self.navigable_tile_grid[self.current_coords[1]-1][self.current_coords[0]]
                center_coords = destination_tile.rect.center

                # Check to see if this is erasing old input
                if self.path_list[-1][1] == 'DOWN':
                    self.master.change_sprites([self.arrow_sprite_list[-1]], 'overlay_sprites', add=False, layer=0)
                    self.arrow_sprite_list.pop()
                    self.path_list.pop()
                    self.current_coords = (self.current_coords[0], self.current_coords[1]-1)
                    self.draw_arrow()
                    return

                # If not, make sure movement is left and the tile is navigable
                if destination_tile.passable:
                    remaining_movement = self.path_list[-1][2]
                    move_cost = MOVE_COST
                    if destination_tile.difficult: move_cost *= 2
                    if remaining_movement - move_cost >= 0:
                        self.path_list.append([(self.current_coords[0], self.current_coords[1]-1), 'UP', remaining_movement-move_cost])
                        print self.path_list
                        self.current_coords = (self.current_coords[0], self.current_coords[1]-1)
                        self.draw_arrow()

            # Right Arrow
            if incoming_event.key == 275:

                if self.current_coords[0] + 1 > len(self.navigable_tile_grid[0]) - 1: return

                # Draw the arrow for debug mode
                destination_tile = self.navigable_tile_grid[self.current_coords[1]][self.current_coords[0]+1]
                center_coords = destination_tile.rect.center

                # Check to see if this is erasing old input
                if self.path_list[-1][1] == 'LEFT':
                    self.master.change_sprites([self.arrow_sprite_list[-1]], 'overlay_sprites', add=False, layer=0)
                    self.arrow_sprite_list.pop()
                    self.path_list.pop()
                    self.current_coords = (self.current_coords[0] + 1, self.current_coords[1])
                    self.draw_arrow()
                    return

                # If not, make sure movement is left and the tile is navigable
                if destination_tile.passable:
                    remaining_movement = self.path_list[-1][2]
                    move_cost = MOVE_COST
                    if destination_tile.difficult: move_cost *= 2
                    if remaining_movement - move_cost >= 0:
                        self.path_list.append([(self.current_coords[0]+1, self.current_coords[1]), 'RIGHT', remaining_movement-move_cost])
                        print self.path_list
                        self.current_coords = (self.current_coords[0]+1, self.current_coords[1])
                        self.draw_arrow()

            # Down arrow
            if incoming_event.key == 274:

                if self.current_coords[1] + 1 > len(self.navigable_tile_grid) - 1: return

                # Draw the arrow for debug mode
                destination_tile = self.navigable_tile_grid[self.current_coords[1]+1][self.current_coords[0]]
                center_coords = destination_tile.rect.center

                # Check to see if this is erasing old input
                if self.path_list[-1][1] == 'UP':
                    self.master.change_sprites([self.arrow_sprite_list[-1]], 'overlay_sprites', add=False, layer=0)
                    self.arrow_sprite_list.pop()
                    self.path_list.pop()
                    self.current_coords = (self.current_coords[0], self.current_coords[1]+1)
                    self.draw_arrow()
                    return

                # If not, make sure movement is left and the tile is navigable
                if destination_tile.passable:
                    remaining_movement = self.path_list[-1][2]
                    move_cost = MOVE_COST
                    if destination_tile.difficult: move_cost *= 2
                    if remaining_movement - move_cost >= 0:
                        self.path_list.append([(self.current_coords[0], self.current_coords[1]+1), 'DOWN', remaining_movement-move_cost])
                        print self.path_list
                        self.current_coords = (self.current_coords[0], self.current_coords[1]+1)
                        self.draw_arrow()

            # Enter Button or z (a) button
            if incoming_event.key == 13 or incoming_event.key == 122: pass

            # Back Button (x)
            if incoming_event.key == 120:
                self.master.change_state('menu_mode', True)
                self.delete()

    # .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .
    def draw_arrow(self):

        # Delete the old arrow
        self.master.change_sprites(self.arrow_sprite_list, 'overlay_sprites', add=False, layer=0)
        self.arrow_sprite_list = []

        for i in xrange(1, len(self.path_list)):

            # Figure out what the new and old directions are
            old_direction = self.path_list[i-1][1]
            new_direction = self.path_list[i][1]

            if old_direction == 'NULL':
                if new_direction == 'LEFT': arrow_sprite = ORIGIN_LEFT
                elif new_direction == 'RIGHT': arrow_sprite = ORIGIN_RIGHT
                elif new_direction == 'UP': arrow_sprite = ORIGIN_UP
                elif new_direction == 'DOWN': arrow_sprite = ORIGIN_DOWN
            elif old_direction == new_direction:
                if old_direction == 'LEFT' or old_direction == 'RIGHT': arrow_sprite = HORZ_ARROW
                if old_direction == 'UP' or old_direction == 'DOWN': arrow_sprite = VERT_ARROW
            else:
                if old_direction == 'DOWN':
                    if new_direction == 'LEFT': arrow_sprite = UPPER_LEFT
                    elif new_direction == 'RIGHT': arrow_sprite = UPPER_RIGHT
                elif old_direction == 'LEFT':
                    if new_direction == 'UP': arrow_sprite = UPPER_RIGHT
                    elif new_direction == 'DOWN': arrow_sprite = BOTTOM_RIGHT
                elif old_direction == 'RIGHT':
                    if new_direction == 'UP': arrow_sprite = UPPER_LEFT
                    elif new_direction == 'DOWN': arrow_sprite = BOTTOM_LEFT
                elif old_direction == 'UP':
                    if new_direction == 'LEFT': arrow_sprite = BOTTOM_LEFT
                    if new_direction == 'RIGHT': arrow_sprite = BOTTOM_RIGHT

            if old_direction != 'NULL':
                # self.master.change_sprites([self.arrow_sprite_list[-1]], 'overlay_sprites', add=False, layer=0)
                self.arrow_sprite_list.pop()

                # Replace the old arrow
                draw_tile = self.navigable_tile_grid[self.path_list[i-1][0][1]][self.path_list[i-1][0][0]]
                self.arrow_sprite_list.append(MovementArrow(arrow_sprite, draw_tile.rect.center, scale=self.scale))

            else:
                # Just draw their old arrow and call it a day
                draw_tile = self.navigable_tile_grid[self.path_list[i-1][0][1]][self.path_list[i-1][0][0]]
                self.arrow_sprite_list.append(MovementArrow(arrow_sprite, draw_tile.rect.center, scale=self.scale))


            if new_direction == 'UP': arrow_sprite = UP_ARROW
            elif new_direction == 'DOWN': arrow_sprite = DOWN_ARROW
            elif new_direction == 'LEFT': arrow_sprite = LEFT_ARROW
            elif new_direction == 'RIGHT': arrow_sprite = RIGHT_ARROW
            print new_direction

            # Draw the new arrow
            draw_tile = self.navigable_tile_grid[self.path_list[-1][0][1]][self.path_list[-1][0][0]]
            self.arrow_sprite_list.append(MovementArrow(arrow_sprite, draw_tile.rect.center, scale=self.scale))

        # Refresh the arrows master has to draw
        self.master.change_sprites(self.arrow_sprite_list, 'overlay_sprites', add=True, layer=0)



    # .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .
    def delete(self):
        self.master.change_sprites(self.sprite_list, 'overlay_sprites', add=False, layer=0)
        self.master.change_sprites(self.arrow_sprite_list, 'overlay_sprites', add=False, layer=0)


# ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~
class MovementArrow(pygame.sprite.DirtySprite):

    def __init__(self, sprite, center_coords, scale=1):

        pygame.sprite.DirtySprite.__init__(self)
        # self.image = sprite
        print scale
        self.image = pygame.transform.scale(sprite, (TILESIZE * scale, TILESIZE * scale))
        self.rect = self.image.get_rect()
        self.rect.center = center_coords
        self.dirty = 1
        self.layer = 0

    def update(self):
        pass


# ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~
class MovementSquare(pygame.sprite.DirtySprite):

    def __init__(self, center_coords, rect, text):

        pygame.sprite.DirtySprite.__init__(self)
        surface = pygame.Surface(rect.size)
        surface.fill((0, 0, 250, 150))
        self.layer = 0

        self.font = pygame.font.Font(FONTS['nintendo_nes_font'], 16)
        text_surface = self.font.render(str(text), True, (255, 255, 255))
        text_rect = text_surface.get_rect(x=10,
                                          y=10)
        surface.blit(text_surface, text_rect)


        surface.set_alpha(50)
        self.image = surface
        self.rect = self.image.get_rect()
        self.rect.center = center_coords
        self.dirty = 1

    def update(self):
        self.dirty = 1


# ==================================================================================================================== #
#  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  - #
# ==================================================================================================================== #
#  DEBUG ZONE     DEBUG ZONE     DEBUG ZONE     DEBUG ZONE     DEBUG ZONE     DEBUG ZONE     DEBUG ZONE     DEBUG ZONE #
# ==================================================================================================================== #
#  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  - #
# ==================================================================================================================== #

if __name__ == "__main__":

    pass