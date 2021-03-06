# Generic Imports
import pygame
from pygame.locals import *
from math import sqrt

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

orange_sprite = sprite_sheet((TILESIZE, TILESIZE), str(os.path.join('CharacterGraphics', 'orange_arrow.png')).strip())
ORANGE_ARROW = orange_sprite[0]

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
        for j, row in enumerate(movement_cost_matrix):
            for i, column in enumerate(row):
                if movement_cost_matrix[j][i] <= self.master.current_creature.movement:
                    self.sprite_list.append(MovementSquare(self.navigable_tile_grid[j][i].rect.center, self.navigable_tile_grid[j][i].rect, text=movement_cost_matrix[j][i]))

        # Finally, now that we've filled out the sprite list, let the battleground know about it
        self.master.change_sprites(self.sprite_list, 'overlay_sprites', add=True, layer=0)
        self.movement_cost_matrix = movement_cost_matrix

    # .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .
    def process_input(self, incoming_event):

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
                        self.current_coords = (self.current_coords[0], self.current_coords[1]+1)
                        self.draw_arrow()

            # Enter Button or z (a) button
            if incoming_event.key == 13 or incoming_event.key == 122:

                # Pass a digested movement script to the player avatar and terminate
                if len(self.path_list) <= 1: return
                move_script = self.generate_movement_script()
                self.character.avatar.puppet_commands(move_script)
                self.character.movement = self.path_list[-1][2]
                self.delete()


            # Back Button (x)
            if incoming_event.key == 120:
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

            # Draw the new arrow
            draw_tile = self.navigable_tile_grid[self.path_list[-1][0][1]][self.path_list[-1][0][0]]
            self.arrow_sprite_list.append(MovementArrow(arrow_sprite, draw_tile.rect.center, scale=self.scale))

        # Refresh the arrows master has to draw
        self.master.change_sprites(self.arrow_sprite_list, 'overlay_sprites', add=True, layer=0)

    # .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .
    def delete(self):
        self.master.change_state('menu_mode', True)
        self.master.change_sprites(self.sprite_list, 'overlay_sprites', add=False, layer=0)
        self.master.change_sprites(self.arrow_sprite_list, 'overlay_sprites', add=False, layer=0)

    # .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .
    def generate_movement_script(self):

        move_script = []

        for i, step in enumerate(self.path_list):
            if i == 0: continue # the first step is the null, we don't need to mover where we already are!

            x_vel = 0
            y_vel = 0
            destination_tile = self.master.give_target_tile(0, 0, step[0][0], step[0][1])
            if step[1] == 'LEFT': x_vel = -25
            elif step[1] == 'RIGHT': x_vel = 25
            elif step[1] == 'UP': y_vel = -25
            elif step[1] == 'DOWN': y_vel = 25

            move_script.append(['move', {'state_set': 'RUN', 'destination_coords': destination_tile.battle_coords,
                      'velocity_x': x_vel, 'velocity_y': y_vel, 'decay': 1, 'return_x': 0, 'return_y': 0}])

        move_script.append(['update_base_coords', {'new_tile': destination_tile}])
        return move_script




# ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~
class MovementArrow(pygame.sprite.DirtySprite):

    def __init__(self, sprite, center_coords, scale=1):

        pygame.sprite.DirtySprite.__init__(self)
        # self.image = sprite
        self.image = pygame.transform.scale(sprite, (TILESIZE * scale, TILESIZE * scale))
        self.rect = self.image.get_rect()
        self.rect.center = center_coords
        self.dirty = 1
        self.layer = 0

    def update(self):
        pass


# ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~
class MovementSquare(pygame.sprite.DirtySprite):

    def __init__(self, center_coords, rect, text=None, color=(0, 0, 250, 150)):

        pygame.sprite.DirtySprite.__init__(self)
        surface = pygame.Surface(rect.size)
        surface.fill(color)

        self.layer = 0

        if text is not None:
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

    def delete(self):
        self.dirty = 1

    def update(self):
        self.dirty = 1

# ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~
class TargetOverlay(object):

    def __init__(self, master, creature, command, target_info):

        self.master = master
        self.creature = creature
        self.command = command
        self.target_info = target_info
        self.tile_sprite_list = []
        self.splash_sprite_list = []
        self.arrow_sprite_list = []
        self.splash = 0

        # From the target information, figure out which tiles are in reach
        delta_value = target_info['range']
        if self.target_info['shape'] != 'single':
            self.splash = int(self.target_info['shape'].split('splash')[1])

        # Next, grab all tiles currently in range of the user
        origin_x = creature.avatar.tile.gridx
        origin_y = creature.avatar.tile.gridy
        viable_tiles = []
        splash_tiles = []

        for j in xrange(origin_y-delta_value, origin_y+delta_value+1):
            for i in xrange(origin_x-delta_value, origin_x+delta_value+1):
                # if i == 0 and j == 0: continue
                tile = self.master.give_target_tile(0, 0, i, j)
                if tile is not None:
                    viable_tiles.append(tile)
                    self.tile_sprite_list.append(MovementSquare(tile.rect.center, tile.rect, color=(255, 165, 0, 0)))
                    # if abs(i-origin_x) + abs(j-origin_y) <= self.splash and self.splash > 0:
                    #     splash_tiles.append(tile)
                    #     self.splash_sprite_list.append(MovementSquare(tile.rect.center, tile.rect, color=(255, 0, 0, 0)))

        # Make an orange overlay showing everything currently in range
        self.master.change_sprites(self.tile_sprite_list, 'overlay_sprites', add=True)

        # Put an arrow over everything that is a viable target
        # Abort everything if the number of target tiles is zero
        self.target_tiles = []
        for tile in viable_tiles:
            if self.check_target(tile):
                self.target_tiles.append(tile)
        if len(self.target_tiles) == 0: return

        # Make tiny arrows over each of them. Redraw these each time we get a new selection...
        # Make the first targettable tile the currently selected by default
        offset = True
        if self.target_info['target'] == 'tile': offset = False
        self.target_tile = self.target_tiles[0]
        self.arrow_sprite_list.append(TargetArrow(ORANGE_ARROW, self.target_tiles[0].rect.center, scale=2, offset=offset))

        origin_x = self.target_tile.gridx
        origin_y = self.target_tile.gridy
        splash_tiles = []

        for j in xrange(origin_y - delta_value, origin_y + delta_value + 1):
            for i in xrange(origin_x - delta_value, origin_x + delta_value + 1):
                # if i == 0 and j == 0: continue
                tile = self.master.give_target_tile(0, 0, i, j)
                if tile is not None:
                    if abs(i-origin_x) + abs(j-origin_y) <= self.splash and self.splash > 0:
                        splash_tiles.append(tile)
                        self.splash_sprite_list.append(MovementSquare(tile.rect.center, tile.rect, color=(255, 0, 0, 0)))

        # Put arrows on viable targets or red on the splash zone
        if len(self.target_tiles) > 1 and target_info['target'] != 'tile':
            for tile in self.target_tiles[1:]:
                self.arrow_sprite_list.append(TargetArrow(ORANGE_ARROW, tile.rect.center, scale=1))

        self.master.change_sprites(self.arrow_sprite_list, 'popup_sprites', add=True, layer=4)
        self.master.change_sprites(self.splash_sprite_list, 'overlay_sprites', add=True, layer=0)

    # .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .
    # Decompose the targetting info to see if a given tile is a valid location to aim the attack or whatever
    def check_target(self, tile):

        target_type = self.target_info['target']

        if target_type == 'creature':
            for creature in self.master.turn_order:
                if creature.avatar.tile.gridx == tile.gridx and creature.avatar.tile.gridy == tile.gridy: return True

        elif target_type == 'tile': return True

        elif target_type == 'self':
            if self.creature.tile.gridx == tile.gridx and self.creature.tile.gridy == tile.gridy: return True

        # Otherwise... return FALSE
        return False

    # .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .
    def update(self):
        pass

    # .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .
    def delete(self):
        self.master.change_sprites(self.tile_sprite_list, 'overlay_sprites', add=False)
        self.master.change_sprites(self.splash_sprite_list, 'overlay_sprites', add=False)
        self.master.change_sprites(self.arrow_sprite_list, 'popup_sprites', add=False)
        self.master.change_state('menu_mode', True)

    # .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .
    # This function searches out the tile closest to the currently selected one in the direction chosen
    def change_target(self, direction):

        # Now for the harder generalized case...
        delta_x = 0; delta_y = 0
        if direction == 'LEFT': delta_x = -1
        elif direction == 'RIGHT': delta_x = 1
        elif direction == 'UP': delta_y = -1
        elif direction == 'DOWN': delta_y = 1

        best_distance = 9999
        best_index = -1
        for i, tile in enumerate(self.target_tiles):
            if tile.gridx == self.target_tile.gridx and tile.gridy == self.target_tile.gridy: continue
            distance = sqrt((self.target_tile.gridx + delta_x - tile.gridx)**2 + (self.target_tile.gridy + delta_y - tile.gridy)**2)
            if distance < best_distance:
                best_distance = distance
                best_index = i
        self.target_tile = self.target_tiles[best_index]

        # Now, regenerate the arrows and crap
        offset = True
        if self.target_info['target'] == 'tile': offset = False
        self.master.change_sprites(self.arrow_sprite_list, 'popup_sprites', add=False)

        self.arrow_sprite_list = []
        self.arrow_sprite_list.append(TargetArrow(ORANGE_ARROW, self.target_tile.rect.center, scale=2, offset=offset))

        if len(self.target_tiles) > 1 and self.target_info['target'] != 'tile':
            for tile in self.target_tiles:
                if tile.gridx == self.target_tile.gridx and tile.gridy == self.target_tile.gridy: continue
                self.arrow_sprite_list.append(TargetArrow(ORANGE_ARROW, tile.rect.center, scale=1))

        if self.splash != 0:
            self.master.change_sprites(self.splash_sprite_list, 'overlay_sprites', add=False, layer=0)
            self.splash_sprite_list = []

            origin_x = self.target_tile.gridx
            origin_y = self.target_tile.gridy

            for j in xrange(origin_y - self.splash, origin_y + self.splash + 1):
                for i in xrange(origin_x - self.splash, origin_x + self.splash + 1):
                    if abs(i-origin_x) + abs(j-origin_y) > self.splash: continue
                    tile = self.master.give_target_tile(0, 0, i, j)
                    if tile is not None: self.splash_sprite_list.append(MovementSquare(tile.rect.center, tile.rect, color=(255, 0, 0, 0)))

        self.master.change_sprites(self.arrow_sprite_list, 'popup_sprites', add=True, layer=4)
        self.master.change_sprites(self.splash_sprite_list, 'overlay_sprites', add=True, layer=0)

    # .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .
    def process_input(self, incoming_event):

        if incoming_event.type == KEYDOWN:

            # Left Arrow
            if incoming_event.key == 276:
                self.change_target('LEFT')

            # Up Arrow
            if incoming_event.key == 273:
                self.change_target('UP')

            # Right Arrow
            if incoming_event.key == 275:
                self.change_target('RIGHT')

            # Down arrow
            if incoming_event.key == 274:
                self.change_target('DOWN')

            # Enter Button or z (a) button
            if incoming_event.key == 13 or incoming_event.key == 122:
                if self.target_info['type'] == 'spell': self.master.cast_spell(self.creature, self.command, target_tile=self.target_tile)
                else: self.master.give_character_basic_command(self.creature, self.command, target_tile=self.target_tile)
                self.delete()

            # Back Button (x)
            if incoming_event.key == 120:
                self.delete()


class TargetArrow(pygame.sprite.DirtySprite):

        def __init__(self, sprite, center_coords, scale=1, offset=True):
            pygame.sprite.DirtySprite.__init__(self)
            self.layer = 4
            self.image = pygame.transform.scale(sprite, (TILESIZE * scale, TILESIZE * scale))
            self.rect = self.image.get_rect()
            if offset: self.rect.center = (center_coords[0], center_coords[1] - (TILESIZE * scale + TILESIZE*scale/2))
            else: self.rect.center = (center_coords[0], center_coords[1] - (TILESIZE*scale)/2)

            self.dirty = 1

        def update(self):
            pass

class TextPopup(pygame.sprite.DirtySprite):

    def __init__(self, master, text, center_coords, color=(255, 255, 255), size=24, scale=1):

        pygame.sprite.DirtySprite.__init__(self)

        self.master = master
        # self.font = pygame.font.Font(FONTS['nintendo_nes_font'], size)
        self.font = pygame.font.Font(FONTS['nintendo_nes_font'], size)
        self.image = self.font.render(text.upper(), True, color)
        self.rect = self.image.get_rect(x=10, y=10)
        self.rect.center = (center_coords[0], center_coords[1] - (TILESIZE * scale + TILESIZE*scale/2))

        self.layer = 5
        self.dirty = 1

        self.velocity = 3
        self.duration = 15

    def update(self):

        self.rect.center = (self.rect.center[0], self.rect.center[1] - self.velocity)
        self.duration -= 1
        self.dirty = 1

        if self.duration == 0:
            self.master.change_sprites([self], 'popup_sprites', add=False)


# ==================================================================================================================== #
#  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  - #
# ==================================================================================================================== #
#  DEBUG ZONE     DEBUG ZONE     DEBUG ZONE     DEBUG ZONE     DEBUG ZONE     DEBUG ZONE     DEBUG ZONE     DEBUG ZONE #
# ==================================================================================================================== #
#  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  - #
# ==================================================================================================================== #

if __name__ == "__main__":

    pass