from abc import ABC, abstractmethod
from random import uniform, random, randint




# if __name__ == "__main__":
#     start()
#     game()



# def start(n:int, m:int, player_lvl:int)-> tuple["Board","Player"]:

class Board():
    def __init__(self, rows:int,cols:int,grid: list[list[tuple["Entity"| None, bool]]],start: tuple[int,int],goal:tuple[int,int]) -> None:
        self.rows = rows
        self.cols = cols
        self.grid = grid
        self.start = start
        self.goal = goal

    def place(self,entity:Entity, pos: tuple[int,int]) -> None:
        self.grid[[pos]] = self.entity
        
    def entity_at(self, pos: tuple[int, int]) -> Entity | None:
        return self.grid[[pos]]
    
    def in_bounds(self, pos: tuple[int, int]) -> bool
        





class Entity(ABC):
    def __init__(self,position: tuple[int, int]) -> None:
        self.position = position
    
    @abstractmethod
    def symbol(self) -> str:
        pass


class Damageable(ABC):
    def __init__(self, hp: float, max_hp: float) -> None:
        self.hp = hp
        self.max_hp = max_hp
    
    def is_alive(self) -> bool:
        if self.hp > 0:
            return True
        else:
            return False
    
    def heal(self, amount: float) -> float:
        self.hp = self.hp + amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp
        return self.hp
    
    def take_damage(self, amount: float) -> float:
        self.hp = self.hp - amount
        return amount


class Attacker(ABC):
    @abstractmethod
    def attack(self, target: Damageable) -> float:
        pass
        
# class Player(Entity,Damageable,Attacker):
#     def __init__(self,lvl:int,weapon:Weapon,inventory: dict[str,int], statuses: dict[str,int], rage:float = 1.0, accuracy:float=1.0,) -> None:
#         self.lvl = lvl
#         self.weapon = weapon
#         self.inventory = inventory
#         self.statuses = statuses
#         self.rage = rage
#         self.accuracy = accuracy
    
#     def move(self,d_row:int, d_col:int) -> None:
        

class Bonus(ABC, Entity):

    @abstractmethod
    def apply(self, player: 'Player') -> None:
        pass


class Weapon(ABC):
    def __init__(self, name:str,max_damage:float) -> None:
        self.name = name
        self.max_damage = max_damage
    
    @abstractmethod
    def roll_damage(self) -> float:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass


class MeleeWeapon(Weapon):
    def is_available(self) -> bool:
        pass

    def roll_damage(self) -> float:
        w_damage = uniform(0, self.max_damage)
        return w_damage
       
    def damage(self,rage: float) -> float:
        if self.roll_damage() * rage <= self.max_damage:
            return self.roll_damage() * rage 
        else:
            return self.max_damage

     
class RangedWeapon(Weapon):
    def is_available(self) -> bool:
        pass

    def __init__(self,ammo:int)-> None:
        self.ammo = ammo
    
    def roll_damage(self) -> float:
        w_damage = uniform(0, self.max_damage)
        return w_damage
    
    def consume_ammo(self, n: int = 1) -> bool:
        if n <= self.ammo:
            return True
        else:
            return False
    
    def damage(self, accuracy: float) -> float:
        if self.consume_ammo() is True: 
            if self.roll_damage() * accuracy <= self.max_damage:
                return accuracy * self.roll_damage()
            else:
                return self.max_damage
        else:
            return "Увы, ваш боезапас пуст!"


class Fist(MeleeWeapon):
    def __init__(self) -> None:
        self.name:str = "Кулак"
        self.max_damage:float = 20

    def is_available(self) -> bool:
        pass

    def damage(self,rage: float) -> float:
        if self.roll_damage() * rage <= self.max_damage:
            return self.roll_damage() * rage 
        else:
            return self.max_damage


class Stick(MeleeWeapon):
    def __init__(self) -> None:
        self.name:str = "Палка"
        self.max_damage:float = 25
        self.durability:int = uniform(10,20)
    
    def is_available(self) -> bool:
        if self.durability > 0:
            return True
        else:
            return False
    
    def damage(self,rage: float) -> float:
        if self.roll_damage() * rage <= self.max_damage:
            self.durability = self.durability - 1
            return self.roll_damage() * rage 
        else:
            return self.max_damage


class Bow(RangedWeapon):
    def __init__(self) -> None:
        self.name:str = "Лук"
        self.max_damage:float = 35
        self.ammo:int = uniform(10,15)

    def is_available(self) -> bool:
        if self.ammo > 0:
            return True
        else:
            return False
        
    def damage(self, accuracy: float) -> float:
        if self.consume_ammo() is True: 
            if self.roll_damage() * accuracy <= self.max_damage:
                self.ammo = self.ammo - 1
                return accuracy * self.roll_damage()
            else:
                return self.max_damage
        else:
            return "Увы, ваш боезапас пуст!"


class Revolver(RangedWeapon):
    def __init__(self) -> None:
        self.name:str = "Револьер"
        self.max_damage:float = 45
        self.ammo:int = uniform(5,10)
    
    def is_available(self) -> bool:
        if self.ammo > 0:
            return True
        else:
            return False
    
    def damage(self, accuracy: float) -> float:
        if self.consume_ammo() is True: 
            if self.roll_damage() * accuracy <= self.max_damage:
                self.ammo = self.ammo - 1
                return accuracy * self.roll_damage()
            else:
                return self.max_damage
        else:
            return "Увы, ваш боезапас пуст!"
        
class Medkit(Bonus):
    def __init__(self):
        self.power = uniform(10,40)
    
    def apply(self, player: 'Player') -> None:
        #if in boi:
        player.hell(self.power) 
        #else
        if "Medkit" in player.inventory:
            player.invetory["Medkit"] += 1
        else:
            player.invetory[self] = 1

class Rage(Bonus):
    def __init__(self):
        self.multiplier = uniform(0.1,1.0)

    def apply(self, player: 'Player') -> None:
        #if in boi:
        player.rage += self.multiplier
        #после боя вернуть обратно 
        #else
        if "Rage" in player.inventory:
            player.invetory["Rage"] += 1
        else:
            player.invetory["Rage"] = 1


class Arrows(Bonus): # нельзя купить
    def __init__(self):
        self.amount = uniform(1,20)

    def apply(self, player: 'Player') -> None:
        if isinstance(player.weapon,Bow):
            player.inventory["BowAmmo"] += self.amount
        else:
            if "Arrows" in player.inventory:
                player.invetory["Arrows"] += 1
            else:
                player.invetory["Arrows"] = 1

class Bullets(Bonus):
    def __init__(self) -> None:
        self.amount = uniform(1,10)

    def apply(self, player: 'Player') -> None:
        if isinstance(player.weapon,Revolver):
            player.inventory["RevAmmo"] += self.amount
        else:
            if "Bullets" in player.inventory:
                player.invetory["Bullets"] += 1
            else:
                player.invetory["Bullets"] = 1

class Accuracy(Bonus):
    def __init__(self):
        self.multiplier = uniform(0.1,1.0)
        self.price:int = 50

    def apply(self, player: 'Player') -> None:
        #if in boi:
        player.accuracy += self.multiplier
        #после боя вернуть обратно 
        #else
        if "Accuracy" in player.inventory:
            player.invetory["Accuracy"] += 1
        else:
            player.invetory["Accuracy"] = 1


class Coins(Bonus):
    def __init__(self):
        self.amount = uniform(50,100)

    def apply(self, player: 'Player') -> None:
        if "Coins" in player.inventory:
            player.inventory["Coins"] += self.amount
        else:
             player.inventory["Coins"] = self.amount


class Structure(ABC, Entity):
    @abstractmethod
    def interact(self, player: 'Player') -> None:
        pass

class Tower(Structure):
    def __init(self):
        self.reveal_radius: int = 2
  #  def interact(self, board: "Board") -> None):

class Enemy(ABC, Entity, Damageable, Attacker):
    def __init__( self, lvl:int, max_enemy_damage:float,reward_coins: int)-> None:
        self.lvl = lvl
        self.max_enemy_damage = max_enemy_damage
        self.reward_coins = reward_coins

    @abstractmethod
    def before_turn(self, player: 'Player') -> None:
        pass
    def roll_enemy_damage(self) -> float:
        return uniform(0,self.max_enemy_damage)
    

class Rat(Enemy):
    def __init__(self):
        self.infection_chance: float = 0.25
        self.flee_chance_low_hp: float = 0.10
        self.flee_threshold: float = 0.15 #доля HP, при которой возможен побег.
        self.infection_damage_base: float = 5.0
        self.infection_turns: int = 3
        self.reward_coins: int = 200
    
    def before_turn(self, player: "Player") -> None:
        a = randint(1,1/self.flee_threshold)
        if a == 1:
            if self.hp == 0.15 * 100 * (1 + self.lvl / 10):
                #крыса убегает
                pass
        else:
            pass
        b = randint(1,1/self.infection_chance)
        if b == 1:
            #крыса должна дополнительно в начале снимать
            if "infection" in player.statusses:
                player.statusses["infection"] += self.turns
            else: 
                player.statusses["infection"] = self.turns

    def attack(self, target: Damageable) -> float:
        target.take_damage(0,15 * (1 + self.lvl / 10)))
        return uniform(0,15 * (1 + self.lvl / 10))
    
class Spider(Enemy):
    poison_chance: float = 0.10
    summon_chance_low_hp: float = 0.10
    poison_damage_base: float = 15.0
    poison_turns: int = 2
    reward_coins: int = 250

    def before_turn(self, player: "Player") -> None:
        pass
    def attack(self, target: Damageable) -> float:
        target.take_damage(uniform(0,20 * (1 + self.lvl / 10)))
        return uniform(0,20 * (1 + self.lvl / 10))

class Skeleton(Enemy):
    def __init__(self,weapon:Weapon):
        self.reward_coins: int = 150

    def before_turn(self, player: "Player") -> None:
        pass

    def attack(self, target: Damageable) -> float:
            target.damage(self.weapon.damage())
            return self.weapon.damage()
  
    def drop_loot(self, player: "Player") -> Weapon | None:
        if isinstance(self.weapon, Fist):
            pass
        else:
            #опустить оружие

        







        
    

        
