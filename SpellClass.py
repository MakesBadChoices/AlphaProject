# Generic Imports
import pygame
from math import sqrt
from pygame.locals import *

# Project Specific Imports
from Config import *
from CharacterSupport import *
from TileEngine import sprite_sheet

# ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~
class Spell(object):

    def __init__(self, name, caster, primary_stat, duration):

        self.name = name
        self.caster = caster
        self.primary_stat = primary_stat
        self.duration = duration

        self.DC = 8 + bonus_table[getattr(self.caster, self.primary_stat)]
        self.attack_bonus = bonus_table[getattr(self.caster, self.primary_stat)] + level_bonus_table[caster.level]

# ==================================================================================================================== #
# SPELL LIST
# ==================================================================================================================== #

class Fireball(Spell):

    def __init__(self, caster, level=3):

        Spell.__init__(self, 'Fireball', caster, 'int', 'Instantaneous')
        self.level = level
        self.target_dictionary = {'target': 'tile', 'shape': 'splash5', 'range': 10, 'direction': 'line_of_sight',
                'attack_type': 'save', 'type': 'spell'}

    def setup_avatar(self, master, source_tile, end_tile):
        self.avatar = FireballAvatar(master, source_tile, end_tile)
        master.change_sprites([self.avatar], 'effect_sprites', add=True)

    def query(self):
        return self.target_dictionary

    def resolve(self, tile, master):

        targets = []
        damage = dice_reader_plus('8d6+0')

        origin_x = tile.gridx
        origin_y = tile.gridy
        delta_value = int(self.target_dictionary['shape'].split('splash')[1])

        for j in xrange(origin_y - delta_value, origin_y + delta_value + 1):
            for i in xrange(origin_x - delta_value, origin_x + delta_value + 1):
                # if i == 0 and j == 0: continue
                if abs(i-origin_x) + abs(j-origin_y) > delta_value: continue
                splash_tile = master.give_target_tile(0, 0, i, j)
                if splash_tile is not None and splash_tile.occupant is not None:
                    targets.append(splash_tile.occupant)

        for target in targets:
            save_roll = target.Roll_Save('dex', advantage=0)
            if save_roll >= self.DC: target.TakeDamage(40, damage/2, 'Fire', magical_damage=True);
            else: target.TakeDamage(40, damage, 'Fire', magical_damage=True);


class FireballAvatar(pygame.sprite.DirtySprite):

    def __init__(self, master, source_tile, end_tile):
        pygame.sprite.DirtySprite.__init__(self)
        self.master = master
        self.source_tile = source_tile
        self.end_tile = end_tile

        self.fireball_projectile_sprites = sprite_sheet((32, 32), str(os.path.join('SpellGraphics', 'FireballProjectile.png')).strip(), scale=master.scale)
        self.fireball_explosion_sprites = sprite_sheet((160, 160), str(os.path.join('SpellGraphics', 'FireballExplosion.png')).strip(), scale=master.scale)
        self.current_state = 1
        self.frame = 0
        self.max_frame = len(self.fireball_projectile_sprites) - 1

        self.dirty = 1
        self.layer = 4

        self.image = self.fireball_projectile_sprites[0]
        self.rect = self.image.get_rect()
        self.rect.center = self.source_tile.rect.center

        self.form = 'Projectile'
        self.source_tile = source_tile
        self.end_tile = end_tile

        # Speed in pixels
        spell_velocity = 50.0
        delta_x = self.end_tile.rect.center[0] - self.source_tile.rect.center[0]
        delta_y = self.end_tile.rect.center[1] - self.source_tile.rect.center[1]
        distance = sqrt(delta_x**2 + delta_y**2)
        time_steps = distance / spell_velocity
        self.vel_x = delta_x / time_steps
        self.vel_y = delta_y / time_steps
        self.center_coords = self.rect.center

    def update(self):

        self.frame += 1
        self.dirty = 1

        print self.rect.center

        if self.form == 'Projectile':
            if self.frame > self.max_frame: self.frame = 0
            self.image = self.fireball_projectile_sprites[self.frame]

            # Update the center
            self.rect = self.image.get_rect()
            self.rect.center = (self.center_coords[0] + self.vel_x, self.center_coords[1] + self.vel_y)
            self.center_coords = self.rect.center

            # Update to the next form when we get to the target tile
            if (self.vel_x > 0 and self.rect.center[0] >= self.end_tile.rect.center[0])\
                    or (self.vel_y > 0 and self.rect.center[1] >= self.end_tile.rect.center[1])\
                    or (self.vel_x < 0 and self.rect.center[0] <= self.end_tile.rect.center[0])\
                    or (self.vel_y < 0 and self.rect.center[1] <= self.end_tile.rect.center[1]):
                self.form = 'Fireball'
                self.frame = -1
                self.max_frame = len(self.fireball_explosion_sprites) - 1

        else:
            if self.frame > self.max_frame:
                self.delete()
                return

            self.image = self.fireball_explosion_sprites[self.frame]
            self.rect = self.image.get_rect()
            self.rect.center = self.end_tile.rect.center

    def delete(self):
        self.master.change_sprites([self], 'avatar_sprites', add=False)










