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

        Spell.__init__(self, 'Fireball', caster, 'INT', 'Instantaneous')
        self.level = level

    def setup_avatar(self, master, source_tile, end_tile):
        self.avatar = FireballAvatar(master, source_tile, end_tile)

    def query(self):
        return {'target': 'tile', 'shape': 'splash5', 'range': 5, 'direction': 'line_of_sight',
                'attack_type': 'save', 'type': 'spell'}

    def resolve(self, targets):

        damage = dice_reader_plus('8d6+0')
        full_damage_list = []

        for target in targets:
            save_roll = target.Roll_Save('DEX', advantage=0, type=1)
            if save_roll >= self.DC: target.TakeDamage(damage/2, 'Fire', magical_damage=True); full_damage_list.append(0)
            else: target.TakeDamage(damage, 'Fire', magical_damage=True); full_damage_list.append(1)

        return_dict = {'damage_type': 'Fire', 'full_damage': damage, 'half_damage': damage / 2, 'report': full_damage_list}
        return return_dict

class FireballAvatar(pygame.sprite.DirtySprite):

    def __init__(self, master, source_tile, end_tile):
        pygame.sprite.DirtySprite.__init__(self)
        self.master = master
        self.fireball_projectile_sprites = sprite_sheet((32, 32), str(os.path.join('SpellGraphics', 'FireballProjectile.png')).strip())
        self.fireball_explosion_sprites = sprite_sheet((160, 160), str(os.path.join('SpellGraphics', 'FireballExplosion.png')).strip())

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

        if self.form == 'Projectile':
            if self.frame > self.max_frame: self.frame = 0
            self.image = self.fireball_projectile_sprites[self.frame]

            # Update the center
            self.rect = self.image.get_rect()
            self.rect.center = (self.center_coords[0] + self.vel_x, self.center_coords[1] + self.vel_y)

            # Update to the next form when we get to the target tile
            if self.rect.center[0] >= self.end_tile.rect.center[0] or self.rect.center[1] >= self.end_tile.rect.center[1]:
                self.form = 'Fireball'
                self.frame = -1

        else:
            if self.frame > self.max_frame:
                self.delete()
                return

            self.image = self.fireball_projectile_sprites[self.frame]
            self.rect = self.image.get_rect()
            self.rect.center = self.end_tile.rect.center

    def delete(self):
        self.master.change_sprites([self], 'avatar_sprites', add=False)










