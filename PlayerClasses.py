
# Generic Imports


# Project Specific Imports
from CharacterClass import Player
from AvatarClass import Avatar

class Matt(Player):

    def __init__(self):
        Player.__init__(self, name='Matt', hp_die=10, level=1, ac=['heavy', 16], stats=[16, 24, 12, 10, 16, 8], weakness=None,
                 resist=None, immune=None, icon='M')

        # Set up an avatar for visualization purposes
        self.avatar = Avatar(self.name, facing='LEFT')

        # Set up a list of 'powers' this character has by building a menu tree
        self.menu_tree = {
            'Actions': ['Weapon Attack', 'Dash', 'Cast Cantrip'],
            'Bonus Actions': ['Derp', 'Offhand Attack'],
            'Setup Reactions': ['Ready Attack'],
            'Cast Cantrip': ['Firebolt']
        }



class TestDummy(Player):

    def __init__(self):
        Player.__init__(self, name='TestDummy', hp_die=10, level=1, ac=['heavy', 16], stats=[16, 1, 12, 10, 16, 8],
                        weakness=None,
                        resist=None, immune=None, icon='M')

        self.avatar = Avatar(self.name)
