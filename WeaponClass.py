# Generic Imports
import numpy.random as rand

# Project Specific Imports

# ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~
class Weapon(object):

    def __init__(self, name, die_num, weapon_die, reach, bonus_stat, damage_type, magic=False, tags=None):

        self.name = name
        self.die_num = die_num
        self.weapon_die = weapon_die
        self.reach = reach
        self.bonus_stat = bonus_stat
        self.damage_type = damage_type
        self.magic = magic
        self.tags = tags

        if tags == None: self.tags = []

    # .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .     .
    def RollDamage(self):

        total_damage = 0

        for i in xrange(0, self.die_num):
            total_damage += rand.randint(1, self.weapon_die+1)

        return total_damage

# ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~
class Longsword(Weapon):

    def __init__(self):

        Weapon.__init__(self, 'Longsword', 1, 8, 1, 'str', 'slashing')

# ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~
class Dagger(Weapon):

    def __init__(self):

        Weapon.__init__(self, 'Dagger', 1, 4, 1, 'fin', 'piercing', tags=['throwable'])

class Fists(Weapon):

    def __init__(self):

        Weapon.__init__(self, 'Fists', 1, 1, 1, 'str', 'bludgeoning')




# ==================================================================================================================== #
#  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  - #
# ==================================================================================================================== #
#  DEBUG ZONE     DEBUG ZONE     DEBUG ZONE     DEBUG ZONE     DEBUG ZONE     DEBUG ZONE     DEBUG ZONE     DEBUG ZONE #
# ==================================================================================================================== #
#  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  - #
# ==================================================================================================================== #

if __name__ == "__main__":

    a = Longsword()
    print a.RollDamage()