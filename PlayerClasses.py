
# Generic Imports


# Project Specific Imports
from CharacterClass import Player
from AvatarClass import Avatar
from WeaponClass import *

class Matt(Player):

    def __init__(self):
        Player.__init__(self, name='Matt', hp_die=10, level=1, ac=['heavy', 16], stats=[16, 24, 12, 10, 16, 8], weakness=None,
                 resist=None, immune=None, icon='M')

        # Set up an avatar for visualization purposes
        self.avatar = Avatar(self, self.name, facing='LEFT')
        self.movement = 50
        self.weapon = Longsword()

        # Set up a list of 'powers' this character has by building a menu tree
        self.menu_tree = {
            'Actions': ['Weapon Attack', 'Dash', 'Cast Spell'],
            'Bonus Actions': ['Derp', 'Offhand Attack'],
            'Setup Reactions': ['Ready Attack'],
        }

        self.spell_list = {
            0: ['Firebolt'],
            1: ['Bless'],
            2: ['Acid Arrow'],
            3: ['Fireball']
        }

        self.spell_slots = {
            0: None,
            1: [4, 4],
            2: [3, 3],
            3: [2, 2]
        }



class TestDummy(Player):

    def __init__(self):
        Player.__init__(self, name='TestDummy', hp_die=10, level=1, ac=['heavy', 16], stats=[16, 1, 12, 10, 16, 8],
                        weakness=None,
                        resist=None, immune=None, icon='M')

        self.avatar = Avatar(self, self.name)
        self.movement = 30
        self.weapon = Dagger()

        # Set up a list of 'powers' this character has by building a menu tree
        self.menu_tree = {
            'Actions': ['Weapon Attack', 'Dash'],
            'Bonus Actions': ['Derp', 'Offhand Attack'],
            'Setup Reactions': ['Ready Attack'],
        }

        self.spell_list = {}

