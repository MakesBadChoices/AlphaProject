
# Generic Imports
import pygame
from pygame.locals import *

# Project Specific Imports
from Config import *

# ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~
# size: iterable which describes the expected length and height of each sprite in the sheet
# file: the file path location of the sheet in question
# pos: iterable which describes the starting location of the first sprite on the sheet
def sprite_sheet(size, file, pos=(0, 0), scale=1, single=False):

    # Initial Values
    len_sprt_x,len_sprt_y = size
    sprt_rect_x,sprt_rect_y = pos

    # Load the sheet
    print file
    sheet = pygame.image.load(file).convert_alpha()
    sheet_rect = sheet.get_rect()
    sprites = []

    if single: return sheet_rect

    # Iterate over rows
    for i in range(0, sheet_rect.height-len_sprt_y+1, size[1]):

        # Iterate over columns
        for j in range(0, sheet_rect.width-len_sprt_x+1, size[0]):

            sheet.set_clip(pygame.Rect(sprt_rect_x, sprt_rect_y, len_sprt_x, len_sprt_y))
            sprite = sheet.subsurface(sheet.get_clip())
            if scale != 1: sprite = pygame.transform.scale(sprite, (size[0]*scale, size[1]*scale))
            sprites.append(sprite)

            sprt_rect_x += len_sprt_x

        sprt_rect_y += len_sprt_y
        sprt_rect_x = 0

    print sprites
    return sprites


# ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~
# DEPRECATED
# Helper function which handily does the heavy lifting in making a tile object.
# size: iterable which describes the expected length and height of each sprite in the sheet
# file: the file path location of the sheet in question
# pos: iterable which describes the starting location of the first sprite on the sheet
def make_tile(name, passable, sprite, size, animation_series=None, collision_override=None):
    pass


# ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~
# This is meant for standard, static sprite sheets.
# If the animated flag is turned to true, then the tile sheet argument should be a list, where each subsequent page is
# the next fram
def make_tile_dictionary(tile_size, tile_sheet, animated=False, starting_key=0, pos=(0, 0)):

    # Make a tile dictionary for each sprite sheet you are fed
    sprite_list = sprite_sheet(tile_size, tile_sheet)

    # THere is a hardcoded limit of 48 different tiles per sheet. Deal wit' it
    dict_codes = '0123456789-=abcdefghijklmnopqrstuvwxyz!@#$%^&*()_+ABCDEFGHIJKLMNOPQRSTUVWXYZ`'

    tile_dictionary = {}

    if animated:
        tile_dictionary[dict_codes[starting_key]] = sprite_list
    else:
        for i, sprite in enumerate(sprite_list):
            tile_dictionary[dict_codes[i+starting_key]] = sprite
            if i == len(dict_codes)-1: break

    return tile_dictionary

# ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~
# This function takes in txt based tile maps and turns them into sprite based maps to be drawn on screen
# tile_map_files: iterable which describes the text files with the tilemaps. They are read/stacked first to last
# tile_dictionary
def read_tile_map(tile_map_files, tile_dictionary, tile_size):

    # Note: By default, the first map read is considered the background. The background probably shouldn't be animated.
    all_tiles = pygame.sprite.LayeredDirty()
    centerx = tile_size[0]/2; centery = tile_size[1]/2

    for i, map in enumerate(tile_map_files):
        map_handle = open(map)

        # Reading down the y-axis line by line, then the x-axis character by character
        for line in map_handle:
            for char in line.strip():
                current_image = tile_dictionary[char]
                if type(current_image) is list: current_tile = Tile('DEFAULT', True, current_image[0], tile_size, animation_series=current_image)
                else: current_tile = Tile('DEFAULT', True, current_image, tile_size)
                current_tile.place_tile((centerx, centery))
                centerx += current_tile.size[0]
                all_tiles.add(current_tile)

            centery += current_tile.size[1]
            centerx = tile_size[0]/2
        map_handle.close()

    return all_tiles

# ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~
# This function takes in txt based tile maps and turns them into sprite based maps to be drawn on screen
# tile_map_files: iterable which describes the text files with the tilemaps. They are read/stacked first to last
# tile_dictionary
def read_tiled_map(tile_lists, tile_file, tile_size=None, scale=1):

    if tile_size is None: tile_size = (TILESIZE, TILESIZE)



    # Note: By default, the first map read is considered the background. The background probably shouldn't be animated.
    all_tiles = pygame.sprite.LayeredDirty()
    centerx = tile_size[0]*scale/2; centery = tile_size[1]*scale/2

    # Read in the tile_file
    sprites = sprite_sheet(tile_size, tile_file, scale=scale)

    for i, line in enumerate(tile_lists):

        # Reading down the y-axis line by line, then the x-axis character by character
        for index in line.split(','):
            current_image = sprites[int(index)]
            if type(current_image) is list: current_tile = Tile('DEFAULT', True, current_image[0], (tile_size[0]*scale, tile_size[1]*scale), animation_series=current_image)
            else: current_tile = Tile('DEFAULT', True, current_image, (tile_size[0]*scale, tile_size[1]*scale))
            current_tile.place_tile((centerx, centery))
            centerx += current_tile.size[0]
            all_tiles.add(current_tile)

        centery += current_tile.size[1]
        centerx = tile_size[0]*scale/2

    return all_tiles

# ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~
class Tile(pygame.sprite.DirtySprite):

    def __init__(self, name, passable, sprite, size, animation_series=None, collision_override=None, update_timer=300):

        pygame.sprite.DirtySprite.__init__(self)

        # Set up some internal memory
        self.name = name
        self.image = sprite
        self.size = size
        self.animation_series = animation_series

        # Detect if the user desires a collision box different than a simple rectangle surrounding the sprite
        if collision_override:
            self.rect = collision_override
        else:
            self.rect = self.image.get_rect()

        # Set up some variables for the tiles inevitable use in battle
        self.passable = passable
        self.difficult = False
        self.occupant = None
        self.prop = None
        self.gridx = None
        self.gridy = None
        self.battle_coords = (self.rect.center[0], self.rect.center[1] - self.size[1] / 2)

        # Set up some internal properties regarding visible sprites and animations
        if self.animation_series is None:
            self.animated = False
            self.dirty = 0
        else:
            self.animated = True
            self.update_timer = update_timer
            self.time_passed = 0
            self.frame = 0
            self.max_frame = len(self.animation_series)-1
            self.dirty = 1

    # .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .
    def update(self):

        if self.animated:
            self.frame += 1
            if self.frame > self.max_frame: self.frame = 0
            self.image = self.animation_series[self.frame]
            self.rect = self.image.get_rect()
            self.dirty = 1
        else:
            pass

    def place_tile(self, coords):
        self.rect.center = coords
        self.battle_coords = (self.rect.center[0], self.rect.center[1] - int(self.size[1] * .4))


# ==================================================================================================================== #
#  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  - #
# ==================================================================================================================== #
#  DEBUG ZONE     DEBUG ZONE     DEBUG ZONE     DEBUG ZONE     DEBUG ZONE     DEBUG ZONE     DEBUG ZONE     DEBUG ZONE #
# ==================================================================================================================== #
#  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  - #
# ==================================================================================================================== #

if __name__ == "__main__":

    import Utilities

    # Initialize Everything
    pygame.init()
    screen = pygame.display.set_mode((96, 96))
    pygame.display.set_caption('Tile Debug')

    # Create The Backgound
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((250, 250, 250))

    # Prepare Game Objects
    clock = pygame.time.Clock()

    tile_sheet = r'C:\Users\Matt\PycharmProjects\AlphaProject\BattleBackgrounds\Sewer_1_tiles.png'
    tile_dictionary = make_tile_dictionary((32, 32), tile_sheet, animated=False, starting_key=0, pos=(0, 0))
    tile_dictionary2 = make_tile_dictionary((32, 32), tile_sheet, animated=True, starting_key=10, pos=(0,0))

    print tile_dictionary
    print tile_dictionary2
    tile_dictionary3 = Utilities.merge_dictionaries(tile_dictionary, tile_dictionary2)

    map1 = r'C:\Users\Matt\PycharmProjects\AlphaProject\Maps\Debug2.txt'
    all_tiles = read_tile_map([map1], tile_dictionary3, (32, 32))

    print all_tiles
    map_tile_refresh_rate = 1000

    # Draw Everything
    all_tiles.update()
    rects = all_tiles.draw(screen)
    pygame.display.update(rects)

    # all_tiles.draw(screen)

    going = True
    time_passed = 0
    while going:
        time_passed += clock.tick(60)
        for event in pygame.event.get():
            if event.type == QUIT:
                going = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                going = False

        if time_passed >= map_tile_refresh_rate:
            all_tiles.update()
            time_passed = 0

        rects = all_tiles.draw(screen)
        pygame.display.update(rects)

    print tile_dictionary
    # Need to make a screen object first
    # TILE_GROUP.DRAW(SCREEN)