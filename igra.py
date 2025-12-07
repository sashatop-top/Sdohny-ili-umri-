from abc import ABC, abstractmethod
from random import uniform, randint, choice,random
from pathlib import Path
import json

CLASS_SERIALIZE = {}
def register_class(cls):
    CLASS_SERIALIZE[cls.__name__] = cls
    return cls


class Entity(ABC):
    def __init__(self,position: tuple[int, int] = (0,0)) -> None:     
        self.position = position
    
    @abstractmethod
    def symbol(self) -> str:
        pass

@register_class
class Board():
    def __init__(self, rows:int,cols:int,grid: list[list[tuple[Entity| None, bool]]],start: tuple[int,int],goal:tuple[int,int]) -> None:
        self.rows = rows
        self.cols = cols
        self.grid = grid
        self.start = start
        self.goal = goal

    def place(self,entity:Entity, pos: tuple[int,int]) -> None:
        coors = self.grid[pos[0]][pos[1]]
        self.grid[pos[0]][pos[1]] = [entity, coors[1]]
        
    def entity_at(self, pos: tuple[int, int]) -> Entity | None:
        coors = self.grid[pos[0]][pos[1]]
        return coors[0]
    
    def in_bounds(self, pos: tuple[int, int]) -> bool:
        if pos[0] < self.rows and pos[1] < self.cols and pos[0]>=0 and pos[1] >= 0:
            return True
        else:
            return False
    def render(self, player: "Player") -> None:
        for i in range(self.rows):
            for y in range(self.cols):
                coors = self.grid[i][y]
                if (i,y) == player.position and isinstance(self.entity_at((i,y)), Enemy):
                    print(f'|{player.symbol()},{Spider().symbol()}|', end = "")
                elif (i,y) == player.position and isinstance(self.entity_at((i,y)), Bonus):
                    print(f'|{player.symbol()},{Medkit().symbol()}|', end = "")
                elif (i,y) == player.position and isinstance(self.entity_at((i,y)), Weapon):
                    print(f'|{player.symbol()},{Fist().symbol()}|', end = "")
                elif (i,y) == player.position and isinstance(self.entity_at((i,y)), Tower):
                    print(f'|{player.symbol()},{Tower().symbol()}|', end = "")
                elif (i,y) == player.position and self.entity_at((i,y)) == None:
                    print(f'|{player.symbol()}|', end = " ")
                else:
                    if coors[1] == True:
                        if isinstance(self.entity_at((i,y)), Enemy):
                            print(f'|{Spider().symbol()}|', end =' ')
                        elif isinstance(self.entity_at((i,y)), Bonus):
                            print(f'|{Medkit().symbol()}|', end =' ')
                        elif isinstance(self.entity_at((i,y)), Weapon):
                            print(f'|{Fist().symbol()}|', end =' ')
                        elif isinstance(self.entity_at((i,y)), Tower):
                            print(f'|{Tower().symbol()}|', end =' ')
                        else:
                            print("| |", end =' ')
                    else:
                        print("|X|",end =' ')
            print("\n")

    def save_board(self):
        grid_dict = {}
        for i in range(self.rows):
            for y in range(self.cols):
                coors = self.grid[i][y]
                if coors[0] != None:
                    grid_dict[f'({i},{y})'] = [coors[0].to_dict(), coors[1]]
                else:
                    grid_dict[f'({i},{y})'] = [coors[0], coors[1]]


        board_dict = {"rows": self.rows,
                      'cols': self.cols,
                      'grid': grid_dict,
                      'start': self.start,
                      'goal': self.goal}
        return board_dict
    
    @classmethod
    def from_dict(cls, d):
        return cls(**d)

class Damageable(ABC):
    def __init__(self, hp: float, max_hp: float) -> None:
        self.hp = hp
        self.max_hp = max_hp
        super().__init__()
    
    def is_alive(self) -> bool:
        if self.hp > 0:
            return True
        else:
            return False
    
    def heal(self, amount: float) -> float:
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp
        return amount
    
    def take_damage(self, amount: float) -> float:
        if self.hp - amount >= 0:
            self.hp = self.hp - amount
        else:
            self.hp = 0
        return amount


class Attacker(ABC):
    @abstractmethod
    def attack(self, target: Damageable) -> float:
        pass

@register_class       
class Player(Entity,Damageable,Attacker):
    def __init__(self, lvl:int,weapon:"Weapon",inventory: dict[str,int], statuses: dict[str,int], hp: float = 200, max_hp: float = 200, position: tuple = (0,0), rage:float = 1.0, accuracy:float=1.0, fight: bool = False) -> None:
        self.lvl = lvl
        Entity.__init__(self, position = position)
        Damageable.__init__(self, hp =150*(1+self.lvl/10), max_hp = 150*(1+self.lvl/10))
        self.weapon = weapon
        self.inventory = inventory
        self.statuses = statuses
        self.rage = rage
        self.accuracy = accuracy
        self.fight = fight
        self.position = position
        self.hp = hp 
        self.max_hp = max_hp

    
    def del_inventory(self):
        for key in list(self.inventory.keys()):
            if self.inventory[key] <= 0:
                del self.inventory[key]
    def move(self,d_row:int, d_col:int) -> None:
        self.position = (d_row, d_col)

    def attack(self, target: Damageable) -> float:
        if isinstance(self.weapon, RangedWeapon): 
            amount = round(self.weapon.damage(self.accuracy),2)
            return target.take_damage(amount)
        elif isinstance(self.weapon,MeleeWeapon):
            amount = round(self.weapon.damage(self.rage),2)
            return target.take_damage(amount)
    
    def choose_weapon(self,new_weapon: "Weapon") -> None:
        self.weapon = new_weapon
        print("Вы взяли новое оружие!")

    def apply_status_tick(self) -> float:
        amount = 0
        for key in self.statuses:
            if key == "Infection":
                amount += 5*(1+self.lvl/10)
                self.statuses["Infection"] -=1
            if key == "Poison":
                amount += 15*(1+self.lvl/10)
                self.statuses["Poison"] -=1

        
        return self.take_damage(amount)
    
    def add_coins(self, amount: int) -> None:
        if "Coins" in self.inventory:
            self.inventory["Coins"] += amount
        else:
            self.inventory["Coins"] = amount

    def use_bonus(self, bonus: "Bonus") -> None:
        bonus.apply(self)
    
    def buy_auto_if_needed(self, bonus: str) -> "Bonus":
        self.use_bonus(bonus)

    def symbol(self) -> str:
        return "P"
    
    def change_fight(self) -> None:
        if self.change_fight == True:
            self.change_fight = False
        else:
            self.change_fight = True
    
    def save_player(self):
        player_dict = {'lvl' : self.lvl, 
                    'weapon' : self.weapon.to_dict(),
                    'inventory': self.inventory,
                    'statuses': self.statuses,
                    'rage': self.rage,
                    'accuracy': self.accuracy,
                    'position': self.position,
                    'fight': self.fight,
                    'hp': self.hp, 
                    'max_hp': self.max_hp}

        return player_dict
    
    @classmethod
    def from_dict(cls, d):
        return cls(**d)


class Bonus(Entity):
    @abstractmethod
    def apply(self, player: 'Player') -> None:
        pass

    def symbol(self):
        return "B"
    
class Weapon(Entity):
    def __init__(self, name:str,max_damage:float) -> None:
        self.name = name
        self.max_damage = max_damage
    
    @abstractmethod
    def roll_damage(self) -> float:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass

    def symbol(self):
        return "W"

class MeleeWeapon(Weapon):
    def is_available(self) -> bool:
        pass

    def roll_damage(self) -> float:
        w_damage = round(uniform(0, self.max_damage),2)
        return w_damage
       
    def damage(self,rage: float) -> float:
        uron = round(self.roll_damage() * rage,2)
        if uron <= self.max_damage:
            return uron
        else:
            return self.max_damage
     
class RangedWeapon(Weapon):
    def is_available(self) -> bool:
        pass

    def __init__(self,ammo:int)-> None:
        self.ammo = ammo
    
    def roll_damage(self) -> float:
        w_damage = round(uniform(0, self.max_damage),2)
        return w_damage
    
    def consume_ammo(self, n: int = 1) -> bool:
        if n <= self.ammo:
            return True
        else:
            return False
    
    def damage(self, accuracy: float = 1) -> float:
        if self.consume_ammo() is True:
            uron = self.roll_damage() * accuracy
            if uron <= self.max_damage:
                return accuracy * self.roll_damage()
            else:
                return self.max_damage

@register_class
class Fist(MeleeWeapon):
    def __init__(self) -> None:
        self.name:str = "Fist"
        self.max_damage:float = 20
    
    def __str__(self):
        return self.name

    def is_available(self) -> bool:
        True

    def damage(self,rage: float) -> float:
        return super().damage(rage)

    def to_dict(self):
        return self.__dict__
    
    @classmethod
    def from_dict(cls, d):
        return cls(**d)

@register_class
class Stick(MeleeWeapon):
    def __init__(self) -> None:
        self.name:str = "Stick"
        self.max_damage:float = 25
        self.durability:int = uniform(10,20)
    
    def __str__(self):
        return self.name
    
    def is_available(self) -> bool:
        if self.durability > 0:
            return True
        else:
            return False
    
    def damage(self,rage: float = 1) -> float:
        uron = self.roll_damage() * rage
        if uron <= self.max_damage:
            self.durability = self.durability - 1
            return uron
        else:
            return self.max_damage

    def to_dict(self):
        return self.__dict__
    
    @classmethod
    def from_dict(cls, d):
        return cls(**d)

@register_class
class Bow(RangedWeapon):
    def __init__(self) -> None:
        self.name:str = "Bow"
        self.max_damage:float = 35
        self.ammo:int = randint(10,15)
    
    def __str__(self):
        return self.name

    def is_available(self) -> bool:
        if self.ammo > 0:
            return True
        else:
            return False
        
    def damage(self, accuracy: float = 1) -> float:
        if self.consume_ammo() is True: 
            uron = self.roll_damage() * accuracy
            if uron <= self.max_damage:
                self.ammo = self.ammo - 1
                return uron
            else:
                return self.max_damage

    def to_dict(self):
        return self.__dict__
    
    @classmethod
    def from_dict(cls, d):
        return cls(**d)


@register_class
class Revolver(RangedWeapon):
    def __init__(self) -> None:
        self.name:str = "Revolver"
        self.max_damage:float = 45
        self.ammo:int = randint(5,10)
    
    def __str__(self):
        return self.name
    
    def is_available(self) -> bool:
        if self.ammo > 0:
            return True
        else:
            return False
    
    def damage(self, accuracy: float = 1) -> float:
        if self.consume_ammo() is True: 
            uron = self.roll_damage() * accuracy
            if uron <= self.max_damage:
                self.ammo = self.ammo - 1
                return uron
            else:
                return self.max_damage

    def to_dict(self):
        return self.__dict__
    
    @classmethod
    def from_dict(cls, d):
        return cls(**d)

@register_class       
class Medkit(Bonus):
    def __init__(self):
        self.power = round(uniform(10,40),2)
        self.price: int = 75
        self.name = 'Medkit'
    
    def __str__(self) -> None:
        return "Medkit"
    
    def apply(self, player: 'Player') -> None:
        if player.fight == True:
            player.heal(self.power) 
            if self.__str__() in player.inventory:
                player.inventory[self.__str__()] -= 1
                player.del_inventory()
            else:
                if player.inventory["Coins"] >= self.price:
                    player.inventory["Coins"] -= self.price
                    player.del_inventory()
                else: 
                    print("Не хватает денег!")
        else:
            if self.__str__() in player.inventory:
                player.inventory[self.__str__()] += 1
            else:
                player.inventory[self.__str__()] = 1

    def to_dict(self):
        return self.__dict__
    
    @classmethod
    def from_dict(cls, d):
        return cls(**d)

@register_class
class Rage(Bonus):
    def __init__(self):
        self.multiplier = round(uniform(0.1,1.0),2)
        self.price: int = 50
        self.name = 'Rage'

    def __str__(self) -> None:
        return "Rage"

    def apply(self, player: 'Player') -> None:
        if player.fight == True:
            player.rage += self.multiplier
            if self.__str__() in player.inventory:
                player.inventory[self.__str__()] -= 1
                player.del_inventory()
            else:
                if player.inventory["Coins"] >= self.price:
                    player.inventory["Coins"] -= self.price
                    player.del_inventory()
                else: 
                    print("Не хватает денег!")
        else:
            if self.__str__() in player.inventory:
                player.inventory[self.__str__()] += 1
            else:
                player.inventory[self.__str__()] = 1

    def to_dict(self):
        return self.__dict__
    
    @classmethod
    def from_dict(cls, d):
        return cls(**d)

@register_class
class Arrows(Bonus): # нельзя купить
    def __init__(self):
        self.amount = randint(1,20)
        self.name = 'Arrows'

    def __str__(self) -> None:
        return "Arrows"
    
    def apply(self, player: 'Player') -> None:
        if isinstance(player.weapon,Bow):
            if player.fight == True:
                player.inventory["BowAmmo"] += self.amount
                player.inventory[self.__str__]-=1
                player.del_inventory()
            else:
                player.inventory["BowAmmo"] += self.amount
        else:
            if self.__str__() in player.inventory:
                player.inventory[self.__str__()] += 1
            else:
                player.inventory[self.__str__()] = 1

    def to_dict(self):
        return self.__dict__
    
    @classmethod
    def from_dict(cls, d):
        return cls(**d)

@register_class
class Bullets(Bonus):
    def __init__(self) -> None:
        self.amount = randint(1,10)
        self.name = 'Bullets'

    def __str__(self) -> None:
        return "Bullets"
    
    def apply(self, player: 'Player') -> None:
        if isinstance(player.weapon,Revolver):
            if player.fight == True:
                player.inventory["RevAmmo"] += self.amount
                player.inventory[self.__str__()]-=1
                player.del_inventory()
            else:
                player.inventory["RevAmmo"] += self.amount
        else:
            if  self.__str__() in player.inventory:
                player.inventory[self.__str__()] += 1
            else:
                player.inventory[self.__str__()] = 1

    def to_dict(self):
        return self.__dict__
    
    @classmethod
    def from_dict(cls, d):
        return cls(**d)

@register_class
class Accuracy(Bonus):
    def __init__(self):
        self.multiplier = uniform(0.1,1.0)
        self.price:int = 50
        self.name = 'Accuracy'

    def __str__(self) -> None:
        return "Accuracy"

    def apply(self, player: 'Player') -> None:
        if player.fight == True:
            old_accuracy = player.accuracy #после боя вернуть обратно
            player.accuracy += self.multiplier
            if self.__str__() in player.inventory:
                player.inventory[self.__str__()] -= 1
                player.del_inventory()
            else:
                if player.inventory["Coins"] >= self.price:
                    player.inventory["Coins"] -= self.price
                    player.del_inventory()
                else: 
                    print("Не хватает денег!")
        else:
            if  self.__str__()  in player.inventory:
                player.inventory[self.__str__()] += 1
            else:
                player.inventory[self.__str__()] = 1

    def to_dict(self):
        return self.__dict__
    
    @classmethod
    def from_dict(cls, d):
        return cls(**d)

@register_class
class Coins(Bonus):
    def __init__(self):
        self.amount = randint(50,100)
        self.name = 'Coins'
    
    def __str__(self) -> None:
        return "Coins"

    def apply(self, player: 'Player') -> None:
        if  self.__str__()  in player.inventory:
            player.inventory[self.__str__()] += self.amount
        else:
             player.inventory[self.__str__()] = self.amount
  
    def to_dict(self):
        return self.__dict__
    
    @classmethod
    def from_dict(cls, d):
        return cls(**d)

@register_class
class Structure(Entity):
    @abstractmethod
    def interact(self, board: 'Board') -> None:
        pass

    def symbol(self):
        return "T"
    
@register_class    
class Tower(Structure):
    def __init__(self):
        self.reveal_radius: int = 2
        self.name = 'Tower'
        super().__init__()

    def interact(self, board: "Board") -> None:
        circle_i = (self.position[0] - self.reveal_radius, self.position[0] + self.reveal_radius)
        circle_y = (self.position[1] -  self.reveal_radius, self.position[1] +  self.reveal_radius)
        
        for i in range(circle_i[0], circle_i[1]+1):
            for y in range(circle_y[0], circle_y[1]+1):
                if i>= 0 and y>=0 and i<= board.goal[0] and y<= board.goal[1]:
                    place = board.grid[i][y]
                    place[1] = True

    def to_dict(self):
        return self.__dict__
    
    @classmethod
    def from_dict(cls, d):
        return cls(**d)


@register_class
class Enemy(Entity, Damageable, Attacker):
    def __init__( self, lvl:int, max_enemy_damage:float,reward_coins: int)-> None:
        self.lvl = lvl
        self.max_enemy_damage = max_enemy_damage
        self.reward_coins = reward_coins
        super().__init__()

    @abstractmethod
    def before_turn(self, player: 'Player') -> None:
        pass
    def roll_enemy_damage(self) -> float:
        return uniform(0,self.max_enemy_damage)
    
    def symbol(self) -> str:
        return "E"
    
@register_class
class Rat(Enemy):
    def __init__(self, name = "Rat", lvl = randint(1,10),hp = 200):
        self.name = name
        self.lvl = lvl
        self.max_damage = 15 * (1 + self.lvl / 10)
        self.infection_chance: float = 0.25
        self.flee_chance_low_hp: float = 0.10
        self.flee_threshold: float = 0.15 #доля HP, при которой возможен побег.
        self.infection_damage_base: float = 5.0
        self.infection_turns: int = 3
        self.reward_coins: int = 200
        Damageable.__init__(self, hp = 100*(1+self.lvl/10), max_hp = 100*(1+self.lvl/10))
        self.hp = hp

    def __str__(self):
        return "Rat"
    
    def before_turn(self, player: "Player") -> None:
            if self.hp <= self.flee_threshold * 100 * (1 + self.lvl / 10):
                a = randint(1,int(1/self.flee_chance_low_hp))
                if a==1:
                    player.add_coins(self.reward_coins)
                    return "Крыса убежала!"
                else:
                    pass
            b = randint(1,int(1/self.infection_chance))
            if b == 1:
                if "Infection" in player.statuses:
                    player.statuses["Infection"] += self.infection_turns
                else: 
                    player.statuses["Infection"] = self.infection_turns
                return player.apply_status_tick()

    def attack(self, target: Damageable) -> float:
        amount = round(uniform(0, 15 * (1 + self.lvl / 10)),2)
        target.take_damage(amount)
        return amount
    
    def to_dict(self):
        en_dict = {"name": self.name,
                   "lvl": self.lvl,
                   "hp": self.hp}
        return en_dict
    
    @classmethod
    def from_dict(cls, d):
        return cls(**d)
        
@register_class   
class Spider(Enemy):
    def __init__(self, hp: int = 200, name = 'Spider', lvl = randint(1,10)):
        self.name = name
        self.lvl = lvl
        self.max_damage = 20 * (1 + self.lvl / 10)
        self.poison_chance: float = 0.10
        self.summon_chance_low_hp: float = 0.10
        self.poison_damage_base: float = 15.0
        self.poison_turns: int = 2
        self.reward_coins: int = 250
        Damageable.__init__(self, hp = 100*(1+self.lvl/10), max_hp = 100*(1+self.lvl/10))
        self.hp = hp

    
    def __str__(self):
        return "Spider"

    def before_turn(self, player: "Player") -> str:
        if self.hp == 0.15 * 100 * (1 + self.lvl / 10):
                a = randint(1,int(1/self.summon_chance_low_hp))
                if a==1:
                    return Spider()
                else:
                    pass
        b = randint(1,int(1/self.poison_chance * (1 + self.lvl / 10)))
        if b == 1:
            if "Poison" in player.statuses:
                player.statuses["Poison"] += self.poison_turns
            else: 
                player.statuses["Poison"] = self.poison_turns
            return player.apply_status_tick()

    def attack(self, target: Damageable) -> float:
        amount = round(uniform(0,20 * (1 + self.lvl / 10)),2)
        target.take_damage(amount)
        return amount
    
    def to_dict(self):
        en_dict = {"name": self.name,
                   "lvl": self.lvl,
                   "hp": self.hp}
        return en_dict
    
    @classmethod
    def from_dict(cls, d):
        return cls(**d)

@register_class
class Skeleton(Enemy):
    def __init__(self,weapon:Weapon, lvl = randint(1,10), name = "Skeleton", hp = 200):
        self.name = name
        self.reward_coins: int = 150
        self.lvl = lvl
        self.max_damage = 10 * (1 + self.lvl / 10)
        self.weapon = weapon
        Damageable.__init__(self,hp = 100*(1+self.lvl/10), max_hp = 100*(1+self.lvl/10))
        self.hp = hp 


    
    def __str__(self):
        return "Skeleton"
    
    def before_turn(self, player: "Player") -> None:
        pass

    def attack(self, target: Damageable) -> float:
            if isinstance(self.weapon, RangedWeapon):
                self.weapon.ammo = 100
                amount = self.weapon.damage()
                if amount > self.max_damage:
                    amount = self.max_damage
                    target.take_damage(amount)
            elif isinstance(self.weapon, MeleeWeapon):
                if isinstance(self.weapon, Stick):
                    self.durability = 100
                amount = self.weapon.damage()
                if amount > self.max_damage:
                    amount = self.max_damage
                    target.take_damage(amount)
            return amount
  
    def drop_loot(self, player: "Player") -> Weapon | None:
        if isinstance(self.weapon, Fist):
            pass
        else:
            player.weapon = self.weapon

    def to_dict(self):
        en_dict = {"name": self.name,
                   "weapon": self.weapon.to_dict(),
                   "lvl": self.lvl,
                   "hp": self.hp}
        return en_dict
    
    @classmethod
    def from_dict(cls, d):
        return cls(**d)


def start(n,m,our_dict: dict[str:float], level: int, dificutly: str, board: Board)-> tuple["Board","Player"]:
    player_lvl = randint(1,10)
    fist = Fist()
    desk = []
    for i in range(n):
        lst = []
        for y in range(m):
            lst.append([0, False])
        desk.append(lst)
    board.grid = desk
    weapons = [Revolver(),Stick(),Bow()]
    bonuses = [Medkit(),Arrows(),Rage(),Bullets(),Accuracy(),Coins()]
    enemies = [Skeleton,Rat, Spider]
    p_tower = our_dict["tower_multiplier"]
    p_weapon = our_dict["weapon_multiplier"]
    p_enemy = our_dict["enemy_multiplier"]
    p_bonus = our_dict["bonus_multiplier"]
    for i in range(n):
        for y in range(m):
            if i == 0 and y == 0:
                board.place(None, (i,y))
                board.grid[i][y][1] = True
            elif i==n-1 and y==m-1:
                board.place(None, (i,y))
                board.grid[i][y][1] = True
            else:
                tow = [0 if k > int(n*m*p_tower) else 1 for k in range(n*m)]
                rand_tow = choice(tow)
                if rand_tow == 1:
                    board.place(Tower(), (i,y))
                    board.grid[i][y][1] = False
                else:
                    bon = [0 if k > int(n*m*p_bonus) else 1 for k in range(n*m)]
                    rand_bon = choice(bon)
                    if rand_bon == 1:
                        board.place(choice(bonuses), (i,y))
                        board.grid[i][y][1] = False
                       
                    else:
                        ene = [0 if k > int(n*m*p_enemy) else 1 for k in range(n*m)]
                        rand_ene = choice(ene)
                        if rand_ene == 1:
                            enemy = choice(enemies)
                            if enemy == Skeleton:
                                board.place(Skeleton(choice(weapons)), (i,y))
                                board.grid[i][y][1] = False
                            else:
                                board.place(choice(enemies)(), (i,y))
                                board.grid[i][y][1] = False

                        else:
                            wea = [0 if k > int(n*m*p_weapon) else 1 for k in range(n*m)]
                            rand_wea = choice(wea)
                            if rand_wea == 1:
                                board.place(choice(weapons), (i,y))
                                board.grid[i][y][1] = False
                                
                            else:
                                board.place(None, (i,y))
                                board.grid[i][y][1] = False
    desk = board.grid

   
    game(Board(n,m,desk,(0,0),(n-1,m-1)), Player(player_lvl, fist, {}, {}), level, dificutly)

def pre_game(board: Board, player: Player) -> None:
    print('Добро пожаловать в игру "Сдохни или умри!"\n')
    path = Path("save.json")
    if path.exists():
        with open("save.json", "r", encoding = "utf-8") as file:
            igra_dict = json.load(file)
            dificutly = igra_dict['dificutly']
            level = igra_dict['current_lvl']
            print(f'Ты на {level+1} уровне\nПродолжить уровень(незавершенная игра)(p) или начать новую игру(z)?\n')
            command = input()
            if command == 'p':
                player_dict = igra_dict['player']
                player = player.from_dict(player_dict)
                weapons = [Fist(), Stick(), Revolver(), Bow()]
                for wea in weapons:
                    if wea.name == (player_dict['weapon'])['name']:
                        player.weapon = wea
                board_dict = igra_dict['board']
                board = board.from_dict(board_dict)
                b_grid = board_dict['grid']
                board.grid = []
                for i in range(board.rows):
                    lst = []
                    for y in range(board.cols):
                        lst.append([0, False])
                    board.grid += [lst]

                for i in range(board.rows):
                    for y in range(board.cols):
                        coors = b_grid[f'({i},{y})']
                        entity =  coors[0]
                        status = coors[1]

                        if entity is not None:
                    
                            if entity["name"] == Skeleton(Fist()).name:
                                board.place(Skeleton(Fist()).from_dict(entity), (i,y)) #из-за кол-во hp может быть важно
                                board.grid[i][y][1] = status

                            elif entity['name'] == Rat().name:
                                board.place(Rat().from_dict(entity), (i,y))
                                board.grid[i][y][1] = status

                            elif entity['name'] == Spider().name:
                                board.place(Spider().from_dict(entity), (i,y))
                                board.grid[i][y][1] = status
                            else:
                                board.place(CLASS_SERIALIZE[entity['name']](), (i,y))
                                board.grid[i][y][1] = status
                        else:
                            board.grid[i][y][0] = None
                            board.grid[i][y][1] = status

                game(board, player, dificutly, level)

            if command == "z":
                print("Выберите уровень\neasy\nnormal\nhard")
                command = input()
                our_dict = {}
                with open("dificutly.json", "r", encoding = "utf-8") as file:
                    urov_dict = json.load(file)

                if command == 'easy':
                    with open("dificutly.json", "r", encoding = "utf-8") as file:
                        our_dict = urov_dict["easy"]
                        dificutly = "easy"
                        n = randint(our_dict['board_min'], our_dict['board_max'])
                        m = randint(our_dict['board_min'], our_dict['board_max'])
                    if Path("save.json").exists():
                        with open("save.json", "r", encoding = "utf-8") as file2:
                            save_dict = json.load(file2)
                            if save_dict["dificutly"] == 'easy':
                                level = save_dict['current_lvl']+1
                            else: 
                                level = 1
                    else:
                        level = 1
                    return n,m, our_dict, level, dificutly
                
                elif command == 'normal':
                    with open("dificutly.json", "r", encoding = "utf-8") as file:
                        our_dict = urov_dict["normal"]
                        dificutly = "normal"
                        n = randint(our_dict['board_min'], our_dict['board_max'])
                        m = randint(our_dict['board_min'], our_dict['board_max'])

                    if Path("save.json").exists():
                        with open("save.json", "r", encoding = "utf-8") as file2:
                            save_dict = json.load(file2)
                            if save_dict["dificutly"] == 'normal':
                                level = save_dict['current_lvl']+1
                            else: 
                                level = 1
                    else:
                        level = 1
                
                    return n,m, our_dict, level, dificutly


                elif command == 'hard':
                    with open("dificutly.json", "r", encoding = "utf-8") as file:
                        our_dict = urov_dict["hard"]
                        dificutly = 'hard'
                        n = randint(our_dict['board_min'], our_dict['board_max'])
                        m = randint(our_dict['board_min'], our_dict['board_max'])
        
                    if Path("save.json").exists():
                        with open("save.json", "r", encoding = "utf-8") as file2:
                            save_dict = json.load(file2)
                            if save_dict["dificutly"] == 'hard':
                                level = save_dict['current_lvl']+1
                            else: 
                                level = 1
                    else:
                        level = 1
            
                    return n,m, our_dict, level, dificutly
                        
                
    else:
        print("Выберите уровень\neasy\nnormal\nhard")
        command = input()
        our_dict = {}
        with open("dificutly.json", "r", encoding = "utf-8") as file:
            urov_dict = json.load(file)

            if command == 'easy':
                with open("dificutly.json", "r", encoding = "utf-8") as file:
                    our_dict = urov_dict["easy"]
                    dificutly = "easy"
                    n = randint(our_dict['board_min'], our_dict['board_max'])
                    m = randint(our_dict['board_min'], our_dict['board_max'])
                if Path("save.json").exists():
                    with open("save.json", "r", encoding = "utf-8") as file2:
                        save_dict = json.load(file2)
                        if save_dict["dificutly"] == 'easy':
                            level = save_dict['current_lvl']+1
                        else: 
                            level = 1
                else:
                    level = 1
                return n,m, our_dict, level, dificutly
                
            elif command == 'normal':
                with open("dificutly.json", "r", encoding = "utf-8") as file:
                    our_dict = urov_dict["normal"]
                    dificutly = "normal"
                    n = randint(our_dict['board_min'], our_dict['board_max'])
                    m = randint(our_dict['board_min'], our_dict['board_max'])

                if Path("save.json").exists():
                    with open("save.json", "r", encoding = "utf-8") as file2:
                        save_dict = json.load(file2)
                        if save_dict["dificutly"] == 'normal':
                            level = save_dict['current_lvl']+1
                        else: 
                            level = 1
                else:
                    level = 1
                
                return n,m, our_dict, level, dificutly


            elif command == 'hard':
                with open("dificutly.json", "r", encoding = "utf-8") as file:
                    our_dict = urov_dict["hard"]
                    dificutly = 'hard'
                    n = randint(our_dict['board_min'], our_dict['board_max'])
                    m = randint(our_dict['board_min'], our_dict['board_max'])
        
                if Path("save.json").exists():
                    with open("save.json", "r", encoding = "utf-8") as file2:
                        save_dict = json.load(file2)
                        if save_dict["dificutly"] == 'hard':
                            level = save_dict['current_lvl']+1
                        else: 
                            level = 1
                else:
                    level = 1
            
                return n,m, our_dict, level, dificutly

    
def game(board: Board, player: Player, level: int, dificutly: int) -> None:
    print('Команды:\n w - вперед \n a - налево \n d - направо \n s - назад \n f - атака \n i - Посмотреть инвентарь\n x - Посмотреть оружие\n')
    print(board.grid)
    print(player.position)
    i=player.position[0]
    y=player.position[1]
    coors = board.grid[i][y]
      
    while player.position[0] != board.goal[0] or  player.position[1] != board.goal[1] :

        command = input()


        if command == "exit":
            dict_igra = {'current_lvl': level,
                         'dificutly': dificutly,
                         'player': player.save_player(),
                         'board': board.save_board()}
            igra_string = json.dumps(dict_igra, ensure_ascii=False)
            with open ("save.json", "w", encoding = "utf-8") as file:
                file.write(igra_string)
            print("Вы вышли из игры!")
            break

        if command == "y":
            player.choose_weapon(coors[0])
            if isinstance(coors[0], Revolver):
                player.inventory["RevAmmo"] = coors[0].ammo
            elif isinstance(coors[0], Bow):
                player.inventory["BowAmmo"] = coors[0].ammo    
            coors[0] = None
        
        elif command == "x":
            print(player.weapon)
        
        elif command == "i":
            for key in player.inventory:
                print(f"{key} - {player.inventory[key]}")
      
        elif command == "w":
            if board.in_bounds((i+1,y)):
                player.move(i+1,y)
                print("Вы пошли вперед!")
                coors[1] = True
                board.render(player)
            else:
                 print("не удалось пойти")
            
        
        elif command == "a":
            if board.in_bounds((i,y+1)):
                player.move(i,y+1)
                print("Вы пошли налево!")
                coors[1] = True
                board.render(player)
            else:
                print("не удалось пойти")
            

        elif command == "d":
            if board.in_bounds((i,y-1)) and y>0:
                player.move(i,y-1)
                print("Вы пошли направо!")
                coors[1] = True
                board.render(player)
            else:
                print("не удалось пойти")

        elif command == "s":
            if board.in_bounds((i-1,y)) and i>0:
                player.move(i-1,y)
                print("Вы пошли назад!")
                coors[1] = True
                board.render(player)
            else:
                print("не удалось пойти")
        
        i=player.position[0]
        y=player.position[1]
        coors = board.grid[i][y]

            
        if isinstance(coors[0], Tower):
            print("\033[1;33m Tower!\033[0m \n")
            coors[0].position = (i,y)
            coors[0].interact(board)
            board.render(player)
            print("Открыты новые поля!\n")
           
        
        elif isinstance(coors[0], Bonus):
            print(f"\033[1;32m {coors[0]}!\033[0m\n")
            coors[0].apply(player)
            coors[0] = None
        
        elif isinstance(coors[0], Weapon):
            print(f"\033[1;32m {coors[0]}!\033[0m\n")
            print("Взять это оружие? y\n")
        
        elif isinstance(coors[0], Enemy):
            ulala = 0
            counter = 0
            print(f"\033[1;31m{coors[0]}!\033[0m\n")
            player.fight = True
            while player.is_alive() and coors[0].is_alive():
                old_rage = player.rage
                old_accuracy = player.accuracy
                if isinstance(player.weapon, MeleeWeapon):
                    print("Использовать бонус? y,n\nПри n будет выполнена атака без бонуса\n" )
                    command = input()
                    if command == "y":
                        bonuses = {"Rage":50, "Medkit":75}
                        for bon in bonuses:
                            if bon in player.inventory:
                                print(f"{bon} - {player.inventory[bon]} thing")
                            else:
                                 print(f"{bon} - {bonuses[bon]} coins")
                        if "Coins" in player.inventory:
                            print(f"You have {player.inventory['Coins']} coins\n")
                        else:
                            print("You have no money!\n")
                        print(f"medkit - m\nRage - r\n")

                        command = input()
                        if command == "m": 
                            if "Medkit" not in player.inventory:
                                player.buy_auto_if_needed(Medkit())
                                print(f"\033[1;32m +{player.heal(Medkit().power)}!\033[0m\n")
                            else:
                                player.use_bonus(Medkit())
                                print(f"\033[1;32m +{player.heal(Medkit().power)}!\033[0m\n")
                        elif command == "r":
                            if "Rage" not in player.inventory:
                                    player.buy_auto_if_needed(Rage())
                                    print("You use Rage!")
                            else:
                                player.use_bonus(Rage())
                                print("You use Rage!")

                        for item in player.statuses:
                            if player.statuses[item] > 0:
                                player.statuses[item] -=1
                                print(f"\033[1;31m {item}! {round(player.apply_status_tick(),2)}\033[0m\n")
                        if player.weapon.is_available():
                            print(f" You attack! {round(player.attack(coors[0]),2)}\n")
                        else:
                            player.weapon = Fist()
                            print(f" You attack! {round(player.attack(coors[0]),2)}\n")
                        

                    elif command == "n":
                        for item in player.statuses:
                            if player.statuses[item] > 0:
                                player.statuses[item] -=1
                                print(f"\033[1;31m {item}! {round(player.apply_status_tick(),2)}\033[0m\n")
                        if player.weapon.is_available():
                            print(f"You attack! {round(player.attack(coors[0]),2)}\n")
                        else:
                            player.weapon = Fist()
                            print(f"You attack! {round(player.attack(coors[0]),2)}\n")
                        
                elif isinstance(player.weapon, RangedWeapon):
                    print("Использовать бонус? y,n\n")
                    command = input()
                    if command == "y":
                        bonuses = {"Accuracy":50, "Medkit":75, "Bullets": -10, "Arrows": -10}
                        for bon in bonuses:
                            if bon in player.inventory:
                                print(f"{bon} - {player.inventory[bon]} thing")
                            else:
                                if bonuses[bon] != -10:
                                    print(f"{bon} - {bonuses[bon]} coins")
                                else:
                                    print(f"{bon} - Нельзя купить!")
                        if "Coins" in player.inventory:
                            print(f"You have {player.inventory['Coins']} coins\n")
                        else:
                            print("You have no money!\n")
                        print(f"medkit - m\nAccuracy - ac\nBullets - b\nArrows\n")
                        if command == "m":
                            if "Medkit" not in player.inventory:
                                player.buy_auto_if_needed(Medkit())
                                print(f"\033[1;32m +{player.heal(Medkit().power)}!\033[0m\n")
                            else:
                                player.use_bonus(Medkit())
                                print(f"\033[1;32m +{player.heal(Medkit().power)}!\033[0m\n")
                        elif command == "ac":
                            if "Accuracy" not in player.inventory:
                                    player.buy_auto_if_needed(Accuracy())
                                    print("You use Accuracy!")
                            else:
                                player.use_bonus(Accuracy())
                                print("You use Accuracy!")
                        elif command == "b":
                            player.use_bonus(Bullets())
                            print(f"\033[1;32m +{Bullets().amount}!\033[0m\n")
                            print("You use Bullets!")
                        elif command == "ar":
                            player.use_bonus(Arrows())
                            print(f"\033[1;32m +{Arrows().amount}!\033[0m\n")
                            print("You use Bullets!")
                        for item in player.statuses:
                            if player.statuses[item] > 0:
                                player.statuses[item] -=1
                                print(f"\033[1;31m {item}! {round(player.apply_status_tick(),2)}\033[0m\n")
                        if player.weapon.is_available():
                                print(f"You attack! {round(player.attack(coors[0]),2)}\n")
                        else:
                            player.weapon = Fist()
                            print(f"You attack! {round(player.attack(coors[0]),2)}\n")
                    
                    elif command == "n":
                        for item in player.statuses:
                            if player.statuses[item] > 0:
                                player.statuses[item] -=1
                                print(f"\033[1;31m {item}! {round(player.apply_status_tick(),2)}\033[0m\n")
                        if player.weapon.is_available() and not isinstance(player.weapon,Fist):
                            print(f"You attack! {round(player.attack(coors[0]),2)}\n")
                        else:
                            player.weapon = Fist()
                            print(f"You attack! {round(player.attack(coors[0]),2)}\n")
                        
                player.accuracy = old_accuracy
                player.rage = old_rage

                opa = coors[0].before_turn(player)

                if opa == "Крыса убежала!":
                    print(f"{coors[0].before_turn(player)}\n")
                    player.add_coins(coors[0].reward_coins)
                    coors[0] = None
                    break
                
                elif opa == player.apply_status_tick() and isinstance(coors[0], Rat):
                    print(f"\033[1;31m О нет! Вас инфецировали на несколько ходов! Damage! {round(coors[0].attack(player),2)}\033[0m\n")
                
                elif opa == player.apply_status_tick() and isinstance(coors[0], Spider):
                    print(f"\033[1;31m О нет! Вы отравлены на несколько ходов! Damage! {round(coors[0].attack(player),2)}\033[0m\n")

                elif isinstance(opa, Spider):
                     print(f"\033[1;31m О нет! Новый паук! Damage! {round(coors[0].attack(player),2)}\033[0m\n")
                     ulala = 1
                     counter += 1
                     spider = coors[0].before_turn(player)

                if ulala == 1:
                    if coors[0].hp == 0:
                        coors[0] = spider
                        counter-=1
                    for i in range(counter):
                        print(f"\033[1;31m Damage! {round(coors[0].attack(player),2)}\033[0m\n")

                if isinstance(coors[0],Skeleton) and coors[0].hp == 0:
                    coors[0].drop_loot(player)
                    print(f'Новое оружие!')

                print(f"\033[1;31m Damage! {round(coors[0].attack(player),2)}\033[0m\n")
                print(f"Your hp: {round(player.hp,2)}\nEnemy hp: {round(coors[0].hp,2)}\n")

            if player.hp == 0:
                print(f"\033[1;31m FATAL! Вы проиграли!\033[0m\n")
                if Path('save_json.py').exists():
                    with open('save.json', 'r', encoding = 'utf-8') as file:
                        dict_info = json.load(file)
                        dict_info['current_lvl'] = 0
                        string_info = json.dumps(dict_info)
                    with open('save.json', 'w', encoding = 'utf-8') as file:
                        file.write(string_info)
                    break
            
            elif coors[0].hp == 0:
                print(f"\033[1;32m Ура вы победили врага!\033[0m\n")
                player.add_coins(coors[0].reward_coins)
                coors[0] = None

    if player.position[0] == board.goal[0] and player.position[1] == board.goal[1]:
        print(f"\033[1;32m VICTORY!\033[0m\n")
        dict_igra = {'current_lvl': level,
                         'dificutly': dificutly,
                         'player': player.save_player(),
                         'board': board.save_board()}
        igra_string = json.dumps(dict_igra, ensure_ascii=False)
        with open ("save.json", "w", encoding = "utf-8") as file:
            file.write(igra_string)
        path2 = Path('record')
        if path2.exists():
            with open('record.json', 'r', encoding = 'utf-8') as file:
                record_dict = json.load(file)
                if record_dict['level'] < level:
                    if 'Coins' in player.inventory:
                        record_dict = {'level': level, 
                                       'coins': player.inventory["Coins"]}
                    else:
                        record_dict = {'level': level, 
                                       'coins': 0}
                    record_string = json.dumps(record_dict)
                    with open('record.json', 'w', encoding = 'utf-8') as file:
                        file.write(record_string)
                        print("New Record!")
                
                elif record_dict['level'] == level:
                    if 'Coins' in player.inventory:
                        if record_dict['coins'] < player.inventory["Coins"]:
                            record_dict = {'level': level, 
                                        'coins': player.inventory["Coins"]}
                    else:
                        record_dict = {'level': level, 
                                        'coins': 0}
                    record_string = json.dumps(record_dict)
                    with open('record.json', 'w', encoding = 'utf-8') as file:
                        file.write(record_string)
                        print("New Record!")
                
        else:
            with open('record.json', 'w', encoding = 'utf-8') as file:
                if 'Coins' in player.inventory:
                    dict_record = {'level': level, 
                                    'coins': player.inventory["Coins"]}
                else:
                    dict_record = {'level': level, 
                                    'coins': 0}
                record_string = json.dumps(dict_record)
                file.write(record_string)


if __name__ == "__main__":
    # game(start(10,10,randint(1,10))[0], start(10,10,randint(1,10))[1])
    fun = pre_game(Board(0,0,[],0,0), Player(1, Fist(), {}, {}))
    if fun != None:
        # game(start(fun[0], fun[1], fun[2])[0], start(fun[0], fun[1], fun[2])[1], fun[3], fun[4])
        start(fun[0], fun[1], fun[2], fun[3], fun[4], Board(0,0,[[]],(0,0),(0,0)))
