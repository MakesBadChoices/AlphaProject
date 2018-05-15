# Generic Imports
import pygame
from pygame.locals import *
import numpy.random as rand
import glob
import os

# Project Imports
from CharacterClass import Character
from CharacterSupport import *
from WeaponClass import Weapon
from TileEngine import sprite_sheet

# Some local constants
sprite_size = (32, 32)
base_dir = 'C:\Users\Matt\PycharmProjects\AlphaProject\CharacterGraphics'


class Avatar(pygame.sprite.DirtySprite):

    def __init__(self, name, facing='RIGHT', scale=2):

        pygame.sprite.DirtySprite.__init__(self)

        self.name = name
        self.state = 'IDLE'
        self.override_state = 'Null'
        self.scale = scale
        self.facing = facing
        self.layer = 1

        # These parameters control how the avatar moves about the screen
        self.base_coords = (0, 0)
        self.modified_coords = (0, 0)
        self.destination_coords = None
        self.velx = 0
        self.vely = 0
        self.decay = 1
        self.tile = None
        self.battlefield = None

        # Now load up all the sprites we'll need for this Matt.
        # Note that all sprites are facing towards the left by default
        self.idle_sprites = sprite_sheet(sprite_size, os.path.join(base_dir, '%s_Idle.png' % self.name), scale=scale)
        self.run_sprites = sprite_sheet(sprite_size, os.path.join(base_dir, '%s_Run.png' % self.name), scale=scale)

        # Set up the default animations
        self.animation_series = self.idle_sprites
        self.frame = 0; self.max_frame = len(self.animation_series)-1
        self.play_action = False
        self.image = self.animation_series[0]
        self.rect = self.image.get_rect()
        self.dirty = 1

        # Set up the puppet drive
        self.puppet = False
        self.puppet_script = []
        self.puppet_index = 0


    # .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .
    def update(self):
        self.frame += 1
        if self.frame > self.max_frame:
            self.frame = 0
            if self.play_action: self.play_action = False; self.puppet_commands()

        self.image = self.animation_series[self.frame]

        if self.destination_coords:
            self.compute_moved_coordinates()
            if (self.velx > 0 and self.facing=='LEFT') or (self.velx < 0 and self.facing=='RIGHT'):
                self.image = pygame.transform.flip(self.image, True, False)
        else:
            self.modified_coords = self.base_coords

        self.rect = self.image.get_rect()
        self.rect.center = (self.modified_coords)
        self.dirty = 1

        colorkey = self.image.get_at((0, 0))
        self.image.set_colorkey(colorkey, RLEACCEL)

    # .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .
    def check_state(self):
        pass

    # .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .
    def change_state(self, new_state):
        self.previous_state = self.state
        self.state = new_state
        self.animation_series = getattr(self, new_state.lower() + '_sprites')
        # if new_state == 'IDLE': self.animation_series = self.idle_sprites
        # if new_state == 'RUN': self.animation_series = self.run_sprites
        # Update the index information about the new animation series
        self.frame = 0; self.max_frame = len(self.animation_series)-1

    # .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .
    # This method is called when the avatar needs to be moved around. It sets destination coords and velocities
    def move(self, state_set, destination_coords, velocity_x, velocity_y, decay=1, return_x=None, return_y=None):

        self.override_state = state_set
        self.change_state(state_set)

        self.destination_coords = destination_coords
        self.velx = velocity_x
        self.vely = velocity_y

        self.decay = decay

        self.return_x = return_x
        self.return_y = return_y
        if return_x is None: self.return_x = -self.velx
        if return_y is None: self.return_y = -self.vely

    # .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .
    # This method is called to have the avatar loop through the animations of a given state ONCE and then return to the
    # previous state.
    def perform_animation(self, animation_state):
        self.play_action = True
        self.change_state(animation_state)

    # .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .
    def compute_moved_coordinates(self):

        goal_x = self.modified_coords[0] + self.velx
        goal_y = self.modified_coords[1] + self.vely
        self.velx *= self.decay
        self.vely *= self.decay

        # Account for potential overshoots
        if ((self.velx < 0) and (goal_x <= self.destination_coords[0])): goal_x = self.destination_coords[0]
        if ((self.velx > 0) and (goal_x >= self.destination_coords[0])): goal_x = self.destination_coords[0]
        if ((self.vely < 0) and (goal_y <= self.destination_coords[1])): goal_y = self.destination_coords[1]
        if ((self.vely > 0) and (goal_y >= self.destination_coords[1])): goal_y = self.destination_coords[1]

        # Account for bad coordinates given...
        if self.vely == 0:
            if self.destination_coords[1] > self.modified_coords[1]: self.vely += 1
            if self.destination_coords[1] < self.modified_coords[1]: self.vely -= 1
        if self.velx == 0:
            if self.destination_coords[0] > self.modified_coords[0]: self.velx += 1
            if self.destination_coords[0] < self.modified_coords[0]: self.velx -= 1

        self.modified_coords = (goal_x, goal_y)

        # If we reached the destination, return to base coords in the same animation state you were in.
        if goal_x == self.destination_coords[0] and goal_y == self.destination_coords[1]:

            # If we are home, zero out all this nonsense.
            if goal_x == self.base_coords[0] and goal_y == self.base_coords[1]:
                self.destination_coords = None
                self.override_state = 'Null'
                self.change_state(self.state)

            # If we were told to stay there for something reason, don't go back just yet-- if there's a script, stay.
            elif self.return_x == 0 and self.return_y == 0:
                pass

            # If we aren't come home.
            else:
                self.move(self.override_state, self.base_coords, self.return_x, self.return_y, decay=1/self.decay)

            if self.puppet: self.puppet_commands()

    # .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .
    def update_base_coords(self, new_tile):
        new_coords = new_tile.battle_coords
        self.tile = new_tile
        self.base_coords = new_coords
        self.modified_coords = self.base_coords
        self.destination_coords = None
        self.override_state = 'Null'
        self.change_state('IDLE')

    # .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .
    # This is the master driver for the avatar. It's effectively a mini-script that tells it exactly what to do.
    # I must reserve the possibility of it communicating with the master so it can inject commands into other avatars
    # so we can make them go flying or otherwise react to a script here.
    # We also need to have a way to ping this every time an animation sequence ends.
    #
    def puppet_commands(self, movement_script=None):

        # Update the script if one has been fed to us
        if movement_script is not None:
            self.puppet = True
            self.puppet_script = movement_script
            self.puppet_index = 0

        # Draw the current puppet command
        command_sequence = self.puppet_script[self.puppet_index]
        print command_sequence

        # Figure out which command it wants us to use
        method = getattr(self, command_sequence[0])
        kwargs = command_sequence[1]
        method(**kwargs)

        self.puppet_index += 1

        if self.puppet_index > len(self.puppet_script)-1:
            self.puppet = False
            self.puppet_script = []
            self.puppet_index = 0

        # First, let's decide on the format of the movement script. Obviously a list... but inside each entry...
        # [
        # ['ACTION_TYPE', {kwargs}],
        # ['ACTION_TYPE2', {kwargs}],
        #   ]
