
# Generic Imports
import pygame
from pygame.locals import *

# Project Specific Imports
from Config import *


class BattleMenu(pygame.sprite.DirtySprite):

    def __init__(self, master, center_coords, buttonList, background_image=GFX['MenuSprite'], base_menu=None):

        pygame.sprite.DirtySprite.__init__(self)

        self.master = master
        self.base_menu = base_menu
        self.layer = 2
        if self.base_menu is None: self.base_menu = self

        self.font = pygame.font.Font(FONTS['nintendo_nes_font'], 12)
        self.font_active = pygame.font.Font(FONTS['nintendo_nes_font'], 16)
        self.center_coords = center_coords
        self.background_image = background_image

        # Set up an internal state to keep track of which item is active
        self.active_selection_index = 0
        self.previous_active_selection_index = -1

        # Set up the spacing for individual options. The list is so the order is preserved (dictionaries be weird yo)
        slot_dict = {}
        slot_keys = []
        for i, button in enumerate(buttonList):
            slot_dict[button[0]] = {'x': 10,
                                    'y': (i * 20) + 10}
            slot_keys.append(button[0])

        self.slots = slot_dict
        self.slot_keys = slot_keys

        self.update()

    # .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .
    def update(self):

        # Mark menu as needing to be drawn
        if self.active_selection_index != self.previous_active_selection_index:

            # Increment the previous selection to now be the current one
            self.previous_active_selection_index = self.active_selection_index

            # Set up the background of the menu-box. Default size is 128x160 tall
            rect = self.background_image.get_rect()
            rect.center = self.center_coords
            surface = pygame.Surface(rect.size)
            surface.set_colorkey((0, 0, 0))
            surface.blit(self.background_image, (0, 0))

            for i, text in enumerate(self.slot_keys):

                if i == self.active_selection_index:
                    text_surface = self.font_active.render(text, True, (255, 255, 255))
                else:
                    text_surface = self.font.render(text, True, (1, 0, 0))

                text_rect = text_surface.get_rect(x=self.slots[text]['x'],
                                                  y=self.slots[text]['y'])
                surface.blit(text_surface, text_rect)

            # Set up the final secret ingredients
            self.image = surface
            self.rect = self.image.get_rect()
            self.rect.center = self.center_coords

            # Mark as needing to be redrawn
            self.dirty = 1

        else:
            pass

    # .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .
    def process_input(self, incoming_event):

        if incoming_event.type == KEYDOWN:
            # Left Arrow
            if incoming_event.key == 276: pass

            # Up Arrow
            if incoming_event.key == 273:
                self.active_selection_index -= 1
                if self.active_selection_index < 0: self.active_selection_index = len(self.slots) - 1

            # Right Arrow
            if incoming_event.key == 275: pass

            # Down arrow
            if incoming_event.key == 274:
                self.active_selection_index += 1
                if self.active_selection_index > len(self.slots) - 1: self.active_selection_index = 0

            # Enter Button or z (a) button
            if incoming_event.key == 13 or incoming_event.key == 122:

                descriptor_text = self.slot_keys[self.active_selection_index]

                # Should we spawn a sub-menu?
                if descriptor_text in ['Actions', 'Bonus Actions', 'Cast Spell', 'Setup Reactions']:

                    if descriptor_text == 'Cast Spell':
                        self.spawn_slave_menu(None, spellmode=True)
                    else:
                        buttonList = []
                        for i, entry in enumerate(self.master.current_creature.menu_tree[descriptor_text]):
                            buttonList.append((entry, i+1, None))
                        self.spawn_slave_menu(buttonList)

                # Enter move mode
                elif descriptor_text in ['Move']:
                    self.master.change_state('move_mode', True)

                # If it wasn't a basic option, test to see if the lookup of that item is another dictionary. If so,
                # those are now the new options.
                elif descriptor_text != 'End Turn':
                    self.engage_action(descriptor_text)

                elif descriptor_text == 'End Turn':
                    self.master.next_turn()

            # Back Button (x)
            if incoming_event.key == 120:
                if self.base_menu != self: self.delete()

    # .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .
    def spawn_slave_menu(self, buttonList, spellmode=False):

        menu_coords = (self.center_coords[0] + 150, self.center_coords[1])

        if spellmode:
            new_menu = SpellMenu(self.master, menu_coords, base_menu=self)
        else:
            new_menu = BattleMenu(self.master, menu_coords, buttonList, base_menu=self)
        # self.master.all_sprites.add(new_menu)
        self.master.change_sprites([new_menu], 'menu_sprites', add=True, layer=1)
        self.master.active_object = new_menu

    # .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .
    def engage_action(self, descriptor_text):
        self.delete()
        self.master.give_character_basic_command(self.master.current_creature, descriptor_text)

    # .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .
    def delete(self):
        self.master.active_object = self.base_menu
        self.master.change_sprites([self], 'menu_sprites', add=False, layer=1)
        self.dirty = 1

# ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~
class SpellMenu(pygame.sprite.DirtySprite):

    def __init__(self, master, center_coords, background_image=GFX['SpellMenuSprite'], base_menu=None):

        pygame.sprite.DirtySprite.__init__(self)

        self.master = master
        self.base_menu = base_menu
        self.layer = 2
        if self.base_menu is None: self.base_menu = self

        self.font = pygame.font.Font(FONTS['nintendo_nes_font'], 12)
        self.font_active = pygame.font.Font(FONTS['nintendo_nes_font'], 16)
        self.center_coords = center_coords
        self.background_image = background_image

        # Set up an internal state to keep track of which item is active
        self.active_selection_index = 1
        self.previous_active_selection_index = -1

        self.spell_level = 0
        spell_list, spell_text = self.get_spell_list(0)

        # Set up the spacing for individual options. The list is so the order is preserved (dictionaries be weird yo)
        slot_dict = {}
        slot_keys = []
        for i, button in enumerate([spell_text] + spell_list):
            slot_dict[button] = {'x': 10,
                                 'y': (i * 20) + 10}
            slot_keys.append(button)

        self.slots = slot_dict
        self.slot_keys = slot_keys

        self.update()

    # .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .
    def get_spell_list(self, level):
        caster = self.master.current_creature
        caster_spell_list = caster.spell_list[level]

        if level == 0: level_text = 'Cantrips'
        else: level_text = 'Level %i (%i/%i)' % (level, caster.spell_slots[level][0], caster.spell_slots[level][1])
        return caster_spell_list, level_text

    # .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .
    def update(self):

        # Mark menu as needing to be drawn
        if self.active_selection_index != self.previous_active_selection_index:

            # Increment the previous selection to now be the current one
            self.previous_active_selection_index = self.active_selection_index

            # Set up the background of the menu-box. Default size is 128x160 tall
            rect = self.background_image.get_rect()
            rect.center = self.center_coords
            surface = pygame.Surface(rect.size)
            surface.set_colorkey((0, 0, 0))
            surface.blit(self.background_image, (0, 0))

            for i, text in enumerate(self.slot_keys):

                if i == self.active_selection_index:
                    text_surface = self.font_active.render(text, True, (255, 255, 255))
                else:
                    text_surface = self.font.render(text, True, (1, 0, 0))

                text_rect = text_surface.get_rect(x=self.slots[text]['x'],
                                                  y=self.slots[text]['y'])
                surface.blit(text_surface, text_rect)

            # Set up the final secret ingredients
            self.image = surface
            self.rect = self.image.get_rect()
            self.rect.center = self.center_coords

            # Mark as needing to be redrawn
            self.dirty = 1

        else:
            pass

    # .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .
    def process_input(self, incoming_event):

        if incoming_event.type == KEYDOWN:
            # Left Arrow
            if incoming_event.key == 276:
                self.spell_level -= 1
                if self.spell_level == -1: self.spell_level = self.master.current_creature.spell_list.keys()[-1]
                spell_list, spell_text = self.get_spell_list(self.spell_level)

                # Set up the spacing for individual options. The list is so the order is preserved (dictionaries be weird yo)
                slot_dict = {}
                slot_keys = []
                for i, button in enumerate([spell_text] + spell_list):
                    slot_dict[button] = {'x': 10,
                                         'y': (i * 20) + 10}
                    slot_keys.append(button)

                self.slots = slot_dict
                self.slot_keys = slot_keys

                self.active_selection_index = 1
                self.previous_active_selection_index = -1

            # Up Arrow
            if incoming_event.key == 273:
                self.active_selection_index -= 1
                if self.active_selection_index < 1: self.active_selection_index = len(self.slots) - 1

            # Right Arrow
            if incoming_event.key == 275:
                self.spell_level += 1
                if self.spell_level > self.master.current_creature.spell_list.keys()[-1]: self.spell_level = 0
                spell_list, spell_text = self.get_spell_list(self.spell_level)

                # Set up the spacing for individual options. The list is so the order is preserved (dictionaries be weird yo)
                slot_dict = {}
                slot_keys = []
                for i, button in enumerate([spell_text] + spell_list):
                    slot_dict[button] = {'x': 10,
                                         'y': (i * 20) + 10}
                    slot_keys.append(button)

                self.slots = slot_dict
                self.slot_keys = slot_keys

                self.active_selection_index = 1
                self.previous_active_selection_index = -1

            # Down arrow
            if incoming_event.key == 274:
                self.active_selection_index += 1
                if self.active_selection_index > len(self.slots) - 1: self.active_selection_index = 1

            # Enter Button or z (a) button
            if incoming_event.key == 13 or incoming_event.key == 122:

                if self.master.current_creature.spell_slots[self.spell_level][0] > 0:
                    self.master.current_creature.spell_slots[self.spell_level][0] -= 1
                    descriptor_text = self.slot_keys[self.active_selection_index]
                    self.engage_action(descriptor_text)

            # Back Button (x)
            if incoming_event.key == 120:
                if self.base_menu != self: self.delete()

    # .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .
    def spawn_slave_menu(self, buttonList):

        menu_coords = (self.center_coords[0] + 150, self.center_coords[1])
        image = self.background_image
        new_menu = BattleMenu(self.master, menu_coords, buttonList, image, base_menu=self)
        # self.master.all_sprites.add(new_menu)
        self.master.change_sprites([new_menu], 'menu_sprites', add=True, layer=1)
        self.master.active_object = new_menu

    # .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .
    def engage_action(self, descriptor_text):
        self.delete()
        self.master.cast_spell(self.master.current_creature, descriptor_text)

    # .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .
    def delete(self):
        self.master.active_object = self.base_menu
        self.master.change_sprites([self], 'menu_sprites', add=False, layer=1)
        self.dirty = 1



