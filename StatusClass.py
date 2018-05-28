# Generic Imports
import pygame
from pygame.locals import *
from math import sqrt

# Project Specific Imports
from Config import *
from TileEngine import sprite_sheet
from Utilities import movement_cost_compute

icon_size = 8
offset = 2

def setup_status():

    status_dict = {
        # Regular Buffs
        'dodge': 0,
        'stealth': 0,

        # Spell Buffs
        'bless': 0,

        # Regular Debuffs
        'prone': 0,

        # Spell Debuffs
    }
    return status_dict

class StatusOverlay():

    def __init__(self, character):

        self.character = character
        self.sprites = []
        if self.character.avatar: self.update_active_icons()

    def update_coordinates(self):
        for sprite in self.sprites: sprite.update()

    def update_active_icons(self):

        scale = self.character.avatar.battlefield.scale

        self.character.avatar.battlefield.change_sprites(self.sprites, 'overlay', add=False)
        self.sprites = []
        active_keys = []

        # Figure out how many keys are active and arrange the status icons appropriately from this number
        for status_key in self.character.status_dict:
            if self.character.status_dict[status_key]:
                print status_key
                active_keys.append(status_key)

        # Calculate the initial offset and the offset per icon
        initial_offset = -(len(active_keys)/2 * icon_size*scale + offset*scale) + offset*scale
        if len(active_keys) == 1: initial_offset = 0
        increment = (offset*scale + icon_size*scale)

        for i, key in enumerate(active_keys):

            sprite_icon = os.path.join('StatusGraphics', key+'Icon.png')
            self.sprites.append(StatusIcon(self, self.character.avatar.battlefield, sprite_icon, key, horizontal_offset=initial_offset+(i*increment)))

        self.character.avatar.battlefield.change_sprites(self.sprites, 'overlay', add=True)

class StatusIcon(pygame.sprite.DirtySprite):

    def __init__(self, manager, master, icon_sprite, icon_status, horizontal_offset=0):

        print horizontal_offset

        self.manager = manager
        self.master = master
        self.icon_status = icon_status
        self.horizontal_offset = horizontal_offset
        self.layer = 4
        self.dirty = 1

        pygame.sprite.DirtySprite.__init__(self)
        self.sprite = sprite_sheet((icon_size, icon_size), icon_sprite.strip(), scale=master.scale)[0]
        self.image = self.sprite
        self.rect = self.image.get_rect()
        base_center = self.manager.character.avatar.tile.battle_coords
        vertical_offset = self.manager.character.avatar.size[0] * self.manager.character.avatar.scale * .6
        self.rect.center = (base_center[0] + self.horizontal_offset, base_center[1] - vertical_offset)

    def update(self):

        base_center = self.manager.character.avatar.rect.center
        vertical_offset = self.manager.character.avatar.size[0] * self.manager.character.avatar.scale * .6
        new_center = (base_center[0] + self.horizontal_offset, base_center[1] - vertical_offset)

        if new_center != self.rect.center:
            self.dirty = 1
            self.rect.center = new_center

