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

    def __init__(self, name, scale=2):

        pygame.sprite.DirtySprite.__init__(self)

        self.name = name
        self.state = 'IDLE'
        self.override_state = 'Null'
        self.scale = scale

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

        # set up the default animations
        self.animation_series = self.idle_sprites
        self.frame = 0; self.max_frame = len(self.animation_series)-1
        self.facing = 1
        self.image = self.animation_series[0]
        self.rect = self.image.get_rect()
        self.dirty = 1

        self.image.set_alpha(50)

    def update(self):
        self.frame += 1
        if self.frame > self.max_frame: self.frame = 0
        self.image = self.animation_series[self.frame]


        if self.destination_coords:
            self.compute_moved_coordinates()
            if self.velx > 0:
                self.image = pygame.transform.flip(self.image, True, False)
        else:
            self.modified_coords = self.base_coords

        self.rect = self.image.get_rect()
        self.rect.center = (self.modified_coords)
        self.dirty = 1

        colorkey = self.image.get_at((0, 0))
        self.image.set_colorkey(colorkey, RLEACCEL)

    def check_state(self):
        pass

    def change_state(self, new_state):

        if new_state == 'IDLE': self.animation_series = self.idle_sprites
        if new_state == 'RUN': self.animation_series = self.run_sprites
        # Update the index information about the new animation series
        self.frame = 0; self.max_frame = len(self.animation_series)-1

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

        # If we reached the destination, return to base coords in the same animation state you were in. If we are home,
        # zero out all this nonsense.
        if goal_x == self.destination_coords[0] and goal_y == self.destination_coords[1]:
            if goal_x == self.base_coords[0] and goal_y == self.base_coords[1]:
                self.destination_coords = None
                self.override_state = 'Null'
                self.change_state(self.state)

            else:
                self.move(self.override_state, self.base_coords, self.return_x, self.return_y, decay=1/self.decay)

    def home(self):
        pass
