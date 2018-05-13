
# Generic Imports
import pygame
from pygame.locals import *
from random import randint

# Project Specific Imports
import MenuClass
from OverlayClass import MovementOverlay
from AvatarClass import Avatar
from TileEngine import read_tiled_map, sprite_sheet, Tile
from Config import *


# ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~
# I'm basically going to need to build this from the ground up... yeet
class Battleground(object):

    def __init__(self, screen_size, players, enemies, background_file=None, refresh_rate=100):

        # Set up a holding bin to keep track of all the dirty spriting we'll be doing
        self.all_sprites =  pygame.sprite.LayeredDirty()
        # self.avatar_sprites = pygame.sprite.LayeredDirty()
        # self.menu_sprites = pygame.sprite.LayeredDirty()
        # self.movement_sprites = pygame.sprite.LayeredDirty()
        # self.overlay_sprites = pygame.sprite.LayeredDirty()

        self.delete_sprites = pygame.sprite.LayeredDirty()

        # Bind relevant information
        self.refresh_rate = refresh_rate

        self.players = players
        self.enemies = enemies
        self.setup_grid(background_file)

        # The players always start at a specific location, so spawn their avatar there.
        # For each actor on the battlefield, make a dictionary indicating whether that actor is currently in an animation.
        self.animation_locks = {}

        for i, player in enumerate(players):
            if player.avatar.scale != self.scale: player.avatar = Avatar(player.name, scale=self.scale)
            coords = self.pick_starting_spots(player, player=True)
            player.avatar.base_coords = (coords[0], coords[1])
            player.avatar.rect.center = player.avatar.base_coords
            player.avatar.battlefield = self
            self.animation_locks[player.name] = False
            self.all_sprites.add(player.avatar, layer=player.avatar.layer)
            # self.avatar_sprites.add(player.avatar)

        for i, enemy in enumerate(enemies):
            if enemy.avatar.scale != self.scale: enemy.avatar = Avatar(enemy.name, scale=self.scale)
            coords = self.pick_starting_spots(enemy, player=False)
            enemy.avatar.base_coords = (coords[0], coords[1])
            enemy.avatar.rect.center = enemy.avatar.base_coords
            enemy.avatar.battlefield = self
            self.animation_locks[enemy.name] = False
            self.all_sprites.add(enemy.avatar, layer=enemy.avatar.layer)
            # self.avatar_sprites.add(enemy.avatar)

        # Add the default menu in, set up the variables and triggers for it
        # The tuples are the name, the menu-state it puts the battleground into, and... bonus option (unused)
        buttonList = [
            ('Move', 0, None),
            ('Actions', 1, None),
            ('Bonus Actions', 2, None),
            ('Setup Reactions', 3, None),
            ('End Turn', 4, None)
        ]
        image = GFX['MenuSprite']
        menu_coords = (100, 512)
        self.base_menu = MenuClass.BattleMenu(self, menu_coords, buttonList, image)
        self.sub_menus = []

        # self.menu_sprites.add(self.base_menu)
        self.all_sprites.add(self.base_menu, layer=self.base_menu.layer)

        # Let the battlefield object know what is currently receiving inputs
        self.active_object = self.base_menu
        self.previous_active_object = self.base_menu

        # Set up the turn order
        self.all_creatures = []
        self.current_turn = 0
        self.current_creature = None
        self.compute_turn_order()

        # Finally, make a dictionary of the possible states.
        self.state_dictionary = {
            'menu_mode': False,
            'input_state': True,
            'move_mode': False,
        }

    # .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .
    def process_input(self, incoming_event):

        if self.state_dictionary['input_state']:
            self.active_object.process_input(incoming_event)

    # .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .
    def update(self, incoming_event):
        pass

    # .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .
    def change_state(self, state, new_value):


        # If switching modes, turn off all other modes
        if 'mode' in state:
            self.previous_active_object = self.active_object
            for key in self.state_dictionary:
                if 'mode' in key: self.state_dictionary[key] = False

        self.state_dictionary[state] = new_value

        # If we've entered movement mode, spawn a MovementOverlay
        if self.state_dictionary['move_mode']:
            overlay = MovementOverlay(self, self.current_creature, self.navigable_tile_grid, scale=self.scale)
            self.active_object = overlay

        # If we've entered menu mode, do... nothing.
        if self.state_dictionary['menu_mode']:
            self.active_object = self.base_menu


    # .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .
    def compute_turn_order(self):

        all_creatures = self.players + self.enemies
        for creature in all_creatures:
            creature.Roll_Initiative()

        all_creatures.sort(key=lambda x: x.initiative, reverse=True)
        print all_creatures

        self.turn_order = all_creatures
        self.current_turn = 0
        self.current_creature = self.turn_order[self.current_turn]

    # .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .
    def next_turn(self):

        self.current_turn += 1
        if self.current_turn > len(self.turn_order) - 1: self.current_turn = 0
        self.current_creature = self.turn_order[self.current_turn]

    # .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .
    def setup_grid(self, map_file):

        file_handle = open(os.path.join(base_directory, 'BattleBackgrounds', map_file), 'r')

        map_list = []
        for i, line in enumerate(file_handle):
            if i == 0: source_map = line.split('source_tiles=')[1]
            elif i == 1: horizon_line = int(line.split('horizon_line=')[1])
            elif i == 2: menu_line = int(line.split('menu_line=')[1])
            elif i == 3: scale = int(line.split('scale=')[1])
            else: map_list.append(line)
        file_handle.close()

        # Make the tiles and grid
        # self.tile_list = read_tiled_map(map_list, r'C:\Users\Matt\PycharmProjects\AlphaProject\BattleBackgrounds\Sewer_1_tiles.png', scale=scale)
        source_path = str(os.path.join('BattleBackgrounds', source_map)).strip()
        self.tile_list = read_tiled_map(map_list, source_path, scale=scale)

        grid_sprite = sprite_sheet((TILESIZE, TILESIZE), r'C:\Users\Matt\PycharmProjects\AlphaProject\BattleBackgrounds\grid_outline.png', pos=(0, 0), scale=scale, single=False)
        grid_tile = Tile('DEFAULT', True, grid_sprite[0], (TILESIZE*scale, TILESIZE*scale))

        # Try and make a background from all these tiles...
        # background_group = pygame.sprite.LayeredDirty()
        # background_group.add(self.tile_list)
        background = pygame.Surface((WIDTH, HEIGHT))

        # Now identify all of the tile centers, blit them to background, and make note of their coords
        grid_coords = []
        tile_grid = []
        row_num = 0
        col_num = 0

        for item in self.tile_list:
            background.blit(item.image, (item.rect.center[0] - item.size[0]/2, item.rect.center[1] - item.size[1]/2))

            # If we hit a new row, make a new list
            if len(grid_coords) == 0:
                grid_coords.append([])
                tile_grid.append([])
            elif item.rect.center[1] != grid_coords[-1][-1][1]:
                grid_coords.append([])
                tile_grid.append([])


            item.gridy = row_num
            grid_coords[-1].append(item.rect.center)
            tile_grid[-1].append(item)

        print grid_coords

        # Grid coords is already organized according to rows, then columns. Use the known horizon and menu lines to
        # identify which are valid coords
        row_num = 0
        navigable_tiles = []
        navigable_tile_grid = []
        for i, row in enumerate(grid_coords):
            if i < horizon_line: continue
            if i >= menu_line: continue
            navigable_tile_grid.append([])
            col_num = 0

            for tile in tile_grid[i]:
                tile.gridx = col_num
                tile.gridy = row_num
                col_num += 1
                navigable_tiles.append(tile)
                navigable_tile_grid[-1].append(tile)
                background.blit(grid_tile.image, (tile.rect.center[0] - tile.size[0] / 2, tile.rect.center[1] - tile.size[1] / 2))
            row_num += 1

        self.navigable_tiles = navigable_tiles
        self.navigable_tile_grid = navigable_tile_grid
        self.tile_grid = tile_grid
        self.background = background
        self.scale = scale

    # .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .
    def pick_starting_spots(self, creature, player=True):

        not_good = True
        while not_good is True:
            index = randint(0, len(self.navigable_tiles)-1)
            if player:
                if self.navigable_tiles[index].rect.center[0] < (WIDTH*.6): continue
                if self.navigable_tiles[index].occupant is not None: continue
                self.navigable_tiles[index].occupant = creature; creature.avatar.tile = self.navigable_tiles[index]
                not_good = False
            else:
                if self.navigable_tiles[index].rect.center[0] > (WIDTH*.4): continue
                if self.navigable_tiles[index].occupant is not None: continue
                self.navigable_tiles[index].occupant = creature; creature.avatar.tile = self.navigable_tiles[index]
                not_good = False
        return self.navigable_tiles[index].battle_coords

    # .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .
    def give_target_tile(self, current_x, current_y, delta_x, delta_y):

        # Return nothing if there is an error
        if current_x + delta_x < 0 or current_x + delta_x > len(self.tile_grid[0]) - 1: return None
        if current_y + delta_y < 0 or current_y + delta_y > len(self.tile_grid) - 1: return None

        destination_tile = self.navigable_tile_grid[current_y+delta_y][current_x+delta_x]
        print destination_tile.gridx
        print destination_tile.gridy
        # Otherwise, give it the tile the requester seeks
        return destination_tile

    # .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .
    def change_sprites(self, sprite_list, sprite_group, add=True, layer=0):

        # group_list = getattr(self, sprite_group)
        group_list = self.all_sprites

        for sprite in sprite_list:
            sprite.dirty = 1
            if add:
                group_list.add(sprite, layer=layer)
            else:
                group_list.remove(sprite)
                self.delete_sprites.add(sprite)



# ==================================================================================================================== #
#  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  - #
# ==================================================================================================================== #
#  DEBUG ZONE     DEBUG ZONE     DEBUG ZONE     DEBUG ZONE     DEBUG ZONE     DEBUG ZONE     DEBUG ZONE     DEBUG ZONE #
# ==================================================================================================================== #
#  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  - #
# ==================================================================================================================== #

if __name__ == "__main__":


    background_file = r'C:\Users\Matt\PycharmProjects\AlphaProject\BattleBackgrounds\Secret.png'

    # Initialize Everything
    pygame.display.set_caption('Battle Debug')

    # Spawn some generic test things
    from PlayerClasses import Matt, TestDummy
    matt = Matt()
    test_dummy = TestDummy()

    background_file = 'testmap_export.csv'
    background_file = 'Big_Test.csv'
    bg = Battleground(screen_size, players=[matt], enemies=[test_dummy], background_file=background_file, refresh_rate=100)
    map_tile_refresh_rate = bg.refresh_rate

    # screen.blit(bg.background, (0, 0))
    # screen.blit(bg.base_menu.image, bg.base_menu.center_coords)
    pygame.display.update()

    clock = pygame.time.Clock()

    fps_read = False

    up_checks = 50
    update = 0

    going = True
    time_passed = 0
    while going:

        # Increment the tick-tock, cap at 60fps to spare my virgin CPU
        time_passed += clock.tick(60)

        # If the player has done something, hand the event off to the battlefield object and process it
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN:
                pygame.event.wait()
            if event.type == QUIT:
                going = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                going = False
            else:
                bg.process_input(event)

        if time_passed >= map_tile_refresh_rate:
            # bg.avatar_sprites.update()
            # bg.menu_sprites.update()
            # bg.movement_sprites.update()
            # bg.menu_sprites.update()
            bg.all_sprites.update()

            bg.active_object.update()
            time_passed = 0
            update += 1

        if update == up_checks:
            for player in bg.players:
                # Make the player move 4 tiles to the left
                current_x = player.avatar.tile.gridx
                current_y = player.avatar.tile.gridy
                # destination_tile = bg.give_target_tile(current_x, current_y, -4, 0)
                # player.avatar.move('RUN', destination_tile.battle_coords, -25, 0, decay=1, return_x=None, return_y=None)
            update = 0

        # Clean up sprites before redraws. Note... only some of these actually need to be cleared.
        # bg.avatar_sprites.clear(screen, bg.background)
        # bg.menu_sprites.clear(screen, bg.background)
        # bg.movement_sprites.clear(screen, bg.background)
        # bg.overlay_sprites.clear(screen, bg.background)
        bg.all_sprites.clear(screen, bg.background)

        if len(bg.delete_sprites) > 0:
            bg.delete_sprites.clear(screen, bg.background)
            bg.delete_sprites = pygame.sprite.LayeredDirty()

        if fps_read:
            print "FPS: %s" % str(int(clock.get_fps()))




        # rects = bg.movement_sprites.draw(screen)
        # rects += bg.avatar_sprites.draw(screen)
        # rects += bg.menu_sprites.draw(screen)
        # rects += bg.overlay_sprites.draw(screen)
        rects = bg.all_sprites.draw(screen)
        pygame.display.update(rects)



        # rects = all_tiles.draw(screen)
        # pygame.display.update(rects)
        # screen.blit(bg.background, (0, 0))
        # pygame.display.update()
