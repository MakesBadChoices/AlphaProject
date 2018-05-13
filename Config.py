
# Generic Imports
import os
import pygame


# Project Specific Imports


# Note: This python file controls the setup of the pygame initialization and the loading of the external resources such
# as fonts, sounds, etc.
base_directory = os.path.dirname(os.path.realpath(__file__))

TILESIZE = 32
WIDTH = 832
HEIGHT = 640
NUM_TILES_X = WIDTH / TILESIZE # 25
NUM_TILES_Y = HEIGHT / TILESIZE # 19
MOVE_COST = 5 # Movement in feet per tile


pygame.init()
pygame.event.set_blocked(pygame.MOUSEMOTION)
pygame.key.set_repeat(500, 100)
screen_size = (WIDTH, HEIGHT)
screen = pygame.display.set_mode(screen_size)


# ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~
# Set up all the fonts that are usable within the game
FONTS = {}
for song in os.listdir(os.path.join(base_directory, 'Fonts')):
    name, ext = os.path.splitext(song)
    if ext.lower() in ['.ttf']:
        FONTS[name] = os.path.join(os.path.join(base_directory, 'Fonts'), song)

print FONTS

# ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~
# Set up all the menu images that get called frequently
GFX = {}
colorkey=(255,0,255)
accept=['.png', 'jpg', 'bmp']
for pic in os.listdir(os.path.join(base_directory, 'Graphics')):
    name, ext = os.path.splitext(pic)
    if ext.lower() in accept:
        img = pygame.image.load(os.path.join(base_directory, 'Graphics', pic))
        if img.get_alpha():
            img = img.convert_alpha()
        else:
            img = img.convert()
            img.set_colorkey(colorkey)
        GFX[name] = img



