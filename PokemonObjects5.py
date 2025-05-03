from alexPokemon import Type, Pokemon, Move, Status, PhysicalStatus, Trainer
from alexPokemon import Type
import random
from multipledispatch import dispatch
from abc import ABC, abstractmethod
from alexPokemon import handlePokemon
import alexPokemon


# ----------------------------------------------------------------------
class Move(ABC):
    def __init__(self, name : str, type: Type, power: int, accuracy: int, effect_chance : int, status_effect : str, category : str, priority : int, target_type : str):
        self.name = name
        self.type = type
        self.power = power
        self.accuracy = accuracy
        self.effect_chance = effect_chance
        self.status_effect = status_effect
        self.category = category
        self.priority = priority
        self.target_type = target_type
    
    # Move information method (For when the player wants to see the description of a move)
    @abstractmethod
    def __repr__(self):
        pass
    
    @abstractmethod
    def use_move(self):
        pass
    
    
    # Purpose: Determines if a pokemon is able to use its move
    def can_move(self, pokemon : Pokemon) -> bool:
        can_act = True

        # Checks if the pokemon using a move is paralyzed
        for status in pokemon._status.physical_status:
            # Checks if the pokemon using a move is paralyzed
            if status.condition == "Paralyzed":
                # &= is used for combining the result of checking for paralysis and confusion
                can_act &= paralysis(pokemon)
            # Checks if the pokemon using a move is asleep
            elif status.condition == "Asleep":
                can_act = asleep(status, pokemon)
            # Checks if the pokemon using a move is Frozen
            elif status.condition == "Frozen":
                can_act = frozen(self, status, pokemon)
            # Checks if the pokemon using a move flinched
            elif status.condition == "Flinch":
                can_act = flinch(status, pokemon)
            # Checks if the pokemon using a move is confused
            elif status.condition == "Confused":
                can_act &= confused(status, pokemon)
        # Check if the pokemon has NOT missed its attack
        can_act &= not missed(self, pokemon)

        return can_act
    




#----------------------------------------------------------------------------------------
# HELPER FUNCTIONS FOR can_move()

# Purpose: Checks if a pokemon can move if it has paralysis (25% chance of not moving)
def paralysis(pokemon : Pokemon):
    if random_accuracy() <= 25:
        print(f"{pokemon.name} is paralyzed! It can't move!")
        return False
    else:
        return True
    
# Purpose: Checks if a pokemon can move if its asleep 
def asleep(status : PhysicalStatus, pokemon : Pokemon):
    # A pokemon can be asleep for a max of 3 turns
    if status.turns_active > 3:
        pokemon._status.physical_status.remove(status)
        print(f"{pokemon.name} woke up!")
        return True
    # 33% chance of waking up each turn
    elif random_accuracy() <= 33:
        pokemon._status.physical_status.remove(status)
        print(f"{pokemon.name} woke up!")
        return True
    else:
        print(f"{pokemon.name} is asleep!")
        return False

# Purpose: Checks if a pokemon can move if its frozen
def frozen(move : Move, status : PhysicalStatus, pokemon : Pokemon):
# If the pokemon uses a fire type move, it thaws out
    if move.type == "Fire":
        pokemon._status.physical_status.remove(status)
        print(f"{pokemon.name} thawed out!")
        return True
    # 20% chance of thawing out each turn
    elif random_accuracy() <= 20:
        pokemon._status.physical_status.remove(status)
        print(f"{pokemon.name} thawed out!")
        return True
    else:
        print(f"{pokemon.name} is frozen solid!")
        return False   
    
# Purpose: Prevents a pokemon from moving for a single turn
def flinch(status : PhysicalStatus, pokemon : Pokemon):
    if pokemon.has_moved == False:
        print(f"{pokemon.name} flinched!")
        pokemon._status.physical_status.remove(status)
        return False
    else:
        pokemon._status.physical_status.remove(status)
        return True

# Purpose: Checks if a pokemon can move if its confused
def confused(status : PhysicalStatus, pokemon : Pokemon):
    print(f"{pokemon.name} is confused!")
    if status.duration >= status.turns_active:
        pokemon._status.physical_status.remove(status)
        print(f"{pokemon.name} snapped out of confusion!")
        return True
    elif random_accuracy() <= 33:
        damage = damage_calculation(pokemon, pokemon, ConfusionStatus())
        print(f"{pokemon.name} hurt itself in confusion and took {damage} damage!")
        return False
    else:
        return True

# If a pokemon is unable to move due to confusion,
# if hurts itself via a physical typeless move with base power 40
class ConfusionStatus(Move):
    def __init__(self):
        super().__init__("Confusion status", "None", 40, 100, 0, "", "Physical")

# Purpose: Checks if a pokemon's move wasn't accurate enough to land
def missed(move : Move, pokemon : Pokemon):
    if random_accuracy() > move.accuracy:
        print(f"{pokemon.name} used {move.name}! It missed!")
        return True
    else:
        return False

# Purpose: Apply recoil damage
def apply_recoil(user : Pokemon, damage : int, fraction : float):
    recoil = damage * fraction
    user._hp = max(0, user._hp - recoil)
    print(f"{user.name} took {int(recoil)} recoil damage!")

# Purpose: To print a message after a damage-dealing move is used on another pokemon
def move_statement(move : Move, user : Pokemon, target : Pokemon):
    
    if move.type in target.type1.immunities or move.type in target.type2.immunities:
        print(f"\n{user.name} used {move.name} on {target.name}! It had no effect!")
    elif move.type in target.type1.weaknesses and move.type in target.type2.resistances:
        print(f"\n{user.name} used {move.name} on {target.name}!")
    elif move.type in target.type1.resistances and move.type in target.type2.weaknesses:
        print(f"\n{user.name} used {move.name} on {target.name}!")
    elif move.type in target.type1.weaknesses or move.type in target.type2.weaknesses:
        print(f"\n{user.name} used {move.name} on {target.name}! It's super effective!")
    elif move.type in target.type1.resistances or move.type in target.type2.resistances:
        print(f"\n{user.name} used {move.name} on {target.name}! It's not very effective...")
    else:
        print(f"\n{user.name} used {move.name} on {target.name}!")

# Type objects
fire_type = Type(type_name="\033[1;31mFire\033[0m", 
                 strengths=["Grass", "Bug", "Steel", "Ice"], 
                 weaknesses=["Water", "Ground", "Rock"], 
                 resistances=["Fire", "Grass", "Bug", "Fairy", "Steel", "Ice"],
                 immunities=[])

water_type = Type(type_name="\033[1;34mWater\033[0m", 
                  strengths=["Fire", "Rock", "Ground"], 
                  weaknesses=["Grass", "Electric"], 
                  resistances=["Water", "Fire", "Ice", "Steel"],
                  immunities=[])

grass_type = Type(type_name="\033[1;32mGrass\033[0m", 
                  strengths=["Water", "Ground", "Rock"], 
                  weaknesses=["Fire", "Flying", "Ice", "Bug", "Poison"], 
                  resistances=["Grass", "Water", "Electric", "Ground"],
                  immunities=[])

electric_type = Type(type_name="\033[1;33mElectric\033[0m", 
                     strengths=["Water", "Flying"],
                     weaknesses=["Ground"],
                     resistances=["Steel", "Electric", "Flying"],
                     immunities=[]) 

flying_type = Type(type_name="\033[38;5;147m\033[1mFlying\033[0m", 
                   strengths=["Fighting", "Bug", "Grass"],
                   weaknesses=["Rock", "Electric", "Ice"],
                   resistances=["Bug", "Grass", "Fighting"],
                   immunities=["Ground"])

ice_type = Type(type_name="\033[1;36mIce\033[0m",
                strengths=["Grass", "Flying", "Dragon", "Ground"],
                weaknesses=["Fire", "Fighting", "Steel", "Rock"],
                resistances=["Ice"],
                immunities=[])

fighting_type = Type(type_name="\033[38;5;124m\033[1mFighting\033[0m",
                     strengths=["Rock", "Normal", "Steel", "Ice", "Dark"],
                     weaknesses=["Psychic", "Flying", "Fairy"],
                     resistances=["Bug", "Rock", "Dark"],
                     immunities=[])

poison_type = Type(type_name="\033[38;5;127m\033[1mPoison\033[0m",
                   strengths=["Grass", "Fairy"],
                   weaknesses=["Psychic", "Ground"],
                   resistances=["Grass", "Fighting", "Bug", "Fairy"],
                   immunities=[])

ground_type = Type(type_name="\033[38;5;136m\033[1mGround\033[0m",
                   strengths=["Fire", "Steel", "Poison", "Rock", "Electric"],
                   weaknesses=["Grass", "Water", "Ice"],
                   resistances=["Rock"],
                   immunities=["Poison", "Electric"])

psychic_type = Type(type_name="\033[38;5;199m\033[1mPsychic\033[0m",
                    strengths=["Fighting", "Poison"],
                    weaknesses=["Ghost", "Bug", "Dark"],
                    resistances=["Psychic", "Fighting"],
                    immunities=[])
bug_type = Type(type_name="\033[38;5;154m\033[1mBug\033[0m", 
                strengths=["Grass", "Dark", "Psychic"],
                weaknesses=["Fire", "Rock", "Flying"],
                resistances=["Grass", "Ground", "Fighting"],
                immunities=[])

rock_type = Type(type_name="\033[38;5;180m\033[1mRock\033[0m",
                 strengths=["Flying", "Bug", "Fire", "Ice"],
                 weaknesses=["Fighting", "Water", "Ground", "Grass", "Steel"],
                 resistances=["Fire", "Flying", "Poison", "Bug", "Normal"],
                 immunities=[])

ghost_type = Type(type_name="\033[38;5;92m\033[1mGhost\033[0m",
                  strengths= ["Ghost", "Psychic"],
                  weaknesses=["Dark", "Ghost"],
                  resistances=["Bug", "Poison"],
                  immunities=["Normal", "Fighting"])

dragon_type = Type(type_name= "\033[38;5;99m\033[1mDragon\033[0m",
                   strengths= ["Dragon"],
                   weaknesses= ["Ice", "Dragon", "Fairy"],
                   resistances= ["Fire", "Water", "Grass", "Electric"],
                   immunities= [])

dark_type = Type(type_name= "\033[38;5;95m\033[1mDark\033[0m",
                 strengths= ["Psychic", "Ghost"],
                 weaknesses= ["Fighting", "Bug", "Fairy"],
                 resistances= ["Dark", "Ghost"],
                 immunities= ["Psychic"])

steel_type = Type(type_name = "\033[38;5;251m\033[1mSteel\033[0m",
                  strengths= ["Fairy", "Rock", "Ice"],
                  weaknesses= ["Fighting", "Fire", "Ground"],
                  resistances= ["Steel", "Dragon", "Bug", "Rock", "Grass", "Ice", "Flying", "Fairy"],
                  immunities= ["Psychic", "Poison"])

fairy_type = Type(type_name= "\033[38;5;207m\033[1mFairy\033[0m",
                  strengths= ["Dragon", "Fighting", "Dark"],
                  weaknesses= ["Poison", "Steel"],
                  resistances= ["Dragon", "Bug", "Dark", "Fighting"],
                  immunities= [])
normal_type = Type(type_name= "\033[1mNormal\033[0m",
                   strengths= [],
                   weaknesses=["Fighting"],
                   resistances= [],
                   immunities= ["Ghost"])

none_type = Type(type_name = "None",
                 strengths=[],
                 weaknesses=[],
                 resistances=[],
                 immunities=[])


# chris use this for blank status or just initialization :
blank_status = Status(
    atk_stage=1.0,
    def_stage=1.0,
    sp_atk_stage=1.0,
    sp_def_stage=1.0,
    speed_stage=1.0,
    physical_status=[]
)
 
# ---------------------------------------------------------
# MOVE FUNCTIONS

# Purpose: Generates a random number from 1 to 100 for move accuracy calculations
def random_accuracy() -> int:
    num = random.randint(1,100)
    return num
    
# Purpose: To apply and return the damage done to a single pokemon 
@dispatch(Pokemon, Pokemon, Move)
def damage_calculation(user : Pokemon, target : Pokemon, move : Move) -> int:
    # If the move used is a Physical move
    if move.category == "Physical":
        damage = (((22 * move.power * (user._attack/target._defense)) / 50) * burn(user, move) * reflect(target) + 2) * critical_hit(move) * random_multiplier() * stab_bonus(user, move) * super_effective_type1_multiplier(target, move) * super_effective_type2_multiplier(target, move)
    # If the move used is a Special move
    elif move.category == "Special":
        damage = (((22 * move.power * (user._sp_attack/target._sp_defense)) / 50) * light_screen(target) + 2) * critical_hit(move) * random_multiplier() * stab_bonus(user, move) * super_effective_type1_multiplier(target, move) * super_effective_type2_multiplier(target, move)
    

    # For if a pokemon hurts itself in confusion
    else:
        damage = (((22 * move.power * (user._attack/user._defense)) / 50) * burn(user, move) * reflect(target) + 2) * random_multiplier() 
    
    # Applying the damage
    target._hp -= int(damage)

    # Returning the damage for displaying later on
    return int(damage)

# Purpose: To apply and return the damage done to multiple pokemon 
@dispatch(Pokemon, Pokemon, Pokemon, Move)
def damage_calculation(user : Pokemon, target : Pokemon, target2 : Pokemon, move : Move) -> int:
    if move.category == "Physical":
        # Damage done to the first target
        damage = (((22 * move.power * (user._attack/target._defense)) / 50) * burn(user, move) * reflect(target) * 0.75 + 2) * critical_hit(move) * random_multiplier() * stab_bonus(user, move) * super_effective_type1_multiplier(target, move) * super_effective_type2_multiplier(target, move)
        # Damage done to the second target
        damage2 = (((22 * move.power * (user._attack/target2._defense)) / 50) * burn(user, move) * reflect(target) * 0.75 + 2) * critical_hit(move) * random_multiplier() * stab_bonus(user, move) * super_effective_type1_multiplier(target2, move) * super_effective_type2_multiplier(target2, move)    

    elif move.category == "Special":
        damage = (((22 * move.power * (user._sp_attack/target._sp_defense)) / 50) * light_screen(target) * 0.75 + 2) * critical_hit(move) * random_multiplier() * stab_bonus(user, move) * super_effective_type1_multiplier(target, move) * super_effective_type2_multiplier(target, move)
        damage2 = (((22 * move.power * (user._sp_attack/target2._sp_defense)) / 50) * light_screen(target) * 0.75 + 2) * critical_hit(move) * random_multiplier() * stab_bonus(user, move) * super_effective_type1_multiplier(target2, move) * super_effective_type2_multiplier(target2, move)
    
    else:
        return
    
    # Applying the damage to both targets' hp
    target._hp -= int(damage)
    target2._hp -= int(damage2)

    # Returning the damage for displaying later on
    return int(damage), int(damage2)
    
# Purpose: To apply STAB (Same type attack bonus) to the damage multiplier
def stab_bonus(pokemon : Pokemon, move : Move) -> float:
    # If the pokemons type matches the moves type
    if pokemon.type1 == move.type or pokemon.type2 == move.type:
        return 1.5
    else:
        return 1

# Purpose: To apply a burn multiplier to the damage multiplier
def burn(user : Pokemon, move : Move) -> float:
    for status in user._status.physical_status:
        if status.condition == "Burned" and move.category == "Physical":
            return 0.5        
        
    return 1   

# Purpose: Multiplier for if the target pokemon has Reflect active
def reflect(target : Pokemon):
    for status in target._status.physical_status:
        if status.condition == "Reflect":
            return 0.5
      
    return 1

# Purpose: Multiplier for if the target pokemon has Light Screen active
def light_screen(target : Pokemon):
    for status in target._status.physical_status:
        if status.condition == "Screen":
            return 0.5
       
    return 1



# Purpose: To apply a multiplier for a move against a pokemon's first type
def super_effective_type1_multiplier(target: Pokemon, move : Move):
    if move.type in target.type1.immunities:
        return 0
    elif move.type in target.type1.weaknesses:
        return 2
    elif move.type in target.type1.resistances:
        return 0.5
    else:
        return 1

# Purpose: To apply a multiplier for a move against a pokemon's second type
def super_effective_type2_multiplier(target: Pokemon, move : Move):
    if move.type in target.type2.immunities:
        return 0
    elif move.type in target.type2.weaknesses:
        return 2
    elif move.type in target.type2.resistances:
        return 0.5
    else:
        return 1



# Purpose: To apply a critical hit multiplier to the damage calculation
def critical_hit(move : Move) -> float:
    crit = random.uniform(1,100)
    if move.name == "Night Slash" or move.name == "Stone Edge":
        if crit <= 18.75:
            print("It's a critical hit!")
            return 1.5
        else:
            return 1
    # 6.25% chance of landing a critical hit
    if crit <= 6.25:
        print("It's a critical hit!")
        return 1.5
    else:
        return 1

# Purpose: To apply a multiplier that can slightly fluctuate (natural variation) to the damage calculation
def random_multiplier() -> int:
    random_number = random.randint(85,100) / 100
    return random_number

# Purpose: Gets the pokemon's status condition (helper function for has_other_status)
def get_status_condition(pokemon : Pokemon):
    for status in pokemon._status.physical_status:
        if status.condition in ["Burned", "Paralyzed", "Poisoned", "Asleep", "Frozen"]:
            return status.condition
    
    return ""
    
# Purpose: Checks if the target pokemon already has a non-volatile status condition (Burn, paralyze, etc.) 
def has_other_status(pokemon : Pokemon):
    status_condition = get_status_condition(pokemon)
    if status_condition != "":
        print(f"{pokemon.name} is already {status_condition}!")
        return True
    else:
        return False


# Charizard Moves

class DragonDance(Move):
    def __init__(self):
        super().__init__("Dragon Dance", "Dragon", 0, 100, 100, "Attack and Speed increased", "Status", 0, "None")

    # Move information
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[0m\033[38;5;99m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Raises user's Attack and Speed by one stage each.
        """
    
    def use_move(self, user : Pokemon, target : Pokemon = None, target2 : Pokemon = None):
        if self.can_move(user):
            user._attack = user._attack * 1.5
            user._speed = user._speed * 1.5
            print(f"{user.name} used Dragon Dance! {user.name}'s {self.status_effect}!")

class HeatWave(Move):
    def __init__(self):
        super().__init__("Heat Wave", "Fire", 95, 90, 10, "Burned", "Special", 0, "All")

    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[1;31m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage to both targets and has a 10% chance of inflicting Burn
        """

  
    def use_move(self, user: Pokemon, target : Pokemon):
        if self.can_move(user):

            move_statement(self, user, target)
            
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")
           

            # Apply Burn to the target (10% chance)
            if random_accuracy() <= self.effect_chance:
                target._status.physical_status.append(PhysicalStatus("Burned", 0, -1))
                print(f"{target.name} is now Burned!")
               

    
                    


# Charizard will use Air Slash

class DragonClaw(Move):
    def __init__(self):
        super().__init__("Dragon Claw", "Dragon", 80, 100, 0, "", "Physical", 0, "Single")

    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[0m\033[38;5;99m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage.
        """
    
    
    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):
            move_statement(self, user, target)
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")






# Ampharos moves

class ThunderWave(Move):
    def __init__(self):
        super().__init__("Thunder Wave", "Electric", 0, 90, 100, "Paralyzed", "Status", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[1;33m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Paralyzes the opponent.
        """
    
    
    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):
            if has_other_status(target):
                return
            
            else:
                target._status.physical_status.append(PhysicalStatus("Paralyzed", 0, -1))
                print(f"{user.name} used {self.name}! {target.name} is now Paralyzed!")

    
class LightScreen(Move):
    def __init__(self):
        super().__init__("Light Screen", "Psychic", 0, 100, 0, "Screen", "Status", 0, "None")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;199m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Reduces damage from Special attacks by 50%, for 5 turns.
        """

    def use_move(self, user : Pokemon):
        if self.can_move(user):
            print(f"{user.name} used {self.name}!")
            user._status.physical_status.append(PhysicalStatus("Screen", 0, 5))
            print(f"{user.name} used {self.name}! {user.name}'s Special Defense increased for 5 turns!")



class PowerGem(Move):
    def __init__(self):
        super().__init__("Power Gem", "Rock", 80, 100, 0, "", "Special", 0, "Single")

    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;180m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage.
        """
    
    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):
            move_statement(self, user, target)
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")


class Thunder(Move):
    def __init__(self):
        super().__init__("Thunder", "Electric", 110, 70, 30, "Paralyzed", "Special", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[1;33m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage and has a 30% chance of paralyzing the target.
        """
    


    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):

            move_statement(self, user, target)
            damage = damage_calculation(user, target, self)

            # Apply Paralysis (30% chance)
            if random_accuracy() <= self.effect_chance:
                target._status.physical_status.append(PhysicalStatus("Paralyzed", 0, -1))
                print(f"{target.name} is now Paralyzed!")
            
            print(f"{target.name} took {damage} damage!")


# Swampert moves

class Liquidation(Move):
    def __init__(self):
        super().__init__("Liquidation", "Water", 85, 100, 20, "LowerDef", "Physical", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[1;34m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage and may lower opponent's Defense. (20% chance)
        """
        


    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):

            move_statement(self, user, target)
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")

            # Attempt to decrease target's defense by 1 stage after the damage is applied
            target._defense *= target._status.apply_stage_debuff(target, "def_stage", 20)
            

            

class Earthquake(Move):
    def __init__(self):
        super().__init__("Earthquake", "Ground", 100, 100, 0, "", "Physical", 0, "All")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;136m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage.
        """

    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):

            move_statement(self, user, target)
          
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")
         



class RockSlide(Move):
    def __init__(self):
        super().__init__("Rock Slide", "Rock", 75, 90, 30, "Flinch", "Physical", 0, "All")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;180m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage and has a 30% chance of causing the target to flinch (if the target has not yet moved).
        """

    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):
            # Apply Flinch to both targets (30% chance)
            if random_accuracy() <= self.effect_chance:
                target._status.physical_status.append(PhysicalStatus("Flinch", 0, -1))
            

            move_statement(self, user, target)
            
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")
          


class Blizzard(Move):
    def __init__(self):
        super().__init__("Blizzard", "Ice", 110, 70, 10, "Freeze", "Special", 0, "All")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[1;36m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage to both targets and has a 10% chance of freezing each target.
        """
    
    def use_move(self, user : Pokemon, target : Pokemon):
         if self.can_move(user):
            # Apply Frozen to both targets (10% chance)
            if random_accuracy() <= self.effect_chance:
                target._status.physical_status.append(PhysicalStatus("Frozen", 0, 0))
           

            move_statement(self, user, target)
            
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")

# Metagross moves

class ZenHeadbutt(Move):
    def __init__(self):
        super().__init__("Zen Headbutt", "Psychic", 80, 90, 20, "Flinch", "Physical", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;199m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage and has a 20% chance of causing the target to flinch (if the target has not yet moved).
        """
    
    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):
            # Apply Flinch (20% chance)
            if random_accuracy() <= self.effect_chance:
                target._status.physical_status.append(PhysicalStatus("Flinch", 0, -1))
            
            move_statement(self, user, target)
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")


class MeteorMash(Move):
    def __init__(self):
        super().__init__("Meteor Mash", "Steel", 90, 90, 20, "UserAtkUp", "Physical", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;251m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage and has a 20% chance of raising the user's Attack by one stage.
        """
    
    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):

            move_statement(self, user, target)
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")

            # Attempt to multiply user's attack stat by 1 stage after the damage is applied
            user._attack *= user._status.apply_stage_boost(user, "atk_stage", 20)
         
            



class IronDefense(Move):
    def __init__(self):
        super().__init__("Iron Defense", "Steel", 0, 100, 100, "Defense grew sharply!", "Status", 0, "None")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;251m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Raises the user's Defense by two stages.
        """

    def use_move(self, user : Pokemon):
        if self.can_move(user):
            # Increase user's defense by 2 stages
            user._defense *= user._status.apply_stage_boost(user, "def_stage", 100)
            user._defense *= user._status.apply_stage_boost(user, "def_stage", 100)
            print(f"{user.name}'s defense grew sharply!")
           
            

class HammerArm(Move):
    def __init__(self):
        super().__init__("Hammer Arm", "Fighting", 100, 90, 100, "UserSpeedDown", "Physical", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;124m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage but lowers the user's Speed by one stage after attacking.
        """

    
    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):

            move_statement(self, user, target)
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")

            # Decrease the user's speed stat by 1 stage after the damage is applied
            user._speed *= user._status.apply_stage_debuff(user, "speed_stage", 100)
            



# Abomasnow moves

class IcyWind(Move):
    def __init__(self):
        super().__init__("Icy Wind", "Ice", 55, 95, 100, "LowerSpeed", "Special", 0, "Single")

    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[1;36m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage and lowers the target's Speed by one stage.
        """

    
    def use_move(self, user : Pokemon, target : Pokemon, target2 : Pokemon = None):
        if self.can_move(user):

            move_statement(self, user, target)
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")

            # Decrease target's speed stat by 1 stage after the damage is applied
            target._speed *= target._status.apply_stage_debuff(target, "speed_stage", 100)
        

class WoodHammer(Move):
    def __init__(self):
        super().__init__("Wood Hammer", "Grass", 120, 100, 0, "", "Physical", 0, "Single")

    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[1;32m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage, but the user receives 1⁄3 of the damage it inflicted in recoil.
        """

    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):
            move_statement(self, user, target)
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")

            # User takes 1/3 damage of the damage dealt to the target
            apply_recoil(user, damage, 1/3)



class GigaDrain(Move):
    def __init__(self):
        super().__init__("Giga Drain", "Grass", 75, 100, 0, "", "Special", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[1;32m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage and the user will recover 50% of the HP drained.
        """


    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):
            move_statement(self, user, target)
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")

            
            hp_stolen = int((damage * .50))

            user._hp = min(user._hp + hp_stolen, user.max_hp)

            print(f"{user.name} stole {hp_stolen} HP from {target.name}!")


class SheerCold(Move):
    def __init__(self):
        super().__init__("Sheer Cold", "Ice", 0, 30, 100, "KO", "Special", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[1;36m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m If it hits, It is guaranteed to make the opponent faint. .
        """
    
    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):
            target._hp = 0
            print(f"{user.name} used {self.name} on {target.name}! It's a one hit KO!")


# Dusknoir moves

class ShadowPunch(Move):
    def __init__(self):
        super().__init__("Shadow Punch", "Ghost", 60, 100, 0, "", "Physical", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;92m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage.
        """
    
    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):
            move_statement(self, user, target)
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")
            


class ConfuseRay(Move):
    def __init__(self):
        super().__init__("Confuse Ray", "Ghost", 0, 100, 100, "Confused", "Status", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;92m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Causes the target to become confused.
        """
    
    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):
            for status in target._status.physical_status:
                if status.condition == "Confused":
                    print(f"{target.name} is already confused!")
                    return
                
            target._status.physical_status.append(PhysicalStatus("Confused", 0, random.randint(2,5)))
            print(f"{user.name} used {self.name}! {target.name} is now Confused!")

class MeanLook(Move):
    def __init__(self):
        super().__init__("Mean Look", "Normal", 0, 100, 100, "", "Status", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType: {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Opponent cannot switch.
        """
    # UNFINISHED
    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):
            move_statement(self, user, target)
            target._status.physical_status.append(PhysicalStatus("Trapped", 0, -1))
            print(f"{target.name} can no longer escape!")

class DestinyBond(Move):
    def __init__(self):
        super().__init__("Destiny Bond", "Ghost", 0, 100, 100, "Bonded", "Status", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;92m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m If the user faints, the opponent also faints.
        """
    
        
    # UNFINISHED
    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):
            move_statement(self, user, target)
            target._status.physical_status.append(PhysicalStatus("Bonded", 0, 1))
            print(f"{user.name} is hoping to take {target.name} down with it!")

# Pangoro moves

class NightSlash(Move):
    def __init__(self):
        super().__init__("Night Slash", "Dark", 70, 100, 20, "Critical", "Physical", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;95m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage and has an increased critical hit chance
        """
    

    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):
            move_statement(self, user, target)
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")

class CloseCombat(Move):
    def __init__(self):
        super().__init__("Close Combat", "Fighting", 120, 100, 100, "Defense and Special Defense fell", "Physical", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;124m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage but lowers the user's Defense and Special Defense by one stage each after attacking.
        """
    
    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):
            move_statement(self, user, target)
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")
            

            user._defense *= user._status.apply_stage_debuff(user, "def_stage", 100)
            user._sp_defense *= user._status.apply_stage_debuff(user, "sp_def_stage", 100)
            


class BulletPunch(Move):
    def __init__(self):
        super().__init__("Bullet Punch", "Steel", 40, 100, 0, "", "Physical", 1, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;251m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m deals damage and has a priority of +1.
        """
    
    
    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):
            move_statement(self, user, target)
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")

class XScissor(Move):
    def __init__(self):
        super().__init__("X-Scissor", "Bug", 80, 100, 0, "", "Physical", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;154m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage.
        """
    
    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):
            move_statement(self, user, target)
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")

# Nagandel moves

class Toxic(Move):
    def __init__(self):
        super().__init__("Toxic", "Poison", 0, 90, 100, "Poisoned", "Status", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;127m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Inflicts poison on the target.
        """
    
    
    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):
            if has_other_status(target):
                return
            else:
                move_statement(self, user, target)
                target._status.physical_status.append(PhysicalStatus("Poisoned", 0, -1))
                print(f"{target.name} was badly poisoned!")
           

class DragonPulse(Move):
    def __init__(self):
        super().__init__("Dragon Pulse", "Dragon", 85, 100, 0, "", "Special", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;99m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage.
        """
    
    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):
            move_statement(self, user, target)
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")

class SludgeWave(Move):
    def __init__(self):
        super().__init__("Sludge Wave", "Poison", 95, 100, 10, "Poisoned", "Special", 0, "Single")

    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;127m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage and has a 10% chance of poisoning the target.
        """
    
    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):
            move_statement(self, user, target)
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")

            # 10% chance to inflict poison
            if random_accuracy() <= self.effect_chance:
                target._status.physical_status.append(PhysicalStatus("Poisoned", 0, -1))
                print(f"{target.name} was badly poisoned!")


# Diancie moves

class DiamondStorm(Move):
    def __init__(self):
        super().__init__("Diamond Storm", "Rock", 100, 95, 50, "UserDefUp2", "Physical", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;180m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage and has a 50% chance of raising the user's Defense by 0-2 stages
        """
    
    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):

            move_statement(self, user, target)
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")

            # Increase user's defense stat by 0-2 stages after the damage is applied
            user._defense *= user._status.apply_stage_boost(user, "def_stage", 50)
            user._defense *= user._status.apply_stage_boost(user, "def_stage", 50)

        

class Reflect(Move):
    def __init__(self):
        super().__init__("Reflect", "Psychic", 0, 100, 0, "", "Status", 0, "None")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;199m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Reduces damage from Physical attacks by 50%, for 5 turns.
        """
    
    def use_move(self, user : Pokemon):
        if self.can_move(user):
            print(f"{user.name} used {self.name}!")
            user._status.physical_status.append(PhysicalStatus("Reflect", 0, 5))
            print(f"{user.name} used {self.name}! {user.name}'s Defense increased for 5 turns!")

class Moonblast(Move):
    def __init__(self):
        super().__init__("Moonblast", "Fairy", 95, 100, 30, "Special Attack fell", "Special", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;207m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage and has a 30% chance of lowering the target's Special Attack by one stage.
        """
    
    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):

            move_statement(self, user, target)
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")

            # Decrease target's special attack stat by 1 stage after the damage is applied
            target._sp_attack *= target._status.apply_stage_debuff(target, "sp_atk_stage", 30)
            
        


# Guzzlord moves

class Crunch(Move):
    def __init__(self):
        super().__init__("Crunch", "Dark", 80, 100, 20, "DefDown", "Physical", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;95m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage and has a 20% chance of lowering the target's Defense by one stage.
        """

    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):

            move_statement(self, user, target)
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")

            # Decrease target's defense stat by 1 stage after the damage is applied
            target._defense *= target._status.apply_stage_boost(target, "def_stage", 20)

            
    
class DragonRush(Move):
    def __init__(self):
        super().__init__("Dragon Rush", "Dragon", 100, 75, 20, "Flinch", "Physical", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;99m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage and has a 20% chance of causing the target to flinch.
        """
    
    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):
            # Apply Flinch (20% chance)
            if random_accuracy() <= self.effect_chance:
                target._status.physical_status.append(PhysicalStatus("Flinch", 0, -1))
            
            move_statement(self, user, target)
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")

class DragonTail(Move):
    def __init__(self):
        super().__init__("Dragon Tail", "Dragon", 60, 90, 0, "", "Physical", -6, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;99m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage and makes the target switch Pokemon.
        """
    # UNFINISHED
    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):
            
            move_statement(self, user, target)
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")
    

class BrickBreak(Move):
    def __init__(self):
        super().__init__("Brick Break", "Fighting", 75, 100, 0, "", "Physical", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;124m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage and removes the effects of Reflect and Light Screen before attacking.
        """
    
    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):
            move_statement(self, user, target)
            # Breaks LightScreen or Reflect if the target has it active
            for status in target._status.physical_status:
                if status.condition == "Reflect" or status.condition == "Screen":
                    target._status.physical_status.remove(status)
                    print(f"{target.name}'s barrier was broken!")
            
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")

# Drowsee moves 

class Hypnosis(Move):
    def __init__(self):
        super().__init__("Hypnosis", "Psychic", 0, 60, 100, "Asleep", "Status", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;199m\033[1m  {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Puts the target to sleep
        """
    
    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):
            if has_other_status(target):
                return
                
            target._status.physical_status.append(PhysicalStatus("Asleep", 0, -1))
            print(f"{user.name} used {self.name}! {target.name} is now Asleep!")

class NightShade(Move):
    def __init__(self):
        super().__init__("Night Shade", "Ghost", 50, 100, 0, "", "Special", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;92m\033[1m  {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Always deals 50 damage no matter what.
        """
    
    
    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):
            print(f"{user.name} used {self.name}!")
            # Does 50 damage no matter what
            target._hp -= 50
            print(f"{target.name} took {self.power} damage!")
            

class Psychic(Move):
    def __init__(self):
        super().__init__("Psychic", "Psychic", 90, 100, 10, "Special Defense fell", "Special", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;199m\033[1m  {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage and has a 10% chance of lowering the target's Special Defense by one stage.
        """
    
    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):

            move_statement(self, user, target)
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")

            # Decrease target's special attack stat by 1 stage after the damage is applied
            target._sp_defense *= target._status.apply_stage_debuff(target, "sp_def_stage", 10)
            
            

# Drowsee will also know Reflect

# Cottonee moves

# class StunSpore(Move):
#      def __init__(self):
#         super().__init__("Stun Spore", "Grass", 0, 75, 100, "Paralyzed", "Status")

# class Protect(Move):
#      def __init__(self, priority):
#         super().__init__("Protect", "Normal", 0, 100, 0, "", "Status")
#         self.priority = 4

# class Endeavor(Move):
#      def __init__(self):
#         super().__init__("Endeavor", "Normal", 0, 100, 0, "", "Physical")
    
# class Endure(Move):
#      def __init__(self, priority):
#         super().__init__("Endure", "Normal", 0, 100, 0, "", "Status")
#         self.priority = 4

# Kyruem moves

class BreakingSwipe(Move):
    def __init__(self):
        super().__init__("Breaking Swipe", "Dragon", 60, 100, 100, "Attack fell", "Physical", 0, "All")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;99m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Hits both targets and lowers their attack. (100% chance)
        """

    def use_move(self, user : Pokemon, target : Pokemon):
         if self.can_move(user):

            move_statement(self, user, target)
            
            damage = damage_calculation(user, target, self)

            target._attack *= target._status.apply_stage_debuff(target, "atk_stage", 100)
       
            print(f"{target.name} {self.status_effect}!")
            print(f"{target.name} took {damage} damage!")

            

# Kyreum will learn Icy Wind
    


# Kyreum will learn Draco Meteor


# Kyruem will use Sheer Cold

# Torracat moves

class WillOWisp(Move):
    def __init__(self):
        super().__init__("Will-O-Wisp", "Fire", 0, 85, 100, "Burned", "Status", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[1;31m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Causes the target to become burned.
        """

    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):
            if has_other_status(target):
                return
                
        target._status.physical_status.append(PhysicalStatus("Burned", 0, -1))
        print(f"{target.name} was burned!")
        

# Torracut will use Crunch

# class Roar(Move):
#     def __init__(self):
#         super().__init__("Roar", "Normal", 0, 100, 0, "", "Status")

# Torracat will use FlareBlitz
class FlareBlitz(Move):
    def __init__(self):
        super().__init__("Flare Blitz", "Fire", 120, 100, 10, "Burned", "Physical", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[1;31m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage and has a 10% chance of burning the target, but the user receives 1⁄3 of the damage it inflicted in recoil.
        """

    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):
            move_statement(self, user, target)
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")

            # 10% chance to inflict poison
            if random_accuracy() <= self.effect_chance:
                target._status.physical_status.append(PhysicalStatus("Burned", 0, -1))
                print(f"{target.name} was Burned!")
            
            # User takes 1/3 damage of the damage dealt to the target
            apply_recoil(user, damage, 1/3)

# Mudsdale moves 

# Mudsale will use Earthquake

class LowSweep(Move):
    def __init__(self):
        super().__init__("Low Sweep", "Fighting", 65, 100, 100, "LowerSpeed", "Physical", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;124m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage and lowers the target's Speed by one stage.
        """
    
    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):

            move_statement(self, user, target)
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")

            # Decrease target's speed stat by 1 stage after the damage is applied
            target._speed *= target._status.apply_stage_debuff(target, "speed_stage", 100)
            print(f"{target.name}'s speed fell!")

class Counter(Move):
    def __init__(self):
        super().__init__("Counter", "Fighting", 150, 100, 0, "", "Physical", -5, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;124m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m User goes after the target, but deals big damage.
        """
    
    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):

            move_statement(self, user, target)
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")


class StoneEdge(Move):
    def __init__(self):
        super().__init__("Stone Edge", "Rock", 100, 80, 0, "", "Physical", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;180m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage and has an increased critical hit ratio .
        """
    
    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):
            move_statement(self, user, target)
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")

# Piplup moves

# class Charm(Move):
#     def __init__(self):
#         super().__init__("Charm", "Fairy", 0, 100, 100, "LowerAtk2", "Status")



# Vikavolt moves

class BugBuzz(Move):
    def __init__(self):
        super().__init__("Bug Buzz", "Bug", 90, 100, 10, "Special Defense fell!", "Special", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;154m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage and has a 10% chance of lowering the target's Special Defense by one stage.
        """


    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):

            move_statement(self, user, target)
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")

            # Decrease target's special attack stat by 1 stage after the damage is applied
            target._sp_defense *= target._status.apply_stage_debuff(target, "sp_def_stage", 10)
            
            print(f"{target.name}'s {self.status_effect}!")

class Thunderbolt(Move):
    def __init__(self):
        super().__init__("Thunderbolt", "Electric", 90, 100, 10, "Paralyzed", "Special", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[1;33m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage and has a 10% chance of paralyzing the target.
        """

    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):

            move_statement(self, user, target)
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")

            # Apply Paralysis (10% chance)
            if random_accuracy() <= self.effect_chance:
                target._status.physical_status.append(PhysicalStatus("Paralyzed", 0, -1))
                print(f"{target.name} is now Paralyzed!")
            
           

    
    

# Used by Charizard and Vikavolt
class AirSlash(Move):
    def __init__(self):
        super().__init__("Air Slash", "Flying", 75, 95, 0, "", "Special", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;147m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage and has a 30% chance of causing the target to flinch (if the target has not yet moved).
        """
    
    def use_move(self, user : Pokemon, target: Pokemon):
        if target.has_moved == False:
            if random_accuracy() <= 30:
                target._status.physical_status.append(PhysicalStatus("Flinch", 0, -1))
        
        move_statement(self, user, target)
        damage = damage_calculation(user, target, self)
        print(f"{target.name} took {damage} damage!")

# Vikavolt will use thunderwave

# Snorlax moves

class BodySlam(Move):
    def __init__(self):
        super().__init__("Body Slam", "Normal", 85, 100, 30, "Paralyze", "Physical", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType: {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage and has a 30% chance of paralyzing the target.
        """
    
    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):

            move_statement(self, user, target)
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")

            # Apply Paralysis (30% chance)
            if random_accuracy() <= self.effect_chance:
                target._status.physical_status.append(PhysicalStatus("Paralyzed", 0, -1))
                print(f"{target.name} is now Paralyzed!")

class Rest(Move):
    def __init__(self):
        super().__init__("Rest", "Psychic", 0, 100, 100, "Asleep", "Status", 0, "None")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;199m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Puts user to sleep, but user is fully healed.
        """
    
    def use_move(self, user : Pokemon):
        if self.can_move(user):
            if has_other_status(user):
                print(f"{user.name} is already asleep!")
                return
            user._status.physical_status.append(PhysicalStatus("Asleep", 0, -1))
            print(f"{user.name} fell asleep!")
            user._hp = user.max_hp

            print(f"{user.name} slept and became healthy!")
 
class SleepTalk(Move):
    def __init__(self):
        super().__init__("Sleep Talk", "Normal", 0, 100, 0, "", "Status", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType: {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power} \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m User performs one of its own moves while sleeping.
        """
    
    def use_move(self, user : Pokemon, target : Pokemon):
        if "Asleep" in user._status.physical_status:
            random_number = random.randint(1,3)
            if random_number == 1:
                BodySlam().use_move(user, target)
            elif random_number == 2:
                Crunch().use_move(user, target)
            else:
                Rest().use_move(user)
        
        else:
            print(f"{user.name} used {self.name}! But it failed!")
            return
        
class HealingWish(Move):
    def __init__(self):
        super().__init__("Healing Wish", "Psychic", 0, 100, 0, "", "Status", 0, "None")

    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;199m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power}  \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m The user faints and the next Pokémon released is fully healed.
        """
    
    # WIP
    def use_move(self, user : Pokemon, trainer : Trainer):
        if self.can_move(user):
            user._hp == 0
            print(f"{user.name} used Healing Wish!")
            print(f"{user.name} has fainted!")
            handlePokemon(trainer, False) 
            trainer.active_pokemon.hp = trainer.active_pokemon.max_hp
            print(f"{trainer.active_pokemon} was fully healed!")



# -- Used by Gengar

class ShadowBall(Move):
    def __init__(self):
        super().__init__("Shadow Ball", "Ghost", 80, 100, 20, "Special Defense fell!", "Special", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;92m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power} \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage and has a 20% chance of lowering the target's Special Defense by one stage.
        """
    
    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):

            move_statement(self, user, target)
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")

            # Decrease target's special defense stat by 1 stage after the damage is applied
            target._sp_defense *= target._status.apply_stage_debuff(target, "sp_def_stage", 20)
            
            

class SludgeBomb(Move):
    def __init__(self):
        super().__init__("Sludge Bomb", "Poison", 90, 100, 30, "Poisoned", "Special", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;127m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power} \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage and has a 30% chance of poisoning the target.
        """

    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):

            move_statement(self, user, target)
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")

            # Inflict poison (30% chance)
            if random_accuracy() <= self.effect_chance:
                target._status.physical_status.append(PhysicalStatus("Poisoned", 0, -1))
                print(f"{target.name} was badly poisoned!")

class FocusBlast(Move):
    def __init__(self):
        super().__init__("Focus Blast", "Fighting", 120, 70, 10, "Special Defense fell!", "Special", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;124m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power} \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage and has a 10% chance of lowering the target's Special Defense by one stage.
        """

    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):

            move_statement(self, user, target)
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")

            # Decrease target's special attack stat by 1 stage after the damage is applied
            target._sp_defense *= target._status.apply_stage_debuff(target, "sp_def_stage", 10)
            
            print(f"{target.name}'s {self.status_effect}!")
 
# Gengar will use Thunderbolt
 
# -- Used by Rayquaza

class DragonAscent(Move):
    def __init__(self):
        super().__init__("Dragon Ascent", "Flying", 120, 100, 100, "Defense and Special Defense fell", "Physical", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;147m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power} \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage but lowers the user's Defense and Special Defense by one stage each after attacking.
        """
    
    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):
            # Mega evolve Rayquaza
            print(f"Rayquazza has mega evolved!")
            user.attack += 50
            user.defense += 20
            user.sp_attack += 50
            user.sp_defense += 20
            user.speed += 10

            move_statement(self, user, target)
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")

            # Decrease user's special defense and defense stat by 1 stage after the damage is applied
            user._defense *= user._status.apply_stage_debuff(user, "def_stage", 100)
            user._sp_defense *= user._status.apply_stage_debuff(user, "sp_def_stage", 100)
            
            print(f"{user.name}'s {self.status_effect}!")

 
# Rayquaza will use outrage
 

class DracoMeteor(Move):
    def __init__(self):
        super().__init__("Draco Meteor", "Dragon", 130, 90, 100, "Special Attack fell", "Special", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;99m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power} \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage but lowers the user's Special Attack by two stages after attacking.
        """
    
    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):

            move_statement(self, user, target)
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")

            # Decrease user's special attack stat by 1 stage after the damage is applied
            user._sp_attack *= user._status.apply_stage_debuff(user, "sp_atk_stage", 100)

            print(f"{user.name}'s {self.status_effect}!")

# Rayquaza will use Earthquake
 
# -- Used by Grimmsnarl

class SpiritBreak(Move):
    def __init__(self):
        super().__init__("Spirit Break", "Fairy", 75, 100, 100, "Special Attack fell", "Physical", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;207m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power} \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage and lowers the target's Special Attack by one stage. 
        """

    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):

            move_statement(self, user, target)
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")

            # Decrease target's special attack stat by 1 stage after the damage is applied
            target._sp_attack *= target._status.apply_stage_debuff(target, "sp_atk_stage", 100)
            
            print(f"{target.name}'s {self.status_effect}!")
 
class DarkestLariat(Move):
    def __init__(self):
        super().__init__("Darkest Lariat", "Dark", 85, 100, 0, "", "Physical", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;95m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power} \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage but lowers target's defense and special defense by 1 stage before attacking.
        """
    
    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):

            # Decrease user's special defense and defense stat by 1 stage before the damage is applied
            target._defense *= target._status.apply_stage_debuff(user, "def_stage", 100)
            target._sp_defense *= target._status.apply_stage_debuff(user, "sp_def_stage", 100)
            print(f"{user.name}'s {self.status_effect}!")

            move_statement(self, user, target)
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")

    
            
            

class PlayRough(Move):
    def __init__(self):
        super().__init__("Play Rough", "Fairy", 90, 90, 10, "Attack fell", "Physical", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;207m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power} \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage and has a 10% chance of lowering the target's Attack by one stage.
        """

    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):

            move_statement(self, user, target)
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")

            # Decrease target's attack stat by 1 stage after the damage is applied
            target._attack *= target._status.apply_stage_debuff(target, "atk_stage", 10)
            
            print(f"{target.name}'s {self.status_effect}!")
 
 
class BulkUp(Move):
    def __init__(self):
        super().__init__("Bulk Up", "Fighting", 0, 100, 100, "Attack and Defense grew", "Status", 0, "None")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;124m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power} \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m raises the user's Attack and Defense by one stage each.
        """

    def use_move(self, user : Pokemon):
        if self.can_move(user):
            print(f"{user.name} used {self.name}!")
            # Increase user's attack stat and defense stat by 1 stage
            user._attack *= user._status.apply_stage_boost(user, "atk_stage", 100)
            user._defense *= user._status.apply_stage_boost(user, "def_stage", 100)
            
            print(f"{user.name}'s {self.status_effect}!")
 
 
# -- Used by Garchomp

# Garchomp will use Dragon Claw
 
class SwordsDance(Move):
    def __init__(self):
        super().__init__("Swords Dance", "Normal", 0, 100, 100, "Attack sharply grew", "Status", 0, "None")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType: {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power} \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Raises the user's Attack by two stages.
        """

    def use_move(self, user : Pokemon):
        if self.can_move(user):
            print(f"{user.name} used {self.name}!")
            # Increase user's attack stat and defense stat by 1 stage
            user._attack *= user._status.apply_stage_boost(user, "atk_stage", 100)
            user._attack *= user._status.apply_stage_boost(user, "atk_stage", 100)
            
            print(f"{user.name}'s {self.status_effect}!")
 
class FireFang(Move):
    def __init__(self):
        super().__init__("Fire Fang", "Fire", 65, 95, 10, "Burned", "Physical", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[1;31m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power} \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage, has a 10% chance of burning the target and a 10% chance of making the target flinch.
        """

    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):
            
            move_statement(self, user, target)
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")

            if random_accuracy() <= self.effect_chance:
               target._status.physical_status.append(PhysicalStatus("Burned", 0, -1))
               print(f"{target.name} was Burned!")
            if random_accuracy() <= self.effect_chance:
               target._status.physical_status.append(PhysicalStatus("Flinch", 0, -1))



# Garchomp will use Earthquake
 
# -- Used by Delphox

class Flamethrower(Move):
    def __init__(self):
        super().__init__("Flamethrower", "Fire", 90, 100, 10, "Burned", "Special", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[1;31m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power} \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage and has a 10% chance of burning the target.
        """

    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):
            
            move_statement(self, user, target)
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")

            if random_accuracy() <= self.effect_chance:
               target._status.physical_status.append(PhysicalStatus("Burned", 0, -1))
               print(f"{target.name} was Burned!")
 
# Delphox will use Psychic

class DazzlingGleam(Move):
    def __init__(self):
        super().__init__("Dazzling Gleam", "Fairy", 80, 100, 0, "", "Special", 0, "All")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;207m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power} \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage and hits both targets. 
        """

    def use_move(self, user : Pokemon, target : Pokemon):
         if self.can_move(user):

            move_statement(self, user, target)
           
            damage = damage_calculation(user, target, self)

            print(f"{target.name} took {damage} damage!")
    

 
class CalmMind(Move):
    def __init__(self):
        super().__init__("Calm Mind", "Psychic", 0, 100, 100, "Special Attack and Special Defense increased", "Status", 0, "None")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;199m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power} \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Raises the user's Special Attack and Special Defense by one stage each.
        """
    
    def use_move(self, user : Pokemon):
        if self.can_move(user):
            print(f"{user.name} used {self.name}!")
            # Increase user's special attack stat and special defense stat by 1 stage
            user._sp_attack *= user._status.apply_stage_boost(user, "sp_atk_stage", 100)
            user._sp_defense *= user._status.apply_stage_boost(user, "sp_def_stage", 100)
            
            print(f"{user.name}'s {self.status_effect}!")
 
 
# -- Used by Dusk Mane Necrozma

class SunsteelStrike(Move):
    def __init__(self):
        super().__init__("Sunsteel Strike", "Steel", 100, 100, 0, "", "Physical", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;251m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power} \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage.
        """
    
    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):
            move_statement(self, user, target)
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")
            
 
class PhotonGeyser(Move):
    def __init__(self):
        super().__init__("Photon Geyser", "Psychic", 100, 100, 0, "", "Special", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;199m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power} \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage, however if the user's attack is greater than its special attack, the move uses its attack stat
        """

    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):
            move_statement(self, user, target)
            if user._attack > user._sp_attack:
                self.category = "Physical"
                damage = damage_calculation(user, target, self)
            else:
                damage = damage_calculation(user, target, self)
            
            print(f"{target.name} took {damage} damage!")
 
    

 
# Necrozma will use swords dance

# Necrozma will use earthquake



# -- Used by Iron Bundle

# class FreezeDry(Move):
#     def __init__(self):
#         super().__init__("Freeze-Dry", "Ice", 70, 100, 10, "Freeze", "Special")
 
class HydroPump(Move):
    def __init__(self):
        super().__init__("Hydro Pump", "Water", 110, 80, 0, "", "Special", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[1;34m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power} \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage.
        """

    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):
            
            move_statement(self, user, target)
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")

 
class IceBeam(Move):
    def __init__(self):
        super().__init__("Ice Beam", "Ice", 90, 100, 10, "Freeze", "Special", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[1;36m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power} \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m Deals damage and has a 10% chance of freezing the target.
        """

    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):
            
            move_statement(self, user, target)
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")

            if random_accuracy() <= self.effect_chance:
               target._status.physical_status.append(PhysicalStatus("Frozen", 0, -1))
               print(f"{target.name} is Frozen!")

 
class UTurn(Move):
    def __init__(self):
        super().__init__("U-Turn", "Bug", 70, 100, 0, "", "Physical", 0, "Single")
    
    def __repr__(self):
        return f"""
    \033[3m{self.name}\033[0m 
    \033[1mType:\033[38;5;154m\033[1m {self.type}\033[0m 
    \033[1mCategory:\033[0m {self.category} 
    \033[1mPower:\033[0m {self.power} \033[1mAccuracy:\033[0m {self.accuracy}
    \033[1mDescription:\033[0m User switches out immediately after attacking.
        """
    
    # WIP
    def use_move(self, user : Pokemon, target : Pokemon):
        if self.can_move(user):
            move_statement(self, user, target)
            damage = damage_calculation(user, target, self)
            print(f"{target.name} took {damage} damage!")

            print(f"{user.name} retreated!")
            handlePokemon(None)
 
# ---------------------------------------------------------
# POKEMON DEFINITIONS


charizard = Pokemon(
    name="Charizard",
    type1=fire_type,
    type2=flying_type,
    max_hp = 138,
    hp= 138,
    attack=89,
    defense=83,
    sp_attack=114,
    sp_defense= 90,
    speed= 105,
    moves=[DragonDance(), HeatWave(), AirSlash(), DragonClaw()],
    status= blank_status,
    legendary=False,
    is_chosen= False,
    has_moved= False
)

ampharos = Pokemon(
    name="Ampharos",
    type1=electric_type,
    type2=none_type,
    max_hp = 165,
    hp= 165,
    attack=85,
    defense=85,
    sp_attack=110,
    sp_defense= 95,
    speed= 65,
    moves=[ThunderWave(), LightScreen(), PowerGem(), Thunder()],
    status= blank_status,
    legendary=False,
    is_chosen= False,
    has_moved= False
)

swampert = Pokemon(
    name="Swampert",
    type1=water_type,
    type2=ground_type,
    max_hp = 175,
    hp= 175,
    attack=105,
    defense=95,
    sp_attack=85,
    sp_defense= 95,
    speed= 65,
    moves=[Liquidation(), Earthquake(), RockSlide(), Blizzard()],
    status= blank_status,
    legendary=False,
    is_chosen= False,
    has_moved= False
)

metagross = Pokemon(
    name="Metagross",
    type1=steel_type,
    type2=psychic_type,
    max_hp = 155,
    hp= 155,
    attack=135,
    defense=130,
    sp_attack=95,
    sp_defense= 90,
    speed= 70,
    moves=[ZenHeadbutt(), MeteorMash(), IronDefense(), HammerArm()],
    status= blank_status,
    legendary=False,
    is_chosen= False,
    has_moved= False
)
 
abomasnow = Pokemon(
    name="Abomasnow",
    type1=ice_type,
    type2=grass_type,
    max_hp = 165,
    hp= 165,
    attack=102,
    defense=95,
    sp_attack=102,
    sp_defense= 95,
    speed= 70,
    moves=[IcyWind(), WoodHammer(), GigaDrain(), SheerCold()],
    status= blank_status,
    legendary=False,
    is_chosen= False,
    has_moved= False
)
dusknoir = Pokemon(
    name="Dusknoir",
    type1=ghost_type,
    type2=none_type,
    max_hp = 137,
    hp= 137,
    attack=110,
    defense=150,
    sp_attack=65,
    sp_defense= 150,
    speed= 45,
    moves=[ShadowPunch(), ConfuseRay(), MeanLook(), DestinyBond()],
    status= blank_status,
    legendary=False,
    is_chosen= False,
    has_moved= False
)

pangoro = Pokemon(
    name="Pangoro",
    type1=dark_type,
    type2=fighting_type,
    max_hp = 167,
    hp= 167,
    attack=112,
    defense=77,
    sp_attack=67,
    sp_defense=71,
    speed= 58,
    moves=[NightSlash(), CloseCombat(), BulletPunch(), XScissor()],
    status= blank_status,
    legendary=False,
    is_chosen= False,
    has_moved= False
)
naganadel = Pokemon(
    name="Naganadel",
    type1=poison_type,
    type2=dragon_type,
    max_hp = 161,
    hp= 161,
    attack=83,
    defense=73,
    sp_attack=127,
    sp_defense=73,
    speed= 121,
    moves=[Toxic(), DragonPulse(), SludgeWave(), DragonDance()],
    status= blank_status,
    legendary=True,
    is_chosen= False,
    has_moved= False
)

diancie = Pokemon(
    name="Diancie",
    type1=rock_type,
    type2=fairy_type,
    max_hp = 100,
    hp= 100,
    attack=100,
    defense=150,
    sp_attack=100,
    sp_defense=150,
    speed= 50,
    moves=[DiamondStorm(), Reflect(), Moonblast(), ThunderWave()],
    status= blank_status,
    legendary=True,
    is_chosen= False,
    has_moved= False
)

guzzlord = Pokemon(
    name="Guzzlord",
    type1=dark_type,
    type2=dragon_type,
    max_hp = 136,
    hp= 136,
    attack=79,
    defense=53,
    sp_attack=79,
    sp_defense=53,
    speed= 34,
    moves=[Crunch(), DragonRush(), DragonTail(), BrickBreak()],
    status= blank_status,
    legendary=True,
    is_chosen= False,
    has_moved= False
)

drowsee = Pokemon(
    name="Drowsee",
    type1=psychic_type,
    type2=none_type,
    max_hp = 70,
    hp= 70,
    attack=25,
    defense=38,
    sp_attack=28,
    sp_defense=55,
    speed= 200,
    moves=[Hypnosis(), NightShade(), Reflect(), Psychic()],
    status= blank_status,
    legendary=False,
    is_chosen= False,
    has_moved= False
)
kyurem = Pokemon(
    name="Kyurem",
    type1=ice_type,
    type2=dragon_type,
    max_hp = 175,
    hp= 175,
    attack=95,
    defense=90,
    sp_attack=105,
    sp_defense=90,
    speed= 85,
    moves=[BreakingSwipe(), SheerCold(), DracoMeteor(), IcyWind()],
    status= blank_status,
    legendary=True,
    is_chosen= False,
    has_moved= False
)
torracat = Pokemon(
    name="Torracat",
    type1=fire_type,
    type2=none_type,
    max_hp = 135,
    hp= 135,
    attack=82,
    defense=67,
    sp_attack=82,
    sp_defense=67,
    speed= 90,
    moves=[FlareBlitz(), Crunch(), WillOWisp(), Rest()],
    status= blank_status,
    legendary=False,
    is_chosen= False,
    has_moved= False
)
mudsdale = Pokemon(
    name="Mudsdale",
    type1=ground_type,
    type2=none_type,
    max_hp = 175,
    hp= 175,
    attack=117,
    defense=110,
    sp_attack=77,
    sp_defense=95,
    speed= 55,
    moves=[Earthquake(), LowSweep(), Counter(), StoneEdge()],
    status= blank_status,
    legendary=False,
    is_chosen= False,
    has_moved= False
)
vikavolt = Pokemon(
    name="Vikavolt",
    type1=bug_type,
    type2=electric_type,
    max_hp = 165,
    hp= 165,
    attack=92,
    defense=97,
    sp_attack=145,
    sp_defense=97,
    speed= 63,
    moves=[BugBuzz(), Thunderbolt(), AirSlash(), ThunderWave()],
    status= blank_status,
    legendary=False,
    is_chosen= False,
    has_moved= False
)

snorlax = Pokemon(
    name="Snorlax",
    type1=normal_type,
    type2=none_type,
    max_hp = 235,
    hp= 235,
    attack=110,
    defense=75,
    sp_attack=75,
    sp_defense=110,
    speed= 30,
    moves=[BodySlam(), Crunch(), SleepTalk(), Rest()],
    status= blank_status,
    legendary=False,
    is_chosen= False,
    has_moved= False
)




# Pokemon to do:  snorlax

gardevoir = Pokemon(
    name="Gardevoir",
    type1=psychic_type,
    type2=fairy_type,
    max_hp= 123,
    hp=123,
    attack=67,
    defense=67,
    sp_attack=127,
    sp_defense=117,
    speed=82,
    moves=[Psychic(), Moonblast(), WillOWisp(), ShadowBall()],
    status=blank_status,
    legendary=False,
    is_chosen=False,
    has_moved=False
)

gengar = Pokemon(
    name="Gengar",
    type1=ghost_type,
    type2=poison_type,
    max_hp=125,
    hp=125,
    attack=72,
    defense=72,
    sp_attack=130,
    sp_defense=75,
    speed=110,
    moves=[ShadowBall(), SludgeBomb(), FocusBlast(), Thunderbolt()],
    status=blank_status,
    legendary=False,
    is_chosen=False,
    has_moved=False
)

 
rayquaza = Pokemon(      # THATS THE GOAT
    name="Rayquaza",
    type1=dragon_type,
    type2=flying_type,
    max_hp=170,
    hp=170,
    attack=150,
    defense=100,
    sp_attack=150,
    sp_defense=100,
    speed=95,
    moves=[DragonAscent(), DragonClaw(), DracoMeteor(), Earthquake()],
    status=blank_status,
    legendary=True,
    is_chosen=False,
    has_moved=False
)
 
grimmsnarl = Pokemon(
    name="Grimmsnarl",
    type1=dark_type,
    type2=fairy_type,
    max_hp= 190,
    hp=190,
    attack=140,
    defense=95,
    sp_attack=100,
    sp_defense=95,
    speed=70,
    moves=[SpiritBreak(), DarkestLariat(), PlayRough(), BulkUp()],
    status=blank_status,
    legendary=False,
    is_chosen= False,
    has_moved=False
)
 
garchomp = Pokemon(
    name="Garchomp",
    type1=dragon_type,
    type2=ground_type,
    max_hp= 183,
    hp=130,
    attack=130,
    defense=105,
    sp_attack=90,
    sp_defense=85,
    speed=102,
    moves=[Earthquake(), DragonClaw(), SwordsDance(), FireFang()],
    status=blank_status,
    legendary=False,
    is_chosen=False,
    has_moved=False
)
 
delphox = Pokemon(
    name="Delphox",
    type1=fire_type,
    type2=psychic_type,
    max_hp= 155,
    hp=155,
    attack=92,
    defense=90,
    sp_attack=132,
    sp_defense=120,
    speed=112,
    moves=[Flamethrower(), Psychic(), DazzlingGleam(), CalmMind()],
    status=blank_status,
    legendary=False,
    is_chosen=False,
    has_moved=False
)
 
duskmanenecrozma = Pokemon(
    name="Dusk Mane Necrozma",
    type1=psychic_type,
    type2=steel_type,
    max_hp=201,
    hp=201,
    attack=157,
    defense=147,
    sp_attack=117,
    sp_defense=127,
    speed=97,
    moves=[SunsteelStrike(), PhotonGeyser(), Earthquake(), SwordsDance()],
    status=blank_status,
    legendary=True,
    is_chosen=False,
    has_moved=False
)
 
ironbundle = Pokemon(
    name="Iron Bundle",
    type1=ice_type,
    type2=water_type,
    max_hp=116,
    hp=116,
    attack=121,
    defense=131,
    sp_attack=141,
    sp_defense=101,
    speed=161,
    moves=[Blizzard(), HydroPump(), IceBeam(), UTurn()],
    status=blank_status,
    legendary=False,
    is_chosen=False,
    has_moved=False
)

# Pokemon objects
#charizard = Pokemon("Charizard", fire_type, Flying, 78, 84, 78, 109, 85, 100, [flare_blitz, air_slash, dragon_claw, heat_wave], False, False)
