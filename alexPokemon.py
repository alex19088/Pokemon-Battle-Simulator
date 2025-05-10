import sqlite3
from typing import List, Tuple
from abc import ABC, abstractmethod
import random
from multipledispatch import dispatch
import inspect
import time
import pytest
from datetime import datetime

#from alexPokeObjs import random_accuracy, Move
import PokemonObjects5
import server


class DatabaseManager:
    def __init__(self, db_name='pokemon_battle.db'):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()

        # Players table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nickname TEXT NOT NULL,
            pokemon_name TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Battles table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS battles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            winner TEXT NOT NULL,
            duration_seconds INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Pokemon choices table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS pokemon_choices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            pokemon_name TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        self.conn.commit()

    def log_player(self, nickname: str, pokemon_name: str):
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO players (nickname, pokemon_name)
        VALUES (?, ?)
        ''', (nickname, pokemon_name))
        self.conn.commit()

    def log_battle(self, winner: str, start_time: datetime):
        duration = (datetime.now() - start_time).total_seconds()
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO battles (winner, duration_seconds)
        VALUES (?, ?)
        ''', (winner, int(duration)))
        self.conn.commit()

    def log_pokemon_choice(self, player_name: str, pokemon_name: str):
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO pokemon_choices (player_name, pokemon_name)
        VALUES (?, ?)
        ''', (player_name, pokemon_name))
        self.conn.commit()

    def close(self):
        self.conn.close()

class PhysicalStatus:
    def __init__(self, condition : str, turns_active : int, duration : int):
        self.condition = condition
        self.turns_active = turns_active # How long the status has been inflicted on the Pokemon
        self.duration = duration # How long the status is set to last (For confusion, barrier, etc.)

# Stat multiplier for Pokemon (eg. charizard's attack raised by 1.5x)
class Status:
    def __init__(self, atk_stage : float, def_stage : float, sp_atk_stage : float, sp_def_stage : float, speed_stage : float, physical_status: list[PhysicalStatus]):
        self.atk_stage = atk_stage
        self.def_stage = def_stage
        self.sp_atk_stage = sp_atk_stage
        self.sp_def_stage = sp_def_stage
        self.speed_stage = speed_stage
        self.physical_status = physical_status
    
    # Purpose: Applies a status boost
    def apply_stage_boost(self, user : any, stat: str, chance: int):
        # If it isn't in the move's effect_chance, no multiplier
        if PokemonObjects5.random_accuracy() > chance:
            return 1  

        if stat == "atk_stage" and self.atk_stage < 6:
            self.atk_stage += 1
            print(f"{user.name}'s Attack increased!")
            return get_stage_multiplier(self.atk_stage)
        elif stat == "def_stage" and self.def_stage < 6:
            self.def_stage += 1
            print(f"{user.name}'s Defense increased!")
            return get_stage_multiplier(self.def_stage)
        elif stat == "sp_atk_stage" and self.sp_atk_stage < 6:
            self.sp_atk_stage += 1
            print(f"{user.name}'s Special Attack increased!")
            return get_stage_multiplier(self.sp_atk_stage)
        elif stat == "sp_def_stage" and self.sp_def_stage < 6:
            self.sp_def_stage += 1
            print(f"{user.name}'s Special Defense increased!")
            return get_stage_multiplier(self.sp_def_stage)
        elif stat == "speed_stage" and self.speed_stage < 6:
            self.speed_stage += 1
            print(f"{user.name}'s Speed increased!")
            return get_stage_multiplier(self.speed_stage)

        return 1  
# use duck typing
    # Purpose: Applies a status debuff
    def apply_stage_debuff(self, target : any, stat: str, chance: int):
        # If it isn't in the move's effect_chance, no multiplier
        if PokemonObjects5.random_accuracy() > chance:
            return 1  

        if stat == "atk_stage" and self.atk_stage > -6:
            self.atk_stage -= 1
            print(f"{target.name}'s Attack fell!")
            return get_stage_multiplier(self.atk_stage)
        elif stat == "def_stage" and self.def_stage > -6:
            self.def_stage -= 1
            print(f"{target.name}'s Defense fell!")
            return get_stage_multiplier(self.def_stage)
        elif stat == "sp_atk_stage" and self.sp_atk_stage > -6:
            self.sp_atk_stage -= 1
            print(f"{target.name}'s Special Attack fell!")
            return get_stage_multiplier(self.sp_atk_stage)
        elif stat == "sp_def_stage" and self.sp_def_stage > -6:
            self.sp_def_stage -= 1
            print(f"{target.name}'s Special Defense fell!")
            return get_stage_multiplier(self.sp_def_stage)
        elif stat == "speed_stage" and self.speed_stage > -6:
            self.speed_stage -= 1
            print(f"{target.name}'s Speed fell!")
            return get_stage_multiplier(self.speed_stage)

        return 1

# Purpose: Formula for calculating the new multiplier of a pokemon's status
def get_stage_multiplier(stage: int) -> float:
    # For increasing a pokemon's stat
    if stage >= 0:
        return (2 + stage) / 2
    # For decreasing a pokemon's stat
    else:
        return 2 / (2 - stage)

# Types of pokemon (WIP, Make children for)
class Type():
    def __init__(self, type_name: str, strengths : list[str], weaknesses: list[str], resistances: list[str], immunities: list[str]):
        self.type_name = type_name
        self.strengths = strengths
        self.weaknesses = weaknesses
        self.resistances = resistances
        self.immunities = immunities


# Abstract class for moves (All moves will have these attributes, but perform a different task)
class Move(ABC):
    def __init__(self, name : str, type: Type, power: int, accuracy: int, effect_chance : float, status_effect : str, category : str):
        self.name = name
        self.type = type
        self.power = power
        self.accuracy = accuracy
        self.effect_chance = effect_chance
        self.status_effect = status_effect
        self.category = category

    @abstractmethod
    def use_move():
        return 120
    
    # overload

   # def use_move(self, target1, target2):


class Pokemon:
    def __init__(self, name: str, type1: Type, type2: Type, max_hp: int, hp: int, attack: int, defense: int,sp_attack : int, sp_defense : int, speed: int,
                 moves: List[Move], status: Status, legendary: bool, is_chosen: bool, has_moved : bool):
        self.name = name # The name of the Pokemon
        self.type1 = type1 # The first type of the pokemon
        self.type2 = type2 # The second type of the pokemon (May just have 1)
        self.max_hp = max_hp # The maximmum number of hitpoints the pokemon has/can have
        self._hp = hp # The number of hitpoints the pokemon has
        self._attack = attack # The attack points of the Pokemon
        self._defense = defense # The defense points of the Pokemon
        self._sp_attack = sp_attack # The special attack points of the Pokemon
        self._sp_defense = sp_defense # The special defense points of the Pokemon
        self._speed = speed # The speed of the Pokemon (Determines when the pokemon gets to use its move)
        self.moves = moves # The list of moves associated with the Pokemon
        self._status = status # The Status of the Pokemon (Physical or Stat Multipliers)
        self.legendary = legendary # If the pokemon is legendary (for the interface when the user is picking pokemon)
        self._is_chosen = is_chosen # If the pokemon is active in battle
        self.has_moved = has_moved # If the pokemon has already moved (For flinch)
    
    # For displaying a Pokemon's information
    def __repr__(self):
        return f"""
Name: {self.name}
Types: {self.type1.type_name}, {self.type2.type_name}
HP: {self._hp}/{self.max_hp}
Attack: {self._attack}
Defense: {self._defense}
Special Attack: {self._sp_attack}
Special Defense: {self.sp_defense}
Speed: {self.speed}
Moves learnt: {self.moves}
"""



    # Getter method for hitpoints
    @property
    def hp(self) -> int:
        return self._hp

    # Setter method for hitpoints
    @hp.setter
    def hp(self, updated_hp : int) -> None:
        self._hp = updated_hp

    # Getter method for attack
    @property
    def attack(self) -> int:
        return self._attack

    # Setter method for attack
    @attack.setter
    def attack(self, updated_attack : int) -> None:
        self._attack = updated_attack

    # Getter method for defense
    @property
    def defense(self) -> int:
        return self._defense

    # Setter method for defense
    @defense.setter
    def defense(self, updated_defense : int) -> None:
        self._defense = updated_defense

    # Getter method for sp_attack
    @property
    def sp_attack(self) -> int:
        return self._sp_attack

    # Setter method for sp_attack
    @sp_attack.setter
    def sp_attack(self, updated_sp_attack : int) -> None:
        self._sp_attack = updated_sp_attack

    # Getter method for sp_defense
    @property
    def sp_defense(self) -> int:
        return self._sp_defense

    # Setter method for sp_defense
    @sp_defense.setter
    def sp_defense(self, updated_sp_defense: int) -> None:
        self._sp_defense = updated_sp_defense

    # Getter method for speed
    @property
    def speed(self) -> int:
        return self._speed

    # Setter method for speed
    @speed.setter
    def speed(self, updated_speed : int) -> None:
        self._speed = updated_speed

    # Getter method for status
    @property
    def status(self) -> int:
        return self._status

    # Setter method for status
    @status.setter
    def status(self, updated_status : Status) -> None:
        self._status = updated_status

    # Getter method for is_chosen
    @property
    def is_chosen(self) -> bool:
        return self._is_chosen

    # Setter method for is_chosen
    @is_chosen.setter
    def is_chosen(self, updated_is_chosen : bool) -> None:
        self._is_chosen = updated_is_chosen




class Trainer:
    def __init__(self, trainer_id: int, trainer_name: str, active_pokemon: Move, trainer_pokemon: List[Pokemon]):
        self.trainer_id = trainer_id
        self.trainer_name = trainer_name
        self.active_pokemon = None # no active pokemon on initialization 
        self.trainer_pokemon = trainer_pokemon
        self.healthPotions = 2 # They will start with 2 health potions
        self.fullHeal = 1 # They will start with 1 full heal

    # Purpose: Determine if a trainer has at least one non-fainted Pokemon
    def has_usable_pokemon(self) -> bool:
        return any(pokemon._hp > 0 for pokemon in self.trainer_pokemon)


    


### CHRIS WORK ----------------------------------------------------

# UNFINISHED
# Purpose: Apply status effects to a pokemon at the start of a game turn 
def apply_status_effects_start(pokemon : Pokemon):
    for status in pokemon._status.physical_status:
        if status.condition == "Paralyzed":
            paralyzed(pokemon, status)
    
        
# Purpose: To apply paralyze to a pokemon
def paralyzed(pokemon : Pokemon, status : Status):
    # Prevents paralysis from being stacked multiple times
    if not status.turns_active:
        pokemon._speed *= 0.5
    
    status.turns_active += 1

    

# Purpose: Applying burn damage at the end of every turn
def burn_damage(pokemon : Pokemon):
    burn_dmg = pokemon.max_hp * 1/16
    pokemon._hp -= burn_dmg
    print(f"{pokemon.name} is hurt by its burn!")

# Purpose: Applying poison damage at the end of every turn
def poison_damage(pokemon : Pokemon, status : PhysicalStatus):
    # Poison damage increases every turn
    if status.turns_active == 0:
        poison_dmg = pokemon.max_hp * 1/8
        pokemon._hp -= poison_dmg
    elif status.turns_active == 1:
        poison_dmg = pokemon.max_hp * 1/4
        pokemon._hp -= poison_dmg
    elif status.turns_active == 2:
        poison_dmg = pokemon.max_hp * 3/8
        pokemon._hp -= poison_dmg
    elif status.turns_active == 3:
        poison_dmg = pokemon.max_hp * 1/2
        pokemon._hp -= poison_dmg
    else:
        poison_dmg = pokemon.max_hp * 5/8
        pokemon._hp -= poison_dmg
    print(f"{pokemon.name} is hurt by poison!")



list_of_queued_moves = []
# Purpose: Queues all of the trainers moves to the list of queued moves to be sorted
def queue_move(move, user : Pokemon, targets : list[Pokemon]):
    move_and_user = (move, user, targets)
    list_of_queued_moves.append(move_and_user)


# Purpose: Sorts the queued list of moves based on priority first, then user's speed
def sort_queued_list(queued_moves : list):
    queued_moves.sort(key=lambda move_and_user: (move_and_user[0].priority, move_and_user[1]._speed), reverse=True)

# Purpose: To make the pokemon use their moves 
def initiate_pokemon_moves(queued_moves : list):
    for move, user, targets in queued_moves:  # unpacking the tuples
        if user.hp <= 0:  # skip if pokemon is dead
            continue
        
        # Checking the # of parameters use_move has (Can attack multiple pokemon)
        move_params = inspect.signature(move.use_move).parameters 
        for target in targets:
            if target.hp > 0:  # only apply if the target is still alive

                if len(move_params) == 1:  # for no target moves 
                    move.use_move(user)
                    
                elif len(move_params) == 2:  # for single target moves
                    move.use_move(user, target)
                
                elif len(move_params) == 3: # for multiple target moves
                    target2 = None #target 2 is assigned only if there are 2 targets
                    for potential_target in targets:
                        if potential_target is not target and potential_target.hp > 0:
                            target2 = potential_target
                            break 
                    
                        move.use_move(user, target) 

                if target.hp <= 0:
                    print(f"{target.name} fainted!")
                    target.hp = 0  # prevent negative hp

                time.sleep(2)

#-------------------

def choose_trainer_name(trainer: Trainer, opp_trainer1: Trainer, opp_trainer2: Trainer) -> None:
    trainer_name: str = input(f"Trainer {trainer.trainer_id}, input your name: ")
    if trainer_name == opp_trainer1.trainer_name:
        print("Invalid choice, try again.")
        choose_trainer_name(trainer, opp_trainer1, opp_trainer2)
    elif trainer_name == opp_trainer2.trainer_name:
        print("Invalid choice, try again.")
        choose_trainer_name(trainer, opp_trainer1, opp_trainer2)
    else:
        trainer.trainer_name = trainer_name

def choose_pokemon(trainer: Trainer, pokemons: List[Pokemon]) -> None:
    while True:

        choice = input(f"{trainer.trainer_name}, choose a pokemon (by number): ")

        if not choice.isdigit():
            print(f"{trainer.trainer_name}, that is not a valid number. Try again.")
            continue

        choice = int(choice)

        if choice < 1 or choice > len(pokemons):
            print(f"{trainer.trainer_name}, that is not an option. Try again.")
            continue

        if pokemons[choice - 1].is_chosen:
            print(f"{trainer.trainer_name}, that pokemon is already selected. Try again.")
            continue

       
        print((pokemons[choice - 1]).__repr__()) # displaying the pokmeon
        option = input(f"Do you want to select this Pokemon?\n1. Yes \n2. No\n")
        if option == "1" or option.lower() == "yes":

            trainer.trainer_pokemon.append(pokemons[choice - 1])
            pokemons[choice - 1].is_chosen = True
            break

        elif option == "2" or option.lower() == "no":
            continue

        else:
            print("Invalid option. Try again.")

    



# - alex
# Contract:
# Purpose: Set the starting pokemon 
def set_initial_active_pokemon(trainer: Trainer):
    print(f"\n{trainer.trainer_name}, choose your starting pokemon:")
    for i, pokemon in enumerate(trainer.trainer_pokemon, start=1):
        print(f"{i}: {pokemon.name} (HP: {pokemon.hp})")

    while True:
        try:
            choice = int(input("Enter the number of your starting pokemon: ")) - 1
            if 0 <= choice < len(trainer.trainer_pokemon):
                trainer.active_pokemon = trainer.trainer_pokemon[choice]
                print(f"{trainer.trainer_name} selected {trainer.active_pokemon.name} as their starting Pokemon!")
                break
            else:
                print("Invalid choice. Please choose a valid number.")
        except ValueError:
            print("Invalid input. Enter a number corresponding to your pokemon.")

# Purpose: Print animated text
# def animated_print(string : str, time : float = 0.15):

#     for char in string:

#         print(char, end='', flush=True)
#         time.sleep(random.uniform(0, time))

#     print()
# - alex
# Contract:
# Purpose: Allows the trainer to pick one of their active Pokemon's moves and apply it to a target's active Pokemon.
def handleFight(trainer: Trainer, trainers: List[Trainer], action_done:bool):
    action_done = False
    while not action_done:
        active_pokemon = trainer.active_pokemon

        # If there is no active pokemon, then return 
        if not active_pokemon or active_pokemon.hp <= 0:
            print(f"{trainer.trainer_name} cannot fight because their active Pokemon is unavailable!")
            return False

        # 1) List the moves for the user's Pokemon
        print(f"\n{trainer.trainer_name}, choose a move for {active_pokemon.name}:")
        for i, move in enumerate(active_pokemon.moves, start=1):
            print(f"{i}. {move.__repr__()}")
        print("0. Cancel\n")

        # 2) Get users move choice
        while True:
            choice_str = input("Enter the move number (or 0 to cancel): ")
            if choice_str == "0":
                print("Canceled fight action; returning to main menu.\n")
                return False  # user canceled

            if choice_str.isdigit():
                choice_idx = int(choice_str) - 1  # -1 becuse of the enumerate logic 
                if 0 <= choice_idx < len(active_pokemon.moves):
                    chosen_move = active_pokemon.moves[choice_idx]
                    break
                else:
                    print("Invalid choice. Please enter a valid move number.")
            else:
                print("Invalid input. Please enter a number corresponding to the move.")

        # 3) Find targets (trainers who still have pokemon)
        possible_targets = [t for t in trainers if t != trainer and not all_pokemon_fainted(t)]

        if not possible_targets:    # if theres no targets  
            print("No valid targets to attack!")
            return

        # If theres only one valid target trainer, skip selection
        if len(possible_targets) == 1 or chosen_move.target_type == "All":
            target_trainer = possible_targets[0]
        else:
            # Let the user pick which trainer to attack
            print("\nChoose a trainer's pokemon to attack (1, 2, or type 0 to cancel):")
            for i, opp_trainer in enumerate(possible_targets, start=1):
                opp_name = opp_trainer.trainer_name
                opp_mon_type1 = opp_trainer.active_pokemon.type1.type_name
                opp_mon_type2 = opp_trainer.active_pokemon.type2.type_name
                opp_hp = opp_trainer.active_pokemon.hp
                opp_active = opp_trainer.active_pokemon
                opp_mon_name = opp_active.name if opp_active and opp_active.hp > 0 else "No Active pokemn"
                print(f"{i}. {opp_name}'s {opp_mon_name} [{opp_mon_type1} {opp_mon_type2}] (HP: {opp_hp})")

            target_choice_str = input("Trainer choice: ")
            if target_choice_str == "0":
                print("Canceled targeting, returning to main menu.\n")
                return False

            try:
                target_idx = int(target_choice_str) - 1
                if target_idx < 0 or target_idx >= len(possible_targets):
                    print("Invalid target choice.\n")
                    return False
            except ValueError:
                print("Invalid input for target.\n")
                break

            target_trainer = possible_targets[target_idx]

        # 4) Get the target pokemon
        target_pokemon = target_trainer.active_pokemon
        if (not target_pokemon) or target_pokemon.hp <= 0: # if the target has no active pokemon, or their active pokemon is fainted
            return
        
        # 5) Determining targets based on move type
        all_pokemon = [trainer.active_pokemon for trainer in trainers if trainer.active_pokemon]
        if chosen_move.target_type == "Single":
            targets = [target_pokemon]
        elif chosen_move.target_type == "All":
            trainer_team = trainer.trainer_pokemon
            targets = [pokemon for pokemon in all_pokemon if pokemon not in trainer_team]
        else:
            targets = []  # Default case

        # 5.5) Adjusting speed in case of paralysis
        apply_status_effects_start(active_pokemon)

        # 6) Queuing the moves 
        queue_move(chosen_move, active_pokemon, targets)

        # 7) Sorting by speed and priority
        sort_queued_list(list_of_queued_moves)

        action_done = True
    
    return True

        # # 8) Use the moves
        # initiate_pokemon_moves(list_of_queued_moves)


        # # Check if the target fainted
        # if target_pokemon.hp <= 0:
        #     target_pokemon.hp = 0
        #     print(f"{target_pokemon.name} fainted!\n")
        # else:
        #     print(f"{target_pokemon.name} has {target_pokemon.hp} HP left.\n")

# - alex
# Contract: handlePokemon(trainer: Trainer, action_done: bool) -> bool
# Purpose: Helper function to manage pokemon selection during turn 
def handlePokemon(trainer: Trainer, action_done: bool):
    action_done = False
    while not action_done:
        print(f"\n{trainer.trainer_name}, choose a new active Pokemon!:")

        for i, pokemon in enumerate(trainer.trainer_pokemon, start=1):  
            status = "(FAINTED)" if pokemon.hp <= 0 else ""      # if a pokemon is dead apply a fainted marker (cannot be picked)
            print(f"{i}: {pokemon.name} (HP: {pokemon.hp}) {status}")      

        print("\nChoosing new Pokemon!")
        print("Your active pokemon is: ", trainer.active_pokemon.name) # print the current active pokemon

        while True: # start loop to error handle misinput
            try:
                choice = int(input("\nEnter the number of your new active Pokemon (or 0 to return to menu): ")) - 1  

                if 0 <= choice < len(trainer.trainer_pokemon):   # if the choice resides within the amount of pokemon the trainer has, 
                    if trainer.trainer_pokemon[choice].hp > 0:   # checks first if the pokemon is alive 
                        if trainer.trainer_pokemon[choice] != trainer.active_pokemon: # Checks if the pokemon is already active

                            trainer.active_pokemon.status = Status(1.0, 1.0, 1.0, 1.0, 1.0, trainer.active_pokemon.status.physical_status)  # first clear the pokemon's stages back to 0 

                            trainer.active_pokemon = trainer.trainer_pokemon[choice] # set the trainer's active pokemon to the selected choice 
                            print(f"{trainer.trainer_name} selected {trainer.active_pokemon.name} as their active Pokemon!")
                            action_done = True # set action_done to true 
                            break
                        else:
                            print("That Pokemon is already selected!")

                    else:                                        # if the pokemon is dead, prompt error (probably wont happen)
                        print("That Pokemon has fainted! Choose another.")

                elif choice == -1:  # if input = 0, return to menu to select through options again 
                    return False
                
                else:  # final possibility, in which loop restarts
                    print("Invalid choice. Please choose a valid number.")

            except ValueError:  # need this error checking because of the choice = int 
                print("Invalid input. Enter a number corresponding to your pokemon.")
                
    return True

# - alex
# Contract: pokemonDied(trainer: Trainer)
# Purpose: Helper function prompt user to select a new pokemon if theirs died 
def pokemonDied(trainer: Trainer):
    
    print(f"\n{trainer.trainer_name}, your pokemon fainted, choose a new one :")

    for i, pokemon in enumerate(trainer.trainer_pokemon, start=1):  
        status = "(FAINTED)" if pokemon.hp <= 0 else ""      # if a pokemon is dead apply a fainted marker (cannot be picked)
        print(f"{i}: {pokemon.name} (HP: {pokemon.hp}) {status}")      

    while True: # start loop to error handle misinput
        try:
            choice = int(input("\nEnter the number of your new active Pokemon (or 0 to return to menu): ")) - 1  

            if 0 <= choice < len(trainer.trainer_pokemon):   # if the choice resides within the amount of pokemon the trainer has, 
                if trainer.trainer_pokemon[choice].hp > 0:   # checks first if the pokemon is alive 
                    if trainer.trainer_pokemon[choice] != trainer.active_pokemon: # Checks if the pokemon is already active

                        trainer.active_pokemon.status = Status(1.0, 1.0, 1.0, 1.0, 1.0, trainer.active_pokemon.status.physical_status)  # first clear the pokemon's stages back to 0 

                        trainer.active_pokemon = trainer.trainer_pokemon[choice] # set the trainer's active pokemon to the selected choice 
                        print(f"{trainer.trainer_name} selected {trainer.active_pokemon.name} as their active Pokemon!")
                        #action_done = True # set action_done to true 
                        break
                    else:
                        print("That Pokemon is already selected!")

                else:                                        # if the pokemon is dead, prompt error (probably wont happen)
                    print("That Pokemon has fainted! Choose another.")

            elif choice == -1:  # if input = 0, return to menu to select through options again 
                return False
            
            else:  # final possibility, in which loop restarts
                print("Invalid choice. Please choose a valid number.")

        except ValueError:  # need this error checking because of the choice = int 
            print("Invalid input. Enter a number corresponding to your pokemon.")
            
    return
                


# - alex
# Contract: handlebag(trainer: Trainer)
# Purpose: Allow trainer to look in their bag and use their items (if any)
def handleBag(trainer: Trainer, action_done):
    action_done = False

    while not action_done:
        if trainer.healthPotions == 0 and trainer.fullHeal == 0:
            print("You have no items left in your bag!")
            return
        
        print(f"\n{trainer.trainer_name}, your active pokemon, {trainer.active_pokemon.name} has {trainer.active_pokemon.hp} HP.") # inform user of pokemon's hp

        print("\n0. Go back to menu")                             # menu for available items
        print(f"1. Health Potion: {trainer.healthPotions}")
        print(f"2. Full Heal: {trainer.fullHeal}")
        
        while True:
            choice = input(f"{trainer.trainer_name}, you have the following items available, choose an option: ")  # prompt an input from the user
            if choice == "0":
                return
            if choice == "1":  # if the user selects health potion,
                if trainer.healthPotions == 0:
                    print("You have no Health Potions left!")  # if they have no health potions, tell them
                else:                        # if they do have health potions, heal the active pokemon          
                    trainer.active_pokemon.hp += 100 # heals pokemon 
                    trainer.healthPotions -= 1
                    print(f"{trainer.active_pokemon.name} has been healed by 100 HP!")
                    if trainer.active_pokemon.hp > trainer.active_pokemon.max_hp:  # if the pokemon has been healed above max hp, set it to max hp
                        trainer.active_pokemon.hp = trainer.active_pokemon.max_hp
                    print(f"{trainer.active_pokemon.name} now has {trainer.active_pokemon.hp} HP.")
                    action_done = True # set action_done to true
                    break
            if choice == "2":
                if trainer.fullHeal == 0:
                    print("You have no Full Heals left!")
                else:
                    trainer.active_pokemon.physical_status = "Healthy" 
                    trainer.active_pokemon.hp = trainer.active_pokemon.max_hp # set the pokemons health to the max
                    trainer.fullHeal -= 1
                    print(f"{trainer.active_pokemon.name} has been fully healed!")
                    action_done = True # set action_done to true
                    break
    action_done = True
    
        
# - alex
# Contract: all_pokemon_fainted(trainer: Trainer) -> bool
# Purpose: Helper function to determine if a trainer has had all their pokemon faint 
def all_pokemon_fainted(trainer: Trainer) -> bool:   
    for pokemon in trainer.trainer_pokemon:   # if there is a pokemon with health above 0, return false (not all pokemon have fainted)
        if pokemon.hp > 0:
            return False
    return True  # if all pokemon have 0 health, return true

# - alex
# Contract: battle_is_over(trainers: list) -> boolean
# Purpose: every time a turn is finished, check if the battle is over (is their one trainer left?)
def battle_is_over(trainers) -> bool:
    activeTrainers = 0 # initialize this variable to count trainers

    for trainer in trainers:                 # For every trainer... 
        if not all_pokemon_fainted(trainer): # if all the pokemon arent fainted then
            activeTrainers += 1
    return activeTrainers <= 1  # If there is 0 OR 1 trainer left, return true. In most cases it will be 1, which ends the game

# - alex
# Contract: getAction(trainer: Trainer) -> str
# Purpose: Handles user input for their option
def getAction(trainer: Trainer) -> str:
    print("'1' - FIGHT")
    print("'2' - BAG")
    print("'3' - POKEMON")
    while True:
        choice = input("Choose one of the following options: ")
        if choice == "1":
            return "fight"
        if choice == "2":
            return "bag"
        if choice == "3":
            return "pokemon"
        else:
            
            print("Enter a valid option 1-3...")
            
# contract: choose_new_active_pokemon(trainer: Trainer) -> None
# Purpose: When a trainers pokemon faints, make the trainer pick another one of their pokemon
def choose_new_active_pokemon(trainer: Trainer):
    if not trainer.has_usable_pokemon():
        print(f"{trainer.trainer_name} has no Pokemon left!")
        return

    print(f"\n{trainer.trainer_name}, choose a new Pokemon:")
    while True:
        new_pokemon = choose_pokemon(trainer, trainer.trainer_pokemon)
        if new_pokemon.hp > 0:  # Ensure it's not fainted
            trainer.active_pokemon = new_pokemon
            print(f"{trainer.trainer_name} sent out {new_pokemon.name}!")
            break
        else:
            print("That Pokemon has fainted! Choose another.")

# contract: apply_end_turn_status_damage(trainers: list) -> None
# Purpose: Applies burn and poison damage at the end of every turn
def apply_end_turn_status_damage(trainers: list):

    for trainer in trainers:
        pokemon = trainer.active_pokemon
        if not pokemon or pokemon.hp <= 0:
            continue  # Skip if Pokemon is fainted
        for status in pokemon._status.physical_status:
            if status.condition == "Burn":
                burn_damage(pokemon)

            if status.condition == "Poison":
                poison_damage(pokemon, status)
        
        # Increases the amount of turns a status has been active if there are any active statuses
        for status in trainer.active_pokemon._status.physical_status:
                status.turns_active += 1
            
        # Check if Pokemon fainted from status damage
        if pokemon.hp <= 0:
            pokemon.hp = 0
            print(f"{pokemon.name} fainted from status damage!\n")
            choose_new_active_pokemon(trainer)
    

    print("--- End of Turn ---\n")

# contract: determine_winner(trainers: list) -> str
# Purpose: Determines which trainer won the game
def determine_winner(trainers: list) -> str:
    """Returns the name of the winning trainer, or None if no winner yet."""
    remaining_trainers = [trainer for trainer in trainers if trainer.has_usable_pokemon()]

    if len(remaining_trainers) == 1:
        return remaining_trainers[0].trainer_name  # The only trainer left is the winner
    return None  # No winner yet


# - alex
# Contract: battle_loop(trainers: list) -> None
# Purpose: The main game loop that handles the battle between trainers
def battle_loop(trainers: list) -> None:
    db = DatabaseManager()  # Create database connection
    while not battle_is_over(trainers):  # While battle isn't over
        for current_trainer in trainers: # Going through each trainer's turn

            # Check if the trainer has any available Pokemon
            if not current_trainer.has_usable_pokemon():
                trainers.remove(current_trainer)
                continue  # Skip trainer's turn if all their Pokemon fainted

            action_done = False
            while not action_done:
                print(f"\n\n\n\n\nIt's {current_trainer.trainer_name}'s turn!")
                action = getAction(current_trainer)  # Get the trainer's chosen action

                if action == 'fight': 
                    action_done = handleFight(current_trainer, trainers, action_done)  
                elif action == 'bag':
                    action_done = handleBag(current_trainer, action_done) 
                elif action == 'pokemon':
                    action_done = handlePokemon(current_trainer, action_done)  
                    
        # Initiate the pokemon moves
        initiate_pokemon_moves(list_of_queued_moves)

        # Check if any active Pokemon fainted and prompt trainer to switch
        for trainer in trainers:
            if trainer.active_pokemon.hp <= 0:
                print(f"{trainer.active_pokemon.name} fainted!")
                pokemonDied(trainer)

        # Apply burn/poison damage at the end of the turn
        apply_end_turn_status_damage(trainers)

        # Clears the move queue
        list_of_queued_moves.clear()

    winner = determine_winner(trainers)
    if winner and server:
        server.log_winner(winner)

    print(f"\nCongrats to {determine_winner(trainers)} for winning!")  # End game
    for trainer in trainers:
        for pokemon in trainer.trainer_pokemon:
            db.insert_player(
                trainer.trainer_name,
                pokemon.name,
                pokemon.type1.type_name,
                pokemon.type2.type_name if pokemon.type2 else None
            )

    db.close()
    return




def main():
    # GAME FUNCTIONS
    all_pokemon: List[Pokemon] = [PokemonObjects5.charizard, PokemonObjects5.ampharos, PokemonObjects5.swampert,
                                  PokemonObjects5.metagross, PokemonObjects5.abomasnow, PokemonObjects5.dusknoir,
                                  PokemonObjects5.pangoro, PokemonObjects5.naganadel, PokemonObjects5.gardevoir,
                                  PokemonObjects5.gengar, PokemonObjects5.rayquaza, PokemonObjects5.grimmsnarl,
                                  PokemonObjects5.garchomp, PokemonObjects5.delphox, PokemonObjects5.duskmanenecrozma,
                                  PokemonObjects5.ironbundle, PokemonObjects5.diancie, PokemonObjects5.guzzlord, 
                                  PokemonObjects5.drowsee, PokemonObjects5.kyurem, PokemonObjects5.torracat, 
                                  PokemonObjects5.mudsdale, PokemonObjects5.vikavolt, PokemonObjects5.snorlax  ]

    trainer1: Trainer = Trainer(1, "", None, [])  # Fix: active_pokemon=None, trainer_pokemon=[]
    trainer2: Trainer = Trainer(2, "", None, [])
    trainer3: Trainer = Trainer(3, "", None, [])

    listof_trainer: List[Trainer] = [trainer1, trainer2, trainer3]
    
    # trainer name choosing
    for trainer in listof_trainer:
        if trainer.trainer_id == 1:
            choose_trainer_name(trainer, listof_trainer[1], listof_trainer[2])
        if trainer.trainer_id == 2:
            choose_trainer_name(trainer, listof_trainer[0], listof_trainer[2])
        if trainer.trainer_id == 3:
            choose_trainer_name(trainer, listof_trainer[0], listof_trainer[1])

    # trainer pokemon choosing
    for i in range(3):
        for trainer in listof_trainer:
            print("\nAvailable Pokemon: ")
            for i in range(len(all_pokemon)):
                if not all_pokemon[i].is_chosen:
                    print(f"{i + 1}: {all_pokemon[i].name}")
            choose_pokemon(trainer, all_pokemon)

    for trainer in listof_trainer:             # -alex, we need each trainer to have an active pokemon
        set_initial_active_pokemon(trainer)

    
    battle_loop(listof_trainer)


# Unit testing --------
# Tests for the Pokemon class and related functions

# test for pokemon creation
def test_pokemon_creation() -> None:
    # Tests that a Pokemon object is created with the correct attributes.
    type1 = Type("Fire", ["Grass"], ["Water"], ["Fire"], [])
    type2 = Type("Flying", ["Grass"], ["Electric"], ["Fighting"], [])
    status = Status(1.0, 1.0, 1.0, 1.0, 1.0, [])
    moves = [PokemonObjects5.DragonDance]
    pokemon = Pokemon("Charizard", type1, type2, 100, 100, 84, 78, 109, 85, 100, moves, status, False, False, False)
    
    assert pokemon.name == "Charizard"
    assert pokemon.type1 == type1
    assert pokemon.type2 == type2
    assert pokemon.max_hp == 100
    assert pokemon.hp == 100
    assert pokemon.attack == 84
    assert pokemon.defense == 78
    assert pokemon.sp_attack == 109
    assert pokemon.sp_defense == 85
    assert pokemon.speed == 100
    assert pokemon.moves == moves
    assert pokemon.status == status
    assert not pokemon.legendary
    assert not pokemon.is_chosen
    assert not pokemon.has_moved

# test for updating hp
def test_update_pokemon_hp() -> None:
    # Tests updating the HP of a Pokemon.
    type1 = Type("Fire", ["Grass"], ["Water"], ["Fire"], [])
    status = Status(1.0, 1.0, 1.0, 1.0, 1.0, [])
    moves = [PokemonObjects5.DragonDance]
    pokemon = Pokemon("Charizard", type1, None, 100, 100, 84, 78, 109, 85, 100, moves, status, False, False, False)
    
    pokemon.hp = 80
    assert pokemon.hp == 80

# test for updating attack
def test_update_pokemon_status() -> None:
    # Tests updating the status of a Pokemon.
    type1 = Type("Fire", ["Grass"], ["Water"], ["Fire"], [])
    status = Status(1.0, 1.0, 1.0, 1.0, 1.0, [])
    moves = [PokemonObjects5.DragonDance]
    pokemon = Pokemon("Charizard", type1, None, 100, 100, 84, 78, 109, 85, 100, moves, status, False, False, False)
    
    new_status = Status(1.5, 1.0, 1.0, 1.0, 1.0, [])
    pokemon.status = new_status
    assert pokemon.status == new_status

def test_trainer_creation() -> None:
    # Tests that a Trainer object is created with the correct attributes.
    trainer = Trainer(1, "Ash", [], None)
    
    assert trainer.trainer_id == 1
    assert trainer.trainer_name == "Ash"
    assert trainer.active_pokemon is None
    assert trainer.trainer_pokemon == []
    assert trainer.healthPotions == 2
    assert trainer.fullHeal == 1

# Test to see if choosing a pokemon works. It passes but prompts a user, so it is commented out.
def test_choose_pokemon() -> None:
    # Tests choosing a Pokemon for a Trainer.
    type1 = Type("Fire", ["Grass"], ["Water"], ["Fire"], [])
    status = Status(1.0, 1.0, 1.0, 1.0, 1.0, [])
    moves = [PokemonObjects5.DragonDance]
    pokemon = Pokemon("Charizard", type1, None, 100, 100, 84, 78, 109, 85, 100, moves, status, False, False, False)
    trainer = Trainer(1, "Ash", [], None)
    
    choose_pokemon(trainer, [pokemon])
    assert trainer.trainer_pokemon == [pokemon]
    assert pokemon.is_chosen 

# Test to see if setting the initial active Pokemon works. It passes but prompts a user, so it is commented out.
def test_set_initial_active_pokemon() -> None:
    # Tests setting the initial active Pokemon for a Trainer.
    type1 = Type("Fire", ["Grass"], ["Water"], ["Fire"], [])
    status = Status(1.0, 1.0, 1.0, 1.0, 1.0, [])
    moves = [PokemonObjects5.DragonDance]
    pokemon = Pokemon("Charizard", type1, None, 100, 100, 84, 78, 109, 85, 100, moves, status, False, False, False)
    trainer = Trainer(1, "Ash", [pokemon], None)
    
    set_initial_active_pokemon(trainer)
    assert trainer.active_pokemon == pokemon 

# Test to see if handling the bag works. It passes but prompts a user, so it is commented out.
def test_handle_bag() -> None:
    # Tests using items from the Trainer's bag.
    type1 = Type("Fire", ["Grass"], ["Water"], ["Fire"], [])
    status = Status(1.0, 1.0, 1.0, 1.0, 1.0, [])
    moves = [PokemonObjects5.DragonDance]
    pokemon = Pokemon("Charizard", type1, None, 100, 50, 84, 78, 109, 85, 100, moves, status, False, False, False)
    trainer = Trainer(1, "Ash", [pokemon], pokemon)
    
    handleBag(trainer, False)
    assert trainer.active_pokemon.hp == 100
    assert trainer.healthPotions == 1


def test_handle_fight() -> None:
    # Tests handling a fight action.
    type1 = Type("Fire", ["Grass"], ["Water"], ["Fire"], [])
    status = Status(1.0, 1.0, 1.0, 1.0, 1.0, [])
    moves = [PokemonObjects5.DragonDance]
    pokemon1 = Pokemon("Charizard", type1, None, 100, 100, 84, 78, 109, 85, 100, moves, status, False, False, False)
    pokemon2 = Pokemon("Blastoise", type1, None, 100, 100, 84, 78, 109, 85, 100, moves, status, False, False, False)
    trainer1 = Trainer(1, "Ash", [pokemon1], pokemon1)
    trainer2 = Trainer(2, "Misty", [pokemon2], pokemon2)
    
    handleFight(trainer1, [trainer1, trainer2], False)
    assert pokemon2.hp < 100

def test_all_pokemon_fainted() -> None:
    # Tests checking if all Pokemon of a Trainer have fainted.
    type1 = Type("Fire", ["Grass"], ["Water"], ["Fire"], [])
    status = Status(1.0, 1.0, 1.0, 1.0, 1.0, [])
    moves = [PokemonObjects5.DragonDance]
    pokemon = Pokemon("Charizard", type1, None, 100, 0, 84, 78, 109, 85, 100, moves, status, False, False, False)
    trainer = Trainer(1, "Ash", [pokemon], pokemon)
    
    assert all_pokemon_fainted(trainer)

def test_battle_is_over() -> None:
    # Tests checking if the battle is over.
    type1 = Type("Fire", ["Grass"], ["Water"], ["Fire"], [])
    status = Status(1.0, 1.0, 1.0, 1.0, 1.0, [])
    moves = [PokemonObjects5.DragonDance]
    pokemon1 = Pokemon("Charizard", type1, None, 100, 0, 84, 78, 109, 85, 100, moves, status, False, False, False)
    pokemon2 = Pokemon("Blastoise", type1, None, 100, 100, 84, 78, 109, 85, 100, moves, status, False, False, False)
    trainer1 = Trainer(1, "Ash", [pokemon1], pokemon1)
    trainer2 = Trainer(2, "Misty", [pokemon2], pokemon2)
    
    assert battle_is_over([trainer1, trainer2])

# Test for apply_status_effects_start
def test_apply_status_effects_start():
    type1 = Type("Electric", [], [], [], [])
    # For testing, use a list containing a string "Paralyzed"
    status = Status(1.0, 1.0, 1.0, 1.0, 100, ["Paralyzed"])
    moves = []
    pokemon = Pokemon("Pikachu", type1, None, 100, 100, 55, 40, 50, 50, 90, moves, status, False, False, False)
    initial_speed = pokemon._speed
    apply_status_effects_start(pokemon)
    assert pokemon._speed == initial_speed / 2


# Test for paralyzed function
def test_paralyzed():
    type1 = Type("Water", [], [], [], [])
    status = Status(1.0, 1.0, 1.0, 1.0, 100, [])
    moves = []
    pokemon = Pokemon("Squirtle", type1, None, 100, 100, 48, 65, 50, 64, 43, moves, status, False, False, False)
    pokemon._speed = 100
    paralyzed(pokemon)
    assert pokemon._speed == 50

# Test for burn_damage function
def test_burn_damage():
    type1 = Type("Fire", [], [], [], [])
    status = Status(1.0, 1.0, 1.0, 1.0, 100, [])
    moves = []
    max_hp = 160
    pokemon = Pokemon("Charmander", type1, None, max_hp, max_hp, 52, 43, 60, 50, 65, moves, status, False, False, False)
    burn_damage(pokemon)
    expected_hp = max_hp - (max_hp/16)
    assert abs(pokemon._hp - expected_hp) < 0.001

# Test for poison_damage function for different turns_active
def test_poison_damage():
    type1 = Type("Poison", [], [], [], [])
    status = Status(1.0, 1.0, 1.0, 1.0, 100, [])
    moves = []
    max_hp = 160
    status0 = PhysicalStatus("Poisoned", 0, 0)
    pokemon = Pokemon("Ekans", type1, None, max_hp, max_hp, 60, 44, 40, 54, 55, moves, status, False, False, False)
    poison_damage(pokemon, status0)
    expected_hp = max_hp - (max_hp/8)
    assert abs(pokemon._hp - expected_hp) < 0.001

    status1 = PhysicalStatus("Poisoned", 1, 0)
    pokemon._hp = max_hp
    poison_damage(pokemon, status1)
    expected_hp = max_hp - (max_hp/4)
    assert abs(pokemon._hp - expected_hp) < 0.001

    status2 = PhysicalStatus("Poisoned", 2, 0)
    pokemon._hp = max_hp
    poison_damage(pokemon, status2)
    expected_hp = max_hp - (max_hp*3/8)
    assert abs(pokemon._hp - expected_hp) < 0.001

    status3 = PhysicalStatus("Poisoned", 3, 0)
    pokemon._hp = max_hp
    poison_damage(pokemon, status3)
    expected_hp = max_hp - (max_hp/2)
    assert abs(pokemon._hp - expected_hp) < 0.001

    status4 = PhysicalStatus("Poisoned", 4, 0)
    pokemon._hp = max_hp
    poison_damage(pokemon, status4)
    expected_hp = max_hp - (max_hp*5/8)
    assert abs(pokemon._hp - expected_hp) < 0.001

# Test for queue_move and sort_queued_list
def test_queue_and_sort_moves():
    global list_of_queued_moves
    list_of_queued_moves = []
    
    class DummyDamagingMove(Move):
        def __init__(self, name, priority, damage=10):
            dummy_type = Type("Normal", [], [], [], [])
            super().__init__(name, dummy_type, 10, 100, 100, None, "physical")
            self.priority = priority
            self.damage = damage
        def use_move(self, user, target):
            target.hp -= self.damage
    
    move1 = DummyDamagingMove("Move1", priority=1, damage=10)
    move2 = DummyDamagingMove("Move2", priority=2, damage=10)
    type1 = Type("Normal", [], [], [], [])
    status = Status(1.0, 1.0, 1.0, 1.0, 100, [])
    pokemonA = Pokemon("A", type1, None, 100, 100, 50, 50, 50, 50, 100, [], status, False, False, False)
    pokemonB = Pokemon("B", type1, None, 100, 100, 60, 50, 50, 50, 80, [], status, False, False, False)
    
    queue_move(move1, pokemonA, [pokemonB])
    queue_move(move2, pokemonA, [pokemonB])
    
    sort_queued_list(list_of_queued_moves)
    assert list_of_queued_moves[0][0].name == "Move2"
    list_of_queued_moves = []

# Test for initiate_pokemon_moves
def test_initiate_pokemon_moves():
    global list_of_queued_moves
    list_of_queued_moves = []
    
    class DummyDamagingMove(Move):
        def __init__(self, name, priority, damage=10):
            dummy_type = Type("Normal", [], [], [], [])
            super().__init__(name, dummy_type, 10, 100, 100, None, "physical")
            self.priority = priority
            self.damage = damage
        def use_move(self, user, target):
            target.hp -= self.damage

    move = DummyDamagingMove("Attack", priority=1, damage=20)
    type1 = Type("Normal", [], [], [], [])
    status = Status(1.0, 1.0, 1.0, 1.0, 100, [])
    pokemon_attacker = Pokemon("Attacker", type1, None, 100, 100, 50, 50, 50, 50, 100, [move], status, False, False, False)
    pokemon_target = Pokemon("Target", type1, None, 100, 100, 50, 50, 50, 50, 100, [], status, False, False, False)
    
    list_of_queued_moves.append((move, pokemon_attacker, [pokemon_target]))
    original_sleep = time.sleep
    time.sleep = lambda x: None
    initiate_pokemon_moves(list_of_queued_moves)
    time.sleep = original_sleep
    assert pokemon_target.hp == 80
    list_of_queued_moves = []

# Test for determine_winner
def test_determine_winner():
    type1 = Type("Normal", [], [], [], [])
    status = Status(1.0, 1.0, 1.0, 1.0, 100, [])
    moves = []
    pokemon1 = Pokemon("Pikachu", type1, None, 100, 0, 55, 40, 50, 50, 90, moves, status, False, False, False)
    pokemon2 = Pokemon("Eevee", type1, None, 100, 100, 55, 40, 50, 50, 90, moves, status, False, False, False)
    trainer1 = Trainer(1, "Ash", [pokemon1], pokemon1)
    trainer2 = Trainer(2, "Gary", [pokemon2], pokemon2)
    winner = determine_winner([trainer1, trainer2])
    assert winner == "Gary"

# Test for apply_end_turn_status_damage
def test_apply_end_turn_status_damage():
    type1 = Type("Fire", [], [], [], [])
    # For this test, we set the status to the string "Burn"
    status = "Burn"
    moves = []
    max_hp = 160
    pokemon = Pokemon("Charmander", type1, None, max_hp, max_hp, 52, 43, 60, 50, 65, moves, status, False, False, False)
    trainer = Trainer(1, "Ash", [pokemon], pokemon)
    current_hp = pokemon.hp
    apply_end_turn_status_damage([trainer])
    expected_hp = current_hp - (max_hp/16)
    assert abs(pokemon.hp - expected_hp) < 0.001

# Run all tests
def run_all_tests():
    number = 1
    test_pokemon_creation()
    print(number)
    test_update_pokemon_hp()
    print(number + 1)
    test_update_pokemon_status()
    print(number + 1)
    #test_trainer_creation()
    print(number + 1)
    #test_choose_pokemon()
    print(number + 1)
    #test_set_initial_active_pokemon()
    print(number + 1)
    test_handle_fight()
    print(number + 1)
    test_all_pokemon_fainted()
    print(number + 1)
    test_battle_is_over()
    print(number + 1)
    test_apply_status_effects_start()
    print(number + 1)
    print(number + 1)
    test_paralyzed()
    print(number + 1)
    test_burn_damage()
    print(number + 1)
    test_poison_damage()
    print(number + 1)
    test_queue_and_sort_moves()
    print(number + 1)
    test_initiate_pokemon_moves()
    print(number + 1)
    test_determine_winner()
    print(number + 1)
    test_apply_end_turn_status_damage()
    print("All tests passed.")
    
if __name__ == "__main__":
#     #run_all_tests()
     main()  











# if __name__ == "__main__":
#     main()

