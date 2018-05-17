# Generic Imports
import numpy.random as rand

# Project Imports
from CharacterSupport import *
from WeaponClass import Weapon

class Character(object):

    def __init__(self, level=1, hp=1, stats=[10, 10, 10, 10, 10, 10], ac=['light', 10], weakness=None,
                 resist=None, immune=None, actions=None, saves=None):

        self.name = 'Placeholder'
        self.hp_cur = hp
        self.hp_max = hp
        self.level = level
        self.base_str = stats[0]
        self.base_dex = stats[1]
        self.base_con = stats[2]
        self.base_int = stats[3]
        self.base_wis = stats[4]
        self.base_cha = stats[5]
        self.ac_params = ac

        self.weakness = weakness
        self.resist = resist
        self.immune = immune
        self.actions = actions

        if self.weakness is None: self.weakness = []
        if self.resist is None: self.resist = []
        if self.immune is None: self.immune = []
        if self.actions is None: self.actions = ['Basic_Attack']

        self.weapon = Weapon('Fists', 1, 1, 'Close', 0, 'Bludgeoning')

        # Combat Stat boni
        self.ac_bonus = 0
        self.str_bonus = 0
        self.dex_bonus = 0
        self.con_bonus = 0
        self.int_bonus = 0
        self.wis_bonus = 0
        self.cha_bonus = 0

        self.temp_checks = [self.ac_bonus, self.str_bonus, self.dex_bonus, self.con_bonus, self.int_bonus, self.wis_bonus,
               self.cha_bonus]

        self.weakness_bonus = []
        self.resist_bonus = []

        # These are all one-turn effects
        self.dodge = 0
        self.exposed = 0
        self.stealth = 0
        self.marked = 0
        self.constrict = 0
        self.buffs = [self.dodge, self.exposed, self.stealth, self.marked, self.constrict]

        self.str = self.base_str + self.str_bonus
        self.dex = self.base_dex + self.dex_bonus
        self.con = self.base_con + self.con_bonus
        self.int = self.base_int + self.int_bonus
        self.wis = self.base_wis + self.wis_bonus
        self.cha = self.base_cha + self.cha_bonus
        self.stats = [self.str, self.dex, self.con, self.int, self.wis, self.cha]

        self.saves = saves
        if self.saves is None: self.saves = []

        # Compute AC
        if ac[0] == 'light': self.base_ac = ac[1] + bonus_table[self.base_dex]
        if ac[0] == 'medium': self.base_ac = ac[1] + min(bonus_table[self.base_dex], 2)
        if ac[0] == 'heavy': self.base_ac = ac[1]
        self.ac = self.base_ac

        # Finally, game related parameters and objects.
        self.alive = 1
        self.death_quip = None
        self.death_saves = 0
        self.death_fails = 0

        # Set up battle related stats
        self.movement = 30
        self.max_movement = 30

        # These are all the game-state related locations they can exist on.
        self.battlefield = None
        self.map = None

    # ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~
    # Attack using equipped weapon
    def Weapon_Attack(self, roll=None, roll_mod=0, damage_mod=0, advantage=0, query=False):

        if query:
            return {'target': 'enemy', 'shape': 'single', 'range': 'weapon', 'direction': 'line_of_sight'}

        bonus_stat = getattr(self, self.weapon.bonus_stat)
        weapon_stat_bonus = bonus_table[bonus_stat]

        # Compute the attack roll
        to_hit_base = 0
        if roll:
            to_hit_base = roll
        elif advantage == 1:
            to_hit_base = max(rand.randint(20)+1, rand.randint(20)+1)
        elif advantage == 0:
            to_hit_base = rand.randint(20)+1
        elif advantage == -1:
            to_hit_base = min(rand.randint(20)+1, rand.randint(20)+1)
        elif not roll:
            to_hit_base = 0

        # Initialize damage
        weapon_damage = self.weapon.RollDamage()

        if to_hit_base == 20: weapon_damage += self.weapon.RollDamage(); to_hit_base = 99
        if to_hit_base == 1: to_hit_base = -99

        # Compute the final to-hit and damage rolls
        damage = weapon_damage + weapon_stat_bonus + damage_mod
        to_hit = to_hit_base + roll_mod + weapon_stat_bonus + level_bonus_table[self.level]

        return to_hit, damage

    # ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~
    # Roll to see what happens first
    def Roll_Initiative(self, advantage=0):
        if advantage == 1:
            self.initiative = max(rand.randint(20)+1 + bonus_table[self.dex], rand.randint(20)+1 + bonus_table[self.dex])
        elif advantage == 0:
            self.initiative = self.initiative = rand.randint(20)+1 + bonus_table[self.dex]
        else:
            self.initiative = min(rand.randint(20)+1 + bonus_table[self.dex], rand.randint(20)+1 + bonus_table[self.dex])
        return self.initiative

    # ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~
    # Roll to see if you make a saving throw
    def Roll_Save(self, stat, advantage=0, type=0):

        save_bonus = 0
        stat_value = getattr(self, stat)
        if self.saves[type]: save_bonus = level_bonus_table[self.level]

        if advantage == 1:
            save = max(rand.randint(20)+1 + bonus_table[stat_value], rand.randint(20)+1 + bonus_table[stat_value])
        elif advantage == 0:
            save = rand.randint(20)+1 + bonus_table[stat_value]
        else:
            save = min(rand.randint(20)+1 + bonus_table[stat_value], rand.randint(20)+1 + bonus_table[stat_value])
        return save + save_bonus

    # ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~
    # Perform an arbitrary check
    def Skill_Check(self, stat, advantage=0, bonus=0):
        stat_value = getattr(self, stat)
        if advantage == 1:
            save = max(rand.randint(20)+1 + bonus_table[stat_value], rand.randint(20)+1 + bonus_table[stat_value])
        elif advantage == 0:
            save = rand.randint(20)+1 + bonus_table[stat_value]
        else:
            save = min(rand.randint(20)+1 + bonus_table[stat_value], rand.randint(20)+1 + bonus_table[stat_value])
        return save + bonus

    # ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~
    # Change to the front/back row of the battlefield
    def Swap_Row(self, debug=False, text_buffer=None):
        if self.row == 'Front':
            self.row = 'Back'
        else:
            self.row = 'Front'
        text_buffer.append("%s deftly changes position!" % self.name)
        if debug: print text_buffer[-1]

    # ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~
    # Control the processes involved in taking damage
    def TakeDamage(self, damage, damage_type, magical_damage=False, debug=False):

        if damage_type in self.weakness: damage *= 2
        if damage_type in self.resist: damage *= .5
        if damage_type in self.immune: damage = 0
        if 'mundane' in self.resist and not magical_damage: damage *= .5

        if self.hp_cur > 0:
            self.hp_cur -= int(damage)
            if self.hp_cur <= 0:
                if self.type == 'Character':
                    self.hp_cur = -1
                    self.alive = 0
                elif self.type == 'Monster':
                    self.alive = -1
                    self.hp_cur = -1
                    if self.death_quip: pass
        else:
            self.DeathSavingThrow(roll=1, debug=debug)
            return

        # If this was healing, reset death saves if needed.
        if damage < 0: self.death_fails = 0

    # ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~
    # Death Saving Throws and whatnot
    def DeathSavingThrow(self, roll=None, debug=False):

        if roll is None: roll = rand.randint(20)+1

        if roll == 1:
            self.death_fails += 2
        elif roll == 20:
            self.death_fails = 0; self.death_saves = 0
            self.alive = 1
            self.hp_cur = 1
        elif roll < 11:
            self.death_fails += 1
        elif roll > 10:
            self.death_saves += 1

        if self.death_fails >= 3:
            self.alive = -1
            self.icon = 'X'
            if self.death_quip: pass

        if self.death_saves >= 3:
            self.hp_cur = 1

    # ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~
    # This is more useful for debugging than anything in game
    def StatusDump(self, full=False, text_buffer=None):
        hp_bit = "%s/%s" % (self.hp_cur, self.hp_max)

        if self.alive != -1:
            print_string = "HP: %s/%s\n" % (self.hp_cur, self.hp_max) + ' '*(8-len(hp_bit)) + "AC: %s" % (self.ac)
        else:
            print_string = "HP: X/%s\n" % (self.hp_max) + ' '*(8-len(hp_bit)) + "AC: %s" % (self.ac)

        if full:
            str = dex = int = con = wis = cha = ''
            if self.str_bonus != 0: str = '+%s' % self.str_bonus
            if self.dex_bonus != 0: dex = '+%s' % self.dex_bonus
            if self.int_bonus != 0: int = '+%s' % self.int_bonus
            if self.con_bonus != 0: con = '+%s' % self.con_bonus
            if self.wis_bonus != 0: wis = '+%s' % self.wis_bonus
            if self.cha_bonus != 0: cha = '+%s' % self.cha_bonus
            print_string += "STR:%s%s    DEX:%s%s     INT:%s%s\nCON:%s%s    WIS:%s%s     CHA:%s%s" % (self.base_str, str, self.base_dex, dex, self.base_int, int, self.base_con, con, self.base_wis, wis, self.base_cha, cha)

        if text_buffer: return print_string
        else: print print_string

    # ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~
    # Why did I call it pretty?
    def PrettyStatusDump(self, full=False, text_buffer=None):

        hp_bit = "{0:>3.0f}/{1:<3.0f}".format(self.hp_cur, self.hp_max)
        if self.alive != -1:
            print_string = "HP: %s" % (hp_bit) + "AC: {0:>2.0f}".format(self.ac)
        else:
            print_string = "HP:   X/{0:<3.0f}".format(self.hp_max) + "AC: {0:>2.0f}\n".format(self.ac)

        count = 0
        if full:
            if self.str_bonus != 0: print_string += ' STR:{:<2.0f}+{:<2.0f}'.format(self.base_str, self.str_bonus); count += 1
            if self.dex_bonus != 0: print_string += ' DEX:{:<2.0f}+{:<2.0f}'.format(self.base_dex, self.dex_bonus); count += 1
            if self.int_bonus != 0: print_string += ' INT:{:<2.0f}+{:<2.0f}'.format(self.base_int, self.int_bonus); count += 1
            if count == 3: print_string += '\n'; count = 0
            if self.con_bonus != 0: print_string += ' CON:{:<2.0f}+{:<2.0f}'.format(self.base_con, self.con_bonus); count += 1
            if count == 3: print_string += '\n'; count = 0
            if self.wis_bonus != 0: print_string += ' WIS:{:<2.0f}+{:<2.0f}'.format(self.base_wis, self.wis_bonus); count += 1
            if count == 3: print_string += '\n'; count = 0
            if self.cha_bonus != 0: print_string += ' CHA:{:<2.0f}+{:<2.0f}'.format(self.base_cha, self.cha_bonus); count += 1

        if text_buffer: return print_string
        else: print print_string

    # ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~
    # Checks for the start of the turn
    def StartTurn(self, debug=False):

        # Iterate through stat buff/debuffs and update them
        for item in self.temp_checks:
            if item > 0: item -= 1
            if item < 0: item += 1

        self.str = self.base_str + self.str_bonus
        self.dex = self.base_dex + self.dex_bonus
        self.con = self.base_con + self.con_bonus
        self.int = self.base_int + self.int_bonus
        self.wis = self.base_wis + self.wis_bonus
        self.cha = self.base_cha + self.cha_bonus
        self.stats = [self.str, self.dex, self.con, self.int, self.wis, self.cha]

        # Recompute AC as needed
        if self.ac_params[0] == 'light': self.ac = self.ac_params[1] + bonus_table[self.dex]
        if self.ac_params[0] == 'medium': self.ac = self.ac_params[1] + max(bonus_table[self.dex], 2)
        if self.ac_params[0] == 'heavy': self.ac = self.ac_params[1]
        self.weapon_stat = bonus_table[self.str]

        for item in self.weakness_bonus:
            if item[0] > 0:
                item[0] -= 1
                if item[0] == 0:
                    self.weakness_bonus.pop(item)

        for item in self.resist_bonus:
            if item[0] > 0:
                item[0] -= 1
                if item[0] == 0:
                    self.resist_bonus.pop(item)

        # Buffs and debuffs increment
        for status in self.buffs:
            if status != 0: status -= 1

        if self.constrict:
            self.hp_cur -= 2

        # Death Check
        if self.hp_cur <= 0 and self.alive == 0:
            self.alive = 0
            self.DeathSavingThrow(debug=debug)
        elif self.alive == -1:
            pass

# ==================================================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #
# Special Super-versions (Characters and Monsters)
# -------------------------------------------------------------------------------------------------------------------- #
# ==================================================================================================================== #

class Player(Character):
    def __init__(self, name='Default', level=1, hp_die=8, ac=['light', 10], stats=[16, 10, 12, 16, 10, 8], weakness=None,
                 resist=None, immune=None, icon='?', xp_total=0):

        Character.__init__(self, level=level, stats=stats, ac=['light', 10], weakness=weakness, resist=resist, immune=immune)

        # Bind the specialized values to self
        self.name = name
        self.hp_die = hp_die
        self.ac_params = ac
        self.icon = icon
        self.original_icon = icon
        self.xp_total = 0

        # Start HP off
        hp = hp_die + bonus_table[self.base_con]
        if self.level > 1:
            for i in xrange(1, self.level):
                hp += (hp_die / 2) + 1 + bonus_table[self.base_con]
        self.hp_die = hp_die
        self.hp_cur = hp
        self.hp_max = hp
        self.type = 'Character'

        self.prompt_string = 'DEFAULT: THIS MUST BE SET UNDER PLAYABLE CHARACTERS'

    # ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~
    def ChooseAction(self, debug=False, text_buffer=None, action_input=None):

        valid_input = False
        while not valid_input:

            if not action_input: input = raw_input(self.prompt_string + '>>>')
            else: input = action_input

            try:
                # User done goofed
                if input == '# help':
                    print "Whoops! I meant the number of the action you were trying to use!"

                # User is requesting more information on an ability
                elif 'help' in input:
                    input = int(input.split()[0])
                    selected_action = self.actions[input-1]
                    print selected_action
                    method = getattr(self, selected_action)
                    method(debug=debug, text_buffer=text_buffer, help=True)

                # User is using an ability with a target
                elif ' ' in input:
                    action = int(input.split()[0])
                    selected_action = self.actions[action-1]
                    target = self.battlefield.find_target(input.split()[1])
                    if not target: continue
                    kwargs = {'target': target, 'debug':debug, 'text_buffer': text_buffer}
                    if selected_action == 'Weapon_Attack':
                        advantage = self.battlefield.adjudicate_attack(self, target)
                        kwargs['advantage'] = advantage
                    method = getattr(self, selected_action)
                    method(**kwargs)
                    valid_input = True
                else:
                    input = int(input)
                    kwargs = {'debug': debug, 'text_buffer': text_buffer}
                    selected_action = self.actions[input-1]
                    print selected_action
                    method = getattr(self, selected_action)
                    method(**kwargs)
                    valid_input = True
            except:
                print "\n...I didn't quite understand that. Try using the form: "

            if action_input:
                return valid_input


class Monster(Character):
    def __init__(self, species='Default', name=None, level=1, hp=1, ac=['light', 10], stats=[10, 10, 10, 10, 10, 10], weakness=None,
                 resist=None, immune=None, actions=None, action_weights=None, saves=None, row='Front', icon='?', xp=1):

        Character.__init__(self, level=level, hp=hp, ac=ac, stats=stats, weakness=weakness, resist=resist, immune=immune, actions=actions, saves=saves)
        self.icon = icon
        self.row = row
        self.species = species
        self.name = name
        self.type = 'Monster'
        self.xp = xp

        # This section handles the action section
        self.actions = actions
        self.action_weights = action_weights
        self.action_deck = []
        for i, entry in enumerate(self.actions): self.action_deck += [entry] * self.action_weights[i]

        if self.name is None: self.name = self.species

    # ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~
    # This is the algorithm which determines how the enemies react. It isn't much to look at right now.
    # In certain intelligent monsters, this is overriden in the specific monster class with something heartier.
    def ChooseAction(self, debug=False, text_buffer=None):

        # Default to an Attack
        selected_action = 'Weapon_Attack'
        kwargs = {'debug': debug, 'text_buffer': text_buffer}

        # Test to see if intelligence dictates special behavior. Otherwise, do as you would normally.
        special_action, special_kwargs = self.SpecialChooseAction(debug=debug)
        if special_action:
            selected_action = special_action
            kwargs = special_kwargs

        # This controls how the randomly selected actions perform.
        else:

            action_index = rand.randint(0, len(self.action_deck))
            selected_action = self.action_deck[action_index]

            # Perform the action recommended. Melee Attackers will ALWAYS choose the nearest targets unless otherwise guided
            if '_Attack' in selected_action:

                valid_target = False
                num_loops = 0
                while not valid_target:
                    if self.weapon.range == 'Close':
                        targets = self.battlefield.nearest_creatures(self)
                    else:
                        targets = []
                        for person in self.battlefield.party:
                            if person.alive != -1: targets.append(person)

                    if len(targets) > 1:
                        target = targets[rand.randint(len(targets))]
                    else:
                        target = targets[0]

                    if target.alive != -1: valid_target = True
                    else: num_loops += 1
                    if num_loops > 4: valid_target = True

                # Calculated advantage for the attack
                advantage = self.battlefield.adjudicate_attack(self, target)

                # Override for marked targets
                for person in self.battlefield.party:
                    if person.marked:
                        text_buffer.append('%s is compelled to attack %s by their mark!' % (self.name, person.name))
                        target = person
                        if advantage == -1: advantage = 0

                # Override for ineffectual weapon range
                if advantage == -999: selected_action = 'Swap_Row'
                else: kwargs = {'target': target, 'advantage': advantage, 'debug': debug, 'text_buffer': text_buffer}

            # if debug: print selected_action
            # if debug: print kwargs

            method = getattr(self, selected_action)
            method(**kwargs)


    # ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~   ~
    # This is a placeholder method that is overwritten by the specific monster class if they have any smarter than
    # random behaviors.
    def SpecialChooseAction(self, debug=False):
        return None, {}