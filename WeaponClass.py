class Weapon(object):

    def __init__(self, name, die_num, weapon_die, range, bonus_stat, damage_type, magic=False, tags=None):

        self.name = name
        self.die_num = die_num
        self.weapon_die = weapon_die
        self.range = range
        self.bonus_stat = bonus_stat
        self.damage_type = damage_type
        self.magic = magic
        self.tags = tags

        if tags == None: self.tags = []
